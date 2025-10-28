#!/usr/bin/env bash
# list-topics.sh - List all Kafka topics

set -e

echo "📋 Listing all Kafka topics..."
echo ""

docker exec kafka kafka-topics \
  --bootstrap-server localhost:29092 \
  --list

echo ""
echo "✅ Topic list complete"
