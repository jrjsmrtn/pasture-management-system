# Roundup Development Best Practices

**Document Version:** 1.6
**Roundup Version:** 2.5.0
**Last Updated:** 2025-11-18
**Official Documentation:** https://www.roundup-tracker.org/docs.html
**Wiki Resources:** https://wiki.roundup-tracker.org

______________________________________________________________________

## Attribution

This document is a derivative compilation of best practices from:

**Primary Sources:**

- **Roundup Official Documentation** (https://www.roundup-tracker.org/docs.html)
  - Copyright © 2001-2025 Roundup-Team, Richard Jones, and contributors
  - Licensed under the MIT License
- **Roundup Community Wiki** (https://wiki.roundup-tracker.org)
  - Contributed by the Roundup community
  - Various contributors and examples

**About This Compilation:**
This document reorganizes, consolidates, and extends the official Roundup documentation and community wiki examples for use with the Pasture Management System's CMDB and ITIL workflow implementation. All original source materials are credited and referenced throughout.

**Roundup Project Credits:**

- Roundup Issue Tracker: https://roundup-tracker.org
- Project maintainers and contributors: https://www.roundup-tracker.org/docs/acknowledgements.html
- Original copyright holders: Roundup-Team (2009-2025), Richard Jones (2003-2009), eKit.com Inc (2002), Bizar Software Pty Ltd (2001)

______________________________________________________________________

## About This Document

This document provides comprehensive best practices for developing with Roundup Issue Tracker, specifically tailored for the Pasture Management System's CMDB and ITIL workflow implementation. It combines insights from official documentation and community wiki patterns.

## Table of Contents

- [Schema Development](#schema-development)
- [Detector Development](#detector-development)
- [Template Customization](#template-customization)
- [REST API Development](#rest-api-development)
- [Server Management](#server-management)
- [Testing Strategies](#testing-strategies)
- [Performance Optimization](#performance-optimization)

______________________________________________________________________

## Schema Development

**Reference:** [Roundup Reference Documentation](https://www.roundup-tracker.org/docs/reference.html)

### Property Types

Roundup provides several property types for schema definition:

| Type        | Use Case                          | Example                      |
| ----------- | --------------------------------- | ---------------------------- |
| `String`    | Text fields, names, descriptions  | `name=String(indexme='yes')` |
| `Link`      | Single reference to another class | `assignedto=Link("user")`    |
| `Multilink` | Multiple references               | `nosy=Multilink("user")`     |
| `Date`      | Timestamps                        | `created=Date()`             |
| `Interval`  | Time durations                    | `estimate=Interval()`        |
| `Number`    | Decimals                          | `priority=Number()`          |
| `Integer`   | Whole numbers                     | `order=Integer()`            |
| `Boolean`   | True/false flags                  | `is_active=Boolean()`        |
| `Password`  | Encrypted credentials             | `password=Password()`        |

### Relationship Patterns for CMDB

#### Parent-Child Hierarchies

Use bidirectional relationships with `rev_multilink` for automatic maintenance:

```python
ci = Class(db, "ci",
    # Forward reference to parent
    parent=Link("ci", rev_multilink="children"),

    # Read-only reverse multilink (auto-generated)
    # children=Multilink("ci")  # Don't define - created automatically
)
```

**Key Points:**

- The `rev_multilink` creates a read-only property on the linked class
- Setting `parent=3456` on ci1234 automatically adds "1234" to ci3456's `children`
- Eliminates manual synchronization of bidirectional relationships

#### Dependencies and Relationships

For CMDB CI relationships, use explicit multilinks:

```python
cirelationship = Class(db, "cirelationship",
    source_ci=Link("ci"),
    target_ci=Link("ci"),
    relationship_type=Link("cirelationshiptype"),
    description=String(),
)
```

**Best Practices:**

- Use junction/association classes for many-to-many with attributes
- Always validate both ends of relationships in detectors
- Consider cascade behavior when retiring related items
- Prevent circular references using loop detection (see below)

#### Preventing Circular References

**Reference:** [Roundup Wiki - LoopCheck](https://wiki.roundup-tracker.org/LoopCheck)

For CMDB relationships with hierarchies and dependencies, circular references can compromise data integrity. Use loop detection in auditors:

```python
from roundup.hyperdb import String, Link, Multilink
from roundup.exceptions import Reject

def check_loop(db, cl, nodeid, prop, attr, ids=None):
    """Recursively check for circular references in Link/Multilink properties."""
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
                # Circular reference detected!
                raise Reject("%s loop: %s" % (
                    prop, ','.join([cl.get(i, label) for i in ids])
                ))
            check_loop(db, cl, a, prop, cl.get(a, prop), ids)
            ids.pop()

# Usage in auditor
def validate_ci_relationships(db, cl, nodeid, newdata):
    """Prevent circular parent-child relationships."""
    if 'parent' in newdata:
        check_loop(db, cl, nodeid, 'parent', newdata['parent'])

# Register in init
def init(db):
    db.ci.audit('set', validate_ci_relationships)
    db.ci.audit('create', validate_ci_relationships)
```

**How It Works:**

- Maintains traversal path in `ids` list
- Recursively follows relationships
- Raises `Reject` exception when loop detected
- Critical for supervisor hierarchies, CI dependencies, issue superseder chains

**Example:** Prevents "CI-A depends on CI-B, which depends on CI-C, which depends on CI-A"

#### Querying Related Items

Access relationships through property navigation:

```python
# Single link
assignee = db.issue.get(itemid, 'assignedto')  # Returns user ID
user_name = db.user.get(assignee, 'username')  # Chain access

# Multilink
nosy_list = db.issue.get(itemid, 'nosy')  # Returns list of IDs
nosy_names = [db.user.get(uid, 'username') for uid in nosy_list]
```

### Schema Best Practices

1. **Use `setkey()` for unique identifiers:**

   ```python
   ci.setkey("name")  # Makes name unique and usable for lookups
   ```

1. **Set display labels with `setlabelprop()`:**

   ```python
   ci.setlabelprop("name")  # Used in dropdowns and lists
   ```

1. **Define sort order with `setorderprop()`:**

   ```python
   ci.setorderprop("name")  # Default sort order
   ```

   **Warning:** ALL items must have a value for the order property, or sorting becomes random.

1. **Index for search performance:**

   ```python
   description=String(indexme='yes')  # Enable full-text search
   ```

   Use selectively - don't index every String property.

1. **Schema changes auto-apply:**

   - Modifications to `schema.py` are automatically applied on next tracker access
   - No manual migration scripts needed for schema additions
   - **Server restart required** to load new schema definitions

### Advanced Schema Patterns

#### Mixin Classes for Code Reuse

**Reference:** [Roundup Wiki - MixinClassFileClass](https://wiki.roundup-tracker.org/MixinClassFileClass)

Use the interceptor pattern to add cross-cutting functionality (compression, deduplication, encryption) to multiple classes:

```python
# In tracker/lib/interceptor.py
from roundup.hyperdb import FileClass
import gzip

class GzipFileClass:
    """Mixin to add compression to FileClass."""

    def set(self, nodeid, **propvalues):
        # Compress content before storing
        if 'content' in propvalues:
            content = propvalues['content']
            propvalues['content'] = gzip.compress(content.encode())
        return super().set(nodeid, **propvalues)

    def get(self, nodeid, propname):
        # Decompress when reading
        value = super().get(nodeid, propname)
        if propname == 'content' and value:
            return gzip.decompress(value).decode()
        return value

def interceptor_factory(classname, *bases):
    """Factory to create mixed-in classes."""
    return type(classname, bases, {})

# In schema.py
from lib.interceptor import interceptor_factory, GzipFileClass
from roundup.hyperdb import FileClass

# Create compressed file class
MessageFileClass = interceptor_factory('MessageFileClass',
                                       GzipFileClass, FileClass)

# Use in schema
msg = Class(db, "msg",
    files=Multilink("MessageFileClass"),
    # ... other properties
)
```

**Benefits:**

- Reduces storage overhead for text-heavy content
- Reusable across multiple class definitions
- No modification to core Roundup classes
- Compatible with all database backends
- Files remain readable with standard tools (e.g., `zcat`)

**Use Cases:**

- Compression for messages, files, descriptions
- Deduplication to prevent duplicate file storage
- Encryption for sensitive data
- Checksum validation for file integrity

#### Bidirectional Linking Extension

**Reference:** [Roundup Wiki - ReverseLinkEdit](https://wiki.roundup-tracker.org/ReverseLinkEdit)

While `rev_multilink` provides automatic read-only reverse links, the ReverseLinkEdit extension allows **manual bidirectional editing** through web interface:

**Syntax in web forms:**

- `(3)` or `(+3)`: Add item 3 to target's multilink
- `(-7)`: Remove item 7 from target's multilink
- `1 2`: Direct links unchanged

**Example:** Editing issue5's superseder field with `1 2 (3) (4) (-7)`:

- Issue5 supersedes: 1, 2
- Issue3 and 4 get 5 added to their superseder
- Issue7 has 5 removed from its superseder

**Implementation:**

- Requires custom `Edit2Action` class in `extensions/`
- Overrides standard `EditItemAction`
- Parses parenthetical notation
- Generates reverse link operations

**Limitations:**

- Only works for editing existing items (not creation)
- Requires edit permissions on all affected items
- Assumes numeric identifiers

______________________________________________________________________

## Detector Development

**Reference:** [Roundup Customization Guide - Detectors](https://www.roundup-tracker.org/docs/customizing.html)

### Auditor vs Reactor Patterns

Roundup provides two detector types:

#### Auditors (Pre-Change Validation)

**Signature:** `audit(db, cl, itemid, newdata)`

- Execute **before** database changes
- Can **veto** operations by raising exceptions
- Used for validation, permission checks, and data normalization

**Example - CI Validation:**

```python
def validate_ci_data(db, cl, nodeid, newdata):
    """Auditor: Validate CI data before creation/modification."""

    # Validate required fields
    if nodeid is None and 'name' not in newdata:
        raise ValueError("CI name is required")

    # Validate name uniqueness
    name = newdata.get('name')
    if name:
        existing = db.ci.filter(None, {'name': name})
        if existing and (nodeid is None or nodeid not in existing):
            raise ValueError(f"CI with name '{name}' already exists")

    # Validate relationships
    if 'ci_type' in newdata and not newdata['ci_type']:
        raise ValueError("CI type is required")

# Register auditor
def init(db):
    db.ci.audit('create', validate_ci_data)
    db.ci.audit('set', validate_ci_data)
```

#### Reactors (Post-Change Automation)

**Signature:** `react(db, cl, itemid, olddata)`

- Execute **after** database changes complete
- Cannot veto operations (changes already committed)
- Used for cascading updates, notifications, logging

**Example - Relationship Management:**

```python
def update_related_cis(db, cl, nodeid, olddata):
    """Reactor: Update related CIs when relationship changes."""

    # Get new relationship data
    rel_type = db.cirelationship.get(nodeid, 'relationship_type')
    source = db.cirelationship.get(nodeid, 'source_ci')
    target = db.cirelationship.get(nodeid, 'target_ci')

    # Update last_modified on related CIs
    from time import time
    now = time()
    db.ci.set(source, last_modified=Date(now))
    db.ci.set(target, last_modified=Date(now))

# Register reactor
def init(db):
    db.cirelationship.react('create', update_related_cis)
    db.cirelationship.react('set', update_related_cis)
```

### Error Handling Patterns

**Rejection with user-friendly messages:**

```python
from roundup.exceptions import Reject

def check_permissions(db, cl, nodeid, newdata):
    if not db.security.hasPermission('Edit', db.getuid(), cl.classname, 'status'):
        raise Reject("You don't have permission to change status")
```

**Validation errors:**

```python
from roundup.exceptions import Reject

def validate_state_transition(db, cl, nodeid, newdata):
    if 'status' in newdata:
        old_status = db.issue.get(nodeid, 'status')
        new_status = newdata['status']

        if not is_valid_transition(old_status, new_status):
            # BEST PRACTICE: Use Reject instead of ValueError
            # - Provides better transaction rollback
            # - Works properly with custom action handlers
            # - Better error message handling in web UI
            raise Reject(f"Invalid status transition from {old_status} to {new_status}")
```

**IMPORTANT: Reject vs ValueError**

**Pattern Discovered** (Sprint 5, 2025-11-17):

Always use `Reject` exception in auditor detectors, not `ValueError`:

```python
from roundup.exceptions import Reject

# ❌ AVOID - ValueError
def audit_ci(db, cl, nodeid, newvalues):
    if not newvalues.get("name"):
        raise ValueError("Name is required")  # Works via CLI, poor web UI UX

# ✅ PREFER - Reject
def audit_ci(db, cl, nodeid, newvalues):
    if not newvalues.get("name"):
        raise Reject("Name is required")  # Works everywhere, better UX
```

**Why Reject is Better**:

1. **Proper Transaction Handling**: Ensures clean rollback on validation failure
1. **Web UI Integration**: Works with Roundup's error message system
1. **Custom Action Support**: Required for custom action handlers to catch errors properly
1. **Consistent Behavior**: Same behavior across CLI, web UI, and API
1. **Better Error Messages**: Roundup handles `Reject` exceptions specially for user display

**When to Use Each**:

- `Reject` - All validation failures in auditors (✅ **preferred**)
- `ValueError` - Internal logic errors, not user-facing validation (rare)
- `Unauthorized` - Permission/security violations

**Unauthorized actions:**

```python
from roundup import security

def restrict_field_changes(db, cl, nodeid, newdata):
    if 'priority' in newdata and db.getuid() != '1':  # Not admin
        raise security.Unauthorized("Only administrators can change priority")
```

### Detector Best Practices

1. **Execution Priority:**

   ```python
   # Higher priority (110) runs after default priority (100)
   db.issue.audit('set', my_auditor, 110)
   ```

   Use when one detector depends on another's modifications.

1. **Performance Considerations:**

   - **Avoid user enumeration:** Don't loop through all users in detectors
   - **Batch operations:** Group multiple updates to reduce overhead
   - **Cache lookups:** Store repeated `db.class.get()` calls in variables

   **Bad:**

   ```python
   # Performance bottleneck - loops through ALL users
   for userid in db.user.list():
       if keyword in db.user.get(userid, 'interests'):
           nosy.append(userid)
   ```

   **Good:**

   ```python
   # Query only relevant users
   users_with_interest = db.user.filter(None, {'interests': keyword})
   nosy.extend(users_with_interest)
   ```

1. **Transaction Safety:**

   - Auditors run within the same transaction as the triggering change
   - If an auditor raises an exception, all changes are rolled back
   - Reactors run after transaction commit (changes already saved)

1. **Testing Detectors:**

   - **Server restart required** after detector changes
   - Test both success and failure paths
   - Use BDD scenarios to validate detector behavior
   - Check transaction rollback on auditor rejections

1. **Common Use Cases:**

   - **Validation:** Required fields, state transitions, data format
   - **Automation:** Auto-assign, nosy list management, status cascades
   - **Security:** Permission enforcement, field-level restrictions
   - **Integration:** External system notifications, logging, auditing

### Email Notification Patterns

**Reference:** [Roundup Wiki - NewIssueCopy](https://wiki.roundup-tracker.org/NewIssueCopy)

Reactors can send email notifications to specific recipients or teams:

```python
from roundup.exceptions import DetectorError
from roundup import roundupdb

def newissuecopy(db, cl, nodeid, oldvalues):
    """Reactor: Send notification when new issue is created."""
    try:
        # Generate creation note
        change_note = cl.generateCreateNote(nodeid)

        # Send to specific recipients (must be a list!)
        recipients = ['team@example.com', 'admin@example.com']

        # Iterate through messages and send
        for msgid in cl.get(nodeid, 'messages'):
            cl.send_message(nodeid, msgid, change_note, recipients)

    except roundupdb.MessageSendError as e:
        # Re-raise as DetectorError for proper handling
        raise DetectorError(str(e))

# Register reactor
def init(db):
    db.issue.react('create', newissuecopy)
```

**Key Points:**

- Recipients parameter **must be a list** (even for single recipient)
- Use `generateCreateNote()` for creation notifications
- Catch `MessageSendError` and re-raise as `DetectorError`
- Consider team addresses instead of individual users to reduce duplicates
- Email configuration must be set in tracker config.ini

### Nosy List Management

**Reference:** [Roundup Wiki - NosyMessagesAllTheTime](https://wiki.roundup-tracker.org/NosyMessagesAllTheTime)

Implement selective notifications based on field changes:

```python
def selective_nosy_notification(db, cl, nodeid, oldvalues):
    """Only notify nosy list when non-silent fields change."""

    # Define fields that don't trigger notifications
    silent_fields = ['nosy', 'activity', 'last_viewed']

    # Check if any non-silent field changed
    significant_change = False
    for field in oldvalues.keys():
        if field not in silent_fields:
            significant_change = True
            break

    # Require message for certain field changes
    if 'assignedto' in oldvalues:
        messages = cl.get(nodeid, 'messages')
        if not messages or len(messages) == len(oldvalues.get('messages', [])):
            raise ValueError("Changing assigned_to requires a message")

    # Send notification only for significant changes
    if significant_change:
        # Standard nosy notification will trigger
        pass

# Register auditor for validation
def init(db):
    db.issue.audit('set', selective_nosy_notification)
```

**Best Practices:**

- Define silent field lists to prevent notification fatigue
- Require messages for critical field changes (status, assignedto)
- Allow users to modify their own nosy status without notifications
- Use conditional logic to balance communication vs. noise
- Audit trail maintained through hyperdatabase journal

### Automated Issue Creation

**Reference:** [Roundup Wiki - AutomatedIssues](https://wiki.roundup-tracker.org/AutomatedIssues)

Programmatically create issues using Python API:

```python
from roundup import instance

# Open tracker
tracker = instance.open('/path/to/tracker')
db = tracker.open('admin')  # Use appropriate username

try:
    # Create issue
    issue_id = db.issue.create(
        title="Automated issue",
        status=db.status.lookup('open'),
        priority=db.priority.lookup('normal'),
        assignedto=db.user.lookup('admin'),
        nosy=[db.user.lookup('admin')]
    )

    # Commit changes
    db.commit()

    print(f"Created issue {issue_id}")

finally:
    db.close()
```

**Use Cases:**

- Automated monitoring alerts
- Batch issue creation from external systems
- Integration with CI/CD pipelines
- Scheduled maintenance task creation

**Configuration:**

- Set `TRACKERHOME` environment variable
- Authenticate with valid `USER` and `USERID`
- Use `db.commit()` to save changes
- Always close database connection with `db.close()`

______________________________________________________________________

## Template Customization

**Reference:** [Roundup Customization Guide - Templates](https://www.roundup-tracker.org/docs/customizing.html)

**Note on Jinja2:** Roundup 1.5.0+ includes **experimental support** for Jinja2 templating as an alternative to TAL. The `jinja2` template is a responsive Bootstrap-based implementation with SimpleMDE markdown support. To create a Jinja2-based tracker: `python demo.py -t jinja2 nuke`. See [Roundup Wiki - Jinja2](https://wiki.roundup-tracker.org/Jinja2) for details. This document focuses on TAL, which remains the standard and well-documented approach.

### PageTemplate (TAL) Syntax

Roundup uses TAL (Template Attribute Language) for dynamic HTML generation.

#### Core TAL Patterns

| Pattern          | Purpose                  | Example                                              |
| ---------------- | ------------------------ | ---------------------------------------------------- |
| `tal:content`    | Replace element content  | `<td tal:content="i/name">placeholder</td>`          |
| `tal:condition`  | Conditional rendering    | `<div tal:condition="context/is_active">...</div>`   |
| `tal:repeat`     | Loop through collections | `<tr tal:repeat="i batch">...</tr>`                  |
| `tal:attributes` | Dynamic attributes       | `<a tal:attributes="href string:ci${i/id}">Link</a>` |
| `tal:replace`    | Replace entire element   | `<span tal:replace="i/priority">-</span>`            |
| `tal:define`     | Define variables         | `<div tal:define="urgent python:i.priority > 5">`    |

#### String Interpolation

```html
<!-- Simple string construction -->
<a tal:attributes="href string:/ci${i/id}">View CI</a>

<!-- Python expressions -->
<td tal:content="python:len(i.nosy)">0</td>

<!-- Format dates -->
<td tal:content="python:i.created.pretty('%Y-%m-%d')">date</td>
```

### Template Variables and Utilities

#### Standard Context Variables

| Variable  | Description                       | Usage                                          |
| --------- | --------------------------------- | ---------------------------------------------- |
| `context` | Current item being displayed      | `context/name`, `context/description`          |
| `request` | HTTP request with user, form data | `request/user/username`, `request/form/status` |
| `db`      | Database access for lookups       | `python:db.ci.get(id, 'name')`                 |
| `utils`   | Registered utility functions      | `python:utils.anti_csrf_nonce()`               |
| `batch`   | Paginated result set              | For index/list templates                       |

#### Form Field Generation

```html
<!-- Input field for editing -->
<input tal:replace="structure context/name/field" />

<!-- Dropdown menu -->
<select tal:replace="structure context/status/menu" />

<!-- Customize field rendering -->
<input tal:replace="structure python:context.due_date.field(display_time=False)" />

<!-- Multilink with checkboxes -->
<div tal:replace="structure python:context.nosy.menu(display='checklist')" />
```

#### TAL Path Expressions for Relationships

**Pattern Discovered** (Sprint 5, 2025-11-17):

Use TAL path expressions instead of Python database calls for traversing relationships:

```html
<!-- ❌ AVOID - Python database calls in templates -->
<tal:block tal:repeat="rel python:db._db.getnode('ci', context.id).get('relationships', [])">
  <td tal:content="python:db.cirelationship.get(rel, 'name')">Name</td>
  <!-- Causes AttributeError: getnode and type errors -->
</tal:block>

<!-- ✅ PREFER - TAL path expressions -->
<tal:block tal:repeat="rel context/relationships">
  <td tal:content="rel/relationship_type/name">Type</td>
  <td tal:content="rel/target_ci/name">Target</td>
  <td tal:content="rel/target_ci/status/name">Status</td>
</tal:block>
```

**Why TAL Path Expressions are Better**:

1. **Automatic Relationship Traversal**: TAL handles Roundup's internal wrapping automatically
1. **Cleaner Templates**: No Python code in templates (better separation of concerns)
1. **Better Error Handling**: TAL provides clear errors for missing properties
1. **More Maintainable**: Simpler syntax, easier to read and debug
1. **Performance**: TAL optimizer can cache path lookups

**Path Expression Syntax**:

| Pattern                     | Description                        | Example                             |
| --------------------------- | ---------------------------------- | ----------------------------------- |
| `object/property`           | Access property                    | `context/name`                      |
| `object/link/property`      | Traverse Link                      | `context/owner/username`            |
| `object/link/link/property` | Multi-level traversal              | `context/issue/assignedto/realname` |
| `object/multilink`          | Access Multilink (returns list)    | `context/relationships`             |
| `item/link/property`        | In repeat, traverse from each item | `rel/target_ci/name`                |

**Complex Example - Bidirectional Relationships**:

```html
<!-- Display outgoing relationships (this CI → others) -->
<h3>Dependencies</h3>
<table>
  <tr tal:repeat="rel context/outgoing_relationships">
    <td tal:content="rel/relationship_type/name">Relationship</td>
    <td>
      <a tal:attributes="href string:ci${rel/target_ci/id}"
         tal:content="rel/target_ci/name">Target CI</a>
    </td>
    <td tal:content="rel/target_ci/status/name">Status</td>
  </tr>
</table>

<!-- Display incoming relationships (others → this CI) -->
<h3>Referenced By</h3>
<table>
  <tr tal:repeat="rel context/incoming_relationships">
    <td tal:content="rel/relationship_type/name">Relationship</td>
    <td>
      <a tal:attributes="href string:ci${rel/source_ci/id}"
         tal:content="rel/source_ci/name">Source CI</a>
    </td>
    <td tal:content="rel/source_ci/criticality/name">Criticality</td>
  </tr>
</table>
```

**Best Practices**:

- ✅ Use TAL path expressions for all relationship traversals
- ✅ Avoid `python:` expressions unless complex logic required
- ✅ Use `python:` only for calculations, not database access
- ✅ Keep templates declarative, not imperative

### Form Handling and Validation

#### Required Fields

```html
<input type="hidden" name="@required" value="name,ci_type" />
```

#### Anti-CSRF Protection

```html
<input name="@csrf" type="hidden"
       tal:attributes="value python:utils.anti_csrf_nonce()" />
```

#### Hidden Control Fields

| Field            | Purpose                 | Example                                                  |
| ---------------- | ----------------------- | -------------------------------------------------------- |
| `@action`        | Server action           | `<input type="hidden" name="@action" value="new">`       |
| `@template`      | Next template to render | `<input type="hidden" name="@template" value="ci.item">` |
| `@link@property` | Link new item to parent | `<input type="hidden" name="@link@issue" value="123">`   |
| `@required`      | Required fields         | `<input type="hidden" name="@required" value="name">`    |

### Multi-Step Workflows

Create wizard-style interfaces:

```html
<!-- Step 1: Select CI Type -->
<form action="ci" method="POST">
  <input type="hidden" name="@action" value="new" />
  <input type="hidden" name="@template" value="ci.item.step2" />

  <select name="ci_type" tal:replace="structure context/ci_type/menu" />
  <input type="submit" value="Next" />
</form>

<!-- Step 2: Enter Details (ci.item.step2.html) -->
<form action="ci" method="POST">
  <input type="hidden" name="@action" value="create" />
  <input type="hidden" name="ci_type"
         tal:attributes="value request/form/ci_type" />

  <!-- Show fields based on ci_type -->
  <div tal:condition="python:request.form.get('ci_type') == 'server'">
    <!-- Server-specific fields -->
  </div>

  <input type="submit" value="Create CI" />
</form>
```

### Template Inheritance and Reuse

#### METAL Macros

```html
<!-- Define macro in macros.html -->
<div metal:define-macro="page_header">
  <h1 tal:content="context/title">Page Title</h1>
</div>

<!-- Use macro in another template -->
<div metal:use-macro="container/templates/macros/page_header">
  <!-- This content will be replaced -->
</div>
```

#### Slots for Customization

```html
<!-- Base template with slot -->
<html metal:define-macro="page">
  <head>
    <title metal:define-slot="title">Default Title</title>
  </head>
  <body>
    <div metal:define-slot="content">Default content</div>
  </body>
</html>

<!-- Child template filling slots -->
<html metal:use-macro="container/templates/page/macros/page">
  <title metal:fill-slot="title">CI Details</title>
  <div metal:fill-slot="content">
    <!-- Custom content here -->
  </div>
</html>
```

### Template Debugging

1. **HTML Comments for Identification:**

   ```html
   <!-- ci.item.html - CI Details Page -->
   ```

1. **TAL Error Messages:**

   - Display in browser with file and line number
   - Check syntax on first page load
   - Server restart needed for persistent servers

1. **Debugging Variables:**

   ```html
   <!-- Show all context properties -->
   <pre tal:content="python:dir(context)">properties</pre>

   <!-- Show request form data -->
   <pre tal:content="python:request.form">form</pre>
   ```

### Template Performance Best Practices

1. **Use Conditions to Avoid Unnecessary Rendering:**

   ```html
   <!-- Bad: Renders empty table -->
   <table>
     <tr tal:repeat="i batch">
       <td tal:content="i/name">name</td>
     </tr>
   </table>

   <!-- Good: Only renders if items exist -->
   <table tal:condition="batch">
     <tr tal:repeat="i batch">
       <td tal:content="i/name">name</td>
     </tr>
   </table>
   ```

1. **Cache Repeated Lookups:**

   ```html
   <!-- Bad: Multiple database lookups -->
   <td tal:content="python:db.user.get(i.assignedto, 'username')">user</td>
   <td tal:content="python:db.user.get(i.assignedto, 'email')">email</td>

   <!-- Good: Define variable once -->
   <tr tal:define="assignee python:db.user.getnode(i.assignedto)">
     <td tal:content="assignee/username">user</td>
     <td tal:content="assignee/email">email</td>
   </tr>
   ```

1. **Limit Loop Iterations:**

   - Use batching for large result sets
   - Implement pagination for index templates
   - Consider lazy loading for related items

1. **Server Restart for Template Changes:**

   - Template changes are **cached** by server
   - **Restart server** to see template updates
   - Use `roundup-server` restart sequence (see [Server Management](#server-management))

______________________________________________________________________

## Custom Action Handlers

**Pattern Discovered** (Sprint 5, 2025-11-17):

Custom action handlers solve a critical limitation in Roundup's web UI error handling: by default, validation errors from auditor detectors are not properly displayed to users in the web interface.

### The Problem

Roundup's default `NewItemAction.handle()` method:

1. Catches `Reject` exceptions from auditors
1. Calls `add_error_message()` to store the error
1. **Returns immediately** without rendering a page
1. Error messages are request-scoped and lost

**Result**: Users see blank pages or redirects without error feedback.

### The Solution: Custom Action Handler

Extend `NewItemAction` to catch `Reject` exceptions and redirect with error messages in the URL.

#### Implementation Pattern

**File**: `tracker/extensions/cirelationship_actions.py`

```python
# SPDX-FileCopyrightText: 2025 Your Name <your@email.com>
# SPDX-License-Identifier: MIT

"""Custom actions for proper error handling in web UI forms."""

import logging

try:
    import urllib.parse as urllib_
except ImportError:
    import urllib as urllib_  # Python 2 compatibility

from roundup.cgi import exceptions
from roundup.cgi.actions import NewItemAction
from roundup.exceptions import Reject

logger = logging.getLogger(__name__)


class CIRelationshipNewAction(NewItemAction):
    """Custom new item action that handles validation errors properly."""

    def handle(self):
        """Create new item with proper error display on validation failure."""

        # Ensure modification comes via POST
        if self.client.env["REQUEST_METHOD"] != "POST":
            raise Reject(self._("Invalid request"))

        # Parse props from form
        try:
            props, links = self.client.parsePropsFromForm(create=1)
        except (ValueError, KeyError) as message:
            self.client.add_error_message(self._("Error: %s") % str(message))
            return

        # Handle the props - this is where auditors run
        try:
            messages = self._editnodes(props, links)
        except (ValueError, KeyError, IndexError, Reject) as message:
            error_msg = str(message)
            logger.warning(f"Item creation failed: {error_msg}")

            # Get source_ci to redirect back to the right page
            source_ci = props.get(("cirelationship", None), {}).get("source_ci")
            if source_ci:
                # Redirect back to source CI with error message in URL
                url = f"{self.base}ci{source_ci}?@error_message={urllib_.quote(error_msg)}"
            else:
                # Fallback: redirect to class list
                url = f"{self.base}{self.classname}?@error_message={urllib_.quote(error_msg)}"

            # Redirect with error message
            raise exceptions.Redirect(url)

        # Commit transaction
        self.db.commit()

        # Redirect to success page
        if "__redirect_to" in self.form:
            redirect_url = self.examine_url(self.form["__redirect_to"].value)
            raise exceptions.Redirect(
                f"{redirect_url}&@ok_message={urllib_.quote(messages)}"
            )

        # Default: redirect to new item's page
        raise exceptions.Redirect(
            f"{self.base}{self.classname}{self.nodeid}"
            f"?@ok_message={urllib_.quote(messages)}"
            f"&@template={urllib_.quote(self.template)}"
        )


def init(instance):
    """Register custom actions with the tracker."""
    instance.registerAction("cirelationship_new", CIRelationshipNewAction)
```

#### Template Integration

Update your form template to use the custom action:

```html
<!-- tracker/html/cirelationship.item.html -->
<form method="POST" enctype="multipart/form-data"
      tal:attributes="action context/designator">

  <!-- Use custom action instead of default "new" -->
  <input type="hidden" name="@action" value="cirelationship_new" />

  <!-- Rest of form fields -->
  <input type="hidden" name="source_ci" tal:attributes="value request/form/source_ci" />
  <select name="relationship_type" tal:replace="structure context/relationship_type/menu" />
  <select name="target_ci" tal:replace="structure context/target_ci/menu" />

  <input type="submit" value="Create Relationship" />
</form>
```

#### Display Error Messages

In your target template (e.g., `ci.item.html`), display the error message:

```html
<!-- Display error message if present -->
<div class="error" tal:condition="request/form/@error_message"
     tal:content="request/form/@error_message">
  Error message here
</div>

<!-- Display success message if present -->
<div class="ok-message" tal:condition="request/form/@ok_message"
     tal:content="request/form/@ok_message">
  Success message here
</div>
```

### Pattern Benefits

1. **Better UX**: Users see clear error messages
1. **Proper Error Handling**: Works with `Reject` exceptions from auditors
1. **Flexible**: Can redirect to different pages based on context
1. **Logging**: Structured logging for debugging
1. **Python 2/3 Compatible**: Handles urllib differences

### When to Use Custom Actions

Use custom action handlers when:

- ✅ Form has complex validation via auditor detectors
- ✅ Need to show validation errors to users
- ✅ Want to redirect to specific pages on error
- ✅ Need structured logging for form submissions
- ✅ Have multi-step workflows requiring error handling

**Standard Actions Work For**:

- Simple forms without complex validation
- Forms where default error handling is acceptable
- CLI/API operations (errors display correctly)

### Registration

Custom actions must be registered in `tracker/extensions/__init__.py`:

```python
def init(db):
    """Initialize all extensions."""

    # Import custom action modules
    from extensions import cirelationship_actions

    # Register custom actions
    cirelationship_actions.init(db.instance)

    # ... other initialization ...
```

### Advanced Pattern: Generic Error Handler

Create a reusable base class for all custom actions:

```python
class ImprovedNewItemAction(NewItemAction):
    """Base class for new item actions with improved error handling."""

    def get_error_redirect_url(self, props, error_msg):
        """Override this to customize error redirect behavior."""
        # Default: redirect to class list with error
        return f"{self.base}{self.classname}?@error_message={urllib_.quote(error_msg)}"

    def handle(self):
        """Handle with improved error display."""
        # ... standard POST check ...

        try:
            props, links = self.client.parsePropsFromForm(create=1)
        except (ValueError, KeyError) as message:
            self.client.add_error_message(self._("Error: %s") % str(message))
            return

        try:
            messages = self._editnodes(props, links)
        except (ValueError, KeyError, IndexError, Reject) as message:
            error_msg = str(message)
            logger.warning(f"{self.classname} creation failed: {error_msg}")

            # Get custom redirect URL
            url = self.get_error_redirect_url(props, error_msg)
            raise exceptions.Redirect(url)

        # ... commit and success redirect ...


class CIRelationshipNewAction(ImprovedNewItemAction):
    """CI Relationship specific action."""

    def get_error_redirect_url(self, props, error_msg):
        """Redirect to source CI on error."""
        source_ci = props.get(("cirelationship", None), {}).get("source_ci")
        if source_ci:
            return f"{self.base}ci{source_ci}?@error_message={urllib_.quote(error_msg)}"
        return super().get_error_redirect_url(props, error_msg)
```

### Debugging Custom Actions

Add logging to troubleshoot custom action behavior:

```python
import logging

logger = logging.getLogger(__name__)

class DebugNewAction(NewItemAction):
    def handle(self):
        logger.info(f"Action called: {self.classname}, Method: {self.client.env['REQUEST_METHOD']}")
        logger.debug(f"Form data: {dict(self.form)}")

        try:
            result = super().handle()
            logger.info(f"Action succeeded: {self.classname}{self.nodeid}")
            return result
        except Exception as e:
            logger.error(f"Action failed: {e}", exc_info=True)
            raise
```

### References

- **Investigation Documentation**: `docs/reference/roundup-error-handling-web-ui.md`
- **Roundup Actions Source**: `roundup/cgi/actions.py`
- **Roundup Client Source**: `roundup/cgi/client.py`

### Python Template Helpers

**Pattern Discovered** (Sprint 6, 2025-11-18):

Python functions registered as template utilities can help reduce TAL complexity, but they require careful handling of Roundup's HTMLItem objects.

#### Registering Custom Utilities

**File Location**: `tracker/extensions/template_helpers.py`

```python
def init(instance):
    """Register template helper functions."""
    instance.registerUtil("sort_ci_ids", sort_ci_ids)
    instance.registerUtil("filter_ci_ids_by_search", filter_ci_ids_by_search)
```

**Usage in Templates**:

```html
<tal:block tal:define="
   all_ci_ids python:db.ci.filter(None, filterspec);
   ci_ids python:utils.filter_ci_ids_by_search(db, all_ci_ids, search_val);
   sorted_ids python:utils.sort_ci_ids(db, ci_ids, sort_val);">
  <!-- Now use sorted_ids in repeat -->
</tal:block>
```

#### HTMLItem Objects - Critical Understanding

**What You Receive**: When TAL passes objects to Python helper functions, they are **HTMLItem wrappers**, not raw database nodes.

**Key Discovery** (2025-11-18, Sprint 6):

```python
# ❌ WRONG - db.ci.getnode() does NOT exist in TAL template context!
def filter_ci_ids_by_search(db, ci_ids, search_term):
    for ci_id in ci_ids:
        id_str = str(ci_id.id)
        node = db.ci.getnode(id_str)  # AttributeError: 'getnode'
        name = node.name
```

**Root Cause**: In TAL template context, `db` is not a full database instance - it's a template-safe wrapper. The `getnode()` method is not available.

**Solution**: Access fields directly from HTMLItem objects:

```python
# ✅ CORRECT - Access fields directly from HTMLItem
def filter_ci_ids_by_search(db, ci_ids, search_term):
    """Filter CI IDs by search term (name or location)."""
    if not search_term:
        return list(ci_ids)

    search_lower = search_term.lower()
    result = []

    for ci_id in ci_ids:
        try:
            # ci_id is already an HTMLItem object with the CI data
            # Access fields directly using .plain() for string extraction
            name = ""
            if hasattr(ci_id, 'name') and ci_id.name:
                if hasattr(ci_id.name, 'plain'):
                    name = ci_id.name.plain()
                else:
                    name = str(ci_id.name)
            name = name.lower()

            location = ""
            if hasattr(ci_id, 'location') and ci_id.location:
                if hasattr(ci_id.location, 'plain'):
                    location = ci_id.location.plain()
                else:
                    location = str(ci_id.location)
            location = location.lower()

            if search_lower in name or search_lower in location:
                result.append(ci_id)
        except (AttributeError, KeyError, Exception):
            # Skip CIs we can't access or have errors
            continue

    return result
```

#### The .plain() Method

**When to Use**: Roundup field objects (String, Link, etc.) are not plain Python strings. Use `.plain()` to extract string values.

```python
# Field object types and their .plain() usage
ci_id.name.plain()           # String field → string
ci_id.type.plain()           # Link field → ID string
ci_id.status.name.plain()    # Link traversal → string
```

**Safe Pattern with Defensive Checks**:

```python
# Defensive field access pattern
value = ""
if hasattr(obj, 'field_name') and obj.field_name:
    if hasattr(obj.field_name, 'plain'):
        value = obj.field_name.plain()
    else:
        value = str(obj.field_name)
```

#### Best Practices for Template Helpers

1. **Never assume database methods exist**: `db` in template context is limited
1. **Access HTMLItem fields directly**: Use `obj.field.plain()` instead of `db.class.getnode()`
1. **Use defensive checks**: Check `hasattr()` before accessing fields
1. **Handle the .plain() method**: Not all fields have it, provide fallback to `str()`
1. **Preserve input types**: Return same type as input (HTMLItem list → HTMLItem list)
1. **Silent error handling**: Template helpers should never raise exceptions - skip problem items instead

**Why This Matters**:

- Avoids `AttributeError: 'getnode'` failures
- Maintains compatibility with TAL template context restrictions
- Provides robust error handling for missing/null fields
- Keeps templates clean by moving complex logic to Python

**Implementation Example**: See `tracker/extensions/template_helpers.py` for complete working examples.

______________________________________________________________________

## REST API Development

**Reference:** [Roundup REST API Documentation](https://www.roundup-tracker.org/docs/rest.html)

### Authentication

#### Basic HTTP Authentication

```python
import requests
from requests.auth import HTTPBasicAuth

response = requests.get(
    'http://localhost:9080/pms/rest/data/ci',
    auth=HTTPBasicAuth('admin', 'admin')
)
```

#### JSON Web Tokens (JWT)

For third-party integrations without sharing credentials:

1. Generate JWT with appropriate role-based permissions
1. Configure `secret_key` in `config.ini`
1. Use JWT in `Authorization` header

**Requirements:**

- User must have "Rest Access" permission
- `secret_key` configured for proper ETag generation
- Rate limiting configurable via `api_failed_login_limit`

### CRUD Operations

#### Create (POST)

```python
import requests

# Create new CI
new_ci = {
    "name": "web-server-01",
    "ci_type": "1",  # Server type
    "description": "Production web server",
    "is_active": True
}

response = requests.post(
    'http://localhost:9080/pms/rest/data/ci',
    json=new_ci,
    auth=HTTPBasicAuth('admin', 'admin'),
    headers={'X-Requested-With': 'rest-client'}
)

# Response includes ID and link
result = response.json()
ci_id = result['data']['id']
ci_link = result['data']['link']
```

#### Read (GET)

```python
# Get all CIs
response = requests.get(
    'http://localhost:9080/pms/rest/data/ci',
    auth=HTTPBasicAuth('admin', 'admin')
)
cis = response.json()

# Get specific CI
response = requests.get(
    f'http://localhost:9080/pms/rest/data/ci/{ci_id}',
    auth=HTTPBasicAuth('admin', 'admin')
)
ci = response.json()

# Get specific property
response = requests.get(
    f'http://localhost:9080/pms/rest/data/ci/{ci_id}/name',
    auth=HTTPBasicAuth('admin', 'admin')
)
name = response.json()['data']
```

#### Update (PUT/PATCH)

**PUT - Replace values:**

```python
# First, get the current ETag
response = requests.get(
    f'http://localhost:9080/pms/rest/data/ci/{ci_id}',
    auth=HTTPBasicAuth('admin', 'admin')
)
etag = response.headers['ETag']

# Update with ETag for concurrency control
updated_data = {
    "description": "Updated production web server"
}

response = requests.put(
    f'http://localhost:9080/pms/rest/data/ci/{ci_id}',
    json=updated_data,
    auth=HTTPBasicAuth('admin', 'admin'),
    headers={
        'If-Match': etag,
        'X-Requested-With': 'rest-client'
    }
)
```

**PATCH - Operators (add, replace, remove):**

```python
patch_operations = {
    "nosy": {
        "add": ["2", "3"],  # Add users to nosy list
        "remove": ["1"]     # Remove user from nosy list
    }
}

response = requests.patch(
    f'http://localhost:9080/pms/rest/data/issue/{issue_id}',
    json=patch_operations,
    auth=HTTPBasicAuth('admin', 'admin'),
    headers={
        'If-Match': etag,
        'X-Requested-With': 'rest-client'
    }
)
```

#### Delete (DELETE)

```python
response = requests.delete(
    f'http://localhost:9080/pms/rest/data/ci/{ci_id}',
    auth=HTTPBasicAuth('admin', 'admin'),
    headers={'If-Match': etag}
)

# Item is retired, not permanently deleted
# Still accessible directly, but removed from search results
```

### Query Syntax and Filtering

#### Basic Filtering

```python
# Substring search (case-insensitive)
response = requests.get(
    'http://localhost:9080/pms/rest/data/ci',
    params={'name': 'web'},
    auth=HTTPBasicAuth('admin', 'admin')
)

# Exact match (case-sensitive)
response = requests.get(
    'http://localhost:9080/pms/rest/data/ci',
    params={'name:': 'web-server-01'},
    auth=HTTPBasicAuth('admin', 'admin')
)
```

#### Link and Multilink Filtering

```python
# Filter by linked status (by ID or symbolic name)
response = requests.get(
    'http://localhost:9080/pms/rest/data/issue',
    params={'status': 'open'},
    auth=HTTPBasicAuth('admin', 'admin')
)

# Filter by multilink membership
response = requests.get(
    'http://localhost:9080/pms/rest/data/issue',
    params={'nosy': 'admin'},
    auth=HTTPBasicAuth('admin', 'admin')
)
```

#### Transitive Searches

Filter by properties of linked objects:

```python
# Find issues with messages from specific author
response = requests.get(
    'http://localhost:9080/pms/rest/data/issue',
    params={'messages.author': 'admin'},
    auth=HTTPBasicAuth('admin', 'admin')
)

# Find CIs related to specific issue
response = requests.get(
    'http://localhost:9080/pms/rest/data/cirelationship',
    params={'source_ci.name': 'web-server-01'},
    auth=HTTPBasicAuth('admin', 'admin')
)
```

### Relationship Traversal (HATEOAS)

#### Embedded Fields

```python
# Get CI with embedded relationship data
response = requests.get(
    f'http://localhost:9080/pms/rest/data/ci/{ci_id}',
    params={'@fields': 'name,ci_type,relationships'},
    auth=HTTPBasicAuth('admin', 'admin')
)
```

#### Verbose Levels

| Level | Description                        |
| ----- | ---------------------------------- |
| 0     | Minimal data, IDs only             |
| 1     | Include links to related resources |
| 2     | Include relationship metadata      |
| 3     | Full resource representation       |

```python
response = requests.get(
    'http://localhost:9080/pms/rest/data/ci',
    params={'@verbose': '2'},
    auth=HTTPBasicAuth('admin', 'admin')
)
```

### Error Responses and Status Codes

| Code | Meaning                | Common Causes                       |
| ---- | ---------------------- | ----------------------------------- |
| 200  | Success                | GET/PUT/PATCH succeeded             |
| 201  | Created                | POST succeeded                      |
| 400  | Bad Request            | Malformed JSON, validation failure  |
| 401  | Unauthorized           | Authentication failure, invalid JWT |
| 403  | Forbidden              | Insufficient permissions            |
| 406  | Not Acceptable         | Unsupported Accept header           |
| 415  | Unsupported Media Type | Wrong Content-Type                  |
| 429  | Too Many Requests      | Rate limit exceeded                 |

#### Rate Limit Headers

```python
response = requests.get(url, auth=auth)

limit = response.headers.get('X-RateLimit-Limit')
remaining = response.headers.get('X-RateLimit-Remaining')
reset = response.headers.get('X-RateLimit-Reset')

if response.status_code == 429:
    retry_after = response.headers.get('Retry-After')
    # Wait and retry
```

### Pagination

```python
# Get paginated results
response = requests.get(
    'http://localhost:9080/pms/rest/data/ci',
    params={
        '@page_size': 25,
        '@page_index': 1
    },
    auth=HTTPBasicAuth('admin', 'admin')
)

result = response.json()
total_size = result['data']['@total_size']
links = result['data']['@links']

# Follow pagination links
if 'next' in links:
    next_url = links['next']['uri']
    next_response = requests.get(next_url, auth=auth)
```

### Best Practices for BDD Testing

#### With Behave Step Definitions

```python
# features/steps/api_steps.py
import requests
from behave import given, when, then

@given('I am authenticated as {username}')
def step_authenticate(context, username):
    context.auth = HTTPBasicAuth(username, 'password')
    context.headers = {'X-Requested-With': 'rest-client'}

@when('I create a CI with name "{name}"')
def step_create_ci(context, name):
    data = {"name": name, "ci_type": "1"}
    context.response = requests.post(
        f'{context.base_url}/rest/data/ci',
        json=data,
        auth=context.auth,
        headers=context.headers
    )
    context.ci_id = context.response.json()['data']['id']

@then('the response status should be {status:d}')
def step_check_status(context, status):
    assert context.response.status_code == status

@then('the CI should exist in the database')
def step_verify_ci_exists(context):
    response = requests.get(
        f'{context.base_url}/rest/data/ci/{context.ci_id}',
        auth=context.auth
    )
    assert response.status_code == 200
```

#### With Playwright for API Interception

```python
# Monitor API calls from web interface
def test_ci_creation_api(page):
    # Intercept REST API calls
    api_calls = []

    def handle_response(response):
        if '/rest/data/ci' in response.url:
            api_calls.append({
                'url': response.url,
                'status': response.status,
                'method': response.request.method
            })

    page.on('response', handle_response)

    # Trigger CI creation via UI
    page.goto('http://localhost:9080/pms/ci?@template=item')
    page.fill('input[name="name"]', 'test-server')
    page.click('input[type="submit"]')

    # Verify API was called
    assert len(api_calls) > 0
    assert api_calls[0]['method'] == 'POST'
    assert api_calls[0]['status'] == 201
```

#### Testing Best Practices

1. **Store ETags for Updates:**

   ```python
   # Get resource
   get_response = requests.get(url, auth=auth)
   etag = get_response.headers['ETag']

   # Use ETag in update
   put_response = requests.put(
       url,
       json=data,
       auth=auth,
       headers={'If-Match': etag}
   )
   ```

1. **Use `@verbose=0` as Templates:**

   ```python
   # Get minimal payload structure
   response = requests.get(
       f'{base_url}/rest/data/ci/1',
       params={'@verbose': 0},
       auth=auth
   )
   template = response.json()['data']

   # Use as template for POST
   new_ci = template.copy()
   new_ci.update({'name': 'new-server', 'ci_type': '1'})
   ```

1. **Implement POE (Post Once Exactly) for Reliability:**

   ```python
   # Request single-use URL
   poe_response = requests.get(
       f'{base_url}/rest/@poe',
       auth=auth
   )
   poe_url = poe_response.json()['data']['url']

   # Use POE URL for POST
   response = requests.post(
       poe_url,
       json=data,
       auth=auth
   )
   ```

1. **Monitor Rate Limits:**

   ```python
   def api_call_with_rate_limit(url, auth):
       response = requests.get(url, auth=auth)

       remaining = int(response.headers.get('X-RateLimit-Remaining', 999))
       if remaining < 10:
           # Log warning or slow down requests
           logging.warning(f"API rate limit low: {remaining} remaining")

       return response
   ```

______________________________________________________________________

## Server Management

**Reference:** [Roundup Administration Guide](https://www.roundup-tracker.org/docs/admin_guide.html)

### Critical Server Behaviors

1. **Detectors Loaded on Startup:**

   - Detector changes require **server restart** to take effect
   - Use complete restart sequence to avoid stale code

1. **Templates Are Cached:**

   - Template modifications require **server restart** for persistent servers
   - Development mode: use `roundup-server` without `-D` to reduce caching

1. **Schema Changes Auto-Apply:**

   - Modifications to `schema.py` auto-apply on next tracker access
   - **Server restart recommended** after schema changes to ensure clean state

### Database Administration Commands

**Reference:** [Roundup Administration Guide - roundup-admin](https://www.roundup-tracker.org/docs/admin_guide.html)

#### Reindexing

The `reindex` command regenerates search indexes after CLI operations or indexer installation:

```bash
# Reindex entire class
uv run roundup-admin -i tracker reindex ci

# Reindex specific range
uv run roundup-admin -i tracker reindex ci:1-1000

# Reindex all classes
uv run roundup-admin -i tracker reindex
```

**When to Run Reindex:**

- ✅ After creating items via `roundup-admin create`
- ✅ After installing or changing indexer engines
- ✅ After bulk imports via `roundup-admin import`
- ✅ When search results seem incomplete or stale
- ✅ After schema changes affecting indexed properties

#### Database Migration

Run `migrate` to update database schema version before using tracker interfaces:

```bash
uv run roundup-admin -i tracker migrate
```

**When to Run Migrate:**

- After upgrading Roundup to a new version
- Before using web/CLI/mail interfaces on upgraded tracker
- When database schema version is out of sync

#### CLI→Web Visibility Issue

**Problem Discovered** (Sprint 6, 2025-11-18):

Items created via `roundup-admin create` may not be visible through the web interface, even after server restart. This is due to search index synchronization.

**Symptoms:**

- CIs created via CLI exist in database (`roundup-admin list ci` shows them)
- Web interface shows "No configuration items found"
- REST API may not return CLI-created items
- Direct URL access by ID works, but items don't appear in listings

**Root Cause:**

- Search indexes not automatically updated when items created via CLI
- Roundup server loads indexes on startup
- CLI operations bypass index generation

**Solution:**

```bash
# Complete workflow for CLI item creation
# 1. Stop server
pkill -f "roundup-server"
sleep 2

# 2. Create items via CLI
uv run roundup-admin -i tracker create ci name=web-server-01 type=1 status=5

# 3. Reindex the class (CRITICAL STEP)
uv run roundup-admin -i tracker reindex ci

# 4. Start server
uv run roundup-server -p 9080 pms=tracker > /dev/null 2>&1 &
```

**Best Practice for Test Data:**

For BDD/integration testing, consider creating test data via **Web UI** instead of CLI:

```python
# features/steps/ci_steps.py
@given("the following CIs exist:")
def step_create_cis_via_ui(context):
    """Create CIs through web interface for proper indexing."""
    for row in context.table:
        # Navigate to CI creation form
        context.page.goto(f"{context.base_url}/ci?@template=item")

        # Fill form and submit
        context.page.fill('input[name="name"]', row['name'])
        context.page.select_option('select[name="type"]', row['type'])
        context.page.click('input[type="submit"][value="Submit"]')

        # Server sees changes immediately (no reindex needed)
```

**Advantages of Web UI Test Data Creation:**

- ✅ Proper index generation automatically
- ✅ Tests actual user workflow
- ✅ No CLI→Web synchronization issues
- ✅ Detectors and validators fire correctly
- ✅ More realistic BDD scenarios

**When CLI Creation is Appropriate:**

- Bulk data imports from external systems
- Database initialization scripts
- Automated monitoring/alerting integrations
- **Always followed by reindex command**

### Recommended Restart Sequence

```bash
# Stop all Roundup servers
pkill -f "roundup-server"

# Wait for processes to terminate
sleep 2

# Start server in background
uv run roundup-server -p 9080 pms=tracker > /dev/null 2>&1 &

# Verify server is running
curl -s http://localhost:9080/pms/ | grep -q "Roundup" && \
  echo "Server is running" || echo "Server failed to start"
```

### Development vs Production

**Development (foreground for testing):**

```bash
uv run roundup-server -p 9080 pms=tracker
```

- See logs in console
- Ctrl+C to stop
- Good for interactive debugging

**BDD Testing (background):**

```bash
pkill -f "roundup-server" && sleep 2 && \
uv run roundup-server -p 9080 pms=tracker > /dev/null 2>&1 &
```

- Silent background execution
- Required for Behave scenario execution
- Clean restart before test runs

### Server Configuration Best Practices

1. **Logging:**

   - Configure via Python logging module for structured logs
   - Set appropriate log levels per environment (DEBUG/INFO/WARNING)
   - Use file-based logging for production

1. **Full-Text Search:**

   - SQLite: Enable FTS5 for phrase searches and boolean operations
   - PostgreSQL: Configure native full-text search for production scale
   - Index selectively with `indexme='yes'` on String properties

1. **Session Management:**

   - Use Redis for session database in production (better performance)
   - File-based sessions acceptable for development

1. **Security:**

   - Configure Content Security Policy with dynamic nonces
   - Use `secret_key` in config.ini for proper ETag/JWT generation
   - Enable rate limiting for REST API (`api_failed_login_limit`)

### Security Best Practices

**Reference:** [Roundup Wiki - AdministrationExample](https://wiki.roundup-tracker.org/AdministrationExample)

#### Spam Prevention

Implement detector-based spam filters:

```python
# In detectors/spam_filter.py
def reject_spam(db, cl, nodeid, newdata):
    """Auditor: Block spam submissions."""
    # Check for excessive links in messages
    if 'content' in newdata:
        content = newdata['content']
        link_count = content.count('http://') + content.count('https://')
        if link_count > 3:
            raise Reject("Too many links - possible spam")

    # Check for suspicious patterns
    spam_keywords = ['viagra', 'casino', 'lottery']
    for keyword in spam_keywords:
        if keyword.lower() in content.lower():
            raise Reject("Spam content detected")

def init(db):
    db.msg.audit('create', reject_spam)
```

#### Brute-Force Protection

Configure in `config.ini`:

```ini
[web]
# Limit failed login attempts
api_failed_login_limit = 5

# Lockout duration in seconds
api_failed_login_delay = 300
```

#### Content Security Policy

Add CSP headers per tracker in `extensions/`:

```python
def add_csp_header(client):
    """Add Content Security Policy header."""
    nonce = client.db.security.nonce()
    csp = f"default-src 'self'; script-src 'self' 'nonce-{nonce}'"
    client.additional_headers['Content-Security-Policy'] = csp
```

#### OAuth/OpenID Connect

Support external authentication:

- **Google OAuth**: Configure in `config.ini` with client ID and secret
- **GitHub OAuth**: Similar configuration for GitHub integration
- **LDAP/Active Directory**: External user database integration

**Configuration Example:**

```ini
[oauth]
provider = google
client_id = your-client-id
client_secret = your-client-secret
redirect_uri = https://tracker.example.com/oauth/callback
```

#### AppArmor Integration

For Linux deployments, use AppArmor profiles to restrict Roundup capabilities:

```bash
# /etc/apparmor.d/roundup-server
#include <tunables/global>

/usr/bin/roundup-server {
  #include <abstractions/base>
  #include <abstractions/python>

  # Tracker home directory
  /path/to/tracker/** rw,

  # Database access
  /path/to/tracker/db/** rw,

  # Deny network access except localhost
  network inet stream,
  deny network inet dgram,
}
```

#### Security Checklist

- [ ] Change default admin password immediately
- [ ] Configure `secret_key` for JWT/ETag security
- [ ] Enable HTTPS in production (use reverse proxy)
- [ ] Implement rate limiting for API endpoints
- [ ] Add CSP headers to prevent XSS attacks
- [ ] Configure spam filters in detectors
- [ ] Use strong password requirements
- [ ] Enable audit logging for security events
- [ ] Regularly update Roundup to latest version
- [ ] Review and restrict user permissions
- [ ] Implement backup and disaster recovery procedures
- [ ] Monitor for suspicious activity patterns

______________________________________________________________________

## Testing Strategies

### BDD Testing with Behave

**Test Structure:**

```
features/
├── cmdb/
│   ├── ci_creation.feature
│   ├── ci_relationships.feature
│   └── ci_search.feature
└── steps/
    ├── ci_steps.py
    └── common_steps.py
```

**Feature File Example:**

```gherkin
@web-ui @cmdb
Feature: CI Creation
  As a system administrator
  I want to create Configuration Items
  So that I can track infrastructure components

  Background:
    Given the Roundup server is running on "http://localhost:9080/pms"
    And I am logged in as "admin" with password "admin"

  Scenario: Create CI with required fields
    When I navigate to the CI creation page
    And I enter "web-server-01" in the "name" field
    And I select "Server" from the "ci_type" dropdown
    And I click the "Submit" button
    Then I should see "CI created successfully"
    And the CI "web-server-01" should exist in the database
```

**Step Definition Example:**

```python
# features/steps/ci_steps.py
from behave import given, when, then
from playwright.sync_api import expect

@when('I navigate to the CI creation page')
def step_navigate_to_ci_creation(context):
    context.page.goto(f"{context.base_url}/ci?@template=item")

@when('I enter "{value}" in the "{field}" field')
def step_enter_field(context, value, field):
    context.page.fill(f'input[name="{field}"]', value)

@when('I select "{option}" from the "{field}" dropdown')
def step_select_dropdown(context, option, field):
    context.page.select_option(f'select[name="{field}"]', label=option)

@then('the CI "{name}" should exist in the database')
def step_verify_ci_exists(context, name):
    # Use REST API to verify
    import requests
    response = requests.get(
        f'{context.base_url}/rest/data/ci',
        params={'name': name},
        auth=context.auth
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data['data']['collection']) > 0
```

### Roundup + BDD Integration Patterns

**Context:** Roundup has specific behaviors (server caching, search indexing) that require special handling in BDD test scenarios. This section documents patterns learned through implementation.

**Reference:** See ADR-0002 for Behave fixture patterns and best practices.

#### Server Lifecycle Management in BDD Fixtures

**The Challenge:**

Roundup server caches schema, configuration, and search indexes in memory. Items created via CLI while server is running may not be immediately visible through the web interface.

**Solution Pattern:**

Use Behave fixtures to manage database state, but let step definitions control server lifecycle:

```python
# features/environment.py

@fixture
def clean_database(context):
    """
    Provide clean database for each scenario.

    NOTE: Does NOT start server - step definitions start server AFTER
    creating test data to avoid caching issues.
    """
    tracker_dir = getattr(context, 'tracker_dir', 'tracker')

    # Stop any running server
    subprocess.run(['pkill', '-f', 'roundup-server'], capture_output=True)
    time.sleep(2)

    # Delete and reinitialize database
    db_dir = Path(tracker_dir) / 'db'
    if db_dir.exists():
        shutil.rmtree(db_dir)

    # Initialize with consistent tooling
    cmd = ['uv', 'run', 'roundup-admin', '-i', tracker_dir, 'initialise']
    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    stdout, stderr = process.communicate(input="admin\nadmin\n", timeout=30)

    if process.returncode != 0:
        raise RuntimeError(f"Database init failed: {stderr}")

    # Server NOT started - step definitions will start after populating data

    yield context  # Scenario runs here

    # Cleanup: stop server for clean state
    subprocess.run(['pkill', '-f', 'roundup-server'], capture_output=True)

def before_scenario(context, scenario):
    """Set up clean test environment."""
    use_fixture(clean_database, context)
    context.ci_map = {}  # Track created items

    # Only set up browser for web UI scenarios
    if 'web-ui' in scenario.effective_tags:
        use_fixture(browser_context, context)
```

**Why This Works:**

1. **Database fixture** provides clean state but doesn't start server
1. **Step definitions** create test data via CLI while server is stopped
1. **Step definitions** run `reindex` command to update search indexes
1. **Step definitions** start server after data is ready
1. **Web UI tests** see all data without caching issues

#### Test Data Creation Patterns

**Pattern 1: CLI + Reindex Workflow (Recommended for BDD)**

Best for: BDD scenarios testing web UI functionality with pre-existing data

```python
# features/steps/ci_search_steps.py

@given('the following CIs exist')
def step_create_multiple_cis(context):
    """
    Create CIs via CLI and make them visible to web interface.

    CRITICAL: Must run `reindex` command after CLI creation to update
    search indexes. Without reindex, CIs will not appear in web UI.
    """
    tracker_dir = 'tracker'

    for row in context.table:
        # Create CI via roundup-admin (server is stopped from fixture)
        cmd = [
            'uv', 'run', 'roundup-admin', '-i', tracker_dir,
            'create', 'ci',
            f'name={row["name"]}',
            f'type={row["type"]}',
            f'status={row["status"]}'
        ]

        if 'criticality' in row.headings:
            cmd.append(f'criticality={row["criticality"]}')

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode != 0:
            raise RuntimeError(f"Failed to create CI: {result.stderr}")

        # Extract CI ID from output (format: "ci1", "ci2", etc.)
        ci_id = result.stdout.strip()
        context.ci_map[row['name']] = ci_id

    # CRITICAL: Reindex to make CLI-created items visible through web interface
    # Without this, search will return 0 results even though CIs exist in database
    reindex_cmd = ['uv', 'run', 'roundup-admin', '-i', tracker_dir, 'reindex', 'ci']
    subprocess.run(reindex_cmd, capture_output=True, text=True, timeout=30)

    # NOW start server - CIs will be visible
    server_cmd = ['uv', 'run', 'roundup-server', '-p', '9080', 'pms=tracker']
    subprocess.Popen(
        server_cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(3)  # Allow server to fully start
```

**Pattern 2: Web UI Creation**

Best for: Testing CI creation workflows themselves

```python
@when('I create a CI via the web interface')
def step_create_ci_via_ui(context):
    """Create CI through web form - no reindex needed."""
    context.page.goto(f"{context.tracker_url}/ci?@template=item")
    context.page.fill('input[name="name"]', "test-ci")
    context.page.select_option('select[name="type"]', label="Server")
    context.page.click('input[type="submit"]')
    # CI immediately visible - server created it
```

**Pattern 3: REST API Creation**

Best for: Programmatic testing and API validation

```python
@when('I create a CI via REST API')
def step_create_ci_via_api(context):
    """Create CI via REST endpoint - no reindex needed."""
    import requests
    response = requests.post(
        f'{context.tracker_url}/rest/data/ci',
        json={'name': 'test-ci', 'type': '1', 'status': '5'},
        auth=('admin', 'admin')
    )
    assert response.status_code == 201
    # CI immediately visible - server created it
```

**Decision Matrix:**

| Use Case                         | Recommended Pattern | Requires Reindex? |
| -------------------------------- | ------------------- | ----------------- |
| Test search/filter functionality | CLI + Reindex       | ✅ Yes            |
| Test CI creation workflow        | Web UI              | ❌ No             |
| Test bulk data scenarios         | CLI + Reindex       | ✅ Yes            |
| Test API functionality           | REST API            | ❌ No             |
| Test CI relationships            | CLI + Reindex       | ✅ Yes            |

#### Common Pitfalls and Solutions

**Pitfall 1: CIs Created via CLI Not Visible in Web UI**

**Symptom:** Test creates CIs via `roundup-admin create`, but web UI shows "No items found"

**Root Cause:** Search indexes not automatically updated for CLI-created items

**Solution:**

```bash
# After creating CIs via CLI, ALWAYS run reindex
uv run roundup-admin -i tracker reindex ci
```

**Why:** Roundup maintains search indexes separately from database. CLI operations bypass the index update mechanism that web/API operations trigger automatically.

**Pitfall 2: Server Caching Old Data**

**Symptom:** Changes made via CLI don't appear even after reindex

**Root Cause:** Server was running when changes were made, cached old state

**Solution:**

```python
# ALWAYS stop server before database operations
subprocess.run(['pkill', '-f', 'roundup-server'])
time.sleep(2)  # Wait for full shutdown

# Make database changes
# ... create/modify/delete items ...

# Reindex if using CLI
subprocess.run(['uv', 'run', 'roundup-admin', '-i', 'tracker', 'reindex', 'ci'])

# NOW start fresh server
subprocess.Popen(['uv', 'run', 'roundup-server', '-p', '9080', 'pms=tracker'])
time.sleep(3)  # Wait for full startup
```

**Pitfall 3: Template Helper Functions Failing with AttributeError**

**Symptom:** `AttributeError: getnode` or similar errors in template helpers

**Root Cause:** Attempting to use database methods not available in TAL template context

**Solution:**

```python
# ❌ WRONG - db.ci.getnode() not available in template context
def filter_ci_ids_by_search(db, ci_ids, search_term):
    for ci_id in ci_ids:
        id_str = str(ci_id.id) if hasattr(ci_id, 'id') else str(ci_id)
        node = db.ci.getnode(id_str)  # AttributeError!

# ✅ CORRECT - Access fields directly from HTMLItem objects
def filter_ci_ids_by_search(db, ci_ids, search_term):
    for ci_id in ci_ids:
        # ci_id is already an HTMLItem with data
        if hasattr(ci_id, 'name') and ci_id.name:
            if hasattr(ci_id.name, 'plain'):
                name = ci_id.name.plain()  # Extract string value
            else:
                name = str(ci_id.name)
```

**See:** "Python Template Helpers" section for complete defensive patterns.

**Pitfall 4: Screenshot Accumulation Between Tests**

**Symptom:** Screenshots directory grows unbounded, old failures confuse debugging

**Solution:**

```python
def before_scenario(context, scenario):
    """Clean screenshots before each scenario."""
    screenshot_dir = Path("screenshots")
    if screenshot_dir.exists():
        for screenshot in screenshot_dir.glob("*.png"):
            try:
                screenshot.unlink()
            except Exception as e:
                print(f"Warning: Failed to delete {screenshot}: {e}")
```

**Why:** Keeps screenshot directory manageable and ensures only current test failures are visible.

**Pitfall 5: Test Failures Leave Database in Dirty State**

**Symptom:** First test fails, subsequent tests fail due to unexpected data

**Solution:** Use Behave fixtures with generator pattern:

```python
@fixture
def clean_database(context):
    setup_clean_database()

    yield context  # Test runs here

    # Cleanup ALWAYS runs, even on test failure
    cleanup_database()
```

**Why:** Fixtures guarantee cleanup runs in reverse order, even when tests fail.

#### Complete Working Example

**Gherkin Feature:**

```gherkin
@web-ui @cmdb
Feature: CI Search
  Background:
    Given the following CIs exist:
      | name           | type | status |
      | db-server-01   | 1    | 5      |
      | db-server-02   | 1    | 5      |
      | web-server-01  | 1    | 5      |
    And I am on the CI index page

  Scenario: Search CIs by name
    When I search for "db-server"
    Then I should see 2 CIs in the results
    And I should see "db-server-01"
    And I should see "db-server-02"
```

**Step Definition:**

```python
# features/steps/ci_search_steps.py

@given('the following CIs exist')
def step_create_multiple_cis(context):
    """Create CIs via CLI with reindex."""
    for row in context.table:
        cmd = [
            'uv', 'run', 'roundup-admin', '-i', 'tracker',
            'create', 'ci',
            f'name={row["name"]}',
            f'type={row["type"]}',
            f'status={row["status"]}'
        ]
        subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    # CRITICAL: Reindex for web visibility
    subprocess.run(
        ['uv', 'run', 'roundup-admin', '-i', 'tracker', 'reindex', 'ci'],
        capture_output=True, text=True, timeout=30
    )

    # Start server
    subprocess.Popen(
        ['uv', 'run', 'roundup-server', '-p', '9080', 'pms=tracker'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(3)

@when('I search for "{search_term}"')
def step_search_for_term(context, search_term):
    """Perform search via web UI."""
    search_box = context.page.locator('input[name="@search_text"]')
    search_box.fill(search_term)
    search_box.press('Enter')
    # Playwright auto-waits for navigation

@then('I should see {count:d} CIs in the results')
def step_verify_ci_count(context, count):
    """Verify result count."""
    rows = context.page.locator('table.list tbody tr')
    actual_count = rows.count()
    assert actual_count == count, f"Expected {count} CIs, found {actual_count}"
```

**Key Takeaways:**

1. ✅ **Fixtures manage infrastructure** (database, server, browser)
1. ✅ **Step definitions manage server lifecycle** (start after data ready)
1. ✅ **Always reindex after CLI operations** (make data visible)
1. ✅ **Use appropriate pattern for use case** (CLI vs Web UI vs API)
1. ✅ **Let Playwright auto-wait** (avoid manual timeouts when possible)

**References:**

- Server Management: See "Server Management" section
- Database Admin Commands: See "Database Administration Commands" section
- Template Helpers: See "Python Template Helpers" section
- Behave Fixtures: See ADR-0002 "Behave Best Practices"

### Unit Testing with pytest

**Test Detector Logic:**

```python
# tests/test_ci_detector.py
import pytest
from roundup import instance

def test_ci_name_required():
    """Test that CI name is required on creation."""
    tracker = instance.open('tracker')
    db = tracker.open('admin')

    with pytest.raises(ValueError, match="CI name is required"):
        db.ci.create(ci_type='1', description='Test')

    db.close()

def test_ci_name_uniqueness():
    """Test that CI names must be unique."""
    tracker = instance.open('tracker')
    db = tracker.open('admin')

    # Create first CI
    ci1 = db.ci.create(name='unique-ci', ci_type='1')

    # Attempt duplicate
    with pytest.raises(ValueError, match="already exists"):
        db.ci.create(name='unique-ci', ci_type='1')

    db.close()
```

### Integration Testing Across Interfaces

For each feature, test **all three interfaces:**

1. **Web UI (Playwright)** - User workflows
1. **REST API** - Programmatic access
1. **CLI** - `roundup-admin` commands

**Example Test Matrix:**

| Feature          | Web UI | REST API | CLI |
| ---------------- | ------ | -------- | --- |
| Create CI        | ✓      | ✓        | ✓   |
| Search CI        | ✓      | ✓        | ✓   |
| Link CI to Issue | ✓      | ✓        | ✓   |
| CI Relationships | ✓      | ✓        | ✓   |

______________________________________________________________________

## Performance Optimization

### Database Query Optimization

1. **Use Filters Instead of List + Loop:**

   ```python
   # Bad: Enumerate all items
   all_cis = db.ci.list()
   active_cis = [ci for ci in all_cis if db.ci.get(ci, 'is_active')]

   # Good: Filter at database level
   active_cis = db.ci.filter(None, {'is_active': True})
   ```

1. **Cache Expensive Lookups:**

   ```python
   # Bad: Repeated lookups in loop
   for ci_id in ci_list:
       name = db.ci.get(ci_id, 'name')
       type_id = db.ci.get(ci_id, 'ci_type')
       type_name = db.citype.get(type_id, 'name')

   # Good: Batch with getnode()
   for ci_id in ci_list:
       ci = db.ci.getnode(ci_id)
       type_node = db.citype.getnode(ci.ci_type)
       # Use ci.name, type_node.name
   ```

1. **Set Order Properties:**

   ```python
   # In schema.py
   ci.setorderprop('name')  # Define default sort
   ```

   Without `setorderprop`, every query sorts by ID (inefficient).

### Full-Text Search

1. **Index Selectively:**

   ```python
   # Schema.py - only index searchable text
   name=String(indexme='yes')           # User searches by name
   description=String(indexme='yes')    # User searches descriptions
   internal_id=String(indexme='no')     # No need to search UUIDs
   ```

1. **Configure Native FTS:**

   - SQLite FTS5: Phrase searches, proximity, boolean
   - PostgreSQL: Production-scale full-text search
   - See [Admin Guide - Native FTS](https://www.roundup-tracker.org/docs/admin_guide.html)

### Template Performance

1. **Conditional Rendering:**

   - Use `tal:condition` before expensive operations
   - Don't render hidden tables/lists

1. **Batching for Large Results:**

   ```html
   <!-- Use batch helper for pagination -->
   <tr tal:repeat="i batch">
     <td tal:content="i/name">name</td>
   </tr>

   <!-- Pagination controls -->
   <div tal:replace="structure batch/navigation" />
   ```

1. **Minimize Database Calls in Templates:**

   ```html
   <!-- Bad: Repeated db lookups -->
   <td tal:content="python:db.user.get(i.assignedto, 'username')">user</td>
   <td tal:content="python:db.user.get(i.assignedto, 'email')">email</td>

   <!-- Good: Single lookup with define -->
   <tr tal:define="assignee python:db.user.getnode(i.assignedto)">
     <td tal:content="assignee/username">user</td>
     <td tal:content="assignee/email">email</td>
   </tr>
   ```

### Detector Performance

1. **Avoid User Enumeration:**

   - Don't loop through `db.user.list()` in detectors
   - Use filters to query specific users

1. **Batch Related Updates:**

   ```python
   # In reactor
   def update_related_items(db, cl, nodeid, olddata):
       related_ids = db.ci.get(nodeid, 'related_cis')

       # Batch update
       for rel_id in related_ids:
           db.ci.set(rel_id, last_modified=Date())
   ```

1. **Use Appropriate Priorities:**

   - Lower priority numbers run first
   - Use for detector dependencies, not performance

### Batch Operations

**Reference:** [Roundup Wiki - BatchSearchAndEditing](https://wiki.roundup-tracker.org/BatchSearchAndEditing)

Batch editing allows simultaneous modification of multiple items without repetitive data entry:

**Workflow:**

1. **Search Page:** Users enter modification details in "Edit Fields" section
1. **Enter Search Criteria:** Specify which items to modify
1. **Results Page:** System processes batch edits on matched items

**Implementation Requirements:**

- `issue.batch_search.html` - Initial search and edit interface
- `issue.batch.html` - Results/confirmation page
- `batch_editing.py` extension with `batch_validate` class

**Example Template Structure:**

```html
<!-- issue.batch_search.html -->
<form action="issue" method="POST">
  <!-- Edit Fields Section -->
  <fieldset>
    <legend>Fields to Modify</legend>
    <select name="priority" tal:replace="structure context/priority/menu" />
    <select name="status" tal:replace="structure context/status/menu" />
    <input type="text" name="nosy_add" placeholder="Add to nosy list" />
  </fieldset>

  <!-- Search Criteria Section -->
  <fieldset>
    <legend>Find Items to Edit</legend>
    <input type="text" name="title" placeholder="Title contains..." />
    <select name="status_search" tal:replace="structure context/status/menu" />
  </fieldset>

  <input type="submit" name="@action" value="batch_edit" />
</form>
```

**Validation:**

- Require at least one edit field contains data
- Confirm batch scope before applying changes
- Provide preview/confirmation step for large batches

**Performance Considerations:**

- Limit batch size to prevent timeouts
- Use database transactions for atomicity
- Consider background processing for very large batches
- Log all batch operations for audit trail

### Advanced Search Patterns

**Reference:** [Roundup Wiki - RegularExpressionSupport](https://wiki.roundup-tracker.org/RegularExpressionSupport)

Regular expression searches enable sophisticated pattern matching across tracker data:

**Implementation:**

```python
# In extensions/regex_search.py
from roundup.cgi.actions import SearchAction
import re

class RegExpSearchAction(SearchAction):
    """Extend SearchAction with regex support."""

    def handle(self):
        # Validate regex pattern exists
        pattern = self.form.getfirst('search_text')
        if not pattern:
            raise ValueError("Regular expression pattern required")

        # Compile pattern with flags
        flags = re.IGNORECASE if self.form.getfirst('ignore_case') else 0
        try:
            regex = re.compile(pattern, flags)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {e}")

        # Search issue titles
        title_matches = []
        for issue_id in self.db.issue.list():
            title = self.db.issue.get(issue_id, 'title')
            if regex.search(title):
                title_matches.append(issue_id)

        # Search message content (with MULTILINE and DOTALL)
        msg_flags = flags | re.MULTILINE | re.DOTALL
        msg_regex = re.compile(pattern, msg_flags)
        msg_matches = []

        for msg_id in self.db.msg.list():
            content = self.db.msg.get(msg_id, 'content')
            if msg_regex.search(content):
                # Find parent issue
                issues = self.db.issue.filter(None, {'messages': msg_id})
                msg_matches.extend(issues)

        # Combine and deduplicate results
        all_matches = list(set(title_matches + msg_matches))
        return all_matches
```

**Template Integration:**

```html
<!-- Add to search template -->
<div>
  <input type="checkbox" name="use_regex" id="use_regex" />
  <label for="use_regex">Regular Expression</label>

  <input type="checkbox" name="ignore_case" id="ignore_case" disabled />
  <label for="ignore_case">Ignore Case</label>
</div>

<script>
// Enable ignore_case only when regex is checked
document.getElementById('use_regex').addEventListener('change', function() {
  document.getElementById('ignore_case').disabled = !this.checked;
});
</script>
```

**Performance Warning:**

- Regex searches can be slow on large trackers
- Cannot be saved as named queries
- Consider limiting to specific fields
- Use database full-text search for simple keyword matching

**Best Practices:**

- Validate regex patterns before execution
- Set reasonable timeouts for regex searches
- Provide examples and syntax help in UI
- Consider caching frequent regex patterns
- Use anchors (`^`, `$`) to improve performance

______________________________________________________________________

## References

**Official Documentation:**

- **Main Docs:** https://www.roundup-tracker.org/docs.html
- **Roundup Version:** 2.5.0
- **Customization Guide:** https://www.roundup-tracker.org/docs/customizing.html
- **Reference Documentation:** https://www.roundup-tracker.org/docs/reference.html
- **Administration Guide:** https://www.roundup-tracker.org/docs/admin_guide.html
- **REST API Documentation:** https://www.roundup-tracker.org/docs/rest.html

**Community Resources:**

- **Roundup Wiki:** https://wiki.roundup-tracker.org
  - [CustomisationExamples](https://wiki.roundup-tracker.org/CustomisationExamples) - User-contributed patterns
  - [LoopCheck](https://wiki.roundup-tracker.org/LoopCheck) - Circular reference prevention
  - [ReverseLinkEdit](https://wiki.roundup-tracker.org/ReverseLinkEdit) - Bidirectional linking
  - [MixinClassFileClass](https://wiki.roundup-tracker.org/MixinClassFileClass) - Class extension patterns
  - [BatchSearchAndEditing](https://wiki.roundup-tracker.org/BatchSearchAndEditing) - Bulk operations
  - [RegularExpressionSupport](https://wiki.roundup-tracker.org/RegularExpressionSupport) - Advanced search
  - [NewIssueCopy](https://wiki.roundup-tracker.org/NewIssueCopy) - Email notifications
  - [NosyMessagesAllTheTime](https://wiki.roundup-tracker.org/NosyMessagesAllTheTime) - Notification patterns
  - [AutomatedIssues](https://wiki.roundup-tracker.org/AutomatedIssues) - Programmatic issue creation
  - [AdministrationExample](https://wiki.roundup-tracker.org/AdministrationExample) - Security and operations
  - [Jinja2](https://wiki.roundup-tracker.org/Jinja2) - Alternative templating engine
- **Issue Tracker:** https://issues.roundup-tracker.org

______________________________________________________________________

## Document History

| Date       | Version | Changes                                                                                                                                                                                                                                                                                                            |
| ---------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 2025-01-17 | 1.0     | Initial comprehensive best practices document                                                                                                                                                                                                                                                                      |
| 2025-01-17 | 1.1     | Added wiki-sourced patterns: circular reference prevention, mixin classes, bidirectional linking, email notifications, nosy list management, automated issue creation, batch operations, regex search, security best practices                                                                                     |
| 2025-01-17 | 1.2     | Removed personal copyright; added proper attribution to Roundup project, copyright holders, and community contributors                                                                                                                                                                                             |
| 2025-11-17 | 1.3     | **Sprint 5 Lessons Learned**: Added custom action handlers section (solving web UI error handling limitation), TAL path expressions for relationship traversal, Reject vs ValueError best practices, structured logging patterns. Discoveries from production implementation providing reusable Roundup patterns   |
| 2025-11-18 | 1.4     | **Sprint 6 Day 2 Discovery**: Added Database Administration Commands section with reindex/migrate commands, documented CLI→Web visibility issue and solution, provided best practices for test data creation (Web UI vs CLI), includes complete workflow for CLI item creation with reindex                        |
| 2025-11-18 | 1.5     | **Sprint 6 Day 2 Bug Fix**: Added Python Template Helpers section documenting HTMLItem object handling in TAL templates, defensive patterns for `.plain()` method usage, explained why `db.ci.getnode()` fails in template context, fixed search functionality bug                                                 |
| 2025-11-18 | 1.6     | **Sprint 6 Day 2 Integration**: Added comprehensive "Roundup + BDD Integration Patterns" section consolidating Roundup-specific BDD testing patterns: server lifecycle management, test data creation patterns (CLI+Reindex, Web UI, REST API), decision matrix, 5 common pitfalls with solutions, working example |

______________________________________________________________________

**For questions or improvements to this document, please create an issue in the project tracker.**
