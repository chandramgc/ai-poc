"""
Chat router with conversation support.

Provides chat endpoint with message history support.
"""

from typing import AsyncGenerator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.api.dependencies import APIKeyDep, RateLimitDep
from app.api.schemas import ChatMessage, ChatRequest, ChatResponse
from app.core.cache import get_cache, get_chat_history_cache
from app.core.config import get_settings
from app.core.logging import get_logger
from app.core.security import filter_content, sanitize_output, validate_prompt_length
from app.llm.loader import generate_text
from app.utils.errors import GenerationError

logger = get_logger(__name__)
router = APIRouter(prefix="/v1", tags=["chat"])


def format_chat_prompt(messages: list[ChatMessage]) -> str:
    """
    Format chat messages into a single prompt.
    
    Parameters:
        messages (list[ChatMessage]): List of chat messages
        
    Returns:
        str: Formatted prompt
    """
    prompt_parts = []
    
    for msg in messages:
        if msg.role == "system":
            prompt_parts.append(f"System: {msg.content}")
        elif msg.role == "user":
            prompt_parts.append(f"User: {msg.content}")
        elif msg.role == "assistant":
            prompt_parts.append(f"Assistant: {msg.content}")
    
    # Add assistant prefix for response
    prompt_parts.append("Assistant:")
    
    return "\n\n".join(prompt_parts)


async def generate_stream(prompt: str, **kwargs) -> AsyncGenerator[str, None]:
    """
    Generate text in streaming mode (stub for future implementation).
    
    Note: Most Hugging Face pipelines don't support true streaming.
    This is a placeholder that yields the full response.
    
    Parameters:
        prompt (str): Input prompt
        **kwargs: Generation parameters
        
    Yields:
        str: Text chunks
    """
    # TODO: Implement true streaming if model supports it
    # For now, generate full response and yield it
    logger.warning("Streaming requested but not fully supported, returning full response")
    
    generated_text = generate_text(prompt=prompt, **kwargs)
    
    # Simulate streaming by yielding in chunks
    chunk_size = 10  # words per chunk
    words = generated_text.split()
    
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i + chunk_size])
        yield f"data: {chunk}\n\n"
    
    yield "data: [DONE]\n\n"


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    api_key: APIKeyDep,
    rate_limit: RateLimitDep,
):
    """
    Chat with the LLM using conversation history.
    
    Supports multi-turn conversations with message history.
    If session_id is provided, the conversation history will be maintained
    across requests and automatically merged with the provided messages.
    
    Parameters:
        request (ChatRequest): Chat request with message history
        api_key (APIKeyDep): Validated API key
        rate_limit (RateLimitDep): Rate limit check
        
    Returns:
        ChatResponse or StreamingResponse: Chat response or stream
        
    Raises:
        GenerationError: If generation fails
    """
    settings = get_settings()
    cache = get_cache()
    history_cache = get_chat_history_cache()
    
    # Retrieve and merge session history if session_id is provided
    all_messages = []
    if request.session_id:
        # Get existing history from cache
        session_history = history_cache.get_history(request.session_id)
        
        # Convert cached history to ChatMessage objects (exclude timestamps)
        for msg in session_history:
            all_messages.append(ChatMessage(role=msg["role"], content=msg["content"]))
        
        logger.info(f"Loaded {len(session_history)} messages from session {request.session_id}")
    
    # Add current request messages
    all_messages.extend(request.messages)
    
    # Format all messages into prompt
    prompt = format_chat_prompt(all_messages)
    
    # Validate prompt
    validate_prompt_length(prompt)
    
    # Filter last user message for content safety
    last_user_message = [m for m in request.messages if m.role == "user"][-1]
    filter_content(last_user_message.content)
    
    # Handle streaming
    if request.stream:
        logger.info("Streaming response requested")
        
        return StreamingResponse(
            generate_stream(
                prompt=prompt,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
            ),
            media_type="text/event-stream",
        )
    
    # Prepare generation parameters
    gen_params = {
        "max_tokens": request.max_tokens,
        "temperature": request.temperature,
    }
    gen_params = {k: v for k, v in gen_params.items() if v is not None}
    
    # Check cache
    cached_response = cache.get(
        model_name=settings.model.name,
        prompt=prompt,
        params=gen_params,
    )
    
    if cached_response:
        logger.info("Serving chat response from cache")
        return ChatResponse(
            message=ChatMessage(role="assistant", content=cached_response),
            model=settings.model.name,
            tokens_generated=len(cached_response.split()),
            cached=True,
        )
    
    # Generate response
    try:
        logger.info("Generating chat response")
        
        generated_text = generate_text(
            prompt=prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
        )
        
        # Sanitize output
        generated_text = sanitize_output(generated_text.strip())
        
        # Cache response
        cache.set(
            model_name=settings.model.name,
            prompt=prompt,
            params=gen_params,
            response=generated_text,
        )
        
        # Save to session history if session_id is provided
        if request.session_id:
            # Add all current messages to history
            for msg in request.messages:
                history_cache.add_message(
                    session_id=request.session_id,
                    role=msg.role,
                    content=msg.content,
                )
            
            # Add assistant response to history
            history_cache.add_message(
                session_id=request.session_id,
                role="assistant",
                content=generated_text,
            )
            
            logger.info(f"Updated session {request.session_id} with new messages")
        
        logger.info(f"Successfully generated chat response: {len(generated_text)} chars")
        
        return ChatResponse(
            message=ChatMessage(role="assistant", content=generated_text),
            model=settings.model.name,
            tokens_generated=len(generated_text.split()),
            cached=False,
        )
        
    except Exception as e:
        logger.error(f"Chat generation failed: {str(e)}")
        raise GenerationError(
            message="Failed to generate chat response",
            details={"error": str(e)}
        ) from e
