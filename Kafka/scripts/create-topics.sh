#!/usr/bin/env bash
# create-topics.sh - Create Kafka topics

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
PARTITIONS=${2:-$TOPIC_PARTITIONS}
REPLICATION=${3:-$TOPIC_REPLICATION}

echo "📋 Creating topic: $TOPIC_NAME"
echo "   Partitions: $PARTITIONS"
echo "   Replication Factor: $REPLICATION"

docker exec kafka kafka-topics \
  --bootstrap-server localhost:29092 \
  --create \
  --topic "$TOPIC_NAME" \
  --partitions "$PARTITIONS" \
  --replication-factor "$REPLICATION" \
  --if-not-exists

echo "✅ Topic '$TOPIC_NAME' created successfully!"
