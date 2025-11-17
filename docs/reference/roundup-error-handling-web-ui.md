<!--
SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
SPDX-License-Identifier: MIT
-->

# Roundup Error Handling in Web UI

## Overview

This document describes how Roundup handles validation errors from auditor detectors in the web UI, based on investigation during Sprint 5 (Story 3: CI Relationships).

**Date**: 2025-11-17
**Roundup Version**: 2.5.0
**Context**: Circular dependency detector implementation

## The Problem

Auditor detectors that raise `Reject` exceptions work correctly via CLI but don't display error messages to users via the web UI.

### Symptoms

- **CLI**: Error displayed immediately, transaction rolled back ✅
- **Web UI**: Error logged, transaction rolled back, BUT no error shown to user ❌
- User sees blank page or gets redirected without feedback

## Root Cause

### 1. Exception Handling in NewItemAction

From `roundup/cgi/actions.py`:

```python
def handle(self):
    """Add a new item to the database."""
    # ... code ...

    try:
        messages = self._editnodes(props, links)
    except (ValueError, KeyError, IndexError, Reject) as message:
        escape = not isinstance(message, RejectRaw)
        self.client.add_error_message(_('Error: %s') % str(message), escape=escape)
        return  # <-- Just returns, no redirect!

    # Commit now that all the tricky stuff is done
    self.db.commit()

    # Redirect to success page
    raise exceptions.Redirect(...)  # Never reached if exception occurred
```

**Issue**: When `Reject` is caught:

1. Error message is added via `add_error_message()`
1. Method returns immediately
1. **No redirect occurs**
1. No page is rendered to show the error

### 2. Request-Scoped Error Messages

From `roundup/cgi/client.py`:

```python
def __init__(self, instance, request, env, form=None, translator=None):
    # ... code ...
    self._error_message = []  # Request-scoped!
    # ... code ...

def add_error_message(self, msg, escape=True):
    add_message(self._error_message, msg, escape)
    self.form_wins = True
```

**Issue**: Error messages are stored in `self._error_message`:

- Created fresh for each HTTP request
- Not persisted in session
- Lost on HTTP redirects
- Only visible if the same request renders a page

## Solution: Custom Action Handler

Create a custom action that explicitly redirects with the error message.

### Implementation

**File**: `tracker/extensions/cirelationship_actions.py`

```python
from roundup.cgi.actions import NewItemAction
from roundup.exceptions import Reject, RejectRaw
from roundup.cgi import exceptions
import urllib.parse as urllib_
import logging

logger = logging.getLogger(__name__)

class CIRelationshipNewAction(NewItemAction):
    """Custom new item action with proper error display."""

    def handle(self):
        # ... same POST check and form parsing ...

        try:
            messages = self._editnodes(props, links)
        except (ValueError, KeyError, IndexError, Reject) as message:
            escape = not isinstance(message, RejectRaw)
            error_msg = str(message)
            logger.warning(f"CI relationship creation failed: {error_msg}")

            # Get source_ci to redirect back to the right CI page
            source_ci = props.get(('cirelationship', None), {}).get('source_ci')
            if source_ci:
                url = f"{self.base}ci{source_ci}?@error_message={urllib_.quote(error_msg)}"
            else:
                url = f"{self.base}ci?@error_message={urllib_.quote(error_msg)}"

            # IMPORTANT: Redirect with error in URL
            raise exceptions.Redirect(url)

        # ... commit and success redirect ...

def init(instance):
    """Register custom action."""
    instance.registerAction('cirelationship_new', CIRelationshipNewAction)
```

### Template Integration

**File**: `tracker/html/cirelationship.item.html`

```html
<form method="POST" name="cirelForm"
      onSubmit="return submit_once()"
      enctype="multipart/form-data"
      tal:attributes="action context/designator">
  <!-- Use custom action for new items -->
  <input type="hidden" name="@action" value="cirelationship_new"
         tal:condition="not:context/id" />
  <input type="hidden" name="@action" value="edit_item"
         tal:condition="context/id" />

  <!-- ... rest of form ... -->
</form>
```

## Best Practices

### 1. Use Reject Exception

Always use `Reject` from `roundup.exceptions`, not `ValueError`:

```python
from roundup.exceptions import Reject

def validate_something(db, cl, nodeid, newvalues):
    if something_invalid:
        raise Reject("Clear error message for user")
```

### 2. Add Structured Logging

Help debugging with proper logging:

```python
import logging

logger = logging.getLogger(__name__)

def validate_something(db, cl, nodeid, newvalues):
    logger.info("Validator called", extra={
        "nodeid": nodeid,
        "newvalues": newvalues
    })

    if something_invalid:
        logger.warning("Validation failed", extra={
            "reason": "specific_reason",
            "details": {...}
        })
        raise Reject("User-friendly error message")
```

### 3. Test Both Interfaces

Always test validators via both CLI and web UI:

```bash
# CLI test
roundup-admin -i tracker create classname field=value

# Web UI test
# Use BDD scenarios with Playwright
```

## Verification

### CLI Verification

```bash
$ roundup-admin -i tracker create cirelationship source_ci=1 target_ci=1 relationship_type=3
Error: A CI cannot have a relationship with itself
```

✅ Error displayed immediately

### Web UI Verification (Before Fix)

1. Submit form with invalid data
1. Page goes blank or redirects elsewhere
1. No error message visible

❌ Poor UX, user confused

### Web UI Verification (After Fix)

1. Submit form with invalid data
1. Redirected back to source page
1. Error message displayed: `@error_message=A+CI+cannot+have+a+relationship+with+itself`

✅ User sees clear error message

## Related Files

- `tracker/detectors/ci_relationship_validator.py` - Detector with Reject exceptions
- `tracker/extensions/cirelationship_actions.py` - Custom action handler
- `tracker/html/cirelationship.item.html` - Form using custom action
- `docs/reference/roundup-development-practices.md` - General best practices

## References

- Roundup Documentation: https://www.roundup-tracker.org/docs/customizing.html
- Roundup Source: `roundup/cgi/actions.py` (NewItemAction class)
- Roundup Source: `roundup/cgi/client.py` (error message handling)
- Sprint 5 Progress: `docs/sprints/sprint-5-progress.md`

## Lessons Learned

1. **Roundup's default error handling is optimized for CLI, not web UI**
1. **Error messages don't persist across HTTP redirects** (request-scoped)
1. **Custom actions needed for good UX** when using Reject in auditors
1. **Always verify web UI behavior**, even if CLI works
1. **Logging is essential** for debugging Roundup detectors

______________________________________________________________________

**Last Updated**: 2025-11-17
**Status**: Verified and documented
**Impact**: Applies to all Roundup classes using auditor validators
