<!--
SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
SPDX-License-Identifier: MIT
-->

# Administration Guide

**Audience**: Homelab sysadmins administering production PMS installations

**Purpose**: System administration procedures, maintenance tasks, and troubleshooting

**Estimated Time**: Reference guide (task-specific)

## Overview

This guide covers day-to-day administration tasks for the Pasture Management System. It assumes you have completed the [Installation Guide](installation-guide.md) and [Deployment Guide](deployment-guide.md).

## User Management and Permissions

### Roundup Permission Model

PMS uses Roundup's built-in permission system with roles and permissions.

**Default Roles**:

- **Admin**: Full system access (user management, configuration, all data)
- **User**: Standard access (create/edit issues, changes, CIs based on permissions)
- **Anonymous**: Read-only access (if enabled)

### Creating New Users

#### Via Web UI (Recommended)

1. Log in as admin
1. Navigate to **Admin** → **Users**
1. Click **Create New User**
1. Fill in user details:
   - **Username**: Unique identifier (lowercase, no spaces)
   - **Password**: Strong password (8+ characters)
   - **Email**: User's email address (optional but recommended)
   - **Real Name**: Display name
   - **Roles**: Assign appropriate role(s)
1. Click **Submit**

#### Via Command Line

```bash
cd /opt/pms/pasture-management-system/tracker
uv run roundup-admin create user username=jsmith password=SecurePass123 realname="John Smith" roles=User
```

### Resetting User Passwords

#### Via Web UI

1. Log in as admin
1. Navigate to **Admin** → **Users**
1. Click on the user to edit
1. Enter new password in **Password** field
1. Click **Submit**

#### Via Command Line

```bash
cd /opt/pms/pasture-management-system/tracker
uv run roundup-admin set user password=NewSecurePass123
```

**Reset admin password** (if locked out):

```bash
cd /opt/pms/pasture-management-system/tracker
uv run roundup-admin set user1 password=NewAdminPassword
```

(Note: `user1` is typically the admin user ID)

### Managing User Roles

**Available Permissions** (see `tracker/schema.py`):

- **User**: Standard user access
- **Admin**: Administrative access

**Assign role via CLI**:

```bash
uv run roundup-admin set user5 roles=Admin
```

**Remove admin role**:

```bash
uv run roundup-admin set user5 roles=User
```

### Disabling Users

**Via Web UI**:

1. Navigate to **Admin** → **Users**
1. Edit user
1. Set **Active** to "No"
1. Click **Submit**

**Via CLI**:

```bash
uv run roundup-admin retire user username=jsmith
```

### Listing Users

```bash
# List all users
cd /opt/pms/pasture-management-system/tracker
uv run roundup-admin list user

# Show user details
uv run roundup-admin get user5
```

## Database Maintenance

### Database Backup

**Manual Backup**:

```bash
# Stop service for consistent backup
sudo systemctl stop pms.service

# Create backup
tar -czf /var/backups/pms/pms-backup-$(date +%Y%m%d).tar.gz \
  -C /opt/pms/pasture-management-system \
  tracker/db tracker/config.ini

# Restart service
sudo systemctl start pms.service
```

**Automated Backup** (already configured in [Deployment Guide](deployment-guide.md)):

```bash
# Check backup script
cat /opt/pms/scripts/backup-pms.sh

# Run manually
/opt/pms/scripts/backup-pms.sh

# Verify backups
ls -lh /var/backups/pms/
```

### Database Vacuum (SQLite Optimization)

SQLite databases can become fragmented over time. Vacuuming reclaims space and optimizes performance.

**Check database size**:

```bash
du -sh /opt/pms/pasture-management-system/tracker/db/
```

**Vacuum database** (requires downtime):

```bash
# Stop service
sudo systemctl stop pms.service

# Vacuum each database file
cd /opt/pms/pasture-management-system/tracker/db
for db in *.db; do
    echo "Vacuuming $db..."
    sqlite3 "$db" "VACUUM;"
done

# Check new size
du -sh /opt/pms/pasture-management-system/tracker/db/

# Restart service
sudo systemctl start pms.service
```

**Schedule monthly vacuum**:

Add to crontab:

```
# Monthly database vacuum (first Sunday at 3 AM)
0 3 1-7 * 0 /opt/pms/scripts/vacuum-db.sh
```

Create `/opt/pms/scripts/vacuum-db.sh`:

```bash
#!/bin/bash
# Monthly SQLite vacuum script

systemctl stop pms.service
sleep 5

cd /opt/pms/pasture-management-system/tracker/db
for db in *.db; do
    sqlite3 "$db" "VACUUM;"
done

systemctl start pms.service
```

### Database Integrity Check

```bash
# Stop service
sudo systemctl stop pms.service

# Check each database
cd /opt/pms/pasture-management-system/tracker/db
for db in *.db; do
    echo "Checking $db..."
    sqlite3 "$db" "PRAGMA integrity_check;"
done

# Restart service
sudo systemctl start pms.service
```

### Database Recovery

If database corruption is detected:

```bash
# Stop service
sudo systemctl stop pms.service

# Restore from latest backup
cd /opt/pms/pasture-management-system
tar -xzf /var/backups/pms/pms-backup-YYYYMMDD.tar.gz

# Fix permissions
sudo chown -R pms:pms tracker/db

# Restart service
sudo systemctl start pms.service

# Verify
curl -f http://localhost:9080/pms/ && echo "Recovery successful"
```

## Log Management and Rotation

### Log Locations

**systemd journal** (default):

```bash
# View logs
sudo journalctl -u pms.service

# Follow logs (tail -f)
sudo journalctl -u pms.service -f

# Last 100 lines
sudo journalctl -u pms.service -n 100

# Since yesterday
sudo journalctl -u pms.service --since yesterday

# Specific time range
sudo journalctl -u pms.service --since "2025-01-01 00:00:00" --until "2025-01-02 00:00:00"
```

**File logs** (if configured):

- `/var/log/pms/roundup.log` - Roundup application logs
- `/var/log/pms/pms.log` - systemd stdout logs
- `/var/log/pms/pms-error.log` - systemd stderr logs
- `/var/log/nginx/pms-access.log` - nginx access logs
- `/var/log/nginx/pms-error.log` - nginx error logs

### Log Rotation

**Verify logrotate configuration**:

```bash
cat /etc/logrotate.d/pms
```

**Test logrotate**:

```bash
# Dry run
sudo logrotate -d /etc/logrotate.d/pms

# Force rotation (for testing)
sudo logrotate -f /etc/logrotate.d/pms

# Check rotated logs
ls -lh /var/log/pms/
```

### Analyzing Logs

**Common log queries**:

```bash
# Find errors
sudo journalctl -u pms.service | grep -i error

# Find login attempts
sudo journalctl -u pms.service | grep -i "login"

# Count errors by type
sudo journalctl -u pms.service | grep ERROR | sort | uniq -c | sort -rn

# Export logs to file
sudo journalctl -u pms.service --since "7 days ago" > /tmp/pms-logs-7days.txt
```

**nginx access log analysis**:

```bash
# Top 10 IPs by request count
awk '{print $1}' /var/log/nginx/pms-access.log | sort | uniq -c | sort -rn | head -10

# Response codes
awk '{print $9}' /var/log/nginx/pms-access.log | sort | uniq -c | sort -rn

# Most accessed URLs
awk '{print $7}' /var/log/nginx/pms-access.log | sort | uniq -c | sort -rn | head -10
```

## Performance Tuning

### System Resource Monitoring

**Check resource usage**:

```bash
# CPU and memory
htop

# Disk I/O
iostat -x 1

# Disk usage
df -h

# PMS process specifically
ps aux | grep roundup-server
```

### Performance Baselines

Expected performance for homelab scale (see [Performance Benchmarks](../reference/performance-benchmarks.md)):

- **Database queries**: \<1 second
- **Page loads**: \<2 seconds
- **API responses**: \<500ms
- **Concurrent users**: 5-10 without degradation

### Optimization Techniques

#### 1. Enable SQLite WAL Mode

Edit `tracker/config.ini`:

```ini
[database]
sqlite_pragmas = journal_mode=WAL,synchronous=NORMAL,cache_size=-64000
```

Restart service:

```bash
sudo systemctl restart pms.service
```

#### 2. Increase System Cache (Linux)

For systems with 2GB+ RAM:

```bash
# Temporary (until reboot)
echo 3 > /proc/sys/vm/drop_caches

# Permanent - add to /etc/sysctl.conf
vm.swappiness=10
vm.vfs_cache_pressure=50
```

Apply changes:

```bash
sudo sysctl -p
```

#### 3. Move Database to SSD

If database is on HDD, move to SSD:

```bash
# Stop service
sudo systemctl stop pms.service

# Move database
sudo mv /opt/pms/pasture-management-system/tracker/db /mnt/ssd/pms-db
sudo ln -s /mnt/ssd/pms-db /opt/pms/pasture-management-system/tracker/db

# Fix permissions
sudo chown -R pms:pms /mnt/ssd/pms-db

# Restart service
sudo systemctl start pms.service
```

#### 4. nginx Caching

Add to nginx configuration:

```nginx
# Enable caching
proxy_cache_path /var/cache/nginx/pms levels=1:2 keys_zone=pms_cache:10m max_size=100m inactive=60m;

location / {
    proxy_pass http://pms_backend;
    proxy_cache pms_cache;
    proxy_cache_valid 200 5m;
    proxy_cache_bypass $http_pragma $http_authorization;
    # ... other proxy settings ...
}
```

### Performance Troubleshooting

**Slow queries** (no built-in profiling yet):

Future versions will include query profiling. Current approach:

```bash
# Check database size
du -sh tracker/db/

# Check for database locks
lsof tracker/db/*.db

# Monitor during slow operation
htop
iostat -x 1
```

**High memory usage**:

```bash
# Check PMS memory usage
ps aux | grep roundup-server | awk '{print $6}'

# Restart service if excessive
sudo systemctl restart pms.service
```

## Troubleshooting Common Issues

### Issue 1: Service Won't Start

**Symptoms**:

```bash
sudo systemctl status pms.service
# Status: failed
```

**Diagnosis**:

```bash
# Check logs
sudo journalctl -u pms.service -n 50

# Check port availability
lsof -i :9080

# Check permissions
ls -la /opt/pms/pasture-management-system/tracker/db/
```

**Solutions**:

1. **Port conflict**: Kill process using port 9080 or change PMS port
1. **Permission denied**: Fix ownership: `sudo chown -R pms:pms /opt/pms/pasture-management-system`
1. **Database corruption**: Restore from backup

### Issue 2: Login Failures

**Symptoms**: Cannot log in with correct credentials

**Diagnosis**:

```bash
# Check user exists
cd /opt/pms/pasture-management-system/tracker
uv run roundup-admin list user | grep username

# Check rate limiting logs
sudo journalctl -u pms.service | grep "rate limit"
```

**Solutions**:

1. **Rate limited**: Wait 10 minutes or reset: edit `tracker/config.ini`, restart service
1. **Wrong password**: Reset password via admin CLI
1. **User disabled**: Re-enable via admin CLI

### Issue 3: 502 Bad Gateway

**Symptoms**: nginx returns 502 error

**Diagnosis**:

```bash
# Check Roundup is running
sudo systemctl status pms.service

# Check nginx can reach backend
curl http://localhost:9080/pms/

# Check nginx logs
sudo tail -f /var/log/nginx/pms-error.log
```

**Solutions**:

1. **Roundup not running**: `sudo systemctl start pms.service`
1. **Port mismatch**: Verify nginx upstream matches Roundup port
1. **Firewall blocking**: Check `iptables -L` or `firewall-cmd --list-all`

### Issue 4: Database Locked

**Symptoms**:

```
database is locked
```

**Solutions**:

```bash
# Stop service
sudo systemctl stop pms.service

# Wait for locks to release
sleep 10

# Restart service
sudo systemctl start pms.service

# If persists, check for stale processes
lsof tracker/db/*.db
kill <pid>
```

### Issue 5: Disk Space Full

**Symptoms**: Service stops, logs show disk errors

**Diagnosis**:

```bash
# Check disk usage
df -h

# Find large files
du -ah /opt/pms | sort -rh | head -20

# Check database size
du -sh /opt/pms/pasture-management-system/tracker/db/
```

**Solutions**:

1. **Clean old backups**: `find /var/backups/pms -mtime +30 -delete`
1. **Vacuum database**: See "Database Vacuum" section above
1. **Clean logs**: `sudo journalctl --vacuum-time=7d`
1. **Expand disk**: Add storage or move database to larger volume

### Issue 6: Slow Performance

**Diagnosis**:

```bash
# Check system load
uptime

# Check CPU and memory
htop

# Check disk I/O
iostat -x 1

# Check database size
du -sh tracker/db/
```

**Solutions**:

1. **High load**: Restart service, check for runaway processes
1. **Low memory**: Increase system RAM or reduce other services
1. **Disk I/O**: Move database to SSD
1. **Large database**: Vacuum database (see "Database Vacuum" section)

## Security Hardening Checklist

Regular security maintenance tasks:

### Monthly Security Tasks

- [ ] Review user accounts - disable inactive users
- [ ] Check for failed login attempts: `sudo journalctl -u pms.service | grep "login failed"`
- [ ] Review nginx access logs for suspicious activity
- [ ] Verify backups are current and restorable
- [ ] Check SSL certificate expiry: `sudo certbot certificates`
- [ ] Update system packages: `sudo apt-get update && sudo apt-get upgrade`

### Quarterly Security Tasks

- [ ] Review and rotate admin passwords
- [ ] Audit user permissions
- [ ] Review firewall rules
- [ ] Test backup restore procedure
- [ ] Update PMS to latest version
- [ ] Review [Security Considerations](../reference/security-considerations.md)

### Security Monitoring

**Failed login attempts**:

```bash
# Count failed logins by IP
sudo journalctl -u pms.service | grep "login failed" | awk '{print $X}' | sort | uniq -c
```

**Unusual access patterns**:

```bash
# Access outside business hours (adjust times as needed)
awk '$4 ~ /T(0[0-7]|2[0-3]):/ {print $0}' /var/log/nginx/pms-access.log
```

**Multiple login failures**:

Roundup's rate limiting (configured: 4 failures in 10 minutes) automatically blocks excessive attempts.

## Capacity Planning

### Database Growth Estimation

**Current size**:

```bash
du -sh tracker/db/
```

**Estimated growth** (rough guidelines):

- **Issues**: ~5-10 KB per issue with moderate description
- **Changes**: ~5-10 KB per change request
- **CIs**: ~2-5 KB per CI
- **Attachments**: Varies (not yet implemented in v1.0.0)

**Example**: 100 issues + 50 changes + 200 CIs = ~2-3 MB

### When to Scale

Consider scaling when:

- Database size > 1 GB (still fine for SQLite, but monitor performance)
- Concurrent users > 10 (SQLite limitation)
- Query response time > 2 seconds consistently
- Disk I/O consistently > 80%

**Scaling options** (future versions):

- Migrate to PostgreSQL/MySQL (v1.2.0+)
- Multi-server deployment (v1.2.0+)
- Read replicas (v1.2.0+)

## Disaster Recovery

### Recovery Scenarios

#### Scenario 1: Database Corruption

**Detection**: Integrity check fails or service won't start

**Recovery**:

1. Stop service
1. Restore from latest backup
1. Restart service
1. Verify data integrity

**Time**: 10-15 minutes

#### Scenario 2: Complete System Failure

**Detection**: Hardware failure, VM corruption

**Recovery**:

1. Provision new server
1. Install PMS (see [Installation Guide](installation-guide.md))
1. Restore database and config from backup
1. Configure reverse proxy and SSL
1. Update DNS (if needed)

**Time**: 1-2 hours

#### Scenario 3: Accidental Data Deletion

**Detection**: User reports missing data

**Recovery**:

1. Identify deletion time
1. Restore from backup before deletion
1. Export affected data
1. Restore current database
1. Import affected data

**Time**: 30 minutes - 1 hour

**Note**: Point-in-time recovery not yet available (planned for v1.2.0 with PostgreSQL).

### Backup Verification

**Monthly backup test**:

```bash
# Create test restore directory
mkdir -p /tmp/pms-restore-test

# Extract backup
tar -xzf /var/backups/pms/pms-backup-latest.tar.gz -C /tmp/pms-restore-test

# Verify database integrity
cd /tmp/pms-restore-test/tracker/db
for db in *.db; do
    sqlite3 "$db" "PRAGMA integrity_check;"
done

# Cleanup
rm -rf /tmp/pms-restore-test
```

## Maintenance Schedules

### Daily Tasks (Automated)

- [ ] Automated backups (2 AM)
- [ ] Health check monitoring (every 5 minutes)
- [ ] Log rotation (if configured)

### Weekly Tasks (10 minutes)

- [ ] Review logs for errors: `sudo journalctl -u pms.service --since "1 week ago" | grep ERROR`
- [ ] Check disk space: `df -h`
- [ ] Verify backup success: `ls -lh /var/backups/pms/ | tail -7`
- [ ] Check service status: `sudo systemctl status pms.service`

### Monthly Tasks (30 minutes)

- [ ] Vacuum database (first Sunday at 3 AM)
- [ ] Security audit (see Security Hardening Checklist)
- [ ] Test backup restore
- [ ] Review performance metrics
- [ ] Check for PMS updates
- [ ] Review user accounts
- [ ] SSL certificate check

### Quarterly Tasks (1-2 hours)

- [ ] Full security audit
- [ ] Disaster recovery drill
- [ ] Capacity planning review
- [ ] Update documentation
- [ ] Review and update monitoring/alerting
- [ ] System package updates

## Administrative Commands Reference

### Roundup Admin Commands

```bash
# All commands run from tracker directory
cd /opt/pms/pasture-management-system/tracker

# User management
uv run roundup-admin list user                           # List all users
uv run roundup-admin get user5                           # Get user details
uv run roundup-admin create user username=john ...       # Create user
uv run roundup-admin set user5 password=newpass          # Set password
uv run roundup-admin retire user username=john           # Disable user

# Data queries
uv run roundup-admin list issue                          # List all issues
uv run roundup-admin get issue42                         # Get issue details
uv run roundup-admin list ci                             # List all CIs
uv run roundup-admin list change                         # List all changes

# Database operations
uv run roundup-admin reindex                             # Rebuild search index
uv run roundup-admin export /tmp/export                  # Export all data
uv run roundup-admin import /tmp/export                  # Import data
```

### System Service Commands

```bash
# systemd (Linux)
sudo systemctl start pms.service      # Start service
sudo systemctl stop pms.service       # Stop service
sudo systemctl restart pms.service    # Restart service
sudo systemctl status pms.service     # Check status
sudo systemctl enable pms.service     # Enable on boot
sudo systemctl disable pms.service    # Disable on boot

# journalctl (logs)
sudo journalctl -u pms.service        # View all logs
sudo journalctl -u pms.service -f     # Follow logs
sudo journalctl -u pms.service -n 50  # Last 50 lines
sudo journalctl -u pms.service --since "1 hour ago"
```

## Related Documentation

- [Installation Guide](installation-guide.md) - Installation procedures
- [Deployment Guide](deployment-guide.md) - Production deployment
- [Security Considerations](../reference/security-considerations.md) - Security best practices
- [Performance Benchmarks](../reference/performance-benchmarks.md) - Performance targets
- [Roundup Development Practices](../reference/roundup-development-practices.md) - Roundup internals

______________________________________________________________________

**Document Version**: 1.0.0
**Last Updated**: 2025-11-20
**Maintained By**: PMS Team
