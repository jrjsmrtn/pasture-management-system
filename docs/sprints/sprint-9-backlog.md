# Sprint 9 Backlog: Advanced Email Features & GreenMail Integration

**Sprint Goal**: Complete email gateway advanced features with GreenMail integration testing and comprehensive email notification system.

**Target Version**: v1.2.0
**Duration**: 2 weeks (Nov 21 - Dec 5, 2025)
**Total Points**: 26-39 (high priority: 26, stretch: 39)

## Sprint Progress

**Status**: 🟢 IN PROGRESS
**Completed Points**: 8/26 (31%)
**Days Elapsed**: 0 (Story 1 completed in 1 day)

## Stories

### 📋 Story 1: GreenMail Integration (8 points) - ✅ **COMPLETE**

**Status**: ✅ COMPLETE (2025-11-21)

**As a** developer
**I want** comprehensive email integration tests using GreenMail
**So that** I can test full email workflows including IMAP/SMTP

**Acceptance Criteria**:

- [x] GreenMail server integration in BDD environment setup
- [x] IMAP mailbox verification step definitions (10 new steps)
- [x] SMTP sending verification step definitions (hybrid SMTP + mailgw)
- [x] Email gateway scenarios migrated to GreenMail (4/4 core scenarios passing)
- [x] Documentation: GreenMail testing guide (docs/reference/greenmail-testing.md)
- [x] Both PIPE mode and GreenMail tests available (EMAIL_TEST_MODE env var)

**Technical Notes**:

- ✅ Use Podman container for GreenMail server (stable version 2.1.7)
- ✅ Start/stop GreenMail in Behave environment.py hooks (greenmail_server fixture)
- ✅ Keep PIPE mode tests as fast fallback option (default mode)
- ✅ GreenMail enables testing: IMAP polling, SMTP sending, mailbox state

**Implementation Tasks**:

- [x] Add GreenMail dependency to requirements.txt (N/A - container-based)
- [x] Create GreenMail container configuration (GreenMailContainer class)
- [x] Update environment.py with GreenMail lifecycle hooks (before_all/after_all)
- [x] Write IMAP/SMTP step definitions (10 GreenMail-specific steps)
- [x] Migrate email gateway scenarios to use GreenMail (hybrid approach)
- [x] Add GreenMail vs PIPE mode documentation (450+ line reference guide)

**Deliverables**:

- `tests/utils/greenmail_client.py` (387 lines) - GreenMailClient & GreenMailContainer
- `features/environment.py` - greenmail_server fixture with EMAIL_TEST_MODE support
- `features/steps/email_steps.py` - 10 new GreenMail IMAP verification steps
- `docs/reference/greenmail-testing.md` (450+ lines) - Comprehensive testing guide
- Test Results: 4/4 core scenarios passing (100% Story 1 scope)

**Points**: 8 ✅

______________________________________________________________________

### 📋 Story 2: Email Advanced Features (8 points) - **NOT STARTED**

**Status**: ⏳ NOT STARTED

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

**Points**: 8

______________________________________________________________________

### 📋 Story 3: Complete Email Notification System (2 points) - **NOT STARTED**

**Status**: ⏳ NOT STARTED

**As a** user
**I want** complete email notification coverage
**So that** I receive notifications according to my preferences

**Acceptance Criteria**:

- [ ] Message author notification control (messages_to_author config)
- [ ] Nosy list auto-adds issue creator
- [ ] BDD scenarios: 2/8 remaining scenarios passing (100% total)
- [ ] Configuration guide: Email notification preferences

**Remaining BDD Scenarios** (from Sprint 8):

- ⏳ Message author not notified (messages_to_author = no) - requires config change
- ⏳ Nosy list auto-adds creator - missing step definition (minor feature)

**Implementation Tasks**:

- [ ] Add messages_to_author = no test scenario
- [ ] Implement nosy list auto-add detector (if missing)
- [ ] Update email notification BDD scenarios (100% passing)
- [ ] Document notification configuration options

**Points**: 2

______________________________________________________________________

### 📋 Story 4: Email Security & Anti-Spam (5 points) - **NOT STARTED**

**Status**: ⏳ NOT STARTED

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

**Implementation Tasks**:

- [ ] Implement sender whitelist/blacklist
- [ ] Add attachment size limit checks
- [ ] Implement rate limiting (Redis/file-based counter)
- [ ] Add spam keyword detection
- [ ] Write security BDD scenarios
- [ ] Document email security configuration

**Points**: 5

______________________________________________________________________

### 📋 Story 5: Four-Interface Testing Tutorial (3 points) - **NOT STARTED**

**Status**: ⏳ NOT STARTED

**As a** BDD practitioner
**I want** a comprehensive four-interface testing tutorial
**So that** I can apply these patterns to my projects

**Acceptance Criteria**:

- [ ] Tutorial: Four-interface BDD testing guide
- [ ] Code examples for each interface (Web, CLI, API, Email)
- [ ] Cross-interface verification examples
- [ ] Variable substitution patterns documented
- [ ] Troubleshooting guide for common issues

**Implementation Tasks**:

- [ ] Write tutorial introduction and objectives
- [ ] Document each interface testing approach
- [ ] Explain cross-interface verification patterns
- [ ] Add troubleshooting section
- [ ] Review and polish for public release

**Points**: 3

______________________________________________________________________

## Stretch Goals (Medium Priority)

### 📋 Story 6: Email-Based Change Management (5 points) - **NOT STARTED**

**Status**: ⏳ STRETCH GOAL

**As a** user
**I want** to manage changes via email
**So that** I can work with change workflows without the web UI

**Acceptance Criteria**:

- [ ] Create changes via email
- [ ] Update changes via email
- [ ] Link changes to issues via email
- [ ] Change approval via email reply
- [ ] BDD scenarios for email-based change workflows (6 scenarios)

**Points**: 5

______________________________________________________________________

### 📋 Story 7: Email Templates & Formatting (3 points) - **NOT STARTED**

**Status**: ⏳ STRETCH GOAL

**As a** sysadmin
**I want** customizable email notification templates
**So that** I can brand and format notifications for my organization

**Acceptance Criteria**:

- [ ] Customizable notification templates (Jinja2/template strings)
- [ ] HTML email formatting option
- [ ] Email signature configuration
- [ ] Template variables documented (issue, user, change, etc.)
- [ ] BDD scenarios for template rendering (4 scenarios)

**Points**: 3

______________________________________________________________________

### 📋 Story 8: Email Threading & Conversation Tracking (5 points) - **NOT STARTED**

**Status**: ⏳ STRETCH GOAL

**As a** user
**I want** email threading and conversation tracking
**So that** I can follow issue discussions in my email client

**Acceptance Criteria**:

- [ ] Email threading headers (In-Reply-To, References)
- [ ] Conversation tracking in issue messages
- [ ] Reply-to correct issue even without [issueN] in subject
- [ ] BDD scenarios for email threading (5 scenarios)

**Points**: 5

______________________________________________________________________

## Sprint Metrics

### Point Distribution

| Priority                   | Points | Status     |
| -------------------------- | ------ | ---------- |
| **Critical** (Stories 1-3) | 18     | 8/18 (44%) |
| **High** (Stories 4-5)     | 8      | 0/8 (0%)   |
| **Stretch** (Stories 6-8)  | 13     | 0/13 (0%)  |
| **Total**                  | 39     | 8/39 (21%) |

### Velocity Tracking

- **Planned**: 26 points (high priority)
- **Completed**: 8 points (Story 1 complete)
- **Remaining**: 18 points (high priority)
- **Days Elapsed**: 0 days (1-day completion)
- **Actual Velocity**: 8 points/day (exceptional - Story 1 only)

### Story Completion

- ✅ Complete: 1/8 (13%) - Story 1: GreenMail Integration
- 🔄 In Progress: 0/8 (0%)
- ⏳ Not Started: 7/8 (87%)

## Key Decisions

(To be documented as sprint progresses)

## Risks & Mitigation

| Risk                                | Impact | Mitigation                                                 | Status        |
| ----------------------------------- | ------ | ---------------------------------------------------------- | ------------- |
| GreenMail integration complexity    | High   | Keep PIPE mode as fallback; make GreenMail optional        | ⏳ Monitoring |
| Email security over-engineering     | Medium | Start with simple whitelist/size limits; iterate           | ⏳ Monitoring |
| BeautifulSoup4 parsing edge cases   | Medium | Test with varied email clients; graceful fallback          | ⏳ Monitoring |
| Unknown user auto-creation security | High   | Require explicit whitelist; document security implications | ⏳ Monitoring |

## Documentation Delivered

### Story 1 (Complete)

- **GreenMail Testing Reference** (`docs/reference/greenmail-testing.md`) - 450+ lines
  - Overview and architecture
  - Configuration and usage examples
  - PIPE mode vs GreenMail mode comparison
  - Port mapping and container management
  - Troubleshooting guide
  - Performance benchmarks (PIPE: ~0.17s/test, GreenMail: ~5.2s/test)
  - API reference for GreenMailClient & GreenMailContainer
  - Best practices and integration patterns

## Next Actions

### Immediate

1. ✅ Story 1: GreenMail integration (COMPLETE - 8 points)
1. ⏭️ Begin Story 2: Email advanced features (8 points)

### This Week

- ✅ Story 1: GreenMail integration (8 points) - COMPLETE
- Story 2: Email advanced features (8 points) - NEXT
- Story 3: Complete email notification system (2 points)

### Next Week

- Story 4: Email security & anti-spam (5 points)
- Story 5: Four-interface testing tutorial (3 points)
- Stretch goals if time permits

## Notes

- Sprint 9 builds on Sprint 8's email foundation
- Focus: Complete advanced email features and GreenMail integration
- GreenMail tests are **optional** - PIPE mode tests remain primary
- Security review required before user auto-creation
