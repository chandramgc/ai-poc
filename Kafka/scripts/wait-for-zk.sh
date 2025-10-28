#!/usr/bin/env bash
# wait-for-zk.sh - Wait for ZooKeeper to be ready

set -e

MAX_RETRIES=30
RETRY_COUNT=0
SLEEP_TIME=2

echo "⏳ Waiting for ZooKeeper to be ready..."

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
  if docker exec zookeeper bash -c "echo srvr | nc localhost 2181" >/dev/null 2>&1; then
    echo "✅ ZooKeeper is ready!"
    exit 0
  fi
  
  RETRY_COUNT=$((RETRY_COUNT + 1))
  echo "   Attempt $RETRY_COUNT/$MAX_RETRIES - ZooKeeper not ready yet..."
  sleep $SLEEP_TIME
done

echo "❌ ZooKeeper failed to become ready after $MAX_RETRIES attempts"
exit 1
