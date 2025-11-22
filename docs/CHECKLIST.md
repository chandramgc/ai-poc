# Setup Checklist

## ✅ Pre-Deployment Checklist

### 1. Environment Setup
- [ ] Python 3.11+ installed
- [ ] Poetry 1.7+ installed (`poetry --version`)
- [ ] Docker installed (if using Docker)
- [ ] Git repository cloned
- [ ] Hugging Face account created
- [ ] Hugging Face token generated ([huggingface.co/settings/tokens](https://huggingface.co/settings/tokens))

### 2. Dependency Installation
- [ ] Run `poetry install`
- [ ] Verify installation: `poetry run python --version`
- [ ] Check dependencies: `poetry show`

### 3. Configuration
- [ ] Copy `.env.example` to `.env`
- [ ] Set `HUGGINGFACE_TOKEN` in `.env`
- [ ] Set `SECURITY__API_KEY` in `.env`
- [ ] Review `config.yml` settings
- [ ] Choose appropriate model in `MODEL__NAME`
- [ ] Set `MODEL__DEVICE` (cpu or cuda)

### 4. Testing Locally
- [ ] Run service: `make run` or `poetry run uvicorn app.main:app --reload`
- [ ] Test health endpoint: `curl http://localhost:8000/health`
- [ ] Test generation: Use examples from `QUICKSTART.md`
- [ ] Run test suite: `make test`
- [ ] Check code quality: `make lint`

### 5. Docker Setup (If Using)
- [ ] Review `Dockerfile`
- [ ] Build image: `make build-docker`
- [ ] Test container locally: `make run-docker`
- [ ] Verify container health: `docker ps`
- [ ] Check container logs: `docker logs [container-id]`

### 6. Security Configuration
- [ ] Generate strong API key (min 32 characters)
- [ ] Secure `.env` file (chmod 600)
- [ ] Review rate limits in config
- [ ] Enable PII filtering if needed: `SECURITY__ENABLE_PII_FILTER=true`
- [ ] Set appropriate `SECURITY__MAX_PROMPT_CHARS`

### 7. Performance Tuning
- [ ] Set appropriate `MODEL__MAX_TOKENS`
- [ ] Configure cache: `CACHE__SIZE` and `CACHE__TTL_SECONDS`
- [ ] Adjust rate limits for expected traffic
- [ ] Choose device based on hardware (CPU/CUDA)

### 8. Monitoring Setup
- [ ] Verify metrics endpoint: `curl http://localhost:8000/metrics`
- [ ] Set up Prometheus scraping (if using)
- [ ] Configure log aggregation
- [ ] Set up alerting for `/health` endpoint

### 9. Documentation Review
- [ ] Read `README.md`
- [ ] Review `QUICKSTART.md`
- [ ] Check `DEPLOYMENT.md` for deployment options
- [ ] Review `PROJECT_STRUCTURE.md`

### 10. Production Readiness
- [ ] Set `APP__LOG_LEVEL=WARNING` or `INFO`
- [ ] Disable debug mode
- [ ] Set up HTTPS/TLS
- [ ] Configure reverse proxy (nginx/traefik)
- [ ] Set up backup strategy
- [ ] Document runbook for common issues

---

## 📝 Quick Start Commands

```bash
# Install
poetry install

# Configure
cp .env.example .env
# Edit .env with your tokens

# Run locally
make run
# Or: poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000

# Test
curl http://localhost:8000/health
./examples.sh your-api-key

# Run tests
make test

# Build Docker
make build-docker

# Run Docker
make run-docker
```

---

## 🔍 Verification Steps

### After Starting Service

1. **Health Check**
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy","model_loaded":true,...}
```

2. **Status Check**
```bash
curl http://localhost:8000/status
# Should show cache stats, model info, etc.
```

3. **API Documentation**
- Open: http://localhost:8000/docs
- Verify all endpoints are listed
- Try interactive testing

4. **Generate Text**
```bash
curl -X POST http://localhost:8000/v1/generate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key" \
  -d '{"prompt":"Test","max_tokens":50}'
```

5. **Check Metrics**
```bash
curl http://localhost:8000/metrics
# Should show Prometheus metrics
```

6. **Test Rate Limiting**
```bash
# Run multiple requests rapidly
for i in {1..15}; do
  curl -X POST http://localhost:8000/v1/generate \
    -H "X-API-Key: your-api-key" \
    -H "Content-Type: application/json" \
    -d '{"prompt":"test"}' &
done
wait
# Some should return 429 (rate limit exceeded)
```

7. **Test Authentication**
```bash
# Without API key (should fail with 401)
curl -X POST http://localhost:8000/v1/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt":"test"}'

# With wrong API key (should fail with 403)
curl -X POST http://localhost:8000/v1/generate \
  -H "X-API-Key: wrong-key" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"test"}'
```

---

## 🐛 Troubleshooting Checklist

### Model Not Loading
- [ ] Check `HUGGINGFACE_TOKEN` is set correctly
- [ ] Verify internet connection for model download
- [ ] Check disk space (models can be 2-10GB)
- [ ] Check logs: `docker logs [container]` or terminal output
- [ ] Try smaller model: `MODEL__NAME=google/flan-t5-small`

### Service Won't Start
- [ ] Check port 8000 is not already in use: `lsof -i :8000`
- [ ] Verify Python version: `python --version` (should be 3.11+)
- [ ] Check Poetry installation: `poetry --version`
- [ ] Review logs for errors
- [ ] Verify `.env` file exists and is readable

### Authentication Errors
- [ ] Check `SECURITY__API_KEY` is set in `.env`
- [ ] Verify API key matches in request header
- [ ] Check header name is exactly `X-API-Key`
- [ ] Ensure no extra spaces in API key

### Rate Limit Issues
- [ ] Increase `RATE_LIMIT__REQUESTS_PER_MINUTE`
- [ ] Increase `RATE_LIMIT__BURST_SIZE`
- [ ] Or disable: `RATE_LIMIT__ENABLED=false` (not recommended for prod)

### Slow Performance
- [ ] Check `MODEL__DEVICE` (use cuda if available)
- [ ] Reduce `MODEL__MAX_TOKENS`
- [ ] Enable cache: `CACHE__ENABLED=true`
- [ ] Use smaller model
- [ ] Check system resources (CPU, RAM)

### Import Errors
- [ ] Run `poetry install` again
- [ ] Check virtual environment: `poetry env info`
- [ ] Clear cache: `poetry cache clear . --all`
- [ ] Remove lock file and reinstall: `rm poetry.lock && poetry install`

### Docker Issues
- [ ] Check Docker is running: `docker ps`
- [ ] Verify image built: `docker images | grep llm`
- [ ] Check container logs: `docker logs [container-id]`
- [ ] Verify env variables passed: `docker inspect [container-id]`
- [ ] Check port mapping: `docker port [container-id]`

---

## 📊 Performance Benchmarks

Run these to establish baseline performance:

```bash
# Single request latency
time curl -X POST http://localhost:8000/v1/generate \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Test","max_tokens":100}'

# Throughput test (requires apache bench)
ab -n 100 -c 10 -p request.json -T application/json \
  -H "X-API-Key: your-key" \
  http://localhost:8000/v1/generate

# Memory usage
docker stats [container-name]
# Or: ps aux | grep uvicorn
```

---

## 🎯 Next Steps After Setup

1. **Customize Prompts**
   - Edit `app/llm/prompts/base_system.txt`
   - Add domain-specific context

2. **Add Custom Endpoints**
   - Create new router in `app/api/routers/`
   - Register in `app/main.py`
   - Add tests in `tests/`

3. **Integrate with Your Application**
   - Use provided API endpoints
   - Implement client library
   - Add to your microservices

4. **Monitor and Optimize**
   - Set up Grafana dashboards
   - Monitor metrics at `/metrics`
   - Tune cache and rate limits based on usage

5. **Scale**
   - Deploy multiple instances
   - Add load balancer
   - Consider GPU acceleration

---

## 📞 Getting Help

If you encounter issues:

1. Check logs carefully
2. Review `DEPLOYMENT.md` troubleshooting section
3. Verify all checklist items
4. Test with simpler configuration
5. Check GitHub issues
6. Review FastAPI documentation
7. Check Hugging Face model card

---

## ✨ Success Indicators

You're ready for production when:

- ✅ All health checks pass
- ✅ Tests pass with >80% coverage
- ✅ Authentication works correctly
- ✅ Rate limiting is enforced
- ✅ Metrics are being collected
- ✅ Logs are structured and clear
- ✅ Response times are acceptable
- ✅ Model loads successfully
- ✅ Cache is working (check `/status`)
- ✅ Documentation is reviewed

---

**Good luck with your deployment! 🚀**
