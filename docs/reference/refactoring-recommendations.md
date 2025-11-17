<!--
SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
SPDX-License-Identifier: MIT
-->

# Refactoring and Improvement Recommendations

**Date:** 2025-01-17
**Sprint:** Post-Sprint 4 (CMDB Implementation Complete)
**Related:** [Roundup Development Best Practices](roundup-development-practices.md)

This document identifies refactoring opportunities and improvements based on Roundup best practices research and code review.

## Executive Summary

The CMDB implementation (Sprint 4) is functional and well-structured. However, several optimization opportunities exist that would:
- Improve performance and user experience
- Enhance security posture
- Align with Roundup community best practices
- Prepare for production deployment

## Priority Levels

- 🔴 **Critical** - Security or data integrity issues
- 🟡 **High** - Performance or usability improvements
- 🟢 **Medium** - Code quality and maintainability
- 🔵 **Low** - Nice-to-have enhancements

---

## 1. Schema Optimizations

### 🟡 Missing Label and Order Properties

**Issue:** Many classes lack `setlabelprop()` and `setorderprop()` definitions.

**Current State:**
```python
# tracker/schema.py
ci = Class(db, "ci", name=String(), ...)
# Missing setlabelprop() and setorderprop()
```

**Impact:**
- Dropdown menus may show IDs instead of meaningful names
- Default sorting by ID is inefficient
- Poor user experience in CI selection

**Recommendation:**
```python
# Add to schema.py after each class definition
ci.setlabelprop("name")      # Display CI name in dropdowns
ci.setorderprop("name")      # Sort CIs alphabetically by name

change.setlabelprop("title")  # Display change title
change.setorderprop("id")     # Sort by ID (most recent first)

cirelationship.setlabelprop("description")  # Or composite label
cirelationship.setorderprop("source_ci")    # Sort by source CI
```

**Reference:** [Best Practices - Schema](roundup-development-practices.md#schema-best-practices)

**Effort:** Low (15 minutes)

---

### 🟡 Missing Selective Full-Text Indexing

**Issue:** No String properties have `indexme='yes'` specified.

**Current State:**
```python
ci = Class(db, "ci",
    name=String(),           # Should be indexed
    description=String(),    # Should be indexed
    location=String(),       # Maybe indexed
    os=String(),            # Probably not indexed
    ip_address=String(),    # Probably not indexed
)
```

**Impact:**
- Full-text search may not work as expected
- Or ALL string fields are indexed (performance overhead)
- Inefficient search queries

**Recommendation:**
```python
ci = Class(db, "ci",
    name=String(indexme='yes'),           # User searches by name
    description=String(indexme='yes'),    # User searches descriptions
    location=String(indexme='yes'),       # User searches by location
    os=String(indexme='no'),             # Rarely searched
    ip_address=String(indexme='no'),     # Rarely searched via FTS
    vendor=String(indexme='yes'),        # User searches by vendor
)

change = IssueClass(db, "change",
    description=String(indexme='yes'),
    justification=String(indexme='yes'),
    impact=String(indexme='yes'),
)
```

**Reference:** [Best Practices - Full-Text Search](roundup-development-practices.md#full-text-search)

**Effort:** Low (30 minutes)

---

### 🟢 Consider CI Parent-Child Hierarchy

**Issue:** No hierarchical CI relationships (parent-child).

**Current State:**
- Only peer-to-peer relationships via `cirelationship`
- No built-in parent-child modeling

**Potential Enhancement:**
```python
ci = Class(db, "ci",
    # ... existing fields ...
    parent=Link("ci", rev_multilink="children"),
    # children automatically created as read-only Multilink
)
```

**Benefits:**
- Automatic bidirectional relationship maintenance
- Useful for: VMs → Host, Apps → Server, Components → System
- Simpler queries for hierarchical structures

**Trade-offs:**
- Current `cirelationship` approach is more flexible
- May not be needed if all relationships are typed

**Reference:** [Best Practices - Parent-Child Hierarchies](roundup-development-practices.md#parent-child-hierarchies)

**Effort:** Medium (2 hours) - Requires schema migration testing

**Recommendation:** Defer to Sprint 5+ unless specific use case emerges

---

## 2. Detector Improvements

### 🟡 Refactor Circular Reference Detection

**Issue:** Current `ci_relationship_validator.py` uses custom pattern instead of canonical wiki pattern.

**Current Implementation:**
```python
def has_circular_dependency(db, source_ci, target_ci, visited=None):
    if visited is None:
        visited = set()
    # ... set-based tracking
```

**Wiki Best Practice:**
```python
def check_loop(db, cl, nodeid, prop, attr, ids=None):
    """Canonical loop detection from Roundup wiki."""
    # ... list-based tracking with better error messages
```

**Analysis:**
- ✅ **Current code works correctly**
- ✅ **Current code is well-documented**
- ⚠️ Wiki pattern provides better error messages (shows full cycle path)
- ⚠️ Wiki pattern is more generic (works for Link and Multilink)

**Recommendation:**
- **Keep current implementation** (it works well for your use case)
- **OR** Refactor to wiki pattern for:
  - Better error messages showing full dependency chain
  - Reusability for other relationship types
  - Alignment with community standards

**If Refactoring:**
```python
# In tracker/lib/relationship_utils.py (new shared module)
from roundup.hyperdb import Link, Multilink
from roundup.exceptions import Reject

def check_loop(db, cl, nodeid, prop, attr, ids=None):
    """Check for circular references (canonical wiki pattern)."""
    if ids is None:
        ids = []

    is_multi = isinstance(cl.properties[prop], Multilink)
    assert (is_multi or isinstance(cl.properties[prop], Link))

    label = cl.labelprop()
    if nodeid:
        ids.append(nodeid)

    if attr:
        if not is_multi:
            attr = [attr]
        for a in attr:
            if a in ids:
                # Show full cycle path in error
                raise Reject("Circular %s dependency: %s" % (
                    prop, ' → '.join([cl.get(i, label) for i in ids + [a]])
                ))
            check_loop(db, cl, a, prop, cl.get(a, prop), ids[:])
            ids.pop()

# In tracker/detectors/ci_relationship_validator.py
from tracker.lib.relationship_utils import check_loop

def validate_ci_relationship(db, cl, nodeid, newvalues):
    # ... existing validation ...

    # Use canonical loop checker
    if 'source_ci' in newvalues or 'target_ci' in newvalues:
        source_ci = newvalues.get("source_ci", cl.get(nodeid, "source_ci") if nodeid else None)
        target_ci = newvalues.get("target_ci", cl.get(nodeid, "target_ci") if nodeid else None)

        # Check loop using relationship chain
        check_loop(db, db.ci, source_ci, 'target_ci', target_ci)
```

**Reference:** [Best Practices - Circular Reference Prevention](roundup-development-practices.md#preventing-circular-references)

**Effort:** Medium (1-2 hours) - Only if prioritizing error message quality

**Decision:** **Recommend keeping current implementation unless error messages become a pain point**

---

### 🟢 Add Email Notification Reactor

**Issue:** No automated email notifications for critical events.

**Potential Use Cases:**
- Notify admins when new CIs are created
- Notify CI owners when relationships change
- Notify change owners when change status transitions

**Example Implementation:**
```python
# In tracker/detectors/ci_notifications.py
from roundup.exceptions import DetectorError
from roundup import roundupdb

def notify_ci_owner_on_relationship(db, cl, nodeid, oldvalues):
    """Reactor: Notify CI owner when relationships change."""
    try:
        # Get the relationship
        source_ci = db.cirelationship.get(nodeid, 'source_ci')
        target_ci = db.cirelationship.get(nodeid, 'target_ci')

        # Get CI owners
        source_owner = db.ci.get(source_ci, 'owner')
        target_owner = db.ci.get(target_ci, 'owner')

        # Build notification message
        rel_type = db.cirelationship.get(nodeid, 'relationship_type')
        type_name = db.cirelationshiptype.get(rel_type, 'name')

        source_name = db.ci.get(source_ci, 'name')
        target_name = db.ci.get(target_ci, 'name')

        message = f"CI relationship created: {source_name} {type_name} {target_name}"

        # Send to owners (if they exist and are different)
        recipients = set()
        if source_owner:
            recipients.add(db.user.get(source_owner, 'address'))
        if target_owner and target_owner != source_owner:
            recipients.add(db.user.get(target_owner, 'address'))

        if recipients:
            # TODO: Implement email sending logic
            # cl.send_message(nodeid, msgid, message, list(recipients))
            pass

    except roundupdb.MessageSendError as e:
        raise DetectorError(str(e))

def init(db):
    db.cirelationship.react('create', notify_ci_owner_on_relationship)
```

**Reference:** [Best Practices - Email Notifications](roundup-development-practices.md#email-notification-patterns)

**Effort:** Medium (2-3 hours) - Requires email configuration testing

**Recommendation:** Defer to Sprint 5+ (Reporting and Analytics sprint may include notification requirements)

---

### 🟢 Add Nosy List Management for Changes

**Issue:** Change class has nosy list (from IssueClass) but no selective notification logic.

**Current Behavior:**
- All nosy list members notified on every change
- Potential for notification fatigue

**Recommendation:**
```python
# In tracker/detectors/change_notifications.py
def selective_change_notification(db, cl, nodeid, oldvalues):
    """Only notify when significant fields change."""

    # Silent fields that don't trigger notifications
    silent_fields = ['nosy', 'activity']

    # Check if any significant field changed
    significant_change = False
    for field in oldvalues.keys():
        if field not in silent_fields:
            significant_change = True
            break

    # Require message for status transitions
    if 'status' in oldvalues:
        messages = cl.get(nodeid, 'messages')
        if not messages or len(messages) == len(oldvalues.get('messages', [])):
            raise ValueError("Status changes require an explanatory message")

    # Let standard notification proceed only for significant changes
    return significant_change

def init(db):
    db.change.audit('set', selective_change_notification)
```

**Reference:** [Best Practices - Nosy List Management](roundup-development-practices.md#nosy-list-management)

**Effort:** Low (1 hour)

**Recommendation:** Consider for Sprint 5+ if users report notification issues

---

## 3. Template Optimizations

### 🟡 CI Form Field Conditional Rendering

**Issue:** `ci.item.html` shows ALL type-specific fields for all CI types.

**Current State:**
```html
<!-- Lines 77-100+ in ci.item.html -->
<!-- Server/VM specific fields: show all when creating new, filter by type when editing -->
<tr>
 <th i18n:translate="">CPU Cores</th>
 <td tal:content="structure python:context.cpu_cores.field(size=10)">cpu_cores</td>
 <th i18n:translate="">RAM (GB)</th>
 <td tal:content="structure python:context.ram_gb.field(size=10)">ram_gb</td>
</tr>
```

**Impact:**
- Confusing UX: Network devices see "CPU Cores", Storage sees "Ports"
- Form validation complexity
- Cluttered interface

**Recommendation:**
```html
<!-- Conditional field groups based on CI type -->
<tal:block define="ci_type python:context.type.plain() if context.id else None">

<!-- Server/VM fields (type_id=1) -->
<tal:block condition="python:not ci_type or ci_type == '1'">
<tr>
 <th i18n:translate="">CPU Cores</th>
 <td tal:content="structure python:context.cpu_cores.field(size=10)">cpu_cores</td>
 <th i18n:translate="">RAM (GB)</th>
 <td tal:content="structure python:context.ram_gb.field(size=10)">ram_gb</td>
</tr>
<tr>
 <th i18n:translate="">Operating System</th>
 <td colspan=3 tal:content="structure python:context.os.field(size=60)">os</td>
</tr>
</tal:block>

<!-- Network device fields (type_id=2) -->
<tal:block condition="python:not ci_type or ci_type == '2'">
<tr>
 <th i18n:translate="">Ports</th>
 <td tal:content="structure python:context.ports.field(size=10)">ports</td>
 <th i18n:translate="">IP Address</th>
 <td tal:content="structure python:context.ip_address.field(size=20)">ip_address</td>
</tr>
</tal:block>

<!-- Storage fields (type_id=3) -->
<tal:block condition="python:not ci_type or ci_type == '3'">
<tr>
 <th i18n:translate="">Capacity (GB)</th>
 <td tal:content="structure python:context.capacity_gb.field(size=10)">capacity_gb</td>
</tr>
</tal:block>

<!-- Software/Service fields (type_id=4) -->
<tal:block condition="python:not ci_type or ci_type == '4'">
<tr>
 <th i18n:translate="">Version</th>
 <td tal:content="structure python:context.version.field(size=20)">version</td>
 <th i18n:translate="">Vendor</th>
 <td tal:content="structure python:context.vendor.field(size=40)">vendor</td>
</tr>
</tal:block>

</tal:block>
```

**Alternative:** Use JavaScript to dynamically show/hide field groups based on selected CI type.

**Reference:** [Best Practices - Template Performance](roundup-development-practices.md#template-performance)

**Effort:** Medium (2-3 hours) - Requires testing for all CI types

**Recommendation:** **High priority for Sprint 5 - significantly improves UX**

---

### 🟡 CI Index Page Performance

**Issue:** Need to review `ci.index.html` for batching and query optimization.

**Check Points:**
1. ✅ Is batching enabled for large CI lists?
2. ✅ Are related lookups cached (e.g., CI type, status)?
3. ✅ Is pagination implemented?

**Example Optimization:**
```html
<!-- Use tal:define to cache lookups -->
<tr tal:repeat="ci batch"
    tal:define="ci_type python:db.citype.getnode(ci.type);
                ci_status python:db.cistatus.getnode(ci.status);
                ci_owner python:db.user.getnode(ci.owner) if ci.owner else None">
  <td tal:content="ci/name">name</td>
  <td tal:content="ci_type/name">type</td>
  <td tal:content="ci_status/name">status</td>
  <td tal:content="ci_owner/username | string:Unassigned">owner</td>
</tr>
```

**Reference:** [Best Practices - Template Performance](roundup-development-practices.md#minimize-database-calls-in-templates)

**Effort:** Low (1 hour) - Review and optimize if needed

**Recommendation:** Check during Sprint 5 testing with larger CI datasets

---

## 4. Security Hardening

### 🔴 Change Default Secret Key

**Issue:** Using default/example secret key in `tracker/config.ini`.

**Current State:**
```ini
# tracker/config.ini:595
secret_key = nvmYevpmN/Z72sllnR8mRPhtkbZmJPpgIDolZPGYHlY=
```

**Impact:**
- **Critical security vulnerability**
- Compromised ETag validation
- Compromised JWT validation
- Anyone with access to default can forge tokens

**Recommendation:**
```bash
# Generate unique secret key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Update config.ini with generated value
# tracker/config.ini
secret_key = <UNIQUE_GENERATED_VALUE_HERE>
```

**Reference:** [Best Practices - Security](roundup-development-practices.md#security-best-practices)

**Effort:** Immediate (5 minutes)

**Recommendation:** **CRITICAL - Do before any external access or production deployment**

---

### 🔴 Enable API Rate Limiting

**Issue:** No rate limiting configured for REST API.

**Current State:**
- No `api_failed_login_limit` configured
- Vulnerable to brute-force attacks

**Recommendation:**
```ini
# Add to tracker/config.ini [web] section
# Limit failed API login attempts
api_failed_login_limit = 5

# Lockout duration in seconds (5 minutes)
api_failed_login_delay = 300
```

**Reference:** [Best Practices - Brute-Force Protection](roundup-development-practices.md#brute-force-protection)

**Effort:** Immediate (2 minutes)

**Recommendation:** **CRITICAL - Add before any external API access**

---

### 🟡 Add Content Security Policy

**Issue:** No CSP headers configured.

**Impact:**
- Vulnerable to XSS attacks
- No defense-in-depth against injection

**Recommendation:**
```python
# Create tracker/extensions/security_headers.py
def add_security_headers(client):
    """Add security headers to all responses."""
    # Generate nonce for inline scripts
    nonce = client.db.security.nonce()

    # Content Security Policy
    csp = (
        f"default-src 'self'; "
        f"script-src 'self' 'nonce-{nonce}'; "
        f"style-src 'self' 'unsafe-inline'; "
        f"img-src 'self' data:; "
        f"connect-src 'self'"
    )
    client.additional_headers['Content-Security-Policy'] = csp

    # Other security headers
    client.additional_headers['X-Content-Type-Options'] = 'nosniff'
    client.additional_headers['X-Frame-Options'] = 'SAMEORIGIN'
    client.additional_headers['X-XSS-Protection'] = '1; mode=block'

# Register in tracker/extensions/__init__.py
def init(instance):
    instance.registerUtil('add_security_headers', add_security_headers)
```

**Reference:** [Best Practices - Content Security Policy](roundup-development-practices.md#content-security-policy)

**Effort:** Medium (2 hours) - Requires testing to ensure no breakage

**Recommendation:** Plan for Sprint 5+ security hardening

---

### 🟢 Add Spam Prevention Detector

**Issue:** No spam filtering for messages or issue creation.

**Recommendation:**
```python
# Create tracker/detectors/spam_filter.py
from roundup.exceptions import Reject

def reject_spam_messages(db, cl, nodeid, newdata):
    """Auditor: Block spam in messages."""
    if 'content' in newdata:
        content = newdata['content']

        # Check for excessive links
        link_count = content.count('http://') + content.count('https://')
        if link_count > 3:
            raise Reject("Too many links - possible spam")

        # Check for spam keywords (customize as needed)
        spam_keywords = ['viagra', 'casino', 'lottery', 'bitcoin wallet']
        content_lower = content.lower()
        for keyword in spam_keywords:
            if keyword in content_lower:
                raise Reject("Spam content detected")

def init(db):
    db.msg.audit('create', reject_spam_messages)
```

**Reference:** [Best Practices - Spam Prevention](roundup-development-practices.md#spam-prevention)

**Effort:** Low (1 hour)

**Recommendation:** Add if tracker becomes publicly accessible

---

## 5. Configuration Improvements

### 🟢 Enable Native Full-Text Search

**Issue:** No FTS indexer configured.

**Current State:**
```ini
# tracker/config.ini:137
indexer =
```

**Recommendation:**
```ini
# For production (PostgreSQL backend)
indexer = native-fts
indexer_language = english

# OR for development (SQLite)
# Requires SQLite with FTS5 support
indexer = native-fts
indexer_language = english
```

**Benefits:**
- Phrase searches
- Boolean operators
- Proximity queries
- Better performance than default indexer

**Reference:** [Best Practices - Full-Text Search](roundup-development-practices.md#configure-native-fts)

**Effort:** Low (5 minutes configuration + testing)

**Recommendation:** Consider for Sprint 5+ when search becomes critical

---

## 6. Code Organization

### 🟢 Create Shared Utilities Module

**Issue:** No shared module for reusable detector logic.

**Recommendation:**
```
tracker/
├── lib/                      # New directory
│   ├── __init__.py
│   ├── relationship_utils.py  # check_loop(), validation helpers
│   ├── notification_utils.py  # Email helpers
│   └── security_utils.py      # Spam detection, validation
└── detectors/
    ├── ci_auditor.py         # Uses lib.relationship_utils
    ├── ci_relationship_validator.py
    └── ...
```

**Benefits:**
- DRY (Don't Repeat Yourself)
- Easier testing of utility functions
- Better code organization
- Follows Python package conventions

**Effort:** Medium (2-3 hours) - Refactoring existing detectors

**Recommendation:** Consider for Sprint 6+ refactoring sprint

---

## 7. Testing Enhancements

### 🟡 Add Unit Tests for Circular Reference Detection

**Issue:** Complex detector logic not covered by unit tests.

**Recommendation:**
```python
# Create tests/test_ci_relationship_validator.py
import pytest
from roundup import instance

def test_circular_dependency_detection():
    """Test that circular dependencies are detected."""
    tracker = instance.open('tracker')
    db = tracker.open('admin')

    try:
        # Create CI types and statuses (prerequisites)
        ci_type = db.citype.lookup('Server')
        ci_status = db.cistatus.lookup('Active')
        rel_type = db.cirelationshiptype.lookup('Depends On')

        # Create three CIs
        ci1 = db.ci.create(name='CI-1', type=ci_type, status=ci_status)
        ci2 = db.ci.create(name='CI-2', type=ci_type, status=ci_status)
        ci3 = db.ci.create(name='CI-3', type=ci_type, status=ci_status)

        # Create chain: CI-1 → CI-2 → CI-3
        db.cirelationship.create(
            source_ci=ci1, target_ci=ci2, relationship_type=rel_type
        )
        db.cirelationship.create(
            source_ci=ci2, target_ci=ci3, relationship_type=rel_type
        )

        # Attempt to close the loop: CI-3 → CI-1 (should fail)
        with pytest.raises(ValueError, match="Circular dependency"):
            db.cirelationship.create(
                source_ci=ci3, target_ci=ci1, relationship_type=rel_type
            )

    finally:
        db.close()

def test_self_referencing_relationship():
    """Test that self-referencing relationships are rejected."""
    tracker = instance.open('tracker')
    db = tracker.open('admin')

    try:
        ci_type = db.citype.lookup('Server')
        ci_status = db.cistatus.lookup('Active')
        rel_type = db.cirelationshiptype.lookup('Depends On')

        ci1 = db.ci.create(name='CI-Self', type=ci_type, status=ci_status)

        # Attempt self-reference (should fail)
        with pytest.raises(ValueError, match="cannot have a relationship with itself"):
            db.cirelationship.create(
                source_ci=ci1, target_ci=ci1, relationship_type=rel_type
            )

    finally:
        db.close()
```

**Reference:** [Best Practices - Testing Detectors](roundup-development-practices.md#testing-detectors)

**Effort:** Medium (2-3 hours)

**Recommendation:** Add in Sprint 5 alongside other unit test expansion

---

### 🟡 Add BDD Scenarios for Circular Reference Prevention

**Issue:** No BDD coverage for circular dependency detection.

**Recommendation:**
```gherkin
# features/cmdb/ci_relationship_validation.feature
@cmdb @validation
Feature: CI Relationship Validation
  As a system administrator
  I want relationship validation to prevent circular dependencies
  So that the CMDB maintains data integrity

  Background:
    Given the Roundup server is running on "http://localhost:9080/pms"
    And I am logged in as "admin" with password "admin"
    And the following CIs exist:
      | name      | type   | status |
      | Server-A  | Server | Active |
      | Server-B  | Server | Active |
      | Server-C  | Server | Active |

  Scenario: Prevent circular dependency in three-node chain
    Given CI "Server-A" depends on CI "Server-B"
    And CI "Server-B" depends on CI "Server-C"
    When I attempt to create dependency from "Server-C" to "Server-A"
    Then I should see error "Circular dependency detected"
    And the relationship should not be created

  Scenario: Prevent self-referencing relationship
    When I attempt to create dependency from "Server-A" to "Server-A"
    Then I should see error "cannot have a relationship with itself"
    And the relationship should not be created

  Scenario: Allow valid relationship chain
    Given CI "Server-A" depends on CI "Server-B"
    When I create dependency from "Server-B" to "Server-C"
    Then the relationship should be created successfully
    And I should see "Server-B → Server-C" relationship
```

**Effort:** Medium (2 hours)

**Recommendation:** Add in Sprint 5 for comprehensive CMDB testing

---

## 8. Documentation

### 🟢 Add Inline Documentation for Complex Detectors

**Issue:** Detector logic could benefit from more detailed docstrings.

**Example Enhancement:**
```python
# tracker/detectors/ci_relationship_validator.py
def has_circular_dependency(db, source_ci, target_ci, visited=None):
    """
    Check if creating a relationship would create a circular dependency.

    This function performs a depth-first traversal of the CI dependency graph
    to detect cycles. It follows the chain of dependencies starting from the
    target_ci and checks if we eventually reach the source_ci.

    Example:
        If we have: CI-A → CI-B → CI-C
        And we attempt to add: CI-C → CI-A
        This would create: CI-A → CI-B → CI-C → CI-A (circular!)

    Args:
        db: Database instance
        source_ci: Source CI ID (the CI being depended on)
        target_ci: Target CI ID (the CI that depends on source)
        visited: Set of visited CI IDs for cycle detection (internal)

    Returns:
        bool: True if circular dependency detected, False otherwise

    Raises:
        None (returns boolean for caller to handle)
    """
    # ... implementation ...
```

**Effort:** Low (1 hour)

**Recommendation:** Add during Sprint 5 cleanup

---

## Implementation Priority

### Immediate (Before External Access)

1. 🔴 **Change default secret_key** - 5 minutes
2. 🔴 **Enable API rate limiting** - 2 minutes

### Sprint 5 (Reporting and Analytics)

1. 🟡 **Add label and order properties to schema** - 15 minutes
2. 🟡 **Add selective full-text indexing** - 30 minutes
3. 🟡 **Implement CI form conditional rendering** - 2-3 hours
4. 🟡 **Add unit tests for complex detectors** - 2-3 hours
5. 🟡 **Add BDD scenarios for validation** - 2 hours
6. 🟡 **Review CI index page performance** - 1 hour

### Sprint 6+ (Future Enhancements)

1. 🟢 **Consider parent-child CI hierarchy** - 2 hours
2. 🟢 **Add email notification reactors** - 2-3 hours
3. 🟢 **Add nosy list selective notifications** - 1 hour
4. 🟢 **Add Content Security Policy** - 2 hours
5. 🟢 **Add spam prevention** - 1 hour
6. 🟢 **Enable native FTS** - 30 minutes
7. 🟢 **Create shared utilities module** - 2-3 hours
8. 🟢 **Enhance inline documentation** - 1 hour
9. 🔵 **Refactor to canonical loop detection** - 1-2 hours (optional)

---

## Summary

**Total Critical Issues:** 2 (both security-related)
**Total High Priority:** 7 (performance and UX)
**Total Medium Priority:** 6 (code quality)
**Total Low Priority:** 2 (enhancements)

**Estimated Effort for Sprint 5 Priorities:** ~12-14 hours

---

## References

- [Roundup Development Best Practices](roundup-development-practices.md)
- [Roundup Wiki - CustomisationExamples](https://wiki.roundup-tracker.org/CustomisationExamples)
- [Roundup Official Documentation](https://www.roundup-tracker.org/docs.html)

---

**For questions or discussion, create an issue or bring to Sprint Planning.**
