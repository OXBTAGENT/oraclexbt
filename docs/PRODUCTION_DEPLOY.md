# Production Deployment Guide for OracleXBT

## 🚀 Quick Deployment Options

### Option 1: Docker (Recommended)

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Option 2: Gunicorn (Production Server)

```bash
# Install dependencies
pip install -r requirements-production.txt

# Run with Gunicorn
gunicorn --config gunicorn_config.py bin.api_server:app

# Or in background
gunicorn --config gunicorn_config.py --daemon bin.api_server:app
```

### Option 3: Development Server

```bash
python bin/api_server.py
```

## 📋 Pre-Deployment Checklist

### Security
- [ ] Change all default passwords
- [ ] Set `security.require_https: true` in config.yaml
- [ ] Use environment variables for sensitive data
- [ ] Set up firewall rules
- [ ] Enable rate limiting
- [ ] Review and restrict CORS settings

### Database
- [ ] Set up production database (PostgreSQL recommended)
- [ ] Configure automatic backups
- [ ] Test database migrations
- [ ] Set up connection pooling

### Monitoring
- [ ] Configure logging (check logs/ directory)
- [ ] Set up health check monitoring
- [ ] Enable metrics collection
- [ ] Set up alerting (email/Telegram)

### Performance
- [ ] Configure Redis for caching
- [ ] Tune Gunicorn worker count
- [ ] Set up CDN for static assets
- [ ] Enable response compression

## 🔧 Configuration

Edit `config.yaml` before deployment:

```yaml
server:
  host: "0.0.0.0"
  port: 7777
  debug: false  # MUST be false in production

security:
  require_https: true  # Enable in production
  allow_demo_mode: false  # Disable in production

database:
  type: "postgresql"  # Use PostgreSQL for production
  host: "localhost"
  port: 5432
  name: "oraclexbt"
  user: "oraclexbt"
  password: "CHANGE_THIS_PASSWORD"
```

## 🌐 Nginx Configuration

Create `/etc/nginx/sites-available/oraclexbt`:

```nginx
upstream oraclexbt {
    server 127.0.0.1:7777;
}

server {
    listen 80;
    server_name your-domain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL Configuration
    ssl_certificate /path/to/fullchain.pem;
    ssl_certificate_key /path/to/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Proxy Settings
    location / {
        proxy_pass http://oraclexbt;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Static files
    location /static {
        alias /path/to/oraclexbt/website;
        expires 1d;
        add_header Cache-Control "public, immutable";
    }

    # Health check
    location /api/health {
        proxy_pass http://oraclexbt;
        access_log off;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/oraclexbt /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 🔄 Systemd Service

Create `/etc/systemd/system/oraclexbt.service`:

```ini
[Unit]
Description=OracleXBT Trading Platform
After=network.target

[Service]
Type=notify
User=oraclexbt
Group=oraclexbt
WorkingDirectory=/opt/oraclexbt
Environment="PATH=/opt/oraclexbt/venv/bin"
ExecStart=/opt/oraclexbt/venv/bin/gunicorn --config gunicorn_config.py bin.api_server:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
KillSignal=SIGQUIT
TimeoutStopSec=5
PrivateTmp=true
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable oraclexbt
sudo systemctl start oraclexbt
sudo systemctl status oraclexbt
```

## 📊 Monitoring Setup

### Health Check
```bash
curl http://localhost:7777/api/health
```

### Logs
```bash
# Application logs
tail -f logs/oraclexbt.log

# Gunicorn logs
tail -f logs/gunicorn-error.log

# System logs
sudo journalctl -u oraclexbt -f
```

### Prometheus Metrics (Optional)
Access metrics at: `http://localhost:7777/metrics`

## 🔐 SSL Certificate (Let's Encrypt)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal test
sudo certbot renew --dry-run
```

## 💾 Database Backup

### Automated Backup Script
Create `/opt/oraclexbt/backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/opt/oraclexbt/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# SQLite backup
cp data/oraclexbt.db "$BACKUP_DIR/oraclexbt_$DATE.db"

# PostgreSQL backup (if using)
# pg_dump -U oraclexbt oraclexbt > "$BACKUP_DIR/oraclexbt_$DATE.sql"

# Keep only last 7 days
find $BACKUP_DIR -name "oraclexbt_*.db" -mtime +7 -delete

# Compress old backups
find $BACKUP_DIR -name "oraclexbt_*.db" -mtime +1 -exec gzip {} \;
```

Add to crontab:
```bash
# Daily backup at 2 AM
0 2 * * * /opt/oraclexbt/backup.sh
```

## 📈 Performance Tuning

### Gunicorn Workers
```python
# gunicorn_config.py
workers = (2 * cpu_count) + 1  # Adjust based on load
worker_class = "gevent"  # For I/O bound applications
```

### Database Connection Pool
```yaml
# config.yaml
database:
  pool_size: 20
  max_overflow: 10
  pool_timeout: 30
```

### Redis Caching
```bash
# Install Redis
sudo apt install redis-server

# Enable in config
cache:
  enabled: true
  backend: redis
  redis_url: "redis://localhost:6379/0"
```

## 🚨 Troubleshooting

### Service won't start
```bash
# Check logs
sudo journalctl -u oraclexbt -n 50

# Check port availability
sudo netstat -tulpn | grep 7777

# Check file permissions
ls -la /opt/oraclexbt
```

### High CPU usage
```bash
# Check worker count
ps aux | grep gunicorn

# Monitor system resources
htop

# Check database connections
# For PostgreSQL:
# SELECT count(*) FROM pg_stat_activity;
```

### Memory leaks
```bash
# Monitor memory
watch -n 1 'ps aux | grep gunicorn'

# Restart workers periodically
# Add to gunicorn_config.py:
max_requests = 1000
max_requests_jitter = 50
```

## 🔄 Updates and Maintenance

### Update Application
```bash
cd /opt/oraclexbt
git pull
pip install -r requirements-production.txt --upgrade
sudo systemctl restart oraclexbt
```

### Database Migrations
```bash
# Backup first
./backup.sh

# Run migrations (implement as needed)
python scripts/migrate_database.py
```

### Rolling Updates (Zero Downtime)
```bash
# With Gunicorn
kill -HUP $(cat logs/gunicorn.pid)

# With Docker
docker-compose up -d --no-deps --build web
```

## 📞 Support

For issues or questions:
- GitHub Issues: https://github.com/OXBTAGENT/oraclexbt/issues
- Documentation: https://github.com/OXBTAGENT/oraclexbt/docs

## ⚠️ Important Notes

1. **Never use demo mode in production** - Set `allow_demo_mode: false`
2. **Always use HTTPS** - Set `require_https: true`
3. **Regular backups** - Automate daily database backups
4. **Monitor logs** - Set up log aggregation and alerting
5. **Security updates** - Keep all dependencies up to date
6. **Rate limiting** - Enable to prevent abuse
7. **Firewall** - Restrict access to necessary ports only
