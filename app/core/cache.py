"""
LRU cache module for caching LLM responses and chat history.
"""

import hashlib
import json
import time
from typing import Any, Dict, List, Optional

from cachetools import LRUCache, TTLCache

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class ResponseCache:
    """
    Response cache for LLM outputs.
    
    Uses LRU cache with TTL to store and retrieve cached responses.
    """

    def __init__(self, max_size: int, ttl: int):
        """
        Initialize response cache.
        
        Parameters:
            max_size (int): Maximum number of cached items
            ttl (int): Time to live in seconds
        """
        self.enabled = get_settings().cache.enabled
        self.cache: TTLCache = TTLCache(maxsize=max_size, ttl=ttl)
        self.hits = 0
        self.misses = 0

    def _generate_key(
        self, 
        model_name: str, 
        prompt: str, 
        params: Dict[str, Any]
    ) -> str:
        """
        Generate cache key from inputs.
        
        Parameters:
            model_name (str): Name of the model
            prompt (str): Input prompt
            params (Dict[str, Any]): Generation parameters
            
        Returns:
            str: Cache key hash
        """
        # Create deterministic key from inputs
        key_data = {
            "model": model_name,
            "prompt": prompt,
            "params": params,
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_string.encode()).hexdigest()

    def get(
        self, 
        model_name: str, 
        prompt: str, 
        params: Dict[str, Any]
    ) -> Optional[str]:
        """
        Get cached response if available.
        
        Parameters:
            model_name (str): Name of the model
            prompt (str): Input prompt
            params (Dict[str, Any]): Generation parameters
            
        Returns:
            Optional[str]: Cached response or None if not found
        """
        if not self.enabled:
            return None

        key = self._generate_key(model_name, prompt, params)
        
        if key in self.cache:
            self.hits += 1
            logger.debug(f"Cache hit for key: {key[:16]}...")
            return self.cache[key]
        
        self.misses += 1
        logger.debug(f"Cache miss for key: {key[:16]}...")
        return None

    def set(
        self, 
        model_name: str, 
        prompt: str, 
        params: Dict[str, Any], 
        response: str
    ):
        """
        Store response in cache.
        
        Parameters:
            model_name (str): Name of the model
            prompt (str): Input prompt
            params (Dict[str, Any]): Generation parameters
            response (str): Model response to cache
        """
        if not self.enabled:
            return

        key = self._generate_key(model_name, prompt, params)
        self.cache[key] = response
        logger.debug(f"Cached response for key: {key[:16]}...")

    def clear(self):
        """Clear all cached items."""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
        logger.info("Cache cleared")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dict[str, Any]: Cache statistics
        """
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0.0
        
        return {
            "enabled": self.enabled,
            "size": len(self.cache),
            "max_size": self.cache.maxsize,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate_percent": round(hit_rate, 2),
        }


class ChatHistoryCache:
    """
    Chat history cache for maintaining session-based conversations.
    
    Stores message history per session_id with TTL expiration.
    """

    def __init__(self, ttl: int):
        """
        Initialize chat history cache.
        
        Parameters:
            ttl (int): Time to live in seconds for sessions
        """
        self.enabled = get_settings().chat_history.enabled
        # Use TTLCache to auto-expire old sessions
        # Set maxsize to a reasonable number (1000 sessions)
        self.cache: TTLCache = TTLCache(maxsize=1000, ttl=ttl)
        self.ttl = ttl

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        """
        Get chat history for a session.
        
        Parameters:
            session_id (str): Session identifier
            
        Returns:
            List[Dict[str, str]]: List of messages (role, content)
        """
        if not self.enabled or not session_id:
            return []

        history = self.cache.get(session_id, [])
        logger.debug(f"Retrieved {len(history)} messages for session {session_id}")
        return history

    def add_message(
        self, 
        session_id: str, 
        role: str, 
        content: str
    ):
        """
        Add a message to session history.
        
        Parameters:
            session_id (str): Session identifier
            role (str): Message role (user/assistant/system)
            content (str): Message content
        """
        if not self.enabled or not session_id:
            return

        history = self.get_history(session_id)
        history.append({
            "role": role,
            "content": content,
            "timestamp": time.time(),
        })
        self.cache[session_id] = history
        logger.debug(f"Added {role} message to session {session_id}")

    def update_history(self, session_id: str, messages: List[Dict[str, str]]):
        """
        Replace entire history for a session.
        
        Parameters:
            session_id (str): Session identifier
            messages (List[Dict[str, str]]): Complete message list
        """
        if not self.enabled or not session_id:
            return

        # Add timestamps if not present
        for msg in messages:
            if "timestamp" not in msg:
                msg["timestamp"] = time.time()
        
        self.cache[session_id] = messages
        logger.debug(f"Updated history for session {session_id} with {len(messages)} messages")

    def clear_session(self, session_id: str):
        """
        Clear history for a specific session.
        
        Parameters:
            session_id (str): Session identifier
        """
        if session_id in self.cache:
            del self.cache[session_id]
            logger.info(f"Cleared session {session_id}")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dict[str, Any]: Cache statistics
        """
        return {
            "enabled": self.enabled,
            "active_sessions": len(self.cache),
            "max_sessions": self.cache.maxsize,
            "ttl_seconds": self.ttl,
        }


# Global cache instances
_cache = None
_chat_history_cache = None


def get_cache() -> ResponseCache:
    """
    Get global cache instance.
    
    Returns:
        ResponseCache: Cache instance
    """
    global _cache
    
    if _cache is None:
        settings = get_settings()
        _cache = ResponseCache(
            max_size=settings.cache.size,
            ttl=settings.cache.ttl_seconds,
        )
    
    return _cache


def get_chat_history_cache() -> ChatHistoryCache:
    """
    Get global chat history cache instance.
    
    Returns:
        ChatHistoryCache: Chat history cache instance
    """
    global _chat_history_cache
    
    if _chat_history_cache is None:
        settings = get_settings()
        _chat_history_cache = ChatHistoryCache(
            ttl=settings.chat_history.ttl_seconds,
        )
    
    return _chat_history_cache
