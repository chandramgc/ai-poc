#!/usr/bin/env bash
# sample-producer.sh - Produce messages to a Kafka topic

set -e

# Load environment variables
if [ -f .env ]; then
  while IFS='=' read -r key value; do
    if [[ ! $key =~ ^# ]] && [[ -n $key ]]; then
      export "$key"="$value"
    fi
  done < .env
fi

TOPIC_NAME=${1:-$DEFAULT_TOPIC}

echo "📤 Starting Kafka producer for topic: $TOPIC_NAME"
echo "   Type your messages below (Ctrl+D to exit):"
echo ""

docker exec -i kafka kafka-console-producer \
  --bootstrap-server localhost:29092 \
  --topic "$TOPIC_NAME"

echo ""
echo "✅ Producer session ended"
