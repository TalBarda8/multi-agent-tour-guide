# Production Deployment Guide
## Multi-Agent AI Tour Guide System

**Version:** 1.0
**Last Updated:** November 30, 2025
**Status:** Ready for Production Deployment

---

## 📋 Prerequisites

### System Requirements

- **Python:** 3.10 or higher
- **Operating System:** Linux (Ubuntu 22.04 LTS recommended), macOS, or Windows
- **Memory:** Minimum 2 GB RAM
- **Storage:** 1 GB free space (for logs and cache)
- **Network:** Stable internet connection for API calls

### Required API Keys

1. **Google Maps API Key** (Required for real routes)
   - Get from: [Google Cloud Console](https://console.cloud.google.com/)
   - Enable: Directions API
   - Cost: $0.005 per request (free tier: $200/month credit)

2. **Spotify API Credentials** (Optional, for music enrichment)
   - Get from: [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Need: Client ID and Client Secret
   - Cost: Free

3. **YouTube API Key** (Optional, for video enrichment)
   - Get from: [Google Cloud Console](https://console.cloud.google.com/)
   - Enable: YouTube Data API v3
   - Cost: Free tier sufficient for most use cases

---

## 🚀 Deployment Steps

### Step 1: Clone Repository

```bash
git clone https://github.com/TalBarda8/multi-agent-tour-guide.git
cd multi-agent-tour-guide
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

###Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

```bash
# Copy example configuration
cp .env.example .env

# Edit configuration
nano .env  # or use your preferred editor
```

**Required Configuration (.env):**

```bash
# =============================================================================
# PRODUCTION CONFIGURATION
# =============================================================================

# Google Maps API (REQUIRED for real routes)
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here

# Spotify API (OPTIONAL - for music enrichment)
SPOTIFY_CLIENT_ID=your_spotify_client_id_here
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret_here

# YouTube API (handled by Claude Code agents)
YOUTUBE_API_KEY=your_youtube_key_here

# =============================================================================
# SYSTEM CONFIGURATION
# =============================================================================

# Operating Mode
MOCK_MODE=false  # Set to 'true' for development, 'false' for production

# Timeouts (milliseconds)
AGENT_TIMEOUT_MS=5000
JUDGE_TIMEOUT_MS=3000
ROUTE_RETRIEVAL_TIMEOUT_MS=10000

# Concurrency Settings
MAX_CONCURRENT_WAYPOINTS=5
MAX_AGENT_THREADS=50

# =============================================================================
# LOGGING
# =============================================================================

# Log Level: DEBUG | INFO | WARNING | ERROR | CRITICAL
LOG_LEVEL=INFO

# Log File Path (relative or absolute)
LOG_FILE_PATH=./logs/tour-guide.log

# Log Rotation
LOG_MAX_SIZE_MB=100
LOG_BACKUP_COUNT=5

# =============================================================================
# PERFORMANCE
# =============================================================================

# Enable result caching
ENABLE_CACHING=true

# Cache TTL (seconds)
CACHE_TTL_SECONDS=3600
```

### Step 5: Create Required Directories

```bash
# Create log directory
mkdir -p logs

# Set proper permissions
chmod 755 logs
```

### Step 6: Test Configuration

```bash
# Quick configuration test
python3 -c "from src.config import get_config; config = get_config(); print('✅ Configuration loaded successfully')"

# Test Google Maps API key
python3 -c "from src.google_maps import GoogleMapsClient; client = GoogleMapsClient(); print('✅ Google Maps client initialized')"
```

### Step 7: Run System Test

```bash
# Test with sample route
python3 main.py
```

**Expected Output:**
```
================================================================================
Multi-Agent AI Tour Guide System
================================================================================
Mode: PRODUCTION
Logs: ./logs/tour-guide.log
================================================================================

Origin: Empire State Building, New York, NY
Destination: Central Park, New York, NY

Processing route...

✅ SUCCESS!

Transaction ID: TXID-...
Route Summary:
  Distance: X.X km
  Duration: XX mins
  Waypoints: X
  Enriched: X (XX.X%)
```

---

## 🏭 Production Environment Setup

### Option 1: systemd Service (Linux)

Create a systemd service for automatic startup and management.

**Create service file:** `/etc/systemd/system/tour-guide.service`

```ini
[Unit]
Description=Multi-Agent Tour Guide System
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/tour-guide
Environment="PATH=/opt/tour-guide/venv/bin"
ExecStart=/opt/tour-guide/venv/bin/python3 /opt/tour-guide/main.py
Restart=always
RestartSec=10

# Security
NoNewPrivileges=true
PrivateTmp=true

# Logging
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Enable and start service:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable tour-guide
sudo systemctl start tour-guide

# Check status
sudo systemctl status tour-guide

# View logs
sudo journalctl -u tour-guide -f
```

### Option 2: Docker Deployment

**Create Dockerfile:**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create log directory
RUN mkdir -p logs

# Run application
CMD ["python3", "main.py"]
```

**Build and run:**
```bash
# Build image
docker build -t tour-guide:latest .

# Run container
docker run -d \
  --name tour-guide \
  -v $(pwd)/.env:/app/.env \
  -v $(pwd)/logs:/app/logs \
  --restart unless-stopped \
  tour-guide:latest

# View logs
docker logs -f tour-guide
```

### Option 3: Cloud Deployment (AWS, GCP, Azure)

**General steps:**
1. Create compute instance (EC2, Compute Engine, VM)
2. Install Python 3.10+
3. Clone repository
4. Follow Steps 1-7 above
5. Set up systemd service or use cloud-native orchestration

---

## 📊 Monitoring & Observability

### Log Monitoring

**Log Location:** `./logs/tour-guide.log`

**Log Format:** Structured JSON
```json
{
  "timestamp": "2025-11-30 20:15:55,712",
  "level": "INFO",
  "transaction_id": "TXID-...",
  "module": "orchestrator",
  "message": "Waypoint enrichment completed",
  "waypoint_id": 1,
  "processing_time_ms": 4521
}
```

**Useful Log Queries:**

```bash
# Search by transaction ID
grep "TXID-..." logs/tour-guide.log | jq .

# Find errors
grep '"level":"ERROR"' logs/tour-guide.log | jq .

# Agent performance
grep "agent completed" logs/tour-guide.log | jq '.execution_time_ms'

# Success rate
grep "Waypoint enrichment completed" logs/tour-guide.log | jq '.agent_success_count'
```

### Health Checks

Create a health check endpoint or script:

```python
# health_check.py
from src.config import get_config
from src.google_maps import GoogleMapsClient

def health_check():
    try:
        config = get_config()
        client = GoogleMapsClient()
        return {"status": "healthy", "mode": "production" if not config.mock_mode else "development"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

if __name__ == "__main__":
    result = health_check()
    print(result)
    exit(0 if result["status"] == "healthy" else 1)
```

### Metrics to Monitor

1. **Request Metrics**
   - Total routes processed
   - Average processing time
   - Success rate

2. **Agent Metrics**
   - Agent success rates (YouTube, Spotify, History)
   - Average agent response times
   - Timeout counts

3. **API Metrics**
   - Google Maps API calls
   - API errors
   - Quota usage

4. **System Metrics**
   - CPU usage
   - Memory usage
   - Disk space (logs)
   - Thread pool utilization

---

## 🔐 Security Best Practices

### API Key Security

**✅ DO:**
- Store API keys in `.env` file (never commit)
- Use environment variables in production
- Restrict API keys to specific APIs
- Set usage quotas
- Rotate keys periodically
- Use different keys for dev/staging/production

**❌ DON'T:**
- Commit API keys to version control
- Hardcode keys in source code
- Share keys publicly
- Use same key across environments

### File Permissions

```bash
# Secure .env file
chmod 600 .env

# Secure log directory
chmod 750 logs

# Application files
chmod 644 *.py
chmod 755 $(find src -type d)
```

### Network Security

- Use HTTPS for all external API calls (default)
- Implement rate limiting if exposing as web service
- Use firewall rules to restrict access
- Consider VPN for sensitive deployments

---

## 💰 Cost Optimization

### Google Maps API

**Free Tier:** $200/month credit = ~40,000 requests

**Optimization Strategies:**

1. **Implement Caching**
   ```python
   # Cache common routes for 1 hour
   from functools import lru_cache

   @lru_cache(maxsize=1000)
   def get_cached_route(origin, destination):
       return client.get_directions(origin, destination)
   ```

2. **Batch Requests**
   - Process multiple routes during off-peak hours
   - Group similar routes

3. **Monitor Usage**
   - Set up billing alerts in Google Cloud Console
   - Track daily usage
   - Implement request throttling

### Spotify API

**Cost:** Free for reasonable usage

**Optimization:**
- Cache music search results
- Implement exponential backoff for rate limits

### Agent Costs

Claude Code agents have usage limits:
- Plan accordingly for production load
- Implement fallback mechanisms
- Consider agent response caching

---

## 🔄 Backup & Recovery

### Log Backup

```bash
# Create backup script
#!/bin/bash
# backup_logs.sh

DATE=$(date +%Y%m%d)
tar -czf logs_backup_$DATE.tar.gz logs/
aws s3 cp logs_backup_$DATE.tar.gz s3://your-bucket/tour-guide/logs/
rm logs_backup_$DATE.tar.gz
```

**Run daily via cron:**
```cron
0 2 * * * /opt/tour-guide/backup_logs.sh
```

### Configuration Backup

```bash
# Backup configuration (excluding secrets)
cp .env.example .env.backup.example
# Manually document API key sources
```

### Disaster Recovery

**Recovery Steps:**
1. Provision new server
2. Clone repository
3. Restore `.env` from secure storage
4. Install dependencies
5. Start service
6. Verify health check

**RTO (Recovery Time Objective):** < 30 minutes
**RPO (Recovery Point Objective):** Last successful request (no data loss)

---

## 🧪 Testing in Production

### Smoke Tests

Run these after deployment:

```bash
# 1. Health check
python3 health_check.py

# 2. Simple route test
python3 -c "from src.pipeline import execute_pipeline_safe; r = execute_pipeline_safe('Times Square, NYC', 'Central Park, NYC'); print('✅ OK' if 'error' not in r else '❌ ERROR')"

# 3. Agent test
# (requires Claude Code orchestration)

# 4. Log verification
tail -n 20 logs/tour-guide.log | jq .
```

### Load Testing

**Using locust:**

```python
# locustfile.py
from locust import User, task, between
from src.pipeline import execute_pipeline_safe

class TourGuideUser(User):
    wait_time = between(5, 10)

    @task
    def process_route(self):
        execute_pipeline_safe(
            "Times Square, NYC",
            "Central Park, NYC"
        )
```

**Run test:**
```bash
pip install locust
locust --users 10 --spawn-rate 1 --run-time 5m
```

---

## 📈 Scaling Considerations

### Vertical Scaling (Single Server)

**For up to 100 requests/day:**
- 2 CPU cores
- 4 GB RAM
- Current architecture sufficient

### Horizontal Scaling (Multiple Servers)

**For > 100 requests/day:**

```
               Load Balancer
                     |
      ┌──────────────┼──────────────┐
      |              |               |
  Server 1       Server 2        Server 3
      |              |               |
      └──────────────┼───────────────┘
                     |
              Shared Cache (Redis)
```

**Implementation:**
1. Deploy multiple instances
2. Add load balancer (nginx, HAProxy)
3. Implement shared caching (Redis)
4. Use sticky sessions if needed

### Database Integration (Future)

For persistent storage of routes:
- PostgreSQL for route history
- Redis for caching
- S3 for log archival

---

## 🐛 Troubleshooting Guide

### Common Issues

#### Issue: "API key is invalid"

**Symptoms:**
```
ERROR: Google Maps API error: REQUEST_DENIED
Message: API key is invalid or request was denied
```

**Solutions:**
1. Verify API key in `.env` is correct
2. Check Directions API is enabled in Google Cloud Console
3. Verify API key restrictions aren't blocking requests
4. Confirm billing is enabled in Google Cloud

#### Issue: Agent session limits

**Symptoms:**
```
Session limit reached ∙ resets 12am
```

**Solutions:**
1. Wait for daily reset
2. Implement request queuing
3. Use multiple agent instances if available
4. Cache agent results

#### Issue: High memory usage

**Symptoms:**
- Process using > 1 GB RAM
- System becomes slow

**Solutions:**
1. Reduce `MAX_AGENT_THREADS` in `.env`
2. Reduce `MAX_CONCURRENT_WAYPOINTS`
3. Enable log rotation
4. Clear old logs periodically

#### Issue: Slow response times

**Symptoms:**
- Routes taking > 30 seconds

**Solutions:**
1. Check network latency to Google Maps API
2. Verify agent response times in logs
3. Increase `AGENT_TIMEOUT_MS` if agents timing out
4. Consider reducing waypoints processed in parallel

### Getting Help

1. **Check Logs:** `logs/tour-guide.log`
2. **Review Documentation:** RPD.md, integration guides
3. **Search Issues:** GitHub repository
4. **Check API Status:**
   - [Google Maps Status](https://status.cloud.google.com/)
   - [Spotify Status](https://developer.spotify.com/status/)

---

## 📚 Additional Resources

### Documentation

- **[RPD.md](./RPD.md)** - Complete system specification
- **[README.md](./README.md)** - Project overview
- **[AGENT_CREATION_GUIDE.md](./AGENT_CREATION_GUIDE.md)** - Agent specifications
- **[REAL_AGENT_INTEGRATION.md](./REAL_AGENT_INTEGRATION.md)** - Integration testing report
- **[PHASE4_GOOGLE_MAPS_INTEGRATION.md](./PHASE4_GOOGLE_MAPS_INTEGRATION.md)** - Google Maps integration details

### External APIs

- [Google Maps Directions API Documentation](https://developers.google.com/maps/documentation/directions)
- [Spotify Web API Documentation](https://developer.spotify.com/documentation/web-api)
- [YouTube Data API Documentation](https://developers.google.com/youtube/v3)

### Tools

- [jq - JSON processor](https://stedolan.github.io/jq/)
- [htop - System monitor](https://htop.dev/)
- [locust - Load testing](https://locust.io/)

---

## ✅ Pre-Launch Checklist

### Configuration

- [ ] All API keys obtained and configured
- [ ] `.env` file created from `.env.example`
- [ ] `MOCK_MODE=false` for production
- [ ] Log directory created with proper permissions
- [ ] Timeouts configured appropriately
- [ ] Concurrency settings optimized for server

### Security

- [ ] API keys not committed to version control
- [ ] `.env` file permissions set to 600
- [ ] API key restrictions configured in cloud consoles
- [ ] Usage quotas set
- [ ] Firewall rules configured

### Monitoring

- [ ] Log rotation configured
- [ ] Log monitoring solution in place
- [ ] Health check script created
- [ ] Alerting configured for critical errors
- [ ] Usage tracking enabled

### Testing

- [ ] Smoke tests passed
- [ ] Integration tests passed
- [ ] Load testing completed
- [ ] Error scenarios tested
- [ ] Recovery procedures verified

### Documentation

- [ ] Deployment steps documented
- [ ] Runbook created for common issues
- [ ] API documentation reviewed
- [ ] Team trained on system

---

## 🎉 Deployment Complete!

Once all checklist items are complete, your system is ready for production!

**System Capabilities:**
- ✅ Real route retrieval from Google Maps
- ✅ Multi-agent content enrichment (YouTube, Spotify, History)
- ✅ Intelligent content selection
- ✅ Complete transaction tracing
- ✅ Comprehensive error handling
- ✅ Production-ready performance
- ✅ Scalable architecture

**Support:**
- 📧 Issues: GitHub repository
- 📝 Documentation: See links above
- 🔍 Logs: `./logs/tour-guide.log`

---

**Version:** 1.0
**Status:** Production Ready
**Last Updated:** 2025-11-30
