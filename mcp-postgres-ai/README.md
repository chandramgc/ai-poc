# MCP PostgreSQL AI Agent

Natural language query interface to PostgreSQL using Model Context Protocol (MCP) over WebSocket.

## Architecture

```
User → HTTP Agent → WebSocket MCP Server → PostgreSQL
       (NL→SQL)      (Execute Query)
```

**Components:**
- **MCP Server**: WebSocket server implementing MCP protocol, executes SQL queries
- **Agent**: FastAPI HTTP server, converts natural language to SQL using LLM
- **PostgreSQL**: Database backend

## Prerequisites

- Docker & Docker Compose
- OpenAI API key (for NL→SQL conversion)

## Quick Start

### 1. Clone and Setup

```bash
cd mcp-postgres-ai
cp .env.example .env
```

### 2. Configure Environment

Edit `.env`:

```bash
# Set your OpenAI API key
LLM_API_KEY=sk-your-openai-api-key

# Set secure API key for MCP WebSocket
WS_API_KEY=your-secure-random-key

# Langfuse (optional - for LLM observability)
LANGFUSE_PUBLIC_KEY=pk-lf-your-public-key
LANGFUSE_SECRET_KEY=sk-lf-your-secret-key
LANGFUSE_HOST=http://localhost:6005

# PostgreSQL credentials (optional, defaults work)
POSTGRES_PASSWORD=postgres
```

### 3. Start Services

```bash
docker-compose up -d
```

Services:
- PostgreSQL: `localhost:5432`
- MCP WebSocket Server: `ws://localhost:9001/mcp`
- Agent HTTP API: `http://localhost:9002`

### 4. Check Health

```bash
curl http://localhost:9002/health
```

## Usage

### Natural Language Query

```bash
curl -X POST http://localhost:9002/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "show me the last 5 users",
    "schema_context": "Table: users (id, name, email, created_at)",
    "user_id": "user-123",
    "session_id": "session-456"
  }'
```

**Response:**
```json
{
  "question": "show me the last 5 users",
  "sql_query": "SELECT * FROM users ORDER BY created_at DESC LIMIT 5;",
  "result": {
    "rows": [...],
    "rowCount": 5,
    "executionTimeMs": 12.34
  },
  "trace_url": "https://cloud.langfuse.com/trace/..."
}
```

### Example Queries

**List all tables:**
```bash
curl -X POST http://localhost:9002/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "show all tables in the database"
  }'
```

**Count records:**
```bash
curl -X POST http://localhost:9002/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "how many users do we have?",
    "schema_context": "Table: users"
  }'
```

**Filter with conditions:**
```bash
curl -X POST http://localhost:9002/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "show users created in the last 7 days",
    "schema_context": "Table: users (id, name, email, created_at)"
  }'
```

## Development

### Local Setup (without Docker)

```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Activate virtual environment
poetry shell

# Start PostgreSQL (or use existing instance)
docker run -d -p 5432:5432 \
  -e POSTGRES_PASSWORD=postgres \
  --name postgres postgres:15-alpine

# Configure environment
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export WS_API_KEY=test-key
export LLM_API_KEY=your-openai-key

# Start MCP server
python -m src.mcp_server.main

# In another terminal, start agent
python -m src.agent.http_api
```

### Testing MCP Server Directly

You can test the WebSocket MCP server using `wscat`:

```bash
# Install wscat
npm install -g wscat

# Connect to MCP server
wscat -c ws://localhost:9001/mcp -H "X-API-Key: change-me"

# Send tool list request
{"jsonrpc":"2.0","id":1,"method":"tools/list"}

# Execute SQL
{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"run_sql","arguments":{"query":"SELECT version()"}}}
```

## Langfuse Observability

When Langfuse is configured, the agent automatically tracks:

- 🎯 **LLM calls** - Model, tokens, latency, cost
- 📊 **Traces** - Full request flow (NL→SQL→Execution)
- 👤 **User tracking** - Pass `user_id` and `session_id` in requests
- 💰 **Cost tracking** - Automatic OpenAI cost calculation
- 🔗 **Trace URLs** - Each response includes a Langfuse trace link

**View traces:**
1. Open Langfuse UI: `http://localhost:6005`
2. Click trace URL from API response
3. See detailed breakdown of LLM calls, SQL execution, timing

## Security Features

✅ **SELECT-only queries**: Blocks INSERT/UPDATE/DELETE/DROP/ALTER
✅ **API key authentication**: WebSocket requires X-API-Key header
✅ **Parameterized queries**: Supports prepared statements
✅ **Query timeout**: 60-second command timeout
✅ **Input validation**: SQL validation at both agent and MCP layers
✅ **LLM observability**: Full traceability with Langfuse

## Troubleshooting

### Agent can't connect to MCP server

```bash
# Check MCP server logs
docker-compose logs mcp-server

# Verify WebSocket is accessible
curl -i -N \
  -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  -H "X-API-Key: change-me" \
  http://localhost:9001/mcp
```

### Database connection errors

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Test connection
docker-compose exec postgres psql -U postgres -c "SELECT 1"
```

### LLM API errors

- Verify `LLM_API_KEY` is set correctly
- Check OpenAI API quota/limits
- Review agent logs: `docker-compose logs agent`

## Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f mcp-server
docker-compose logs -f agent
docker-compose logs -f postgres
```

## Stop Services

```bash
# Stop containers
docker-compose down

# Stop and remove volumes (deletes data)
docker-compose down -v
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:9002/docs
- ReDoc: http://localhost:9002/redoc
- Langfuse UI: http://localhost:6005 (if configured)

## Project Structure

```
mcp-postgres-ai/
├── pyproject.toml          # Poetry dependencies
├── docker-compose.yml      # Docker services
├── Dockerfile              # Container image
├── .env.example            # Environment template
└── src/
    ├── mcp_server/
    │   ├── main.py         # MCP server entry point
    │   ├── ws_server.py    # WebSocket handler
    │   ├── tools.py        # run_sql tool
    │   ├── db.py           # Database pool
    │   └── config.py       # Configuration
    └── agent/
        ├── http_api.py     # FastAPI endpoints
        └── ws_client.py    # MCP WebSocket client
```

## License

MIT
