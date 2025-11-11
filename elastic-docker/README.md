# Elasticsearch + Kibana Docker Setup

Complete Elasticsearch and Kibana deployment using Docker Compose for local development.

## 📋 Prerequisites

- Docker Desktop installed and running
- At least 4GB RAM allocated to Docker
- Ports 6015 and 6016 available

## 🚀 Quick Start

### 1. Start the Stack

```bash
cd elastic-docker
docker-compose up -d
```

This will:
- Pull the latest Elasticsearch and Kibana images
- Create a dedicated network
- Set up persistent storage for Elasticsearch data
- Start both services with health checks

### 2. Wait for Services to Be Ready

Monitor the startup process:

```bash
docker-compose logs -f
```

Wait until you see:
- Elasticsearch: `"message": "started"`
- Kibana: `"message": "Status changed from yellow to green"`

Press `Ctrl+C` to exit logs.

### 3. Verify Elasticsearch is Running

```bash
# Check cluster health
curl http://localhost:6015/_cluster/health?pretty

# Get cluster info
curl http://localhost:6015

# Check nodes
curl http://localhost:6015/_cat/nodes?v
```

Expected response for health check:
```json
{
  "cluster_name" : "docker-cluster",
  "status" : "green",
  "number_of_nodes" : 1
}
```

### 4. Access Kibana

Open your browser and navigate to:
```
http://localhost:6016
```

No authentication required - you'll be taken directly to the Kibana home page.

## 🧪 Test Elasticsearch

### Create an Index

```bash
curl -X PUT "http://localhost:6015/test-index" -H 'Content-Type: application/json' -d'
{
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 0
  }
}'
```

### Index a Document

```bash
curl -X POST "http://localhost:6015/test-index/_doc" -H 'Content-Type: application/json' -d'
{
  "name": "Test Document",
  "timestamp": "2025-11-07T10:00:00",
  "message": "Hello from Elasticsearch"
}'
```

### Search Documents

```bash
curl -X GET "http://localhost:6015/test-index/_search?pretty"
```

### List All Indices

```bash
curl http://localhost:6015/_cat/indices?v
```

### Delete the Test Index

```bash
curl -X DELETE "http://localhost:6015/test-index"
```

## 🛠️ Management Commands

### View Running Containers

```bash
docker-compose ps
```

### View Logs

```bash
# All services
docker-compose logs -f

# Elasticsearch only
docker-compose logs -f elasticsearch

# Kibana only
docker-compose logs -f kibana
```

### Stop the Stack

```bash
docker-compose stop
```

### Start the Stack (after stopping)

```bash
docker-compose start
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart elasticsearch
```

### Stop and Remove Containers

```bash
docker-compose down
```

### Stop and Remove Everything (including data)

```bash
docker-compose down -v
```

⚠️ **Warning:** The `-v` flag will delete all data stored in Elasticsearch!

## 🔧 Configuration Details

### Elasticsearch
- **Port:** 6015 (mapped from internal 9200)
- **Mode:** Single-node
- **Security:** Disabled (development only)
- **Memory:** 512MB heap size (adjustable via ES_JAVA_OPTS)
- **Data:** Persisted in named volume `esdata`

### Kibana
- **Port:** 6016 (mapped from internal 5601)
- **Security:** Disabled (development only)
- **Connection:** Connects to Elasticsearch via internal network

## 📊 Health Check Endpoints

```bash
# Elasticsearch health
curl http://localhost:6015/_cluster/health

# Kibana status
curl http://localhost:6016/api/status
```

## 🐛 Troubleshooting

### Elasticsearch won't start

**Check logs:**
```bash
docker-compose logs elasticsearch
```

**Common issues:**
- Insufficient memory: Increase Docker Desktop memory allocation
- Port conflict: Ensure port 6015 is not in use
- VM max map count (Linux): Run `sudo sysctl -w vm.max_map_count=262144`

### Kibana can't connect to Elasticsearch

```bash
# Check if Elasticsearch is healthy
curl http://localhost:6015/_cluster/health

# Restart Kibana
docker-compose restart kibana
```

### Reset Everything

```bash
docker-compose down -v
docker-compose up -d
```

## 📚 Useful Resources

- [Elasticsearch Documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)
- [Kibana Documentation](https://www.elastic.co/guide/en/kibana/current/index.html)
- [Elasticsearch REST API](https://www.elastic.co/guide/en/elasticsearch/reference/current/rest-apis.html)

## ⚠️ Important Notes

- **This setup is for LOCAL DEVELOPMENT ONLY**
- Security features (xpack) are disabled
- Do NOT use this configuration in production
- All data is stored locally in the `esdata` volume
- For production, enable security, SSL, and use proper authentication

## � PostgreSQL to Elasticsearch Sync

### Setup

The `pg_to_es_sync.py` script allows you to load data from PostgreSQL tables into Elasticsearch.

**Quick Setup:**

```bash
# Make setup script executable
chmod +x setup_sync.sh

# Run setup (creates venv and installs dependencies)
./setup_sync.sh

# Activate virtual environment
source venv/bin/activate
```

### Configuration

Edit `pg_to_es_sync.py` and update the PostgreSQL configuration (lines 24-30):

```python
PG_CONFIG = {
    'host': 'localhost',
    'port': 6003,        # Your PostgreSQL port
    'database': 'postgres',  # Your database name
    'user': 'postgres',
    'password': 'your-password-here'  # ⚠️ UPDATE THIS
}
```

### Usage

**Interactive Mode** (recommended for first-time use):

```bash
python3 pg_to_es_sync.py
```

This will:
1. List all available PostgreSQL tables
2. Show existing Elasticsearch indices
3. Let you choose which tables to sync

**Batch Mode** (for automated/scheduled syncs):

1. Edit `TABLES_TO_SYNC` in the script (line 43):
   ```python
   TABLES_TO_SYNC = {
       'users': 'users_index',
       'orders': 'orders_index',
   }
   ```

2. Run:
   ```bash
   python3 pg_to_es_sync.py --batch
   ```

### Features

- ✅ Automatic schema detection and mapping
- ✅ Bulk indexing (1000 docs per batch)
- ✅ Progress tracking
- ✅ Handles all PostgreSQL data types
- ✅ Uses primary key as document ID
- ✅ Creates indices automatically

### Verify Synced Data

```bash
# List all indices
curl 'http://localhost:6015/_cat/indices?v'

# Count documents in an index
curl 'http://localhost:6015/your_index/_count?pretty'

# Search documents
curl 'http://localhost:6015/your_index/_search?pretty'
```

## �📝 Version Information

- **Elasticsearch:** 8.11.1
- **Kibana:** 8.11.1
- **Docker Compose:** 3.8

To use a different version, update the image tags in `docker-compose.yml`.
