<!--
SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
SPDX-License-Identifier: MIT
-->

# How-to: Debugging BDD Scenarios

This guide provides troubleshooting strategies for Behave + Playwright BDD scenarios in the Pasture Management System.

## Overview

BDD scenarios can fail for various reasons beyond functional bugs. This guide focuses on debugging test infrastructure issues, particularly with Playwright browser automation and Roundup issue tracker integration.

## Common Issues and Solutions

### Issue 1: Playwright Finds 0 Elements Despite Visible Rendering

**Symptoms:**

- Test assertion fails: "Expected N items, but found 0"
- Screenshot shows items ARE visible
- Manual browser testing works correctly

**Root Causes:**

1. **Timing Issue**: DOM not fully rendered when selector runs
1. **Selector Mismatch**: Selector doesn't match actual HTML structure
1. **Wrong Element**: Selecting parent/child instead of target element

**Solution - Timing Issues:**

```python
# ❌ BAD: Only wait for network idle
context.page.select_option('select[name="status"]', status_id)
context.page.wait_for_load_state("networkidle")

# ✅ GOOD: Add buffer for template rendering
context.page.select_option('select[name="status"]', status_id)
context.page.wait_for_load_state("networkidle")
context.page.wait_for_timeout(500)  # Roundup TAL processing time
```

**Why This Happens with Roundup:**

- Roundup uses TAL (Template Attribute Language) for server-side rendering
- `networkidle` fires when network requests complete
- TAL still needs time to render the final HTML
- 500ms buffer allows template engine to complete

**Solution - Selector Issues:**

```python
# ❌ BAD: Complex selector with assumptions about href format
ci_links = context.page.locator('a[href*="ci"]')
for i in range(ci_links.count()):
    href = link.get_attribute("href")
    if re.match(r"^ci\d+$", href):  # Assumes relative URLs
        ci_item_links.append(link)

# ✅ GOOD: Direct structural selector
ci_name_links = context.page.locator('table.list tbody tr td:nth-child(2) a')
actual_count = ci_name_links.count()
```

**Why Direct Selectors Work Better:**

- Playwright may return absolute URLs: `http://localhost:9080/pms/ci1`
- Relative path assumptions (`ci1`) fail with absolute URLs
- Structural selectors (nth-child) work regardless of URL format
- Less brittle - doesn't depend on href patterns

### Issue 2: Form Auto-Submit Race Conditions

**Symptoms:**

- Dropdown filter selected but no results shown
- Filter appears to work in manual testing
- Inconsistent test results (flaky tests)

**Root Cause:**
Roundup forms with `onchange="this.form.submit()"` trigger page reload, but Playwright may check DOM before new page renders.

**Solution:**

```python
@when('I filter by type "{ci_type}"')
def step_filter_by_type(context, ci_type):
    """Filter CIs by type."""
    type_id = get_type_id(ci_type)

    # Select option triggers auto-submit
    context.page.select_option('select[name="type"]', type_id)

    # Wait for page reload AND rendering
    context.page.wait_for_load_state("networkidle")  # Network complete
    context.page.wait_for_timeout(500)                # TAL rendering
```

**Alternative - Wait for Specific Element:**

```python
# If you know what should appear after filter
context.page.select_option('select[name="type"]', type_id)
context.page.wait_for_selector('table.list tbody tr', timeout=5000)
```

### Issue 3: Context Object Attribute Errors

**Symptoms:**

```
AttributeError: 'Context' object has no attribute 'step'
```

**Root Cause:**
Attempting to access Behave context attributes that don't exist.

**Solution:**

```python
# ❌ BAD: context.step doesn't exist in Behave
@when('I sort by "{column}" ascending')
@when('I sort by "{column}" descending')
def step_sort(context, column):
    ascending = "ascending" in context.step.name  # ERROR!

# ✅ GOOD: Use separate step functions
@when('I sort by "{column}" ascending')
def step_sort_asc(context, column):
    context.page.click(f'th a:has-text("{column}")')

@when('I sort by "{column}" descending')
def step_sort_desc(context, column):
    # Click twice for descending
    context.page.click(f'th a:has-text("{column}")')
    context.page.wait_for_timeout(300)
    context.page.click(f'th a:has-text("{column}")')
```

### Issue 4: Screenshot Shows Success but Test Fails

**Symptoms:**

- Failure screenshot shows correct data
- Count/assertion still fails
- Selector working in screenshot but not in test

**Explanation:**
Screenshots are captured AFTER the failing assertion, showing the final page state. The selector may have worked eventually, but failed at the assertion moment.

**Debugging Strategy:**

1. Add debug screenshot BEFORE assertion:

```python
@then("I should see {count:d} CIs in the results")
def step_verify_ci_count(context, count):
    # Debug: capture BEFORE checking
    context.page.screenshot(path="debug_before_count.png")

    ci_links = context.page.locator('table.list tbody tr td:nth-child(2) a')
    actual_count = ci_links.count()

    assert actual_count == count, f"Expected {count}, found {actual_count}"
```

2. Add intermediate waits:

```python
# Wait for table to exist
context.page.wait_for_selector('table.list', timeout=5000)

# Then count rows
ci_links = context.page.locator('table.list tbody tr td:nth-child(2) a')
actual_count = ci_links.count()
```

## Diagnostic Tools

### Tool 1: Debug Script for Selector Testing

Create `debug_selectors.py` to test selectors interactively:

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    # Login and navigate
    page.goto("http://localhost:9080/pms/")
    page.fill('input[name="__login_name"]', "admin")
    page.fill('input[name="__login_password"]', "admin")
    page.click('input[type="submit"]')

    # Test your selector
    elements = page.locator('YOUR_SELECTOR_HERE')
    print(f"Found {elements.count()} elements")

    # Inspect attributes
    for i in range(elements.count()):
        elem = elements.nth(i)
        print(f"  [{i}] href={elem.get_attribute('href')}")
        print(f"       text={elem.text_content()}")

    browser.close()
```

### Tool 2: HTML Content Inspection

```python
# In step definition
@then("I should see {count:d} CIs")
def step_verify(context, count):
    # Dump HTML for inspection
    html = context.page.content()
    with open('debug.html', 'w') as f:
        f.write(html)

    # Or just the table
    table_html = context.page.locator('table.list').inner_html()
    print(f"\nTable HTML:\n{table_html}\n")
```

### Tool 3: Wait State Debugging

```python
# Add verbose wait logging
context.page.select_option('select[name="type"]', type_id)
print("Selected option, waiting for networkidle...")

context.page.wait_for_load_state("networkidle")
print("Network idle achieved, waiting for rendering...")

context.page.wait_for_timeout(500)
print("Rendering wait complete")

# Check what's actually there
count = context.page.locator('table.list tbody tr').count()
print(f"Found {count} table rows")
```

## Best Practices

### 1. Use Structural Selectors

```python
# ✅ GOOD: Structure-based
context.page.locator('table.list tbody tr td:nth-child(2) a')

# ⚠️ RISKY: Attribute-based with assumptions
context.page.locator('a[href^="ci"]')  # Assumes relative URLs
```

### 2. Layer Your Waits

```python
# Network complete
context.page.wait_for_load_state("networkidle")

# Template rendering
context.page.wait_for_timeout(500)

# Specific element (optional)
context.page.wait_for_selector('table.list tbody', state='visible')
```

### 3. Fail Fast with Informative Messages

```python
# ❌ BAD: Generic assertion
assert actual == expected

# ✅ GOOD: Detailed context
assert actual == expected, (
    f"Expected {expected} CIs, found {actual}. "
    f"Selector: 'table.list tbody tr td:nth-child(2) a'. "
    f"Check screenshot for visual confirmation."
)
```

### 4. Test in Isolation

```python
# Ensure clean state before each scenario
def before_scenario(context, scenario):
    # Reinitialize database
    _reinitialize_database(context)

    # Fresh browser context
    context.context = context.browser.new_context()
    context.page = context.context.new_page()
```

## Roundup-Specific Considerations

### TAL Template Rendering Timing

Roundup's TAL templates process server-side but HTML generation takes time:

- **Fast**: Static HTML sections
- **Medium**: Simple TAL expressions (`tal:content`)
- **Slow**: Complex TAL logic, loops, database queries

**Recommendation**: Use 500ms buffer after `networkidle` for pages with:

- Database-driven lists
- Filtered results
- Complex forms

### URL Structure

Roundup generates both relative and absolute URLs:

```html
<!-- Relative -->
<a href="ci1">CI Name</a>

<!-- Absolute (from some contexts) -->
<a href="http://localhost:9080/pms/ci1">CI Name</a>
```

**Recommendation**: Use structural selectors, not href pattern matching.

### Form Auto-Submit Behavior

Roundup classic templates often use:

```html
<select name="type" onchange="this.form.submit()">
```

This triggers full page reload, not AJAX. Your tests must account for:

1. Form submission
1. Page navigation
1. Template re-rendering

## Troubleshooting Checklist

When a BDD scenario fails:

- [ ] Check screenshot - is the expected data visible?
- [ ] Review selector - does it match actual HTML structure?
- [ ] Verify timing - does page need more time to render?
- [ ] Inspect HTML - dump page content and examine manually
- [ ] Test selector - use debug script to test selector in isolation
- [ ] Check waits - are you waiting for the right states?
- [ ] Verify clean state - is database initialized properly?
- [ ] Run manually - does it work in real browser with same steps?

## Performance Considerations

### Wait Timeout Trade-offs

```python
# ⚠️ TOO AGGRESSIVE: May fail on slow systems
context.page.wait_for_timeout(100)

# ✅ BALANCED: Works on most systems
context.page.wait_for_timeout(500)

# ❌ TOO CONSERVATIVE: Slows down test suite
context.page.wait_for_timeout(2000)
```

**Recommendation**: Start with 500ms, adjust based on:

- CI/CD environment speed
- Database query complexity
- Template rendering complexity

### Selective Screenshot Capture

```python
# Only capture on failure (default in environment.py)
def after_step(context, step):
    if step.status == "failed":
        context.page.screenshot(path=screenshot_path)

# Optional: Capture on pass for documentation
if os.getenv("SCREENSHOT_ON_PASS", "false").lower() == "true":
    context.page.screenshot(path=screenshot_path)
```

## Related Documentation

- [BDD Testing Best Practices](../reference/bdd-testing-best-practices.md) - Comprehensive Behave fixtures and Playwright best practices
- [Roundup Development Best Practices](../reference/roundup-development-practices.md)
- [BDD Testing Strategy](../explanation/bdd-testing-strategy.md) (planned)
- [Playwright Configuration](../../tests/config/playwright_config.py)
- [Behave Environment Setup](../../features/environment.py)

## Sprint 6 Lessons Learned

**Issue**: CI search BDD scenarios failed with "Expected N CIs, found 0"
**Root Cause**: Playwright selector mismatch + timing issues with TAL rendering
**Solution**: Direct structural selectors + 500ms post-networkidle wait
**Result**: 5/11 scenarios passing (from 0/11)

See [Sprint 6 Backlog](../sprints/sprint-6-backlog.md) for full context.

## Getting Help

If you encounter issues not covered here:

1. **Check Behave docs**: https://behave.readthedocs.io/
1. **Check Playwright docs**: https://playwright.dev/python/
1. **Roundup community**: https://www.roundup-tracker.org/
1. **Project issues**: File in project tracker with:
   - Failing scenario name
   - Screenshot
   - HTML dump
   - Selector used
   - Expected vs actual results
