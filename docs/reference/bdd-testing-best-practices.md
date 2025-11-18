<!--
SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
SPDX-License-Identifier: MIT
-->

# BDD Testing Best Practices

**Document Version:** 1.0
**Last Updated:** 2025-11-18
**Frameworks:** Behave 1.2.6+, Playwright 1.40+

______________________________________________________________________

## About This Document

This document provides comprehensive best practices for Behavior-Driven Development (BDD) testing using Behave and Playwright in the Pasture Management System.

**Purpose**: Technical reference for writing resilient, maintainable BDD tests

**Audience**: Developers writing BDD scenarios and step definitions

**Scope**:

- Behave fixtures and test isolation patterns
- Playwright locator strategies and auto-waiting
- Integration patterns for BDD scenarios
- Migration recommendations

**Related Decision**: See [ADR-0002](../adr/0002-adopt-development-best-practices.md) for the decision to adopt BDD and rationale.

______________________________________________________________________

## Table of Contents

- [Behave Best Practices](#behave-best-practices)
- [Playwright Best Practices for BDD Testing](#playwright-best-practices-for-bdd-testing)
- [Integration with Roundup](#integration-with-roundup)
- [Related Documentation](#related-documentation)
- [Document History](#document-history)

______________________________________________________________________

## Behave Best Practices

Following official Behave documentation patterns for test infrastructure:

### Fixtures and Test Isolation

**Use `use_fixture()` pattern**: Provides automatic cleanup via generator functions with `yield`

- **Generator pattern for fixtures**: Separate setup (before yield) and cleanup (after yield)
- **Cleanup is guaranteed**: Runs even on test failures
- **Fixture execution order**: Test run → Feature → Scenario (cleanup in reverse order)

### Test Isolation Strategy

- **Clean state per scenario**: Each scenario starts with fresh database and environment
- **Proper separation**: Fixtures for technical infrastructure (DB, server, browser), Background for business context (test data, preconditions)
- **Screenshot cleanup**: Clean screenshots directory before each scenario to prevent accumulation
- **Environment hooks**: `before_scenario()` for setup, `after_scenario()` for optional tasks (fixtures handle cleanup)

### Background Usage

- **Keep it brief**: Recommended ~4 lines maximum for readability
- **Business-focused**: Background is for business context users need to understand, not technical setup
- **Descriptive language**: Use vivid, story-like descriptions rather than technical details
- **Runs after hooks**: Background steps execute after `before_scenario()` but before scenario steps

### Practical Implementation

```python
# features/environment.py

from behave import fixture, use_fixture

@fixture
def clean_database(context):
    """Setup database - generator pattern ensures cleanup."""
    # Setup
    cleanup_database()
    initialize_fresh_database()

    yield context  # Scenario runs here

    # Cleanup (guaranteed to run)
    stop_server()
    cleanup_database()

def before_scenario(context, scenario):
    """Use fixtures for automatic cleanup."""
    use_fixture(clean_database, context)  # Registers cleanup automatically
    context.test_data = {}
```

### Key Benefits

- Eliminates manual cleanup code scattered across test files
- Cleanup happens in correct order (reverse of setup)
- Test failures don't leave dirty state
- Clear separation between infrastructure and business logic

______________________________________________________________________

## Playwright Best Practices for BDD Testing

**Reference:** [Playwright Python Documentation](https://playwright.dev/python/docs/intro)

This project uses Playwright for web UI automation in BDD scenarios. Following Playwright's official best practices ensures resilient, maintainable tests.

**Core Philosophy**: Playwright tests perform actions and assert expectations, with automatic waiting eliminating manual timeouts.

### Locator Strategy (Priority Order)

Playwright recommends user-facing locators that reflect how users perceive interfaces:

1. **Role-based locators** (best) - `page.get_by_role("button", name="Submit")`
1. **Text locators** - `page.get_by_text("Configuration Items")`
1. **Label locators** - `page.get_by_label("Name")`
1. **Placeholder/Alt/Title** - `page.get_by_placeholder("Search...")`
1. **Test ID locators** - `page.get_by_test_id("ci-list")` when user-facing options fail
1. **CSS/XPath** (last resort) - Brittle and fragile

**Anti-Pattern to Avoid**:

```python
# ❌ AVOID - Complex, brittle selectors
page.locator("#tsf > div:nth-child(2) > div.A8SBwf > div.RNNXgb...")

# ✅ PREFER - User-facing locators
page.get_by_role("searchbox", name="Search")
```

### Auto-Waiting Behavior

Playwright automatically waits for actionability checks before performing actions. **Do not use manual waits** unless absolutely necessary:

```python
# ❌ AVOID - Explicit waits
context.page.wait_for_timeout(500)  # Manual wait

# ✅ PREFER - Rely on auto-waiting
context.page.click('button[type="submit"]')  # Waits automatically
```

**Current Pattern** (our codebase uses some manual waits - consider reviewing):

- `features/steps/ci_search_steps.py` uses `wait_for_timeout(500)` after searches
- Evaluate if these are necessary or if Playwright's auto-waiting is sufficient

### Web-First Assertions with expect()

Use Playwright's `expect()` API for resilient assertions that retry until conditions are met:

```python
from playwright.sync_api import expect

# Web-first assertions (retry until timeout)
expect(page).to_have_title(re.compile("Roundup"))
expect(page.locator("table.list tbody tr")).to_have_count(5)
expect(page.get_by_role("alert")).to_be_visible()
expect(page.get_by_text("CI created")).to_contain_text("successfully")
```

**Current Pattern** (our codebase uses assert statements - consider migrating):

```python
# Current approach
assert actual_count == count, f"Expected {count} CIs"

# Recommended approach with web-first assertions
expect(page.locator("table.list tbody tr")).to_have_count(count)
```

### Test Isolation via Browser Context

Each Behave scenario should receive a fresh browser context for isolation. Our implementation follows this pattern:

```python
# features/environment.py
@fixture
def browser_context(context):
    """Create isolated browser context per scenario."""
    context.context = context.browser.new_context(**get_context_options())
    context.page = context.context.new_page()

    yield context.context

    # Cleanup
    context.page.close()
    context.context.close()
```

**Benefits**:

- Each scenario starts with clean cookies, local storage, and session
- Tests don't interfere with each other
- Similar to opening a new incognito window

### Locator Filtering and Chaining

Use filtering and chaining to narrow down elements:

```python
# Filter by text content
page.get_by_role("listitem").filter(has_text="Active").get_by_role("button").click()

# Chain locators for scoped searches
dialog = page.get_by_test_id("settings-dialog")
dialog.locator("input[name='name']").fill("web-server-01")
```

### Strictness Principle

Operations fail if multiple elements match. Use `.first`, `.last`, or `.nth()` only when necessary:

```python
# ❌ AVOID - Fragile when DOM changes
page.locator("button").first.click()

# ✅ PREFER - Specific selector
page.get_by_role("button", name="Submit").click()
```

### Screenshot and Debugging

Our implementation captures screenshots on test failures (configured in `features/environment.py`):

```python
def after_step(context, step):
    if step.status == "failed":
        screenshot_path = SCREENSHOT_DIR / f"{context.scenario_name}_{step.name}_FAILED.png"
        context.page.screenshot(path=str(screenshot_path), full_page=False)
```

**Best Practice**: Use viewport screenshots (`full_page=False`) for faster capture and smaller files.

**Debugging Tips**:

- Set `HEADLESS=false` environment variable to see browser UI
- Use `page.pause()` to inspect page state interactively
- Enable slow motion: `browser.launch(slow_mo=1000)` to observe actions
- Check console logs: `page.on("console", lambda msg: print(msg.text))`

### Performance Considerations

Our configuration uses reduced timeouts for small databases (configured in `tests/config/playwright_config.py`):

```python
TIMEOUTS = {
    "default": 10000,      # 10 seconds (reduced from 30s)
    "navigation": 5000,    # 5 seconds for page loads
    "action": 3000,        # 3 seconds for actions
}
```

### Integration with Behave

Our implementation integrates Playwright with Behave fixtures:

1. **Session-scoped browser**: Shared across scenarios (`before_all()`)
1. **Scenario-scoped context**: Fresh context per scenario (`before_scenario()`)
1. **Automatic cleanup**: Context/page closed via fixture pattern
1. **Tag-based activation**: Browser setup only for `@web-ui` scenarios

### BDD Step Definition Best Practices

```python
# features/steps/ci_steps.py
from playwright.sync_api import expect

@when('I navigate to the CI creation page')
def step_navigate_to_ci_creation(context):
    # Good: Clear, user-focused action
    context.page.goto(f"{context.base_url}/ci?@template=item")

@then('I should see {count:d} CIs in the results')
def step_verify_ci_count(context, count):
    # Consider migrating to web-first assertions
    ci_rows = context.page.locator("table.list tbody tr")
    expect(ci_rows).to_have_count(count)
```

### Migration Recommendations

1. **Review manual waits**: Evaluate `wait_for_timeout()` calls - many can be removed
1. **Adopt web-first assertions**: Migrate from `assert` to `expect()` for retrying behavior
1. **Improve locators**: Replace CSS selectors with role-based or text-based locators where possible
1. **Reduce timeouts**: Current 30s default is generous; 10s may be sufficient for small databases

### References

- [Playwright Python Docs](https://playwright.dev/python/docs/intro)
- [Locator Best Practices](https://playwright.dev/python/docs/locators)
- [Writing Tests](https://playwright.dev/python/docs/writing-tests)
- Project implementation: `features/environment.py`, `tests/config/playwright_config.py`

______________________________________________________________________

## Integration with Roundup

For Roundup-specific BDD testing patterns, see:

- **[Roundup + BDD Integration Patterns](roundup-development-practices.md#roundup--bdd-integration-patterns)** - Server lifecycle management, test data creation patterns, common pitfalls

This section covers:

- Server lifecycle management in BDD fixtures
- Test data creation patterns (CLI+Reindex, Web UI, REST API)
- Decision matrix for choosing appropriate patterns
- Common pitfalls and solutions specific to Roundup testing

______________________________________________________________________

## Related Documentation

- **[ADR-0002: Adopt Development Best Practices](../adr/0002-adopt-development-best-practices.md)** - Decision rationale for BDD adoption
- **[Roundup Development Best Practices](roundup-development-practices.md)** - Roundup-specific development patterns
  - See § Roundup + BDD Integration Patterns for Roundup-specific BDD testing
- **[Debugging BDD Scenarios](../howto/debugging-bdd-scenarios.md)** - Troubleshooting guide for test failures

______________________________________________________________________

## Document History

| Date       | Version | Changes                                                      |
| ---------- | ------- | ------------------------------------------------------------ |
| 2025-11-18 | 1.0     | Initial document created by extracting content from ADR-0002 |

______________________________________________________________________

**For questions or improvements to this document, please create an issue in the project tracker.**
