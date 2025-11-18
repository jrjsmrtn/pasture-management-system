<!--
SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
SPDX-License-Identifier: MIT
-->

# Sprint 7 Plan - Pasture Management System

**Sprint Duration**: 2 weeks
**Sprint Goal**: Implement email interface with comprehensive four-interface BDD testing
**Target Version**: v1.1.0
**Start Date**: TBD (Post Sprint 6)
**End Date**: TBD

## Sprint Objective

Implement and test Roundup's email interface for issue tracking, completing the **four-interface testing architecture**: Web UI, CLI, REST API, and Email. Establish comprehensive BDD testing infrastructure using Greenmail or Python SMTP testing tools to verify email-based workflows and demonstrate complete interface coverage.

## Background: Four-Interface BDD Testing

PMS demonstrates BDD best practices across **four distinct interfaces**:

1. **Web UI**: Playwright browser automation (1024x768)
1. **CLI**: Command-line interface (`roundup-admin`)
1. **REST API**: XML-RPC and REST endpoints
1. **Email**: Email gateway (`roundup-mailgw`) ← **Sprint 7 Focus**

This sprint completes the four-interface testing framework, showcasing how BDD scenarios can verify the same functionality across different interaction modes.

### Roundup Email Interface Capabilities

Roundup Issue Tracker includes a built-in email interface that provides:

- **Issue Creation**: Create new issues by sending email
- **Issue Updates**: Reply to notification emails to add messages/update properties
- **Email Notifications**: Automatic notifications on issue changes
- **Email Commands**: Embed commands in email to set properties
- **Authentication**: Email-based user authentication

## User Stories

### Epic: Email Interface Foundation

#### Story 1: Email-Based Issue Creation (Four-Interface BDD)

**As a** homelab sysadmin
**I want** to create issues by sending email
**So that** I can report problems without accessing the web UI

**Acceptance Criteria**:

- Email subject becomes issue title
- Email body becomes issue description
- Sender email maps to PMS user account
- Issue created with correct default status
- Confirmation email sent to creator
- **BDD scenarios passing across all four interfaces**

**BDD Scenarios**: (Feature file: `features/email/issue_creation.feature`)

```gherkin
@story-1 @email @smoke
Scenario: Create issue via email with subject and body
  Given I have a valid email account "admin@example.com"
  When I send an email to "pms@localhost"
  And the subject is "Database server down"
  And the body is "The production database server is not responding"
  Then a new issue should be created
  And the issue title should be "Database server down"
  And the issue description should contain "not responding"
  And I should receive a confirmation email
  And the confirmation should include the issue number

@story-1 @email @web-ui @cross-interface
Scenario: Issue created via email is visible in web UI
  Given I send an email to create issue "Email Test Issue"
  When I navigate to the issue list in the web UI
  Then I should see "Email Test Issue"
  And the issue creator should be shown as my email account

@story-1 @email @cli @cross-interface
Scenario: Issue created via email is retrievable via CLI
  Given I send an email to create issue "CLI Visibility Test"
  When I run "roundup-admin -i tracker list issue"
  Then the output should include "CLI Visibility Test"

@story-1 @email @api @cross-interface
Scenario: Issue created via email is accessible via API
  Given I send an email to create issue "API Test Issue"
  When I GET "/api/issues" via REST API
  Then the response should include an issue with title "API Test Issue"
  And the issue properties should match the email content

@story-1 @email @security
Scenario: Unknown sender receives registration prompt
  Given "unknown@example.com" is not registered
  When they send an email to "pms@localhost"
  Then no issue should be created
  And they should receive a registration prompt email
  And the email should explain how to register
```

**Story Points**: 8

______________________________________________________________________

#### Story 2: Email-Based Issue Updates (Four-Interface BDD)

**As a** homelab sysadmin
**I want** to update issues by replying to notification emails
**So that** I can collaborate without switching contexts

**Acceptance Criteria**:

- Reply to notification email adds message to issue
- Email commands update issue properties (status, priority, assignee)
- Proper threading (In-Reply-To headers)
- Update notifications sent to watchers
- **BDD scenarios verify updates across all four interfaces**

**BDD Scenarios**: (Feature file: `features/email/issue_updates.feature`)

```gherkin
@story-2 @email
Scenario: Add message to issue via email reply
  Given I have issue #123 in the database
  And I received a notification email about issue #123
  When I reply to the notification email
  And the body is "I've investigated this issue"
  Then issue #123 should have a new message
  And the message should contain "I've investigated"
  And watchers should receive update notification

@story-2 @email @web-ui @cross-interface
Scenario: Email update visible in web UI
  Given issue #456 exists
  When I reply to the notification email with "Update via email"
  And I view issue #456 in the web UI
  Then I should see the message "Update via email"
  And the message timestamp should be recent

@story-2 @email @cli @cross-interface
Scenario: Email status update verifiable via CLI
  Given issue #789 has status "in-progress"
  When I reply with email containing "[status=resolved]"
  And I run "roundup-admin -i tracker get issue789 status"
  Then the output should show "resolved"

@story-2 @email @api @cross-interface
Scenario: Email update retrievable via API
  Given issue #100 exists
  When I add a message via email reply
  Then GET "/api/issues/100/messages" should include the new message
  And the message author should match my email account

@story-2 @email
Scenario: Multiple property updates in single email
  Given I have issue #200 in the database
  When I reply with email body:
    """
    [status=resolved]
    [priority=low]
    [assignee=bob]

    Fixed the issue by restarting the service.
    """
  Then issue #200 should have status "resolved"
  And issue #200 should have priority "low"
  And issue #200 should be assigned to "bob"
  And a message "Fixed the issue" should be added
```

**Story Points**: 8

______________________________________________________________________

#### Story 3: Email Notification System (Four-Interface BDD)

**As a** homelab sysadmin
**I want** to receive email notifications for issue changes
**So that** I stay informed regardless of how changes are made

**Acceptance Criteria**:

- Notifications on issue creation (any interface)
- Notifications on issue updates (any interface)
- Notifications on status changes
- Notifications on assignments
- Configurable notification preferences per user
- Digest mode (daily/weekly summaries)
- **Email notifications triggered by actions on all four interfaces**

**BDD Scenarios**: (Feature file: `features/email/notifications.feature`)

```gherkin
@story-3 @email @web-ui @cross-interface
Scenario: Email notification when issue created via web UI
  Given I am watching the "Issues" tracker
  When a new issue is created via web UI
  Then I should receive an email notification
  And the subject should include the issue number
  And the body should include a link to view the issue

@story-3 @email @cli @cross-interface
Scenario: Email notification when issue updated via CLI
  Given I am assigned to issue #300
  When the issue status is changed via CLI command
  Then I should receive an email notification
  And the email should indicate "Status changed via CLI"

@story-3 @email @api @cross-interface
Scenario: Email notification when issue updated via API
  Given I am watching issue #400
  When a message is added via REST API
  Then I should receive an email notification
  And the notification should include the message content

@story-3 @email
Scenario: Daily digest mode
  Given I have configured "daily digest" notifications
  And 5 issues were created today (via web, cli, api, email)
  And 3 issues were updated today
  When the daily digest runs at 6 PM
  Then I should receive one digest email
  And it should summarize all 8 changes
  And it should indicate the interface used for each change
```

**Story Points**: 5

______________________________________________________________________

### Epic: Email Testing Infrastructure

#### Story 4: Greenmail Integration for Email Testing

**As a** developer
**I want** automated email testing with Greenmail or Python SMTP server
**So that** I can verify email workflows without a real SMTP server

**Acceptance Criteria**:

- Email testing server running during BDD tests
- Behave fixtures start/stop email server
- Email assertions in step definitions
- Email content verification (subject, body, headers)
- Test isolation (clean mailbox between scenarios)
- Integration with existing Web/CLI/API test infrastructure
- Documentation of email testing approach

**Technical Approach Options**:

**Option A: Greenmail via Podman**

```bash
# Start Greenmail in container for tests
podman run -d --rm \
  -p 3025:3025 -p 3110:3110 -p 3143:3143 \
  --name greenmail greenmail/standalone:2.0.0
```

**Option B: Python SMTP Testing (Recommended)**

- `aiosmtpd` - Async SMTP server in Python
- `smtpdfix` - pytest fixture for SMTP testing
- `mailtrap-python` - Python email testing library

**Implementation Tasks**:

- [ ] Evaluate Greenmail vs Python alternatives
- [ ] Create Behave fixtures for email server lifecycle
- [ ] Implement email assertion helpers
- [ ] Add email step definitions library
- [ ] Configure Roundup mailgw for test environment
- [ ] Integrate with existing four-interface test framework

**BDD Scenarios**: (Feature file: `features/email/testing_infrastructure.feature`)

```gherkin
@story-4 @email @infrastructure
Scenario: Email server available during tests
  Given the email testing server is running
  When I send a test email to "test@localhost"
  Then the email should be received
  And I should be able to retrieve the email

@story-4 @email @infrastructure @cross-interface
Scenario: Email notifications from all four interfaces testable
  Given the email testing server is configured
  When I create an issue via web UI
  And I update it via CLI
  And I query it via API
  And I reply via email
  Then I should receive 4 notification emails
  And I should be able to verify each email's content
  And each email should indicate the interface used

@story-4 @email @infrastructure
Scenario: Email headers for threading
  Given issue #789 exists with 2 messages
  When a new message is added via email
  Then the notification email should have "In-Reply-To" header
  And the header should reference the previous message
  And email clients should show proper threading
```

**Story Points**: 8

______________________________________________________________________

#### Story 5: Email Step Definition Library

**As a** BDD test writer
**I want** reusable email step definitions
**So that** I can write cross-interface scenarios efficiently

**Acceptance Criteria**:

- Step definitions for sending emails
- Step definitions for verifying email content
- Step definitions for email assertions (count, recipients, subject, body)
- Step definitions for email commands (embedded commands)
- Cross-interface step definitions (email + web + CLI + API)
- Documentation in BDD best practices guide
- Examples in feature files

**Step Definition Examples**:

```python
# features/steps/email_steps.py

@given('I have a valid email account "{email}"')
def step_impl(context, email):
    """Set up email account for testing"""

@when('I send an email to "{recipient}"')
def step_impl(context, recipient):
    """Send email via test SMTP server"""

@when('I reply to the notification email')
def step_impl(context):
    """Reply to last received notification"""

@then('I should receive a confirmation email')
def step_impl(context):
    """Check for confirmation email in mailbox"""

@then('the email subject should be "{subject}"')
def step_impl(context, subject):
    """Verify email subject"""

@then('the email body should contain "{text}"')
def step_impl(context, text):
    """Verify email body content"""

# Cross-interface step definitions
@then('I should receive {count:d} notification emails')
def step_impl(context, count):
    """Verify notification count across all interfaces"""
```

**Documentation Tasks**:

- [ ] Update `docs/reference/bdd-testing-best-practices.md` with email testing
- [ ] Add "Four-Interface Testing" section to BDD best practices
- [ ] Create tutorial: "Testing Across Four Interfaces"
- [ ] Document email step definitions reference
- [ ] Add email testing to debugging guide

**Story Points**: 5

______________________________________________________________________

### Epic: Email Security and Validation

#### Story 6: Email Security and Anti-Spam

**As a** homelab sysadmin
**I want** email security measures
**So that** PMS is protected from spam and malicious emails

**Acceptance Criteria**:

- Rate limiting per sender
- Attachment filtering (size limits, types)
- Email content sanitization (XSS protection)
- Bounce handling
- Blacklist/whitelist support
- Security documentation
- **BDD scenarios verify security across all interfaces**

**BDD Scenarios**: (Feature file: `features/email/security.feature`)

```gherkin
@story-6 @email @security
Scenario: Rate limiting prevents email flooding
  Given rate limiting is set to 10 emails per hour
  When "spammer@example.com" sends 15 emails in 10 minutes
  Then only the first 10 emails should be processed
  And emails 11-15 should be rejected
  And the sender should receive a rate limit notification

@story-6 @email @security @cross-interface
Scenario: Email content sanitization verified across interfaces
  Given I send an email to create an issue
  And the body contains "<script>alert('XSS')</script>"
  Then the issue should be created with sanitized content
  When I view the issue in web UI
  Then I should not see script tags
  When I get the issue via API
  Then the response should not contain script tags
  When I retrieve via CLI
  Then the output should show sanitized text

@story-6 @email @security
Scenario: Large attachments rejected
  Given attachment size limit is 10MB
  When I send an email with a 15MB attachment
  Then the email should be rejected
  And I should receive an error notification
  And no issue should be created
```

**Story Points**: 5

______________________________________________________________________

## Technical Tasks

### Email Infrastructure

- [ ] Configure `roundup-mailgw` for test environment
- [ ] Set up Greenmail or Python SMTP testing server
- [ ] Create Behave fixtures for email server lifecycle
- [ ] Implement email helper utilities
- [ ] Configure email templates in Roundup
- [ ] Integrate email testing with existing four-interface framework

### Email Interface Implementation

- [ ] Implement issue creation via email
- [ ] Implement issue updates via email
- [ ] Implement email command parsing
- [ ] Configure notification system for all four interfaces
- [ ] Set up email threading (In-Reply-To headers)
- [ ] Cross-interface notification triggers

### Four-Interface BDD Testing

- [ ] Create email step definition library
- [ ] Write cross-interface BDD scenarios (email + web + CLI + API)
- [ ] Test email authentication
- [ ] Test email security features
- [ ] Verify notifications from all four interfaces
- [ ] Document four-interface testing patterns

### Documentation

- [ ] Tutorial: "Managing Issues via Email"
- [ ] Tutorial: "Testing Across Four Interfaces"
- [ ] How-to: "Configuring Email Notifications"
- [ ] How-to: "Testing Email Workflows with BDD"
- [ ] Reference: "Email Commands Reference"
- [ ] Reference: "Email Testing Step Definitions"
- [ ] Reference: "Four-Interface BDD Testing Patterns"
- [ ] Explanation: "Email Interface Architecture"
- [ ] Update BDD best practices with four-interface patterns

### Security

- [ ] Implement rate limiting
- [ ] Email content sanitization
- [ ] Attachment validation
- [ ] Security testing for email interface
- [ ] Cross-interface security verification

## Definition of Done

- [ ] All user stories completed with acceptance criteria met
- [ ] All BDD scenarios passing (Email interface)
- [ ] Email testing infrastructure operational
- [ ] Greenmail/Python SMTP testing documented
- [ ] Email step definition library complete
- [ ] **Four-interface BDD tests passing (Web + CLI + API + Email)**
- [ ] Cross-interface scenarios demonstrate complete coverage
- [ ] Security measures implemented and tested
- [ ] Test coverage >85% maintained
- [ ] Code passes all pre-commit hooks
- [ ] CHANGELOG.md updated for v1.1.0
- [ ] Documentation complete (Diátaxis sections)
- [ ] Four-interface testing architecture documented
- [ ] Sprint retrospective completed

## Sprint Backlog

| Task                                | Story Points | Status      |
| ----------------------------------- | ------------ | ----------- |
| Story 1: Email Issue Creation       | 8            | Not Started |
| Story 2: Email Issue Updates        | 8            | Not Started |
| Story 3: Email Notifications        | 5            | Not Started |
| Story 4: Greenmail/SMTP Integration | 8            | Not Started |
| Story 5: Email Step Library         | 5            | Not Started |
| Story 6: Email Security             | 5            | Not Started |

**Total Story Points**: 39

## Four-Interface Testing Architecture

This sprint completes the comprehensive four-interface BDD testing framework:

### Interface Coverage Matrix

| Feature           | Web UI | CLI | API | Email |
| ----------------- | ------ | --- | --- | ----- |
| Issue Creation    | ✅     | ✅  | ✅  | 🔄    |
| Issue Updates     | ✅     | ✅  | ✅  | 🔄    |
| Issue Queries     | ✅     | ✅  | ✅  | N/A   |
| Notifications     | ✅     | ✅  | ✅  | 🔄    |
| Change Management | ✅     | ✅  | ✅  | 🔄    |
| CMDB              | ✅     | ✅  | ✅  | 🔄    |

Legend: ✅ Complete | 🔄 Sprint 7 Target | N/A Not Applicable

### Cross-Interface Testing Patterns

**Pattern 1: Create via Interface A, Verify via Interfaces B, C, D**

```gherkin
Scenario: Issue created via email visible everywhere
  Given I create issue "Test" via email
  Then I should see "Test" in web UI
  And I should see "Test" via CLI list
  And I should see "Test" via API GET
```

**Pattern 2: Notifications Triggered by Any Interface**

```gherkin
Scenario: Email notifications from all interfaces
  Given I am watching issue #123
  When the issue is updated via web UI
  Then I should receive an email notification
  When the issue is updated via CLI
  Then I should receive an email notification
  When the issue is updated via API
  Then I should receive an email notification
```

**Pattern 3: Security Verified Across All Interfaces**

```gherkin
Scenario: XSS protection across all interfaces
  Given I inject malicious content via email
  Then web UI should display sanitized content
  And CLI should output sanitized content
  And API should return sanitized content
```

## Risks and Dependencies

### Risks

- **Email Testing Complexity**: Java-based Greenmail may add complexity
  - *Mitigation*: Prefer Python SMTP alternatives (aiosmtpd) for easier integration
- **Email Parsing**: Complex email formats may cause parsing issues
  - *Mitigation*: Start with simple text emails, iterate to HTML/multipart
- **Cross-Interface Timing**: Race conditions between interfaces
  - *Mitigation*: Add proper wait strategies in BDD tests
- **Roundup mailgw Configuration**: Email gateway may be complex to configure
  - *Mitigation*: Early spike to validate approach, document configuration

### Dependencies

- Sprint 6 complete (v1.0.0 released)
- Roundup mailgw configured and tested
- Email testing infrastructure choice finalized (Greenmail vs Python)
- Existing Web/CLI/API test infrastructure stable

## Success Metrics

- [ ] Email interface fully functional (create, update, notify)
- [ ] Email testing infrastructure operational (Greenmail or Python SMTP)
- [ ] 25+ email BDD scenarios passing
- [ ] 15+ cross-interface BDD scenarios passing (email + web + CLI + API)
- [ ] Email step definition library with 20+ reusable steps
- [ ] Zero critical security vulnerabilities in email interface
- [ ] **Four-interface testing architecture complete and documented**
- [ ] Documentation demonstrates four-interface BDD patterns
- [ ] Sprint goal achieved: Production-ready email interface (v1.1.0)

## Post-Sprint Activities

- [ ] Create v1.1.0 release announcement
- [ ] Update email configuration documentation
- [ ] Publish "Testing Across Four Interfaces" tutorial
- [ ] Demonstrate complete four-interface BDD testing framework
- [ ] Create Marpit presentation: "Four-Interface BDD Testing with Roundup"
- [ ] Plan Sprint 8 enhancements

## BDD Demonstration Value

Sprint 7 completes the **four-interface BDD testing demonstration**, showcasing:

1. **Comprehensive Coverage**: Same functionality tested across 4 interfaces
1. **Cross-Interface Scenarios**: Verify consistency between interfaces
1. **Notification Testing**: Email testing enables complete workflow verification
1. **Real-World Patterns**: Demonstrates practical BDD for complex systems
1. **Educational Value**: Complete example for Python/BDD learners

This sprint delivers the final piece of the PMS BDD demonstration objective, providing a complete reference implementation for multi-interface BDD testing.
