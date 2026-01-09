# ORC Deployment Guide

This guide covers deploying ORC in various environments.

## Table of Contents
- [Local Development](#local-development)
- [Docker Deployment](#docker-deployment)
- [Production Deployment](#production-deployment)
- [Environment Configuration](#environment-configuration)
- [Health Checks](#health-checks)

---

## Local Development

### Prerequisites
- Python 3.8 or higher
- pip package manager
- (Optional) Virtual environment tool

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/orc.git
cd orc
```

2. **Create virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install ORC**
```bash
pip install -e .
```

4. **Install optional dependencies**
```bash
# For AI features
pip install -e .[ai]

# For web interface
pip install -e .[web]

# For development
pip install -e .[dev]
```

5. **Configure environment**
```bash
cd orc
cp .env.example .env
# Edit .env and add your API keys
```

6. **Run ORC**
```bash
orc --help
orc index .
orc chat
```

---

## Docker Deployment

### Build Docker Image

```bash
docker build -t orc:latest -f orc/Dockerfile .
```

### Run with Docker

**Basic usage:**
```bash
docker run -it --rm orc:latest orc --help
```

**Mount your codebase:**
```bash
docker run -it --rm \
  -v $(pwd):/workspace \
  -w /workspace \
  orc:latest orc index .
```

**Run web server:**
```bash
docker run -d \
  --name orc-server \
  -p 8000:8000 \
  -e ORC_SECRET_KEY=your-secret-key \
  -v $(pwd):/workspace \
  orc:latest
```

**With environment file:**
```bash
docker run -d \
  --name orc-server \
  -p 8000:8000 \
  --env-file orc/.env \
  -v $(pwd):/workspace \
  orc:latest
```

### Docker Compose

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  orc:
    build:
      context: .
      dockerfile: orc/Dockerfile
    container_name: orc-server
    ports:
      - "8000:8000"
    environment:
      - ORC_SECRET_KEY=${ORC_SECRET_KEY}
      - GROQ_API_KEY=${GROQ_API_KEY}
    volumes:
      - ./workspace:/workspace
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

Run with:
```bash
docker-compose up -d
```

---

## Production Deployment

### Pre-Deployment Checklist

- [ ] All tests passing
- [ ] Environment variables configured
- [ ] SECRET_KEY generated and set
- [ ] Database path configured
- [ ] HTTPS enabled
- [ ] Firewall rules configured
- [ ] Backup strategy in place

### Using the Deployment Script

```bash
# Test locally
python orc/scripts/deploy.py local

# Build Docker image
python orc/scripts/deploy.py docker

# Production deployment (with checks)
export ORC_SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
python orc/scripts/deploy.py production
```

### Reverse Proxy Setup (Nginx)

Create `/etc/nginx/sites-available/orc`:
```nginx
server {
    listen 80;
    server_name orc.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable and restart:
```bash
sudo ln -s /etc/nginx/sites-available/orc /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### HTTPS with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d orc.yourdomain.com
```

### Systemd Service

Create `/etc/systemd/system/orc.service`:
```ini
[Unit]
Description=ORC Web Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/orc
Environment="PATH=/opt/orc/.venv/bin"
Environment="ORC_SECRET_KEY=your-secret-key-here"
ExecStart=/opt/orc/.venv/bin/gunicorn --bind 0.0.0.0:8000 --workers 4 orc.web.app_prod:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable orc
sudo systemctl start orc
sudo systemctl status orc
```

---

## Environment Configuration

### Required Variables

**Production:**
```bash
ORC_SECRET_KEY=<generate-with-secrets.token_hex(32)>
```

### Optional Variables

**AI Providers (choose one or more):**
```bash
# Free options
OLLAMA_BASE_URL=http://localhost:11434
GROQ_API_KEY=your-groq-key
GEMINI_API_KEY=your-gemini-key

# Paid options
DEEPSEEK_API_KEY=your-deepseek-key
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
```

**Other Settings:**
```bash
ORC_DB_PATH=.orc/index.db
ORC_DEBUG=false
ORC_AI_PROVIDER=groq  # Force specific provider
```

### Generating SECRET_KEY

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Health Checks

### API Health Endpoint

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "2.0.0"
}
```

### Docker Health Check

The Dockerfile includes automatic health checks:
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
```

Check health status:
```bash
docker inspect --format='{{.State.Health.Status}}' orc-server
```

---

## Monitoring

### Logs

**Docker logs:**
```bash
docker logs -f orc-server
```

**Systemd logs:**
```bash
sudo journalctl -u orc -f
```

### Metrics

Monitor these key metrics:
- Response time
- Request count
- Error rate
- Memory usage
- CPU usage

---

## Scaling

### Horizontal Scaling with Kubernetes

Example `deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: orc
spec:
  replicas: 3
  selector:
    matchLabels:
      app: orc
  template:
    metadata:
      labels:
        app: orc
    spec:
      containers:
      - name: orc
        image: orc:latest
        ports:
        - containerPort: 8000
        env:
        - name: ORC_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: orc-secrets
              key: secret-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
```

---

## Backup and Recovery

### Database Backup

```bash
# Backup
cp .orc/index.db .orc/index.db.backup

# Restore
cp .orc/index.db.backup .orc/index.db
```

### Automated Backups

Add to crontab:
```bash
0 2 * * * cp /path/to/.orc/index.db /backups/orc-$(date +\%Y\%m\%d).db
```

---

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues and solutions.

---

## Security Considerations

1. **Never commit secrets** - Use environment variables
2. **Use HTTPS in production** - Enable with reverse proxy
3. **Keep dependencies updated** - Regular security patches
4. **Limit network exposure** - Use firewall rules
5. **Regular backups** - Automated backup strategy
6. **Monitor logs** - Watch for suspicious activity

---

## Support

- Documentation: [README.md](orc/README.md)
- Issues: [GitHub Issues](https://github.com/yourusername/orc/issues)
- Security: [SECURITY.md](SECURITY.md)
