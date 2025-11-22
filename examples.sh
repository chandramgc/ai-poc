#!/bin/bash
# Sample API calls for testing the LLM FastAPI Service
# Usage: ./examples.sh [API_KEY]

# Default API key (override with command line argument)
API_KEY="${1:-changeit}"
BASE_URL="${2:-http://localhost:8000}"

echo "================================"
echo "LLM FastAPI Service - Examples"
echo "================================"
echo "Base URL: $BASE_URL"
echo "API Key: $API_KEY"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 1. Health Check
echo -e "${BLUE}1. Health Check${NC}"
curl -s "$BASE_URL/health" | jq .
echo ""

# 2. Status Check
echo -e "${BLUE}2. Service Status${NC}"
curl -s "$BASE_URL/status" | jq .
echo ""

# 3. Simple Generation
echo -e "${BLUE}3. Simple Text Generation${NC}"
curl -s -X POST "$BASE_URL/v1/generate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "prompt": "What is the meaning of life?",
    "max_tokens": 100,
    "temperature": 0.7
  }' | jq .
echo ""

# 4. Generation with Parameters
echo -e "${BLUE}4. Text Generation with Custom Parameters${NC}"
curl -s -X POST "$BASE_URL/v1/generate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "prompt": "Explain quantum computing to a 5-year-old",
    "max_tokens": 150,
    "temperature": 0.8,
    "top_p": 0.95
  }' | jq .
echo ""

# 5. Simple Chat
echo -e "${BLUE}5. Simple Chat${NC}"
curl -s -X POST "$BASE_URL/v1/chat" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "messages": [
      {"role": "user", "content": "Hello! What can you help me with?"}
    ],
    "max_tokens": 100
  }' | jq .
echo ""

# 6. Multi-turn Chat
echo -e "${BLUE}6. Multi-turn Conversation${NC}"
curl -s -X POST "$BASE_URL/v1/chat" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "messages": [
      {"role": "user", "content": "What is Python?"},
      {"role": "assistant", "content": "Python is a high-level programming language."},
      {"role": "user", "content": "What are its main features?"}
    ],
    "max_tokens": 150,
    "temperature": 0.7
  }' | jq .
echo ""

# 7. Cached Response (run same query twice)
echo -e "${BLUE}7. Testing Cache (running same query twice)${NC}"
echo "First request:"
curl -s -X POST "$BASE_URL/v1/generate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "prompt": "What is 2+2?",
    "max_tokens": 50
  }' | jq '.cached'

echo "Second request (should be cached):"
curl -s -X POST "$BASE_URL/v1/generate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "prompt": "What is 2+2?",
    "max_tokens": 50
  }' | jq '.cached'
echo ""

# 8. Prometheus Metrics
echo -e "${BLUE}8. Prometheus Metrics (sample)${NC}"
curl -s "$BASE_URL/metrics" | head -n 20
echo "... (truncated)"
echo ""

# 9. Error: Missing API Key
echo -e "${BLUE}9. Error Test: Missing API Key${NC}"
curl -s -X POST "$BASE_URL/v1/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Test"
  }' | jq .
echo ""

# 10. Error: Invalid API Key
echo -e "${BLUE}10. Error Test: Invalid API Key${NC}"
curl -s -X POST "$BASE_URL/v1/generate" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: invalid-key-123" \
  -d '{
    "prompt": "Test"
  }' | jq .
echo ""

# 11. Streaming Chat (if supported)
echo -e "${BLUE}11. Streaming Chat Response${NC}"
curl -X POST "$BASE_URL/v1/chat" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "messages": [
      {"role": "user", "content": "Tell me a short story"}
    ],
    "stream": true,
    "max_tokens": 100
  }'
echo ""
echo ""

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}All examples completed!${NC}"
echo -e "${GREEN}================================${NC}"
