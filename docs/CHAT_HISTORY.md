# Chat History Feature Documentation

## Overview

The chat history feature allows multi-turn conversations to persist across API requests using session IDs. This enables contextual conversations where the LLM can reference previous messages automatically.

## Key Features

- **Session-based persistence**: Maintain conversation history using unique `session_id`
- **Automatic context merging**: Previous messages are automatically included in each request
- **Configurable TTL**: Session history expires after a configurable time (default: 2 hours)
- **Memory efficient**: Automatic cleanup of expired sessions
- **Optional**: Works alongside existing single-turn chat without breaking changes

## Configuration

### config.yml

```yaml
chat_history:
  enabled: true
  ttl_seconds: 7200  # 2 hours (configurable)
```

### Environment Variables

```bash
# Override via environment
CHAT_HISTORY__ENABLED=true
CHAT_HISTORY__TTL_SECONDS=7200
```

## API Usage

### Basic Chat (No History)

Single-turn conversation without session persistence:

```bash
curl -X POST http://localhost:8000/v1/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "messages": [
      {"role": "user", "content": "What is Python?"}
    ]
  }'
```

### Chat with Session History

Multi-turn conversation with automatic context:

#### Turn 1: Start conversation

```bash
curl -X POST http://localhost:8000/v1/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "session_id": "user-123-chat",
    "messages": [
      {"role": "user", "content": "What is Python?"}
    ]
  }'
```

Response:
```json
{
  "message": {
    "role": "assistant",
    "content": "Python is a high-level programming language..."
  },
  "model": "google/gemma-3-1b-it",
  "tokens_generated": 50,
  "cached": false
}
```

#### Turn 2: Follow-up (automatic context)

```bash
curl -X POST http://localhost:8000/v1/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "session_id": "user-123-chat",
    "messages": [
      {"role": "user", "content": "What are its main features?"}
    ]
  }'
```

The API automatically includes:
1. Previous user message: "What is Python?"
2. Previous assistant response
3. Current user message: "What are its main features?"

#### Turn 3: Continue conversation

```bash
curl -X POST http://localhost:8000/v1/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{
    "session_id": "user-123-chat",
    "messages": [
      {"role": "user", "content": "Can you give me a code example?"}
    ]
  }'
```

All previous context is automatically included.

## How It Works

### Architecture

1. **ChatHistoryCache**: TTL-based cache storing message history per session
2. **Session Management**: Each `session_id` maps to a list of messages with timestamps
3. **Automatic Merging**: On each request, cached history + new messages = full context
4. **Auto-expiry**: Sessions expire after `ttl_seconds` (default: 7200s / 2 hours)

### Data Flow

```
Request with session_id
    ↓
Retrieve session history from cache
    ↓
Merge: [cached_messages] + [new_messages]
    ↓
Format merged messages → prompt
    ↓
Generate response
    ↓
Save new messages + response to session cache
    ↓
Return response
```

### Storage Format

Messages are stored with metadata:

```python
{
    "role": "user",
    "content": "What is Python?",
    "timestamp": 1700000000.123
}
```

## Session ID Best Practices

### Generating Session IDs

Use unique, stable identifiers:

```python
# Per-user conversation
session_id = f"user-{user_id}-chat-{conversation_id}"

# Timestamped sessions
session_id = f"session-{user_id}-{timestamp}"

# UUID-based
import uuid
session_id = f"chat-{uuid.uuid4()}"
```

### Session ID Scope

- **User-scoped**: `user-123-general` - one ongoing conversation per user
- **Topic-scoped**: `user-123-python-help` - separate conversations per topic
- **Temporary**: `temp-{uuid}` - anonymous or guest sessions

## Testing

### Python Test Script

Run the included test script:

```bash
# Start the server first
make run

# In another terminal, run the test
python test_chat_history.py
```

### Manual Testing

```bash
# Start server
make run

# Run test script
./test_chat_history.sh
```

### Expected Behavior

1. **Turn 1**: Initial question about a topic
2. **Turn 2**: Follow-up question (should understand "it" refers to topic from Turn 1)
3. **Turn 3**: Another follow-up (should have full conversation context)
4. **No session**: Fresh conversation without previous context

## Configuration Options

### TTL Configuration

Adjust session lifetime based on use case:

```yaml
chat_history:
  enabled: true
  ttl_seconds: 7200   # 2 hours (default)
  # ttl_seconds: 1800  # 30 minutes (shorter)
  # ttl_seconds: 86400 # 24 hours (longer)
```

### Disable Chat History

To disable feature:

```yaml
chat_history:
  enabled: false
```

Or via environment:

```bash
CHAT_HISTORY__ENABLED=false
```

## Performance Considerations

### Memory Usage

- Each session stores full message history
- Messages include content + timestamp
- Old sessions auto-expire (TTL cleanup)
- Max 1000 concurrent sessions (configurable in code)

### Cache Efficiency

Session history cache uses `cachetools.TTLCache`:
- Automatic expiration after TTL
- LRU eviction when maxsize reached
- Thread-safe operations

### Recommendations

- **Short conversations**: Use longer TTL (2-4 hours)
- **High traffic**: Use shorter TTL (30-60 minutes)
- **Memory constrained**: Reduce TTL or increase cleanup frequency
- **Long conversations**: Consider summarization to reduce context size

## API Schema

### ChatRequest with session_id

```python
{
    "messages": [
        {"role": "user", "content": "message text"}
    ],
    "session_id": "optional-session-id",  # NEW FIELD
    "max_tokens": 100,
    "temperature": 0.7,
    "stream": false
}
```

### Fields

- `messages` (required): List of messages for current turn
- `session_id` (optional): String identifier for session persistence
- `max_tokens` (optional): Max tokens to generate
- `temperature` (optional): Sampling temperature
- `stream` (optional): Enable SSE streaming

## Monitoring

### Logs

Session operations are logged:

```json
{
  "level": "INFO",
  "message": "Loaded 4 messages from session user-123-chat",
  "timestamp": "2024-11-21T10:30:00Z"
}
```

```json
{
  "level": "INFO",
  "message": "Updated session user-123-chat with new messages",
  "timestamp": "2024-11-21T10:30:05Z"
}
```

### Cache Statistics

Check cache stats via Python API:

```python
from app.core.cache import get_chat_history_cache

cache = get_chat_history_cache()
stats = cache.get_stats()

# Returns:
# {
#   "enabled": true,
#   "active_sessions": 15,
#   "max_sessions": 1000,
#   "ttl_seconds": 7200
# }
```

## Troubleshooting

### Session not persisting

**Check:**
1. `chat_history.enabled` is `true` in config
2. `session_id` is consistent across requests
3. TTL hasn't expired (default: 2 hours)

**Debug:**
```python
# Add logging to see session retrieval
logger.info(f"Session {session_id} history: {len(messages)} messages")
```

### High memory usage

**Solutions:**
1. Reduce `ttl_seconds` for faster cleanup
2. Limit message history length
3. Implement message summarization for long conversations

### Context too long

**Error:** Prompt exceeds model's context window

**Solutions:**
1. Reduce `max_tokens`
2. Trim older messages from history
3. Implement sliding window (keep last N messages)
4. Use summarization for older context

## Migration Guide

### Updating Existing Code

The feature is **backward compatible**. Existing chat requests without `session_id` work unchanged:

```python
# Before (still works)
response = requests.post("/v1/chat", json={
    "messages": [{"role": "user", "content": "Hello"}]
})

# After (with session)
response = requests.post("/v1/chat", json={
    "messages": [{"role": "user", "content": "Hello"}],
    "session_id": "user-123"
})
```

## Future Enhancements

Potential improvements:

1. **Persistence**: Redis/database backend for multi-instance deployments
2. **Summarization**: Auto-compress old messages to save tokens
3. **Sliding window**: Keep only last N messages
4. **Session management endpoints**: GET/DELETE sessions
5. **Configurable max history**: Limit messages per session
6. **Export/import**: Save/restore conversations

## References

- API Schemas: `app/api/schemas.py`
- Cache Implementation: `app/core/cache.py`
- Chat Router: `app/api/routers/chat.py`
- Configuration: `app/core/config.py`
- Test Script: `test_chat_history.py`
