# Kafka + ZooKeeper (ARM64) — macOS M4 Docker Desktop

Single-node **Kafka 3.6 (Confluent Platform 7.6) + ZooKeeper** stack for local development, optimized for Apple Silicon (M1/M2/M4).  
Includes **Kafka UI** for topic and consumer inspection.

> **✅ Tested & Working**: This setup has been verified on macOS M4 with Apple Silicon. All services start successfully and are fully operational.

> **Note**: Using Confluent Platform images (`confluentinc/cp-kafka` and `confluentinc/cp-zookeeper`) which are actively maintained and provide excellent ARM64 support.

---

## 🧰 Prerequisites

- **Docker Desktop for Mac** (Apple Silicon)
- Minimum **4 CPU / 4 GB RAM** allocated to Docker
- All images are ARM64-compatible (Confluent Platform + Provectus)

---

## 🚀 Quick Start

```bash
cd Kafka
chmod +x scripts/*.sh
docker compose up -d
```

Wait for services to be healthy (30-60 seconds):

```bash
./scripts/wait-for-zk.sh
./scripts/wait-for-kafka.sh
```

---

## 📊 Services & Ports

| Service        | Host Port | Container Port | Description         |
|----------------|-----------|----------------|---------------------|
| **ZooKeeper**  | `6006`    | `2181`         | Coordination service|
| **Kafka External** | `6007` | `9092`         | External client access |
| **Kafka Internal** | `6008` | `29092`        | Container-to-container |
| **Kafka UI**   | `6009`    | `8080`         | Web dashboard       |

### Access URLs

- **Kafka UI**: http://localhost:6009
- **Kafka Bootstrap Server** (for host apps): `localhost:6007`
- **Internal container bootstrap**: `kafka:29092`

---

## ✅ Verify Setup

```bash
# Check container status
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Verify ZooKeeper
./scripts/wait-for-zk.sh

# Verify Kafka
./scripts/wait-for-kafka.sh
```

---

## 🪄 Create & List Topics

```bash
# Create default topic (from .env)
./scripts/create-topics.sh

# Create custom topic with 3 partitions, replication factor 1
./scripts/create-topics.sh mytopic 3 1

# List all topics
./scripts/list-topics.sh
```

---

## 💬 Produce / Consume Messages

### Produce messages

```bash
./scripts/sample-producer.sh mytopic
# Type messages, press Ctrl+D to end
```

### Consume messages

```bash
./scripts/sample-consumer.sh mytopic
# Reads from beginning, press Ctrl+C to stop
```

---

## 🧑‍💻 Connecting from External Clients

Use the following connection strings in your client applications:

| Client Type                  | Property             | Value               |
|------------------------------|----------------------|---------------------|
| Kafka CLI / Java / Python    | `bootstrap.servers`  | `localhost:6007`    |
| Kafka UI (internal)          | `bootstrap.servers`  | `kafka:29092`       |
| ZooKeeper clients            | `zookeeper.connect`  | `localhost:6006`    |

### Example: Python (kafka-python)

```python
from kafka import KafkaProducer, KafkaConsumer

# Producer
producer = KafkaProducer(bootstrap_servers='localhost:6007')
producer.send('test-topic', b'Hello Kafka!')
producer.flush()

# Consumer
consumer = KafkaConsumer(
    'test-topic',
    bootstrap_servers='localhost:6007',
    auto_offset_reset='earliest'
)
for message in consumer:
    print(message.value)
```

### Example: Node.js (kafkajs)

```javascript
const { Kafka } = require('kafkajs');

const kafka = new Kafka({
  clientId: 'my-app',
  brokers: ['localhost:6007']
});

// Producer
const producer = kafka.producer();
await producer.connect();
await producer.send({
  topic: 'test-topic',
  messages: [{ value: 'Hello Kafka!' }]
});

// Consumer
const consumer = kafka.consumer({ groupId: 'test-group' });
await consumer.connect();
await consumer.subscribe({ topic: 'test-topic', fromBeginning: true });
await consumer.run({
  eachMessage: async ({ topic, partition, message }) => {
    console.log(message.value.toString());
  }
});
```

---

## 🧹 Stop & Clean

```bash
# Stop containers (preserves data)
docker compose down

# Stop & remove data volumes (full reset)
docker compose down -v
```

---

## ⚙️ Configuration

All configuration is managed via `.env` file:

```bash
# ZooKeeper
ZK_ALLOW_ANONYMOUS=yes

# Kafka
KAFKA_BROKER_ID=1
KAFKA_HEAP_OPTS=-Xms512m -Xmx512m
KAFKA_LOG_RETENTION_HOURS=168

# Ports (Host port mappings)
ZK_HOST_PORT=6006
KAFKA_EXTERNAL_PORT=6007        # Maps to container port 9092
KAFKA_INTERNAL_PORT=6008        # Maps to container port 29092
KAFKA_UI_PORT=6009

# Topic Defaults
DEFAULT_TOPIC=test-topic
TOPIC_PARTITIONS=1
TOPIC_REPLICATION=1
```

### Customizing Ports

Edit `.env` to change port mappings if you have conflicts:

```bash
ZK_HOST_PORT=7006
KAFKA_EXTERNAL_PORT=7007    # External client access
KAFKA_INTERNAL_PORT=7008    # Container-to-container communication
KAFKA_UI_PORT=7009
```

Then restart:

```bash
docker compose down && docker compose up -d
```

---

## ⚠️ Troubleshooting

### Architecture Mismatch Error

**Symptom**: `exec format error` or `platform mismatch`

**Solution**: Ensure `platform: linux/arm64/v8` is present in `docker-compose.yml` for all services.

### Port Already in Use

**Symptom**: `address already in use`

**Solution**: Change ports in `.env`:

```bash
ZK_HOST_PORT=7006
KAFKA_EXTERNAL_PORT=7007
KAFKA_INTERNAL_PORT=7008
KAFKA_UI_PORT=7009
```

### Kafka UI Not Connecting

**Symptom**: UI shows "Cannot connect to cluster"

**Solution**: Verify Kafka UI's bootstrap server is set to `kafka:29092` (internal network):

```yaml
environment:
  - KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS=kafka:29092
```

### ZooKeeper Health Check Failing

**Symptom**: Container restarts repeatedly

**Solution**: Check ZooKeeper logs:

```bash
docker logs zookeeper
```

Ensure anonymous login is enabled in `.env`:

```bash
ZK_ALLOW_ANONYMOUS=yes
```

### Kafka Taking Too Long to Start

**Symptom**: Kafka health checks timeout

**Solution**: Increase Docker Desktop resources:
- **Docker Desktop → Settings → Resources**
- Set **CPUs: 4+** and **Memory: 4GB+**

### Cannot Produce/Consume Messages

**Symptom**: Connection refused or timeout

**Solution**: 
1. Verify Kafka is healthy: `docker ps`
2. Check you're using the correct port: `localhost:6007` for external clients
3. Ensure topic exists: `./scripts/list-topics.sh`

---

## 📦 Data Persistence

Kafka and ZooKeeper data is stored in named Docker volumes:

- `zk_data`, `zk_logs` — ZooKeeper data and logs
- `kafka_data`, `kafka_logs` — Kafka data and logs

### List Volumes

```bash
docker volume ls | grep kafka
```

### Remove Volumes (Clean Slate)

```bash
docker compose down -v
# Or manually:
docker volume rm kafka-stack_zk_data kafka-stack_zk_logs kafka-stack_kafka_data kafka-stack_kafka_logs
```

---

## 🔧 Advanced Usage

### Accessing Kafka Container Shell

```bash
docker exec -it kafka bash
# Kafka binaries are in PATH
kafka-topics --bootstrap-server localhost:29092 --list
```

### Manually Create a Topic

```bash
docker exec kafka kafka-topics \
  --bootstrap-server localhost:29092 \
  --create \
  --topic my-custom-topic \
  --partitions 5 \
  --replication-factor 1
```

### Describe a Topic

```bash
docker exec kafka kafka-topics \
  --bootstrap-server localhost:29092 \
  --describe \
  --topic test-topic
```

### View Consumer Groups

```bash
docker exec kafka kafka-consumer-groups \
  --bootstrap-server localhost:29092 \
  --list
```

### Check Kafka Logs

```bash
docker logs kafka --tail 100 -f
```

---

## 🎯 Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Desktop (M4)                   │
│                                                           │
│  ┌──────────────┐   ┌──────────────┐   ┌─────────────┐ │
│  │  ZooKeeper   │   │    Kafka     │   │  Kafka UI   │ │
│  │              │   │              │   │             │ │
│  │  Port: 6006  │◄──┤  6007 (ext)  │◄──┤ Port: 6009  │ │
│  │              │   │  6008 (int)  │   │             │ │
│  └──────────────┘   └──────────────┘   └─────────────┘ │
│         │                    │                   │       │
│         └────────── kafka_net (bridge) ──────────┘       │
└─────────────────────────────────────────────────────────┘
                          │
                          │
                ┌─────────┴─────────┐
                │                   │
        External Clients       Kafka UI Browser
      (localhost:6007)       (localhost:6009)
```

### Listener Configuration

Kafka has two listeners for flexible connectivity:

1. **INTERNAL** (`kafka:29092`) — Used by containers in the same network (Kafka UI)
2. **EXTERNAL** (`localhost:6007`) — Used by applications running on the host

This dual-listener setup allows seamless communication between containerized services and host applications.

---

## 📚 Resources

- [Confluent Platform Docker Images](https://hub.docker.com/u/confluentinc)
- [Confluent Kafka Documentation](https://docs.confluent.io/platform/current/installation/docker/image-reference.html)
- [Kafka UI GitHub](https://github.com/provectus/kafka-ui)
- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)

---

## ✅ Summary of Exposed Ports

- **ZooKeeper** → `6006`
- **Kafka (External)** → `6007`
- **Kafka (Internal)** → `6008`
- **Kafka UI** → `6009`

---

## 📝 License

This setup is provided as-is for development purposes. Kafka and ZooKeeper are Apache 2.0 licensed.

---

**Happy Streaming! 🚀**
