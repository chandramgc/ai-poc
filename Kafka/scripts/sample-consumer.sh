#!/usr/bin/env bash
# sample-consumer.sh - Consume messages from a Kafka topic

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

echo "📥 Starting Kafka consumer for topic: $TOPIC_NAME"
echo "   Reading from beginning... (Ctrl+C to exit)"
echo ""

docker exec -i kafka kafka-console-consumer \
  --bootstrap-server localhost:29092 \
  --topic "$TOPIC_NAME" \
  --from-beginning
