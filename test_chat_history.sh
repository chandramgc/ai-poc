#!/bin/bash

# Test script for chat history with session management
# Demonstrates multi-turn conversation with session persistence

set -e

API_KEY="changeit"
BASE_URL="http://localhost:8000"
SESSION_ID="test-session-$(date +%s)"

echo "==================================="
echo "Testing Chat History with Sessions"
echo "==================================="
echo "Session ID: $SESSION_ID"
echo ""

# Turn 1: Initial question
echo "Turn 1: What is Python?"
RESPONSE_1=$(curl -s -X POST "$BASE_URL/v1/chat" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"messages\": [
      {\"role\": \"user\", \"content\": \"What is Python?\"}
    ],
    \"max_tokens\": 100
  }")

echo "$RESPONSE_1" | jq -r '.message.content'
echo ""
sleep 2

# Turn 2: Follow-up question (should reference Python from turn 1)
echo "Turn 2: Follow-up question - What are its main features? (should remember Python context)..."
RESPONSE_2=$(curl -s -X POST "$BASE_URL/v1/chat" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"messages\": [
      {\"role\": \"user\", \"content\": \"What are its main features?\"}
    ],
    \"max_tokens\": 100
  }")

echo "$RESPONSE_2" | jq -r '.message.content'
echo ""
sleep 2

# Turn 3: Another follow-up
echo "Turn 3: Can you give me a simple example? (should remember all previous context)..."
RESPONSE_3=$(curl -s -X POST "$BASE_URL/v1/chat" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"messages\": [
      {\"role\": \"user\", \"content\": \"Can you give me a simple example?\"}
    ],
    \"max_tokens\": 150
  }")

echo "$RESPONSE_3" | jq -r '.message.content'
echo ""

# Test without session_id (new conversation)
echo "==================================="
echo "Testing WITHOUT session_id - What are we talking about?(new conversation)..."
RESPONSE_NEW=$(curl -s -X POST "$BASE_URL/v1/chat" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_KEY" \
  -d '{
    "messages": [
      {"role": "user", "content": "What are we talking about?"}
    ],
    "max_tokens": 50
  }')

echo "$RESPONSE_NEW" | jq -r '.message.content'
echo ""

echo "==================================="
echo "Chat history test complete!"
echo "Session ID used: $SESSION_ID"
echo "History TTL: 2 hours (configurable)"
echo "==================================="
