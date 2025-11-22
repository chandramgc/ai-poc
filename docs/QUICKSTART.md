# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites
- Python 3.11+
- Poetry installed (`curl -sSL https://install.python-poetry.org | python3 -`)

### Step 1: Setup

```bash
# Install dependencies
poetry install

# Copy environment template
cp .env.example .env
```

### Step 2: Configure

Edit `.env` and set:
```bash
# Required: Your Hugging Face token
HUGGINGFACE_TOKEN=hf_your_token_here

# Required: Your API key for the service
SECURITY__API_KEY=my-secret-api-key
```

### Step 3: Run

```bash
# Start the service
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Or use Makefile:
```bash
make run
```

### Step 4: Test

#### Check Health
```bash
curl http://localhost:8000/health
```

#### Generate Text
```bash
curl -X POST http://localhost:8000/v1/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: my-secret-api-key" \
  -d '{
    "prompt": "What is artificial intelligence?",
    "max_tokens": 100
  }'
```

#### Chat
```bash
curl -X POST http://localhost:8000/v1/chat \
  -H "Content-Type: application/json" \
  -H "X-API-Key: my-secret-api-key" \
  -d '{
    "messages": [
      {"role": "user", "content": "Hello! Who are you?"}
    ]
  }'
```

### Step 5: View Docs

Open your browser:
- API Documentation: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc
- Metrics: http://localhost:8000/metrics

---

## 🐳 Docker Quick Start

### Build and Run

```bash
# Build image
docker build -t llm-service .

# Run container
docker run -d -p 8000:8000 \
  -e HUGGINGFACE_TOKEN=your_token \
  -e SECURITY__API_KEY=your_key \
  llm-service
```

Or use Makefile:
```bash
make build-docker
make run-docker
```

---

## 🧪 Run Tests

```bash
# All tests with coverage
make test

# Quick tests
make test-quick

# Specific test
poetry run pytest tests/test_config.py -v
```

---

## 🔧 Common Commands

```bash
# Install dependencies
make install

# Run service
make run

# Run tests
make test

# Lint code
make lint

# Format code
make format

# Build Docker image
make build-docker

# Run in Docker
make run-docker

# Clean generated files
make clean
```

---

## 📖 Configuration

### Change Model

Edit `config.yml`:
```yaml
model:
  name: "google/gemma-2-2b-it"  # Change to any HF model
  device: "cpu"                  # or "cuda"
  max_tokens: 512
```

Or use environment variables:
```bash
MODEL__NAME=microsoft/phi-2
MODEL__DEVICE=cuda
```

### Adjust Rate Limiting

In `.env`:
```bash
RATE_LIMIT__REQUESTS_PER_MINUTE=50
RATE_LIMIT__BURST_SIZE=100
```

### Enable/Disable Cache

In `.env`:
```bash
CACHE__ENABLED=true
CACHE__SIZE=100
CACHE__TTL_SECONDS=3600
```

---

## 🐛 Troubleshooting

### Model not loading?
- Check your HUGGINGFACE_TOKEN is valid
- Try a smaller model first: `google/flan-t5-small`
- Check disk space for model download

### CUDA errors?
- Set `MODEL__DEVICE=cpu` in .env
- Or ensure CUDA drivers are installed

### Import errors?
- Run `poetry install` again
- Check Python version: `python --version` (should be 3.11+)

### Rate limit too strict?
- Adjust `RATE_LIMIT__REQUESTS_PER_MINUTE` in .env
- Or disable: `RATE_LIMIT__ENABLED=false`

---

## 📚 Next Steps

1. Read the full [README.md](README.md)
2. Explore the API docs at http://localhost:8000/docs
3. Check the example curl commands
4. Customize prompts in `app/llm/prompts/`
5. Add your own endpoints in `app/api/routers/`

---

**Happy Building! 🎉**
