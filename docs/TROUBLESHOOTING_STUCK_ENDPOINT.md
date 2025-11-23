# Troubleshooting: Endpoint Stuck/Hanging

## Problem: Request Hangs for 6+ Minutes

When running:
```bash
curl "http://localhost:8000/api/v1/search?q=Insulin&limit=5"
```

The request hangs and times out.

## Root Causes

1. **Google Blocking**: Google detects automated traffic and blocks/challenges the request
2. **Timeout Issues**: Network timeout or slow response from Google
3. **Rate Limiting**: Too many requests in short time
4. **CAPTCHA Challenge**: Google presents a CAPTCHA page

## Solutions

### Solution 1: Enable Test Mode (Fastest)

Use mock data for development/testing:

```bash
# Edit .env file
echo "TEST_MODE=true" >> .env

# Or export environment variable
export TEST_MODE=true

# Restart server
make dev
```

With test mode enabled, the API returns mock data instantly without making real requests to Google.

### Solution 2: Increase Timeout

```bash
# Edit .env file
REQUEST_TIMEOUT=30
REQUEST_DELAY=2.0
```

### Solution 3: Check Server Logs

Look for specific errors:

```bash
# In the terminal running the server, check for:
# - "Rate limited by Google"
# - "anti-bot challenge detected"
# - "Connection timeout"
# - "Failed to fetch"
```

### Solution 4: Test Health Endpoint First

```bash
curl http://localhost:8000/api/v1/health
```

If health endpoint works, the server is running correctly and the issue is with the scraper.

### Solution 5: Use Alternative Backends (Future)

For production use:
- **Playwright**: Better anti-bot evasion (install with `poetry install --extras playwright`)
- **Official APIs**: Google Custom Search API, News API

## Configuration Changes Made

The following improvements were implemented:

1. **Increased timeout**: `REQUEST_TIMEOUT` from 10s to 30s
2. **Reduced initial delay**: `REQUEST_DELAY` from 1.0s to 0.5s
3. **Added test mode**: `TEST_MODE=true` returns mock data
4. **Better logging**: Debug mode shows request details
5. **Removed initial delay**: First request doesn't wait unnecessarily

## Quick Test

```bash
# 1. Enable test mode
export TEST_MODE=true

# 2. Restart server (Ctrl+C current server, then)
make dev

# 3. Test immediately
curl "http://localhost:8000/api/v1/search?q=Insulin&limit=5" | python -m json.tool
```

Should return instantly with mock data.

## Production Recommendations

For production use with real Google scraping:

1. **Increase delays**:
   ```
   REQUEST_DELAY=5.0  # 5 seconds between requests
   REQUEST_TIMEOUT=60  # 60 second timeout
   ```

2. **Monitor logs** for blocking indicators

3. **Consider official APIs**:
   - Google Custom Search API
   - News API
   - PubMed API for medical content

4. **Use rotating proxies** (not implemented in this project)

5. **Implement persistent cache** (Redis) to reduce requests

## Updated Environment Variables

Your `.env` file should now have:

```env
DEBUG=true
TEST_MODE=true          # New: Enable for development
REQUEST_TIMEOUT=30      # Increased from 10
REQUEST_DELAY=0.5       # Reduced from 1.0
```

## Testing the Fix

```bash
# 1. Stop current server (Ctrl+C)

# 2. Verify .env file
cat .env | grep TEST_MODE

# 3. Start server
make dev

# 4. In another terminal, test
curl "http://localhost:8000/api/v1/search?q=Insulin&limit=5"

# Should return immediately with 5 mock articles
```

## Understanding Test Mode

When `TEST_MODE=true`:
- ✅ No real HTTP requests to Google
- ✅ Returns instantly (no network delay)
- ✅ Returns realistic mock data
- ✅ Perfect for development/testing
- ✅ Safe (no ToS violations)

When `TEST_MODE=false`:
- ⚠️ Makes real requests to Google
- ⚠️ Subject to rate limiting
- ⚠️ May be blocked by anti-bot measures
- ⚠️ Slower (network + parsing time)
- ⚠️ May violate Google's ToS

## Next Steps

1. **For Development**: Keep `TEST_MODE=true`
2. **For Testing Real Scraping**: Set `TEST_MODE=false` and increase delays
3. **For Production**: Use official APIs instead
