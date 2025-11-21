# Email Security Hardening Guide

**Audience**: Homelab sysadmins deploying Pasture Management System
**Prerequisites**: Basic understanding of email protocols (SMTP, IMAP) and Roundup configuration
**Estimated Time**: 30-60 minutes (basic hardening), 2-3 hours (with PGP setup)

## Overview

This guide explains how to secure your Roundup tracker's email gateway against common threats. For homelab deployments with 1-50 known users, the built-in security features provide excellent protection when properly configured.

## Security Threat Model

### Homelab Context (1-50 Users)

**Typical Threats**:

- **User enumeration**: Attackers probing for valid email addresses
- **Issue ID enumeration**: Discovering valid issue IDs to access sensitive data
- **XSS via HTML email**: Injecting malicious scripts through email
- **Large attachment DoS**: Overwhelming the system with massive email attachments
- **Subject manipulation**: Exploiting prefix parsing to create malformed issues

**Out of Scope for Homelabs**:

- Mass spam campaigns (use MTA-level filtering)
- Per-sender rate limiting (low user count makes this unnecessary)
- Advanced sender reputation systems (known user base)
- Machine learning spam detection (overkill for homelab)

## Built-in Security Features

### 1. Unknown User Rejection (Silent)

**Status**: ✅ Enabled by default
**Configuration**: `tracker/schema.py` (Email Access permission commented out)

**How it works**:

- Emails from unknown addresses are silently rejected
- No user account is automatically created
- No error message is sent back (prevents enumeration)

**Verification**:

```bash
# Test unknown user rejection
behave features/issue_tracking/email_security.feature \
  --tags="@security" --name="Unknown sender"
```

**Security benefit**: Prevents attackers from discovering valid user emails by trial and error.

### 2. Invalid Issue ID Rejection (Silent)

**Status**: ✅ Enabled via strict parsing
**Configuration**: `tracker/config.ini` → `subject_prefix_parsing = strict`

**How it works**:

- Emails with invalid `[issueNNN]` prefixes are silently rejected
- No error message reveals whether the issue ID exists
- Invalid prefixes are also rejected

**Verification**:

```bash
# Test invalid ID rejection
behave features/issue_tracking/email_security.feature \
  --tags="@security" --name="Invalid issue ID"
```

**Security benefit**: Prevents attackers from probing for valid issue IDs.

### 3. HTML Email Sanitization

**Status**: ✅ Enabled via BeautifulSoup4
**Configuration**: `tracker/config.ini` → `convert_htmltotext = beautifulsoup`

**How it works**:

- HTML emails are converted to plain text
- All HTML tags (including `<script>`) are stripped
- Text content is preserved, formatting is lost

**Dependencies**:

```bash
pip install beautifulsoup4 lxml
```

**Verification**:

```bash
# Test XSS prevention
behave features/issue_tracking/email_security.feature \
  --tags="@html" --name="XSS"
```

**Security benefit**: Prevents XSS attacks via HTML email injection.

### 4. Strict Subject Parsing

**Status**: ✅ Enabled by default
**Configuration**: `tracker/config.ini`

```ini
[mailgw]
subject_prefix_parsing = strict
subject_suffix_parsing = strict
```

**How it works**:

- Only recognized prefixes (`[issue123]`, `[priority=urgent]`, `[status=in-progress]`) are accepted
- Malformed prefixes like `[INVALID_PREFIX]` are rejected
- No automatic fallback or error messages

**Verification**:

```bash
# Test malformed prefix rejection
behave features/issue_tracking/email_security.feature \
  --tags="@security" --name="Malformed subject"
```

**Security benefit**: Prevents subject manipulation attacks.

### 5. Attachment Size Limits

**Status**: ✅ Configured (Story 4)
**Configuration**: `tracker/config.ini` → `max_attachment_size = 10485760`

**How it works**:

- Attachments larger than 10MB are NOT included in email notifications
- Instead, a link to the tracker's download page is sent
- This prevents email client crashes and DoS via large attachments

**Customization**:

```ini
[mail]
# 10MB limit (recommended for homelab)
max_attachment_size = 10485760

# 5MB limit (more restrictive)
max_attachment_size = 5242880

# 50MB limit (less restrictive, requires higher resource limits)
max_attachment_size = 52428800
```

**Note**: This setting controls outgoing notification emails, not incoming email to the gateway. For incoming email size limits, configure your MTA (Postfix, Exim, etc.).

**Security benefit**: Prevents large attachment DoS attacks via email notifications.

## Optional Advanced Security

### PGP/GPG Email Encryption (Optional)

**Use Case**: High-security homelabs handling sensitive data
**Complexity**: Advanced (requires GPG key management)
**Status**: Available but not configured by default

#### Prerequisites

1. Install GPG:

   ```bash
   # macOS (MacPorts)
   sudo port install gnupg2

   # Linux (Debian/Ubuntu)
   sudo apt-get install gnupg
   ```

1. Generate GPG key for tracker:

   ```bash
   gpg --full-generate-key
   # Select: RSA and RSA, 4096 bits
   # Email: issue_tracker@yourdomain.com
   ```

#### Configuration

Edit `tracker/config.ini`:

```ini
[pgp]
# Enable PGP processing
enable = yes

# Path to GPG home directory
# Default: ~/.gnupg
homedir =

# Require PGP signatures on all incoming email
# Recommended: no (allows unsigned email from known users)
# Set to yes only if ALL users have GPG keys configured
require_signed = no

# Encrypt outgoing email notifications
# Recommended: yes (if users have GPG keys)
encrypt = no

# Path to GPG binary
# Default: gpg
gpg_binary = /opt/local/bin/gpg
```

#### User GPG Key Management

Each user needs to:

1. Generate their own GPG key
1. Send their public key to the tracker admin
1. Admin imports public keys:
   ```bash
   gpg --import user-public-key.asc
   ```

#### Testing PGP Setup

```bash
# Send a PGP-signed email test
gpg --clearsign test-email.txt | \
  mail -s "PGP Test" issue_tracker@localhost
```

#### Security Tradeoffs

**Pros**:

- End-to-end encryption for sensitive issues
- Cryptographic verification of sender identity
- Tamper-proof email trail

**Cons**:

- Complex key management (generation, distribution, revocation)
- User training required
- Key expiration and rotation overhead
- Not suitable for casual homelab users

**Recommendation**: Only enable PGP if handling truly sensitive data (credentials, security incidents, compliance-required documentation).

## Email Gateway Access Control

### MTA-Level Filtering (Recommended)

For best security, configure your Mail Transfer Agent (Postfix, Exim) to only accept email from known sources:

#### Postfix Example

Edit `/etc/postfix/main.cf`:

```
# Restrict relay to local network only
smtpd_relay_restrictions = permit_mynetworks, reject

# Only accept email from local network
smtpd_client_restrictions = permit_mynetworks, reject

# Define your homelab network
mynetworks = 127.0.0.0/8, 192.168.1.0/24, 10.0.0.0/8
```

#### Firewall Rules

Block external SMTP access:

```bash
# Allow only internal network to reach SMTP port 25
sudo iptables -A INPUT -p tcp --dport 25 -s 192.168.1.0/24 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 25 -j DROP
```

## Security Best Practices

### 1. Regular Security Audits

**Monthly**:

- Review `db/files/` for unexpected large files
- Check `/tmp/roundup-mail-debug.log` for suspicious email patterns
- Verify user list hasn't grown unexpectedly

**Quarterly**:

- Run BDD security scenarios:
  ```bash
  behave features/issue_tracking/email_security.feature --tags="@security"
  ```
- Review Roundup security advisories: https://www.roundup-tracker.org/docs/security.html
- Update Roundup to latest patch version

### 2. Logging and Monitoring

**Enable email debug logging**:

Edit `tracker/config.ini`:

```ini
[mail]
# Log all incoming/outgoing email for security audit
debug = /tmp/roundup-mail-debug.log
```

**Monitor for suspicious patterns**:

```bash
# Check for enumeration attempts (multiple failed emails from same source)
grep "unknown user" /tmp/roundup-mail-debug.log | \
  awk '{print $1}' | sort | uniq -c | sort -rn

# Check for XSS attempts
grep -i "script\|javascript\|onerror" /tmp/roundup-mail-debug.log
```

### 3. Principle of Least Privilege

**Anonymous Role** (default):

- No email access (Email Access permission commented out)
- Read-only web access to public issues only

**User Role**:

- Can create issues via email (if known user)
- Can update issues they created or are assigned to
- Cannot modify other users' issues

**Admin Role**:

- Full access to all issues via email/web
- Can modify permissions and configuration

### 4. Secure Defaults

The following security-first defaults are configured in `tracker/config.ini`:

```ini
[mailgw]
# Strict parsing prevents subject manipulation
subject_prefix_parsing = strict
subject_suffix_parsing = strict

# HTML sanitization prevents XSS
convert_htmltotext = beautifulsoup

# Keep quoted text for audit trail
keep_quoted_text = yes

[mail]
# 10MB attachment limit prevents DoS
max_attachment_size = 10485760

[web]
# Prevent clickjacking
http_x_frame_options = DENY

# XSS protection
http_x_content_type_options = nosniff
```

## Incident Response

### Suspected Email Attack

1. **Stop the mail gateway**:

   ```bash
   # Disable mail processing temporarily
   sudo systemctl stop roundup-mailgw
   # OR for cron-based processing:
   sudo crontab -e  # Comment out mailgw cron job
   ```

1. **Review logs**:

   ```bash
   tail -100 /tmp/roundup-mail-debug.log
   tail -100 /var/log/mail.log
   ```

1. **Check database**:

   ```bash
   cd tracker
   roundup-admin -i . list user    # Check for unexpected users
   roundup-admin -i . list issue   # Check for suspicious issues
   ```

1. **Restore from backup** (if compromised):

   ```bash
   # Stop tracker
   sudo systemctl stop roundup-server

   # Restore database
   rm -rf tracker/db
   tar xzf tracker-backup-YYYY-MM-DD.tar.gz

   # Restart
   sudo systemctl start roundup-server
   ```

### Reporting Security Issues

If you discover a security vulnerability in Roundup itself (not this homelab deployment):

1. **Do NOT** open a public GitHub issue
1. Email security@roundup-tracker.org with details
1. Follow responsible disclosure practices

## Summary

### ✅ Homelab-Appropriate Security (Enabled)

- Unknown user silent rejection
- Invalid issue ID silent rejection
- HTML email sanitization (XSS prevention)
- Strict subject parsing
- 10MB attachment size limit
- MTA-level access control (recommended)

### 🔧 Optional Advanced Security

- PGP/GPG encryption (high-security homelabs only)
- Per-user email quotas (enterprise feature, not needed for homelab)
- ML-based spam detection (overkill for known users)

### 🚫 Descoped Enterprise Features

- Sender reputation systems (not needed for known users)
- Per-sender rate limiting (low user volume)
- Advanced DMARC/SPF/DKIM (configure at MTA level, not tracker)
- Real-time blacklist (RBL) checking (MTA responsibility)

## Further Reading

- [Roundup Security Documentation](https://www.roundup-tracker.org/docs/security.html)
- [Roundup PGP Configuration](https://www.roundup-tracker.org/docs/reference.html#pgp)
- [Email Security Best Practices (OWASP)](https://cheatsheetseries.owasp.org/cheatsheets/Email_Security_Cheat_Sheet.html)
- [Postfix SMTP Access Control](http://www.postfix.org/SMTPD_ACCESS_README.html)

## Conclusion

For a homelab deployment with known users, Pasture Management System's default email security configuration provides strong protection against common threats:

- **User enumeration**: Prevented
- **Issue ID enumeration**: Prevented
- **XSS attacks**: Prevented
- **Large attachment DoS**: Mitigated
- **Subject manipulation**: Prevented

Additional enterprise features (rate limiting, sender reputation, ML spam detection) add complexity without meaningful security improvement for small, trusted user bases.

**Next Steps**:

1. Run security BDD scenarios to verify configuration:
   ```bash
   behave features/issue_tracking/email_security.feature --tags="@security"
   ```
1. Configure MTA-level access control for your network
1. Set up automated security scenario runs (e.g., weekly cron job)
1. Consider PGP only if handling truly sensitive data
