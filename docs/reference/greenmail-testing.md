<!--
SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
SPDX-License-Identifier: MIT
-->

# GreenMail Email Testing Reference

## Overview

GreenMail is an open-source email server for testing. It provides SMTP, IMAP, and POP3 services that can be used to test email functionality in BDD scenarios without requiring a real email server.

**Version**: 2.1.7 (stable)
**Container Image**: `docker.io/greenmail/standalone:2.1.7`
**Documentation**: https://greenmail-mail-test.github.io/greenmail/

## Architecture

```
BDD Test Suite
│
├── Behave (features/environment.py)
│   └── GreenMail Fixture (optional, controlled by EMAIL_TEST_MODE)
│       ├── Start: before_all()
│       ├── Clear mailbox: before_scenario()
│       └── Stop: after_all()
│
├── GreenMailContainer (tests/utils/greenmail_client.py)
│   ├── Manages Podman container lifecycle
│   ├── Ports: SMTP=3025, IMAP=3143, POP3=3110, API=8080
│   └── Auto-cleanup with --rm flag
│
└── GreenMailClient (tests/utils/greenmail_client.py)
    ├── Send emails via SMTP
    ├── Retrieve emails via IMAP
    ├── Clear mailboxes
    └── Wait for messages
```

## Configuration

### Environment Variables

- **`EMAIL_TEST_MODE`**: Testing mode for email scenarios
  - `pipe` (default): Use PIPE mode with `roundup-mailgw` (fast, no external dependencies)
  - `greenmail`: Use GreenMail container (comprehensive, tests full email flow)

### Email Testing Modes

#### PIPE Mode (Default)

- **Use case**: Fast BDD testing, CI/CD pipelines
- **How it works**: Pipe email directly to `roundup-mailgw` stdin
- **Coverage**: Tests 95% of mailgw logic (parsing, issue creation, updates)
- **Pros**: Fast (no container startup), simple, no external dependencies
- **Cons**: Doesn't test SMTP/IMAP protocols, email delivery, or mailbox operations

#### GreenMail Mode

- **Use case**: Comprehensive email testing, pre-release validation
- **How it works**: Full SMTP/IMAP integration with GreenMail container
- **Coverage**: Tests 100% of email flow (SMTP send, IMAP retrieve, notifications)
- **Pros**: Real email protocols, tests notification delivery, mailbox operations
- **Cons**: Slower (container startup ~3-5s), requires Podman/Docker

## Usage

### Running BDD Tests with GreenMail

```bash
# Default mode (PIPE - fast)
behave features/issue_tracking/create_issue_email.feature

# GreenMail mode (comprehensive)
EMAIL_TEST_MODE=greenmail behave features/issue_tracking/create_issue_email.feature
```

### Using GreenMailClient in Tests

```python
from tests.utils.greenmail_client import GreenMailClient

# Create client (assumes GreenMail container is running)
client = GreenMailClient()

# Send email
client.send_email(
    from_addr="test@localhost",
    to_addr="user@localhost",
    subject="Test Subject",
    body="Test body content"
)

# Retrieve emails
messages = client.get_received_messages(
    user="user@localhost",
    password="user@localhost"  # GreenMail accepts any password
)

# Clear mailbox
deleted = client.clear_mailbox(user="user@localhost", password="user@localhost")
```

### Managing GreenMail Container Manually

```bash
# Start GreenMail container
podman run --rm -d \
  --name greenmail-test \
  -p 3025:3025 \
  -p 3143:3143 \
  -p 3110:3110 \
  -p 8080:8080 \
  docker.io/greenmail/standalone:2.1.7

# Check container status
podman ps --filter name=greenmail-test

# View logs
podman logs greenmail-test

# Stop container
podman stop greenmail-test
```

## Port Mapping

| Service | Container Port | Host Port | Protocol |
| ------- | -------------- | --------- | -------- |
| SMTP    | 3025           | 3025      | TCP      |
| SMTPS   | 3465           | (unused)  | TCP      |
| POP3    | 3110           | 3110      | TCP      |
| POP3S   | 3995           | (unused)  | TCP      |
| IMAP    | 3143           | 3143      | TCP      |
| IMAPS   | 3993           | (unused)  | TCP      |
| API     | 8080           | 8080      | HTTP     |

## GreenMail Configuration

### Authentication

GreenMail with `auth.disabled` accepts any credentials:

- **Username**: Email address (e.g., `user@localhost`)
- **Password**: Any value (typically same as username for simplicity)

### User Auto-Creation

Users are automatically created when:

1. Sending an email via SMTP (sender auto-created)
1. Retrieving emails via IMAP (recipient auto-created)

No pre-configuration required!

## Troubleshooting

### Container Won't Start

**Error**: `Error: proxy already running`

**Solution**: Stop existing containers

```bash
podman stop $(podman ps -a --filter name=greenmail --format "{{.Names}}")
```

### Connection Refused

**Error**: `[Errno 61] Connection refused` when connecting to SMTP/IMAP

**Causes**:

1. Container not running: `podman ps --filter name=greenmail`
1. Container still starting: Wait 3-5 seconds after `podman run`
1. Ports already in use: Check `lsof -i :3025`

**Solution**:

```bash
# Check if container is running
podman ps --filter name=greenmail

# Check container logs
podman logs greenmail-test

# Restart container
podman stop greenmail-test
podman run --rm -d --name greenmail-test -p 3025:3025 -p 3143:3143 docker.io/greenmail/standalone:2.1.7
sleep 3
```

### SMTP Connection Unexpectedly Closed

**Error**: `Connection unexpectedly closed` during SMTP send

**Cause**: GreenMail socket ready, but SMTP service not fully initialized

**Solution**: Increase wait time in `wait_for_ready()` (currently 2 seconds after socket connection)

### Emails Not Received

**Issue**: Email sent successfully but not appearing in IMAP mailbox

**Checklist**:

1. Check username matches: `user@localhost` (case-sensitive)
1. Clear mailbox before test: `client.clear_mailbox()`
1. Check GreenMail logs: `podman logs greenmail-test`
1. Verify email was sent: Check SMTP response code

## Performance

### Startup Time

- **Container start**: ~1-2 seconds
- **Service ready**: +2-3 seconds (SMTP/IMAP fully initialized)
- **Total**: ~3-5 seconds

### Test Performance

| Mode      | Startup | Per Test | 100 Tests |
| --------- | ------- | -------- | --------- |
| PIPE      | 0s      | ~0.1s    | ~10s      |
| GreenMail | 5s      | ~0.2s    | ~25s      |

**Recommendation**: Use PIPE mode for CI/CD, GreenMail for pre-release validation.

## Integration with Roundup

### SMTP Configuration

Configure Roundup to send notifications via GreenMail:

```ini
# tracker/config.ini
[mailgw]
host = localhost
port = 3025

[mail]
smtp_server = localhost
smtp_port = 3025
```

### Testing Notifications

1. Start GreenMail container
1. Configure Roundup SMTP to use localhost:3025
1. Create/update issue via Web UI or CLI
1. Retrieve notification via GreenMail IMAP:

```python
client = GreenMailClient()
messages = client.wait_for_message(
    timeout=10,
    user="recipient@localhost",
    password="recipient@localhost"
)
```

## API Reference

### GreenMailClient

```python
class GreenMailClient:
    def __init__(self, smtp_host="localhost", smtp_port=3025,
                 imap_host="localhost", imap_port=3143)

    def send_email(from_addr, to_addr, subject, body, html=None)
    def send_raw_email(raw_message: str)
    def get_received_messages(mailbox="INBOX", user, password) -> List[EmailMessage]
    def get_message_count(mailbox="INBOX", user, password) -> int
    def clear_mailbox(mailbox="INBOX", user, password) -> int
    def wait_for_message(timeout=10, mailbox="INBOX", user, password) -> Optional[EmailMessage]
```

### GreenMailContainer

```python
class GreenMailContainer:
    def __init__(self, container_name="greenmail-bdd",
                 image="docker.io/greenmail/standalone:2.1.7",
                 smtp_port=3025, imap_port=3143, pop3_port=3110, api_port=8080)

    def start() -> bool
    def stop() -> bool
    def is_running() -> bool
    def wait_for_ready(timeout=30) -> bool
```

## Best Practices

1. **Use PIPE mode by default**: Faster, simpler, covers 95% of use cases
1. **Use GreenMail for pre-release testing**: Validates full email flow
1. **Clear mailboxes before tests**: `client.clear_mailbox()` in `before_scenario()`
1. **Use stable versions**: Avoid `-rc` or `-alpha` tags in production
1. **Set timeouts**: SMTP/IMAP operations should timeout (10s recommended)
1. **Check container status**: Verify container is running before tests
1. **Clean up containers**: Use `--rm` flag for auto-cleanup

## Related Documentation

- [Email Gateway How-To](../howto/use-email-gateway.md) - User guide for email interface
- [BDD Testing Best Practices](./bdd-testing-best-practices.md) - General BDD guidelines
- [Roundup Development Practices](./roundup-development-practices.md) - Roundup-specific patterns

## External Resources

- **GreenMail Documentation**: https://greenmail-mail-test.github.io/greenmail/
- **GreenMail Docker Hub**: https://hub.docker.com/r/greenmail/standalone
- **GreenMail GitHub**: https://github.com/greenmail-mail-test/greenmail
- **Roundup Email Gateway**: https://www.roundup-tracker.org/docs/user_guide.html#email-gateway
