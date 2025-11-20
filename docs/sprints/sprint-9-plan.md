# Sprint 9 Plan: GreenMail Integration & Advanced Email Features

**Sprint Goal**: Enhance email testing with GreenMail integration and implement advanced email gateway features

**Target Version**: v1.2.0
**Duration**: 2 weeks
**Points**: 26-34 (estimated)

## Context

Sprint 8 established basic email gateway functionality using PIPE mode testing (stdin → roundup-mailgw). This validates mailgw business logic but doesn't test actual SMTP/IMAP integration. Sprint 9 will add GreenMail-based integration tests and complete advanced email features.

## Sprint Goals

### Primary Objectives

1. **GreenMail Integration Testing** - Test real SMTP/IMAP/POP3 email flows
1. **Advanced Email Features** - Complete remaining email gateway scenarios
1. **Production Email Configuration** - Document and test production setup

### Success Criteria

- ✅ GreenMail test suite operational (docker-compose based)
- ✅ All 12 email gateway BDD scenarios passing
- ✅ Email polling (IMAP/POP3) tested with GreenMail
- ✅ SMTP delivery tested with GreenMail
- ✅ Production deployment guide complete

## Stories

### **Story 1**: GreenMail Test Infrastructure (8 points)

**As a** developer
**I want** GreenMail-based integration tests
**So that** I can test real email server interactions

**Acceptance Criteria**:

- [ ] docker-compose.yml configures GreenMail (SMTP/IMAP/POP3)
- [ ] Python GreenMail client library implemented
- [ ] Integration test suite structure created (`tests/integration/`)
- [ ] CI/CD runs GreenMail tests (optional, manual trigger)
- [ ] Documentation: "Running Integration Tests"

**Technical Tasks**:

```yaml
# docker-compose.greenmail.yml
services:
  greenmail:
    image: greenmail/standalone:latest
    ports:
      - "3025:3025"  # SMTP
      - "3110:3110"  # POP3
      - "3143:3143"  # IMAP
```

```python
# tests/integration/greenmail_client.py
class GreenMailClient:
    def send_email(...)
    def get_received_messages(...)
    def clear_mailbox(...)
```

### **Story 2**: Email Polling Integration Tests (5 points)

**As a** sysadmin
**I want** to test IMAP/POP3 polling
**So that** I know the mail gateway retrieves emails correctly

**Acceptance Criteria**:

- [ ] Test: Poll IMAP mailbox and create issues
- [ ] Test: Poll POP3 mailbox and create issues
- [ ] Test: Handle authentication failures
- [ ] Test: Process multiple messages in one poll
- [ ] Test: Mark messages as read after processing

**BDD Scenarios** (GreenMail-based):

```gherkin
@integration @greenmail
Scenario: Poll IMAP and create issues
  Given GreenMail has 5 unread messages
  When I run roundup-mailgw with IMAP configuration
  Then 5 issues should be created
  And the IMAP mailbox should be empty

@integration @greenmail
Scenario: Handle IMAP authentication failure
  Given GreenMail rejects the credentials
  When I run roundup-mailgw with IMAP configuration
  Then the command should fail gracefully
  And an error should be logged
```

### **Story 3**: SMTP Delivery Integration Tests (5 points)

**As a** user
**I want** to test outgoing email notifications
**So that** I know notifications are delivered correctly

**Acceptance Criteria**:

- [ ] Test: Send notification via SMTP to GreenMail
- [ ] Test: Verify email content and formatting
- [ ] Test: Handle SMTP connection failures
- [ ] Test: Test TLS/authentication
- [ ] Test: Multiple recipients (nosy list)

**BDD Scenarios**:

```gherkin
@integration @greenmail
Scenario: Send notification via SMTP
  Given GreenMail SMTP server is running
  When an issue is created
  Then a notification should be sent to GreenMail
  And the email should contain the issue title

@integration @greenmail
Scenario: Handle SMTP connection failure
  Given GreenMail SMTP server is stopped
  When an issue is created
  Then the notification should fail
  And the error should be logged
```

### **Story 4**: Advanced Email Gateway Features (8 points)

**As a** user
**I want** advanced email features working
**So that** I can use the full email interface

**Acceptance Criteria**:

- [ ] Status update via email subject working
- [ ] Property updates (assignedto, priority) via email
- [ ] Email attachments processed correctly
- [ ] HTML email conversion functional
- [ ] Unknown user auto-creation working
- [ ] Invalid issue ID error handling
- [ ] Quoted text handling verified

**Remaining BDD Scenarios** (from Sprint 8):

1. ❌ Update issue status via email subject
1. ✅ Email with quoted text (should work as-is)
1. ❌ Email from unknown user creates new user
1. ❌ Email with invalid issue ID is rejected
1. ❌ Email with multiple attachments
1. ❌ HTML email is converted to plain text

**Configuration Required**:

```ini
# tracker/config.ini
[mailgw]
# Enable HTML conversion
convert_htmltotext = beautifulsoup

# Auto-create users from email
# (Requires security review)
```

### **Story 5**: Production Email Configuration (5 points)

**As a** sysadmin
**I want** production email setup documented
**So that** I can deploy PMS with real email

**Acceptance Criteria**:

- [ ] Document: Configure SMTP for outgoing mail
- [ ] Document: Configure IMAP/POP3 polling
- [ ] Document: Set up email aliases (Postfix/sendmail)
- [ ] Document: Security considerations (SPF, DKIM, spam)
- [ ] Document: Troubleshooting email issues

**Documentation Structure**:

```
docs/howto/
├── configure-outgoing-email.md
├── configure-incoming-email.md
├── setup-email-aliases.md
└── troubleshoot-email.md
```

### **Story 6**: Email Security & Anti-Spam (5 points) - Stretch Goal

**As a** sysadmin
**I want** spam protection
**So that** my tracker isn't abused

**Acceptance Criteria**:

- [ ] Document: Rate limiting configuration
- [ ] Document: Sender whitelist/blacklist
- [ ] Document: Attachment size limits
- [ ] Test: Reject emails from non-users (configurable)
- [ ] Test: Reject oversized attachments

## Technical Architecture

### Test Structure

```
tests/
├── unit/                  # pytest unit tests
├── bdd/                   # Behave BDD tests (PIPE mode)
│   ├── features/
│   └── steps/
└── integration/           # GreenMail integration tests
    ├── conftest.py       # pytest fixtures
    ├── greenmail_client.py
    ├── test_email_polling.py
    ├── test_smtp_delivery.py
    └── docker-compose.yml
```

### Running Tests

```bash
# Fast BDD tests (always run in CI)
behave

# Unit tests
pytest tests/unit/

# Integration tests (manual/pre-release)
docker-compose -f tests/integration/docker-compose.yml up -d
pytest tests/integration/
docker-compose -f tests/integration/docker-compose.yml down
```

## Story Point Breakdown

| Story                       | Points    | Priority |
| --------------------------- | --------- | -------- |
| 1. GreenMail Infrastructure | 8         | Critical |
| 2. Email Polling Tests      | 5         | High     |
| 3. SMTP Delivery Tests      | 5         | High     |
| 4. Advanced Features        | 8         | High     |
| 5. Production Documentation | 5         | Medium   |
| 6. Security & Anti-Spam     | 5         | Stretch  |
| **Total**                   | **26-36** |          |

## Dependencies

### External

- **Docker** - For GreenMail container
- **GreenMail** - Email server for testing
- **BeautifulSoup4** - For HTML email conversion (optional)

### Configuration

- Roundup mailgw configuration review
- Security review for user auto-creation

## Risks & Mitigation

| Risk                                     | Impact | Mitigation                                         |
| ---------------------------------------- | ------ | -------------------------------------------------- |
| GreenMail adds test complexity           | Medium | Make integration tests optional, document clearly  |
| Docker not available in all environments | Medium | Provide skip instructions, keep PIPE tests primary |
| HTML conversion requires dependencies    | Low    | Make optional, document alternatives               |
| User auto-creation security risk         | High   | Require explicit configuration, document risks     |

## Success Metrics

- **Test Coverage**: >90% for email features
- **Test Speed**: Integration tests \<2 min total
- **BDD Scenarios**: 12/12 passing (100%)
- **Documentation**: 4 new how-to guides
- **CI/CD**: GreenMail tests passing (optional)

## Out of Scope

- Web-based email interface (webmail)
- Email threading/conversation tracking
- Email templates customization
- Multi-language email content
- Calendar invites (.ics files)

## Next Sprint Preview

**Sprint 10** (v1.3.0) - Mobile & API Enhancements:

- Mobile-responsive web UI
- REST API rate limiting
- API authentication (JWT)
- API documentation (OpenAPI/Swagger)

______________________________________________________________________

**Notes**:

- GreenMail tests are **optional** - PIPE mode tests remain primary
- Focus on production deployment readiness
- Security review required before user auto-creation
- Integration tests run manually or in pre-release pipeline
