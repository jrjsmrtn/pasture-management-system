<!--
SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
SPDX-License-Identifier: MIT
-->

# Sprint 9 Plan: Advanced Email Features & GreenMail Integration

**Sprint Goal**: Complete email gateway advanced features with GreenMail integration testing and comprehensive email notification system.

**Target Version**: v1.2.0
**Duration**: 2 weeks (Nov 21 - Dec 5, 2025)
**Total Points**: 26-39 (high priority: 26, stretch: 39)

## Sprint Context

**Building on Sprint 8 achievements**:

- ✅ Core email gateway working (PIPE mode, create/update issues)
- ✅ Email notifications functional (6/8 scenarios passing)
- ✅ Four-interface BDD testing architecture (15/15 scenarios passing)
- ✅ Load testing validated system for 1-50 users

**Sprint 8 deferred items**:

- Email gateway advanced features (8/12 scenarios remaining)
- Email notification edge cases (2/8 scenarios remaining)
- GreenMail integration for comprehensive email testing
- Email security & anti-spam controls
- Email-based change management

## Sprint Objectives

1. **Complete email gateway functionality** (100% BDD coverage)
1. **Implement GreenMail integration** for real email testing
1. **Add email security controls** (anti-spam, rate limiting)
1. **Document four-interface testing** (tutorial guide)
1. **Stretch**: Email-based change management workflows

## User Stories

### Critical Priority (18 points)

#### Story 1: GreenMail Integration (8 points)

**As a** developer
**I want** comprehensive email integration tests using GreenMail
**So that** I can test full email workflows including IMAP/SMTP

**Acceptance Criteria**:

- [ ] GreenMail server integration in BDD environment setup
- [ ] IMAP mailbox verification step definitions
- [ ] SMTP sending verification step definitions
- [ ] Email gateway scenarios migrated to GreenMail (12/12 passing)
- [ ] Documentation: GreenMail testing guide
- [ ] Both PIPE mode and GreenMail tests available (optional modes)

**Technical Notes**:

- Use Docker/Podman container for GreenMail server
- Start/stop GreenMail in Behave environment.py hooks
- Keep PIPE mode tests as fast fallback option
- GreenMail enables testing: IMAP polling, SMTP sending, mailbox state

**Implementation Tasks**:

- [ ] Add GreenMail dependency to requirements.txt
- [ ] Create GreenMail container configuration (docker-compose.yml)
- [ ] Update environment.py with GreenMail lifecycle hooks
- [ ] Write IMAP/SMTP step definitions
- [ ] Migrate email gateway scenarios to use GreenMail
- [ ] Add GreenMail vs PIPE mode documentation

**Story Points**: 8

______________________________________________________________________

#### Story 2: Email Advanced Features (8 points)

**As a** user
**I want** advanced email features (attachments, HTML, status updates)
**So that** I can interact with issues naturally via email

**Acceptance Criteria**:

- [ ] Email attachments preserved when creating/updating issues
- [ ] HTML email conversion to plain text (BeautifulSoup4)
- [ ] Status updates via email (e.g., "[issue123] [status:resolved]")
- [ ] Unknown user auto-creation with configurable security policy
- [ ] Invalid issue ID rejection with helpful error messages
- [ ] BDD scenarios: 8/12 remaining scenarios passing (100% total)

**Technical Notes**:

- BeautifulSoup4 for HTML to plain text conversion
- Attachment handling via Roundup's msg attachments
- Status updates require detector configuration investigation
- Unknown user creation needs security review (whitelist/blacklist)

**Remaining BDD Scenarios** (from Sprint 8):

1. ❌ Update issue status via email subject
1. ✅ Email with quoted text (should work as-is)
1. ❌ Email from unknown user creates new user
1. ❌ Email with invalid issue ID is rejected
1. ❌ Email with multiple attachments
1. ❌ HTML email is converted to plain text

**Implementation Tasks**:

- [ ] Add BeautifulSoup4 dependency
- [ ] Implement HTML to text conversion in mailgw detector
- [ ] Add attachment handling to issue creation/update
- [ ] Implement status update parsing from email subject/body
- [ ] Add unknown user handling with security policy
- [ ] Add invalid issue ID error handling
- [ ] Update email gateway BDD scenarios (100% passing)

**Story Points**: 8

______________________________________________________________________

#### Story 3: Complete Email Notification System (2 points)

**As a** user
**I want** complete email notification coverage
**So that** I receive notifications according to my preferences

**Acceptance Criteria**:

- [ ] Message author notification control (messages_to_author config)
- [ ] Nosy list auto-adds issue creator
- [ ] BDD scenarios: 2/8 remaining scenarios passing (100% total)
- [ ] Configuration guide: Email notification preferences

**Technical Notes**:

- Requires config.ini changes for messages_to_author testing
- Nosy list auto-add may need detector implementation

**Remaining BDD Scenarios** (from Sprint 8):

- ⏳ Message author not notified (messages_to_author = no) - requires config change
- ⏳ Nosy list auto-adds creator - missing step definition (minor feature)

**Implementation Tasks**:

- [ ] Add messages_to_author = no test scenario
- [ ] Implement nosy list auto-add detector (if missing)
- [ ] Update email notification BDD scenarios (100% passing)
- [ ] Document notification configuration options

**Story Points**: 2

______________________________________________________________________

### High Priority (8 points)

#### Story 4: Email Security & Anti-Spam (5 points)

**As a** sysadmin
**I want** email security controls
**So that** I can prevent spam and abuse

**Acceptance Criteria**:

- [ ] Sender whitelist/blacklist configuration
- [ ] Attachment size limits enforced
- [ ] Rate limiting per sender
- [ ] Suspicious email detection (spam keywords, patterns)
- [ ] BDD scenarios for security controls (8 scenarios)
- [ ] Documentation: Email security hardening guide

**Technical Notes**:

- Implement as mailgw detector/auditor
- Use Roundup's permission system for whitelists
- Log blocked emails for audit trail

**Implementation Tasks**:

- [ ] Implement sender whitelist/blacklist
- [ ] Add attachment size limit checks
- [ ] Implement rate limiting (Redis/file-based counter)
- [ ] Add spam keyword detection
- [ ] Write security BDD scenarios
- [ ] Document email security configuration

**Story Points**: 5

______________________________________________________________________

#### Story 5: Four-Interface Testing Tutorial (3 points)

**As a** BDD practitioner
**I want** a comprehensive four-interface testing tutorial
**So that** I can apply these patterns to my projects

**Acceptance Criteria**:

- [ ] Tutorial: Four-interface BDD testing guide
- [ ] Code examples for each interface (Web, CLI, API, Email)
- [ ] Cross-interface verification examples
- [ ] Variable substitution patterns documented
- [ ] Troubleshooting guide for common issues

**Technical Notes**:

- Based on Sprint 8's four_interface_testing.feature
- Include Playwright, API, CLI, Email step definition patterns
- Explain design decisions and tradeoffs

**Implementation Tasks**:

- [ ] Write tutorial introduction and objectives
- [ ] Document each interface testing approach
- [ ] Explain cross-interface verification patterns
- [ ] Add troubleshooting section
- [ ] Review and polish for public release

**Story Points**: 3

______________________________________________________________________

### Stretch Goals (13 points)

#### Story 6: Email-Based Change Management (5 points)

**As a** user
**I want** to manage changes via email
**So that** I can work with change workflows without the web UI

**Acceptance Criteria**:

- [ ] Create changes via email
- [ ] Update changes via email
- [ ] Link changes to issues via email
- [ ] Change approval via email reply
- [ ] BDD scenarios for email-based change workflows (6 scenarios)

**Story Points**: 5

______________________________________________________________________

#### Story 7: Email Templates & Formatting (3 points)

**As a** sysadmin
**I want** customizable email notification templates
**So that** I can brand and format notifications for my organization

**Acceptance Criteria**:

- [ ] Customizable notification templates (Jinja2/template strings)
- [ ] HTML email formatting option
- [ ] Email signature configuration
- [ ] Template variables documented (issue, user, change, etc.)
- [ ] BDD scenarios for template rendering (4 scenarios)

**Story Points**: 3

______________________________________________________________________

#### Story 8: Email Threading & Conversation Tracking (5 points)

**As a** user
**I want** email threading and conversation tracking
**So that** I can follow issue discussions in my email client

**Acceptance Criteria**:

- [ ] Email threading headers (In-Reply-To, References)
- [ ] Conversation tracking in issue messages
- [ ] Reply-to correct issue even without [issueN] in subject
- [ ] BDD scenarios for email threading (5 scenarios)

**Story Points**: 5

______________________________________________________________________

## Sprint Metrics

### Point Distribution

| Priority           | Points | Stories |
| ------------------ | ------ | ------- |
| **Critical** (1-3) | 18     | 3       |
| **High** (4-5)     | 8      | 2       |
| **Stretch** (6-8)  | 13     | 3       |
| **Total**          | 39     | 8       |

### Velocity Planning

- **High Priority Target**: 26 points (Stories 1-5)
- **Stretch Target**: 39 points (all stories)
- **Historical Velocity**: 27 points/day (Sprint 8, exceptional)
- **Conservative Estimate**: 15-20 points/week
- **Optimistic Estimate**: 26-39 points in 2 weeks

## Dependencies

### External

- **GreenMail**: Docker/Podman container (greenmail/standalone:latest)
- **BeautifulSoup4**: HTML parsing library
- **Redis** (optional): For distributed rate limiting

### Internal

- ✅ BDD test framework (Behave + Playwright)
- ✅ Roundup mailgw (included)
- ✅ Four-interface testing infrastructure
- ✅ Email gateway PIPE mode implementation

## Risks & Mitigation

| Risk                                | Impact | Probability | Mitigation                                                 |
| ----------------------------------- | ------ | ----------- | ---------------------------------------------------------- |
| GreenMail integration complexity    | High   | Medium      | Keep PIPE mode as fallback; make GreenMail optional        |
| Email security over-engineering     | Medium | Low         | Start with simple whitelist/size limits; iterate           |
| BeautifulSoup4 parsing edge cases   | Medium | Medium      | Test with varied email clients; graceful fallback          |
| Unknown user auto-creation security | High   | Low         | Require explicit whitelist; document security implications |
| Rate limiting state management      | Low    | Low         | Use simple file-based counter; Redis optional              |

## Success Criteria

**Must Have** (Sprint Success):

- ✅ GreenMail integration complete (Story 1: 8 points)
- ✅ Email advanced features working (Story 2: 8 points)
- ✅ Email notifications 100% complete (Story 3: 2 points)
- ✅ Email security basics (Story 4: 5 points)
- ✅ Documentation: 26+ points delivered

**Nice to Have** (Stretch Goals):

- 🎯 Email-based change management (Story 6: 5 points)
- 🎯 Email templates (Story 7: 3 points)
- 🎯 Email threading (Story 8: 5 points)

**Quality Gates**:

- All high-priority BDD scenarios passing (100%)
- Email security audit passed (no critical vulnerabilities)
- Documentation complete (tutorial + reference)
- Code coverage >85%

## Technical Approach

### GreenMail Integration Architecture

```
BDD Test Environment
├── GreenMail Container (Docker/Podman)
│   ├── SMTP Server (port 3025)
│   ├── IMAP Server (port 3143)
│   └── POP3 Server (port 3110)
├── Roundup Server (port 9080)
│   └── mailgw detector (connects to GreenMail SMTP)
└── Behave Step Definitions
    ├── SMTP sending steps
    ├── IMAP verification steps
    └── Mailbox state assertions
```

### Email Advanced Features Flow

```
Email Gateway Processing
1. Receive email (PIPE mode or IMAP poll)
2. Parse headers (From, Subject, To)
3. Extract issue ID ([issueN] or Reply-To)
4. Convert HTML to plain text (BeautifulSoup4)
5. Process attachments
6. Parse commands (status, priority, nosy)
7. Authenticate sender (whitelist/blacklist)
8. Create/update issue
9. Trigger notifications
```

## Documentation Deliverables

### Tutorials

- [ ] Four-interface BDD testing guide (Story 5)
- [ ] Email gateway advanced features tutorial

### How-To Guides

- [ ] GreenMail testing setup
- [ ] Email security configuration
- [ ] Email template customization
- [ ] Configure outgoing email (SMTP)
- [ ] Configure incoming email (IMAP/POP3)

### Reference

- [ ] Email gateway configuration reference
- [ ] Email security controls reference
- [ ] GreenMail API reference

## Out of Scope (Future Sprints)

- Email dashboard (analytics, delivery rates)
- Email scheduling/delayed sending
- Email digest mode (batch notifications)
- Multi-language email notifications
- Email-based reporting
- Email API (programmatic sending)
- Web-based email interface (webmail)
- Calendar invites (.ics files)

## Sprint Timeline

### Week 1 (Nov 21-27)

- **Days 1-2**: Story 1 - GreenMail integration (8 points)
- **Days 3-4**: Story 2 - Email advanced features (8 points)
- **Day 5**: Story 3 - Complete notifications (2 points)

### Week 2 (Nov 28 - Dec 5)

- **Days 1-2**: Story 4 - Email security (5 points)
- **Day 3**: Story 5 - Four-interface tutorial (3 points)
- **Days 4-5**: Stretch goals (Stories 6-8) or polish

## Definition of Done

**Story Completion**:

- [ ] All acceptance criteria met
- [ ] BDD scenarios passing (100% for story scope)
- [ ] Code reviewed and formatted (ruff)
- [ ] Type checking passed (mypy)
- [ ] Documentation updated (Diátaxis framework)
- [ ] Commit message follows convention

**Sprint Completion**:

- [ ] High priority stories complete (26 points minimum)
- [ ] Sprint backlog updated with final metrics
- [ ] Sprint retrospective written
- [ ] CHANGELOG.md updated with v1.2.0 section
- [ ] Version bumped to 1.2.0
- [ ] Git tag created (v1.2.0)
- [ ] CLAUDE.md updated with Sprint 10 preview

## Next Sprint Preview (Sprint 10)

**Potential Focus Areas**:

- Advanced CMDB features (relationship mapping, dependency tracking)
- Reporting & analytics dashboards
- Integration APIs (webhooks, external tools)
- Multi-language support
- Email digest mode
- Mobile-responsive web UI
- REST API enhancements (rate limiting, JWT authentication)
- API documentation (OpenAPI/Swagger)

______________________________________________________________________

**Document Version**: 2.0
**Date**: 2025-11-21
**Status**: 🟢 Ready to Start
**Previous Version**: 1.0 (created during Sprint 8 planning)
