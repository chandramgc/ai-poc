#!/usr/bin/env bash
# wait-for-kafka.sh - Wait for Kafka to be ready

set -e

MAX_RETRIES=30
RETRY_COUNT=0
SLEEP_TIME=3

echo "⏳ Waiting for Kafka to be ready..."

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
  if docker exec kafka kafka-topics \
    --bootstrap-server localhost:29092 \
    --list >/dev/null 2>&1; then
    echo "✅ Kafka is ready!"
    exit 0
  fi
  
  RETRY_COUNT=$((RETRY_COUNT + 1))
  echo "   Attempt $RETRY_COUNT/$MAX_RETRIES - Kafka not ready yet..."
  sleep $SLEEP_TIME
done

echo "❌ Kafka failed to become ready after $MAX_RETRIES attempts"
exit 1
