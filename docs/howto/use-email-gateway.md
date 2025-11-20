<!--
SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
SPDX-License-Identifier: MIT
-->

# How to Use the Email Gateway

**Goal**: Send and receive emails to create and update issues in the Pasture Management System.

**Audience**: Sysadmins who want to manage issues via email instead of the web interface.

**Time**: 10 minutes for basic setup, 30 minutes for production configuration.

______________________________________________________________________

## Overview

The Roundup email gateway (`roundup-mailgw`) allows you to:

- **Create issues** by sending an email
- **Update issues** by replying to issue emails
- **Set properties** via email subject (priority, status, etc.)
- **Add attachments** to issues via email

## Prerequisites

- PMS tracker instance running (see [Installation Guide](../tutorials/installation.md))
- Email address configured in `tracker/config.ini`
- For production: SMTP server or email alias setup

## Basic Configuration

### 1. Verify Email Settings

Check your tracker's email configuration:

```bash
cd tracker
cat config.ini | grep -A 5 "\[mail\]"
```

**Key settings**:

```ini
[mail]
domain = localhost              # Email domain
host = localhost                # SMTP server
debug = /tmp/roundup-mail-debug.log  # For testing

[tracker]
email = issue_tracker           # Email prefix (becomes issue_tracker@localhost)
```

### 2. Test Email Gateway (PIPE Mode)

The simplest way to test the email gateway is using **PIPE mode** (stdin):

```bash
# Create a test email file
cat > /tmp/test-email.txt <<EOF
From: admin@localhost
To: issue_tracker@localhost
Subject: Test Issue from Email
Date: $(date -R)

This is a test issue created via email.

It demonstrates the email gateway functionality.
EOF

# Send via roundup-mailgw PIPE mode
cd /path/to/pasture-management-system
cat /tmp/test-email.txt | uv run roundup-mailgw tracker
```

**Expected output**: `(No output = success)`

**Verify issue created**:

```bash
uv run roundup-admin -i tracker list issue
# Should show: "1: Test Issue from Email"
```

### 3. View Issue Details

```bash
uv run roundup-admin -i tracker display issue1
```

You should see:

```
title: Test Issue from Email
messages: ['1']
creator: 1
```

## Common Email Operations

### Create a New Issue

**Email format**:

```
From: your-email@localhost
To: issue_tracker@localhost
Subject: Server backup failed
Date: Wed, 20 Nov 2025 10:00:00 +0000

The nightly backup job failed at 2am.
Please investigate.
```

**Send via PIPE**:

```bash
cat email.txt | uv run roundup-mailgw tracker
```

### Reply to an Existing Issue

**Email format**:

```
From: your-email@localhost
To: issue_tracker@localhost
Subject: [issue1] Server backup failed
Date: Wed, 20 Nov 2025 11:00:00 +0000

I've identified the problem - the disk was full.
Cleaning up old backups now.
```

The `[issue1]` designator tells Roundup which issue to update.

### Set Priority via Email

**Email format**:

```
Subject: Network outage detected [priority=urgent]
```

Properties go **after** the title, not before.

**Available priorities**:

- `critical` (ID: 1)
- `urgent` (ID: 2)
- `bug` (ID: 3)
- `feature` (ID: 4)
- `wish` (ID: 5)

### Set Status via Email (Update)

```
Subject: [issue2] Working on this [status=in-progress]
```

**Available statuses**:

- `new` (ID: 1)
- `in-progress` (ID: 2)
- `resolved` (ID: 3)
- `closed` (ID: 4)

### Set Multiple Properties

```
Subject: [issue3] Database issues [priority=urgent;status=in-progress]
```

Use semicolons to separate multiple properties.

## Configuration Reference

### Mailgw Configuration (`tracker/config.ini`)

```ini
[mailgw]
# Keep email citations (quoted text)?
keep_quoted_text = yes

# Default class for new items
default_class = issue

# Subject prefix parsing
subject_prefix_parsing = strict  # strict|loose|none

# Match subject to existing issues?
subject_content_match = always   # always|never|creation + interval
```

### Mail Configuration

```ini
[mail]
# Email domain
domain = localhost

# SMTP server for outgoing mail
host = localhost
port = 25
tls = no

# Debug mode: Write emails to file instead of sending
debug = /tmp/roundup-mail-debug.log

# Authentication (if required)
username =
password =
```

### Nosy List Configuration

```ini
[nosy]
# Send messages to author?
messages_to_author = no

# Add author to nosy list?
add_author = new  # yes|no|new

# Add recipients to nosy list?
add_recipients = new  # yes|no|new
```

## Production Setup

### Option 1: Email Alias (Postfix/Sendmail)

**1. Add email alias**:

```bash
# /etc/aliases
issue_tracker: "|/path/to/roundup-mailgw /path/to/tracker"
```

**2. Rebuild alias database**:

```bash
sudo newaliases
sudo systemctl restart postfix
```

**3. Test**:

```bash
echo "Test issue" | mail -s "Test Subject" issue_tracker@yourdomain.com
```

### Option 2: Poll IMAP/POP3 Mailbox

**1. Create dedicated email account** (e.g., `issues@yourdomain.com`)

**2. Create cron job**:

```bash
# /etc/cron.d/roundup-mailgw
*/5 * * * * roundup roundup-mailgw imaps issues:password@mail.server tracker
```

**3. Or use systemd timer**:

```ini
# /etc/systemd/system/roundup-mailgw.service
[Unit]
Description=Roundup Email Gateway

[Service]
Type=oneshot
User=roundup
ExecStart=/usr/bin/roundup-mailgw imaps issues@mail.server tracker
```

```ini
# /etc/systemd/system/roundup-mailgw.timer
[Unit]
Description=Poll email for Roundup every 5 minutes

[Timer]
OnBootSec=2min
OnUnitActiveSec=5min

[Install]
WantedBy=timers.target
```

**Enable timer**:

```bash
sudo systemctl enable roundup-mailgw.timer
sudo systemctl start roundup-mailgw.timer
```

### Option 3: Use `.netrc` for Credentials

Instead of putting passwords in cron/systemd:

**1. Create `.netrc` file**:

```bash
# /home/roundup/.netrc
machine mail.server
login issues@yourdomain.com
password your-secure-password
```

**2. Set permissions**:

```bash
chmod 600 /home/roundup/.netrc
```

**3. Use in cron without password**:

```bash
*/5 * * * * roundup roundup-mailgw imaps mail.server tracker
```

## Testing Configuration

### Test Outgoing Email (Notifications)

**1. Enable debug mode** (already set):

```ini
[mail]
debug = /tmp/roundup-mail-debug.log
```

**2. Create an issue** (triggers notification to nosy list):

```bash
uv run roundup-admin -i tracker create issue title="Test notification"
```

**3. Check debug log**:

```bash
cat /tmp/roundup-mail-debug.log
```

You should see the email that would have been sent.

### Test Incoming Email Processing

**1. Create test email**:

```bash
cat > /tmp/test-priority.txt <<EOF
From: admin@localhost
To: issue_tracker@localhost
Subject: Critical bug found [priority=critical]
Date: $(date -R)

This is a critical bug that needs immediate attention.
EOF
```

**2. Process via mailgw**:

```bash
cat /tmp/test-priority.txt | uv run roundup-mailgw tracker
```

**3. Verify priority was set**:

```bash
uv run roundup-admin -i tracker display issue1 | grep priority
# Should show: priority: 1
```

## Troubleshooting

### Email Not Creating Issues

**Problem**: Email sent but no issue created.

**Solutions**:

1. **Check mailgw output**:

   ```bash
   cat email.txt | uv run roundup-mailgw tracker 2>&1
   ```

   Look for errors in stderr.

1. **Verify sender is a valid user**:

   ```bash
   uv run roundup-admin -i tracker list user
   ```

   The sender's email must match a user's address.

1. **Check mailgw logs** (if configured):

   ```bash
   tail -f /var/log/roundup/mailgw.log
   ```

### Property Not Being Set

**Problem**: Email has `[priority=urgent]` but priority not set.

**Solutions**:

1. **Check property syntax** - Must be AFTER title:

   ```
   ✅ Correct: Server down [priority=urgent]
   ❌ Wrong: [priority=urgent] Server down
   ```

1. **Use property IDs instead of names**:

   ```
   Subject: Server down [priority=2]  # 2 = urgent
   ```

1. **Check subject_prefix_parsing setting**:

   ```ini
   [mailgw]
   subject_prefix_parsing = strict  # Try 'loose'
   ```

### Issue ID Not Recognized

**Problem**: Email has `[issue99]` but mailgw creates new issue.

**Solutions**:

1. **Verify issue exists**:

   ```bash
   uv run roundup-admin -i tracker list issue
   ```

1. **Check subject_content_match**:

   ```ini
   [mailgw]
   subject_content_match = always
   ```

1. **Use correct format**: `[issue1]` not `[#1]` or `[Issue 1]`

### Unknown Sender Rejected

**Problem**: Emails from new users are rejected.

**Solutions**:

1. **Create user first**:

   ```bash
   uv run roundup-admin -i tracker create user \
     username=newuser \
     address=newuser@localhost \
     roles=User
   ```

1. **Or enable auto-user-creation** (⚠️ Security risk):

   This requires Roundup configuration changes and is **not recommended** for production without additional security measures.

## Security Considerations

### Prevent Email Abuse

1. **Limit sender addresses**:

   - Only allow emails from registered users
   - Use sender whitelist in mail server

1. **Rate limiting**:

   ```ini
   [mailgw]
   # Add custom rate limiting via mail server
   ```

1. **Attachment size limits**:

   ```ini
   [nosy]
   max_attachment_size = 10485760  # 10 MB
   ```

1. **Scan attachments** for viruses (external tool)

### Protect Credentials

- **Never** put passwords in cron jobs
- Use `.netrc` or environment variables
- Use restricted file permissions (600)
- Consider OAuth for IMAP access

## BDD Testing

The email gateway is tested using Behave BDD tests:

```bash
# Run email gateway tests
behave features/issue_tracking/create_issue_email.feature --tags=@smoke
```

**Test scenarios**:

- ✅ Create issue from plain text email
- ✅ Update existing issue via email
- ✅ Create issue with priority set via email
- 📋 Email with attachments (Sprint 9)
- 📋 HTML email conversion (Sprint 9)

See `features/issue_tracking/create_issue_email.feature` for all scenarios.

## Advanced Usage

### Email with Attachments

```bash
# Create multipart email with attachment
cat > /tmp/email-with-attachment.eml <<'EOF'
From: admin@localhost
To: issue_tracker@localhost
Subject: Firewall config issue
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary="boundary123"

--boundary123
Content-Type: text/plain

See attached configuration file.

--boundary123
Content-Type: application/octet-stream; name="firewall.conf"
Content-Disposition: attachment; filename="firewall.conf"
Content-Transfer-Encoding: base64

W0ZJUkVXQUxMXQplbmFibGVkPXllcw==

--boundary123--
EOF

cat /tmp/email-with-attachment.eml | uv run roundup-mailgw tracker
```

### HTML Email Conversion

**1. Enable HTML conversion**:

```ini
[mailgw]
convert_htmltotext = beautifulsoup  # Requires beautifulsoup4
```

**2. Install dependency**:

```bash
pip install beautifulsoup4
```

**3. Send HTML email**:

```html
Content-Type: text/html

<p>The SSL certificate expires in <b>7 days</b>.</p>
```

**Result**: Converted to plain text: "The SSL certificate expires in 7 days."

## Related Documentation

- [Installation Guide](../tutorials/installation.md)
- [Issue Tracking Tutorial](../tutorials/issue-tracking.md)
- [Roundup Email Gateway](https://www.roundup-tracker.org/docs/user_guide.html#email-gateway) (Official)
- [Sprint 9 Plan](../sprints/sprint-9-plan.md) - GreenMail integration tests

## Summary

You've learned to:

- ✅ Configure the email gateway
- ✅ Send test emails via PIPE mode
- ✅ Create and update issues via email
- ✅ Set properties in email subjects
- ✅ Configure production email (aliases, IMAP polling)
- ✅ Troubleshoot common issues

**Next steps**:

- Set up production email configuration
- Configure nosy list notifications
- Test with real email server (Sprint 9: GreenMail)
