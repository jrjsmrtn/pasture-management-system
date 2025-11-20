<!--
SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
SPDX-License-Identifier: MIT
-->

# Deployment Guide

**Audience**: Homelab sysadmins deploying PMS to production

**Purpose**: Production deployment patterns, configurations, and best practices

**Estimated Time**: 1-2 hours (depending on environment complexity)

## Overview

This guide covers deploying the Pasture Management System (PMS) in production environments. It assumes you have completed the [Installation Guide](installation-guide.md) and are familiar with basic PMS operation.

## Production vs Development

### Key Differences

| Aspect          | Development         | Production                          |
| --------------- | ------------------- | ----------------------------------- |
| **Database**    | Reset frequently    | Persistent, backed up               |
| **Server**      | Foreground process  | System service (systemd/supervisor) |
| **Access**      | localhost only      | Network accessible                  |
| **Security**    | Default credentials | Strong passwords, HTTPS             |
| **Logging**     | Console output      | Log files, rotation                 |
| **Performance** | Not critical        | Optimized, monitored                |

### Production Checklist

Before deploying to production:

- [ ] Change default admin password
- [ ] Configure HTTPS/SSL
- [ ] Set up reverse proxy (nginx or Apache)
- [ ] Configure firewall rules
- [ ] Set up backup automation
- [ ] Configure log rotation
- [ ] Set up monitoring
- [ ] Document recovery procedures

## Deployment Patterns

### Pattern 1: Single Server (Homelab - Recommended)

**Use Case**: 1-10 users, homelab environment, low-to-medium traffic

**Architecture**:

```
[Internet] → [Router/Firewall] → [Reverse Proxy] → [PMS Server]
                                      (nginx)         (Roundup)
```

**Characteristics**:

- Single physical or virtual machine
- Reverse proxy for HTTPS termination
- SQLite database (sufficient for homelab scale)
- Simple backup strategy

**Pros**:

- Simple deployment and maintenance
- Low resource requirements
- Cost-effective

**Cons**:

- Single point of failure
- Limited scalability

### Pattern 2: Containerized (Docker/Podman)

**Use Case**: Cloud environments, multi-environment deployments, CI/CD pipelines

**Architecture**:

```
[Container Host]
  ├── [PMS Container] → [Volume: database]
  ├── [Nginx Container]
  └── [Volume: static files]
```

**Note**: Container support is planned for v1.1.0. This section will be expanded in future versions.

### Pattern 3: High Availability (Future)

**Use Case**: Critical environments requiring redundancy

**Note**: HA deployment is not currently supported with SQLite backend. Future versions may support PostgreSQL or MySQL for multi-server deployments.

## Reverse Proxy Configuration

Running PMS behind a reverse proxy provides:

- HTTPS/SSL termination
- Load balancing (future)
- Static file caching
- Security hardening

### nginx Configuration (Recommended)

#### Step 1: Install nginx

**Ubuntu/Debian**:

```bash
sudo apt-get update
sudo apt-get install nginx
```

**macOS** (with MacPorts):

```bash
sudo port install nginx
```

#### Step 2: Create PMS Virtual Host

Create `/etc/nginx/sites-available/pms.conf`:

```nginx
# PMS Production Configuration
# /etc/nginx/sites-available/pms.conf

upstream pms_backend {
    server localhost:9080 fail_timeout=0;
}

server {
    listen 80;
    server_name pms.yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name pms.yourdomain.com;

    # SSL Configuration (Let's Encrypt)
    ssl_certificate /etc/letsencrypt/live/pms.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/pms.yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logging
    access_log /var/log/nginx/pms-access.log;
    error_log /var/log/nginx/pms-error.log;

    # Client upload size (for attachments)
    client_max_body_size 10M;

    # Proxy to Roundup server
    location / {
        proxy_pass http://pms_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # Buffering
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }

    # Static files (if served separately)
    location /@@file/ {
        alias /path/to/pasture-management-system/tracker/html/;
        expires 7d;
        add_header Cache-Control "public, immutable";
    }
}
```

#### Step 3: Enable Site and Test

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/pms.conf /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

### Apache Configuration (Alternative)

#### Step 1: Install Apache and Modules

**Ubuntu/Debian**:

```bash
sudo apt-get install apache2
sudo a2enmod proxy proxy_http ssl headers rewrite
```

#### Step 2: Create PMS Virtual Host

Create `/etc/apache2/sites-available/pms.conf`:

```apache
# PMS Production Configuration
# /etc/apache2/sites-available/pms.conf

<VirtualHost *:80>
    ServerName pms.yourdomain.com

    # Redirect HTTP to HTTPS
    RewriteEngine On
    RewriteCond %{HTTPS} off
    RewriteRule ^(.*)$ https://%{HTTP_HOST}$1 [R=301,L]
</VirtualHost>

<VirtualHost *:443>
    ServerName pms.yourdomain.com
    ServerAdmin admin@yourdomain.com

    # SSL Configuration
    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/pms.yourdomain.com/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/pms.yourdomain.com/privkey.pem
    SSLProtocol all -SSLv2 -SSLv3 -TLSv1 -TLSv1.1
    SSLCipherSuite HIGH:!aNULL:!MD5

    # Security Headers
    Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"
    Header always set X-Frame-Options "SAMEORIGIN"
    Header always set X-Content-Type-Options "nosniff"
    Header always set X-XSS-Protection "1; mode=block"

    # Logging
    ErrorLog ${APACHE_LOG_DIR}/pms-error.log
    CustomLog ${APACHE_LOG_DIR}/pms-access.log combined

    # Proxy Configuration
    ProxyPreserveHost On
    ProxyPass / http://localhost:9080/
    ProxyPassReverse / http://localhost:9080/

    # Timeouts
    ProxyTimeout 60
</VirtualHost>
```

#### Step 3: Enable Site and Test

```bash
# Enable site
sudo a2ensite pms.conf

# Test configuration
sudo apachectl configtest

# Restart Apache
sudo systemctl restart apache2
```

## SSL/TLS Certificate Setup

### Let's Encrypt (Recommended - Free)

#### Step 1: Install Certbot

**Ubuntu/Debian**:

```bash
sudo apt-get install certbot python3-certbot-nginx
```

**macOS** (with MacPorts):

```bash
sudo port install certbot
```

#### Step 2: Obtain Certificate

**With nginx**:

```bash
sudo certbot --nginx -d pms.yourdomain.com
```

**With Apache**:

```bash
sudo certbot --apache -d pms.yourdomain.com
```

**Manual (DNS validation)**:

```bash
sudo certbot certonly --manual --preferred-challenges dns -d pms.yourdomain.com
```

#### Step 3: Configure Auto-Renewal

Certbot automatically installs a renewal timer. Verify:

```bash
sudo systemctl status certbot.timer
```

Test renewal:

```bash
sudo certbot renew --dry-run
```

### Self-Signed Certificate (Testing/Internal)

For homelab internal use only (browsers will show warnings):

```bash
# Generate self-signed certificate (10 years)
sudo openssl req -x509 -nodes -days 3650 -newkey rsa:2048 \
  -keyout /etc/ssl/private/pms-selfsigned.key \
  -out /etc/ssl/certs/pms-selfsigned.crt \
  -subj "/C=US/ST=State/L=City/O=Homelab/CN=pms.local"

# Update nginx/Apache config to use these files
```

## System Service Configuration

Run Roundup server as a system service for automatic startup and monitoring.

### systemd Service (Linux - Recommended)

#### Step 1: Create Service File

Create `/etc/systemd/system/pms.service`:

```ini
[Unit]
Description=Pasture Management System (Roundup)
After=network.target

[Service]
Type=simple
User=pms
Group=pms
WorkingDirectory=/opt/pms/pasture-management-system
Environment="PATH=/opt/pms/pasture-management-system/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/opt/pms/pasture-management-system/venv/bin/roundup-server -p 9080 pms=tracker
Restart=on-failure
RestartSec=5s

# Security hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/pms/pasture-management-system/tracker/db

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=pms

[Install]
WantedBy=multi-user.target
```

#### Step 2: Create Service User

```bash
# Create pms user (no login)
sudo useradd -r -s /bin/false -d /opt/pms pms

# Set ownership
sudo chown -R pms:pms /opt/pms/pasture-management-system
```

#### Step 3: Enable and Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable pms.service

# Start service
sudo systemctl start pms.service

# Check status
sudo systemctl status pms.service

# View logs
sudo journalctl -u pms.service -f
```

### macOS LaunchDaemon (macOS)

Create `/Library/LaunchDaemons/com.yourdomain.pms.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.yourdomain.pms</string>
    <key>ProgramArguments</key>
    <array>
        <string>/opt/pms/venv/bin/roundup-server</string>
        <string>-p</string>
        <string>9080</string>
        <string>pms=tracker</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/opt/pms/pasture-management-system</string>
    <key>StandardOutPath</key>
    <string>/var/log/pms/pms.log</string>
    <key>StandardErrorPath</key>
    <string>/var/log/pms/pms-error.log</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

Load and start:

```bash
sudo launchctl load /Library/LaunchDaemons/com.yourdomain.pms.plist
sudo launchctl start com.yourdomain.pms
```

## Environment Configuration

### Production Environment Variables

Create `/opt/pms/pasture-management-system/.env`:

```bash
# Production Configuration
ROUNDUP_PORT=9080
TRACKER_NAME=pms
TRACKER_DIR=tracker

# Security
ROUNDUP_SECRET_KEY=<generate-random-32-char-string>

# Logging
LOG_LEVEL=INFO

# Performance
ROUNDUP_WORKERS=4
```

**Generate secret key**:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### Update config.ini for Production

Edit `tracker/config.ini`:

```ini
[main]
# ... existing config ...

# Production logging
[logging]
level = INFO
file = /var/log/pms/roundup.log

# Performance tuning
[web]
# Limit login attempts (already configured)
rate_limit_count = 4
rate_limit_period = 600  # 10 minutes

# Session timeout
session_timeout = 3600  # 1 hour
```

## Backup and Restore Procedures

### Backup Strategy

**What to Backup**:

1. Database directory: `tracker/db/`
1. Configuration: `tracker/config.ini`
1. Uploaded files: `tracker/db/files/` (if using file attachments)

### Automated Backup Script

Create `/opt/pms/scripts/backup-pms.sh`:

```bash
#!/bin/bash
# PMS Backup Script

BACKUP_DIR="/var/backups/pms"
PMS_DIR="/opt/pms/pasture-management-system"
DATE=$(date +%Y%m%d-%H%M%S)
BACKUP_FILE="pms-backup-${DATE}.tar.gz"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Create backup
tar -czf "${BACKUP_DIR}/${BACKUP_FILE}" \
    -C "$PMS_DIR" \
    tracker/db \
    tracker/config.ini

# Keep only last 30 days of backups
find "$BACKUP_DIR" -name "pms-backup-*.tar.gz" -mtime +30 -delete

echo "Backup created: ${BACKUP_DIR}/${BACKUP_FILE}"
```

Make executable and schedule:

```bash
chmod +x /opt/pms/scripts/backup-pms.sh

# Add to crontab (daily at 2 AM)
crontab -e
# Add line:
0 2 * * * /opt/pms/scripts/backup-pms.sh
```

### Restore Procedure

```bash
# Stop PMS service
sudo systemctl stop pms.service

# Extract backup
cd /opt/pms/pasture-management-system
tar -xzf /var/backups/pms/pms-backup-YYYYMMDD-HHMMSS.tar.gz

# Fix permissions
sudo chown -R pms:pms tracker/db

# Start PMS service
sudo systemctl start pms.service
```

## Update and Migration Procedures

### Update to New Version

```bash
# Stop service
sudo systemctl stop pms.service

# Backup before update
/opt/pms/scripts/backup-pms.sh

# Update code
cd /opt/pms/pasture-management-system
git pull origin main

# Update dependencies
source venv/bin/activate
uv pip install -r requirements.txt

# Run migrations (if any)
# (Currently no migration system - planned for future versions)

# Start service
sudo systemctl start pms.service

# Verify
curl -s http://localhost:9080/pms/ | grep -q "Roundup"
```

### Rollback Procedure

```bash
# Stop service
sudo systemctl stop pms.service

# Restore from backup
cd /opt/pms/pasture-management-system
tar -xzf /var/backups/pms/pms-backup-BEFORE-UPDATE.tar.gz

# Revert code
git checkout <previous-version-tag>

# Fix permissions
sudo chown -R pms:pms tracker/db

# Start service
sudo systemctl start pms.service
```

## Monitoring and Logging Setup

### Log Configuration

Create log directory:

```bash
sudo mkdir -p /var/log/pms
sudo chown pms:pms /var/log/pms
```

### Log Rotation

Create `/etc/logrotate.d/pms`:

```
/var/log/pms/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    missingok
    create 0640 pms pms
    sharedscripts
    postrotate
        systemctl reload pms.service > /dev/null 2>&1 || true
    endscript
}
```

### Basic Monitoring

**Check service health**:

```bash
# Service status
sudo systemctl status pms.service

# Recent logs
sudo journalctl -u pms.service -n 50

# HTTP health check
curl -f http://localhost:9080/pms/ || echo "PMS is down!"
```

**Simple monitoring script** (`/opt/pms/scripts/monitor-pms.sh`):

```bash
#!/bin/bash
# Simple PMS health check

if ! curl -sf http://localhost:9080/pms/ > /dev/null; then
    echo "ERROR: PMS is not responding"
    # Restart service
    sudo systemctl restart pms.service
    # Send notification (configure as needed)
    # echo "PMS was down and restarted" | mail -s "PMS Alert" admin@yourdomain.com
fi
```

Add to crontab (every 5 minutes):

```
*/5 * * * * /opt/pms/scripts/monitor-pms.sh
```

## High Availability Considerations

### Current Limitations

PMS v1.0.0 uses SQLite, which is single-server only. High availability features are not currently supported.

### Future Roadmap (v1.2.0+)

Planned HA features:

- PostgreSQL/MySQL backend support
- Multi-server deployment
- Database replication
- Load balancing
- Session persistence

### Homelab Alternatives

For homelab reliability without full HA:

1. **VM Snapshots**: Regular snapshots for quick recovery
1. **Automated Backups**: Daily backups to NAS or cloud
1. **Monitoring**: Automated health checks and restarts
1. **UPS**: Protect against power failures
1. **RAID**: Protect against disk failure

## Firewall Configuration

### iptables (Linux)

```bash
# Allow HTTP/HTTPS from LAN only
sudo iptables -A INPUT -p tcp -s 192.168.1.0/24 --dport 80 -j ACCEPT
sudo iptables -A INPUT -p tcp -s 192.168.1.0/24 --dport 443 -j ACCEPT

# Block external access
sudo iptables -A INPUT -p tcp --dport 80 -j DROP
sudo iptables -A INPUT -p tcp --dport 443 -j DROP

# Block direct access to Roundup port
sudo iptables -A INPUT -p tcp --dport 9080 -j DROP

# Save rules
sudo netfilter-persistent save
```

### firewalld (RHEL/CentOS)

```bash
# Allow HTTP/HTTPS
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https

# Block Roundup port from external
sudo firewall-cmd --permanent --add-rich-rule='rule family="ipv4" port port="9080" protocol="tcp" reject'

# Reload
sudo firewall-cmd --reload
```

## Security Hardening Checklist

Production deployment security checklist:

- [ ] Change default admin password
- [ ] Enable HTTPS with valid certificate
- [ ] Configure reverse proxy security headers
- [ ] Restrict network access (firewall rules)
- [ ] Run Roundup as non-root user
- [ ] Set restrictive file permissions (755 for directories, 644 for files)
- [ ] Enable log monitoring
- [ ] Configure automated backups
- [ ] Disable debug mode in production
- [ ] Review [Security Considerations](../reference/security-considerations.md)
- [ ] Set up rate limiting (already configured: 4 failures/10 min)
- [ ] Configure session timeout
- [ ] Regular security updates

## Performance Tuning

### SQLite Optimization

Edit `tracker/config.ini`:

```ini
[main]
# ... existing config ...

# SQLite optimizations
[database]
# Enable WAL mode for better concurrency
sqlite_pragmas = journal_mode=WAL,synchronous=NORMAL,cache_size=-64000
```

### System Resources

For homelab scale (5-10 users):

- **CPU**: 1-2 cores sufficient
- **RAM**: 512 MB - 1 GB
- **Disk**: SSD recommended for database performance
- **Network**: 10 Mbps+ sufficient

### Expected Performance

Based on benchmarks (see [Performance Benchmarks](../reference/performance-benchmarks.md)):

- Database queries: \<1 second
- Page loads: \<2 seconds
- API responses: \<500ms
- Concurrent users: 5-10 without degradation

## Troubleshooting Production Issues

### Service Won't Start

**Check logs**:

```bash
sudo journalctl -u pms.service -n 100
```

**Common causes**:

- Port already in use
- Permission issues
- Missing dependencies
- Database corruption

### 502 Bad Gateway (nginx)

**Cause**: Roundup server not running or not responding

**Solution**:

```bash
# Check Roundup server
sudo systemctl status pms.service

# Restart if needed
sudo systemctl restart pms.service
```

### Database Locked Errors

**Cause**: SQLite database locked (rare with WAL mode)

**Solution**:

```bash
# Stop service
sudo systemctl stop pms.service

# Wait for all processes to release locks
sleep 5

# Start service
sudo systemctl start pms.service
```

### Slow Performance

**Investigation**:

```bash
# Check system resources
htop

# Check disk I/O
iostat -x 1

# Check database size
du -sh /opt/pms/pasture-management-system/tracker/db/
```

**Solutions**:

- Add database indexes (future version)
- Increase system resources
- Move database to faster disk (SSD)
- Archive old data

## Related Documentation

- [Installation Guide](installation-guide.md) - Installation procedures
- [Administration Guide](administration-guide.md) - System administration
- [Security Considerations](../reference/security-considerations.md) - Security best practices
- [Performance Benchmarks](../reference/performance-benchmarks.md) - Performance targets

______________________________________________________________________

**Document Version**: 1.0.0
**Last Updated**: 2025-11-20
**Maintained By**: PMS Team
