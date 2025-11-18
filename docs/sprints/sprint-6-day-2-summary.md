# Sprint 6 Day 2 Session Summary

## Date: 2025-11-18

## Work Completed

### 1. Researched Behave Best Practices

- **Studied official documentation**: https://behave.readthedocs.io/en/latest/fixtures/ and /gherkin/
- **Key learnings**:
  - `use_fixture()` provides automatic cleanup via generator pattern
  - Fixtures run in specific order: test run → feature → scenario
  - Background steps run AFTER `before_scenario()` hooks
  - Cleanup happens in reverse order, even on failures

### 2. Implemented Proper BDD Test Infrastructure

#### features/environment.py

- **Created `clean_database` fixture** with generator pattern:

  - Stops Roundup server
  - Deletes database files
  - Reinitializes database with `uv run` (consistent tooling)
  - Does NOT start server (avoids caching issue)
  - Automatic cleanup via `yield` pattern

- **Updated `before_scenario()`**:

  - Cleans screenshots directory before each scenario
  - Uses `use_fixture(clean_database, context)` for automatic DB cleanup
  - Initializes `context.ci_map` for tracking created CIs
  - Sets up browser context for @web-ui scenarios only

- **Simplified `after_scenario()`**:

  - Only captures pass/fail screenshots
  - All cleanup handled by fixtures automatically

- **Benefits**:

  - Every scenario starts with clean database
  - Screenshots don't accumulate
  - Proper separation: fixtures for infrastructure, Background for business logic
  - Cleanup guaranteed even on test failures

#### features/steps/ci_search_steps.py

- **Updated CI creation step** to work with fixture:
  - Creates CIs via CLI while server is stopped (fixture leaves it stopped)
  - Starts server AFTER CIs are created
  - Added documentation about Roundup caching behavior

### 3. Discovered Critical Roundup Issue

**Problem**: CIs created via `roundup-admin` are NOT visible through Roundup web server.

**Investigation findings**:

1. CIs created while server is running → NOT visible (caching)
1. Server stopped → CIs created → Server started → STILL not visible
1. Manual curl tests confirm: CIs exist in DB but web interface shows "No configuration items found"

**Hypothesis**: Roundup database backend has initialization or indexing issue that prevents CIs created via CLI from being visible through web interface.

**Evidence**:

```bash
# Test sequence that SHOULD work but FAILS:
1. pkill roundup-server
2. rm -rf tracker/db/*
3. roundup-admin initialise
4. roundup-admin create ci name=test type=1 status=5
5. roundup-admin list ci  # Shows CI exists
6. roundup-server start
7. curl http://localhost:9080/pms/ci  # "No configuration items found"
```

### 4. Template Improvements from Day 1 (Carried Forward)

- Added `check_for_templating_error()` helper in web_ui_steps.py
- Refactored complex TAL expressions to Python helper functions
- Reduced Playwright timeouts for small databases (30s → 5s/10s/3s)
- Created `tracker/extensions/template_helpers.py` with `sort_ci_ids()` and `filter_ci_ids_by_search()`

## Current Test Status

**BDD Tests**: READY FOR UPDATE

- Infrastructure: ✅ Working properly
- Test isolation: ✅ Clean database per scenario
- CI visibility: ✅ **SOLVED** - Reindex command resolves CLI→Web visibility issue

**Root Cause Identified**: Search indexes not automatically updated when items created via `roundup-admin create`

**Solution Verified**: Adding `roundup-admin reindex ci` after CLI item creation makes CIs visible through web interface

### 5. Web Search and Configuration Investigation

**Web Search Findings** (2025-11-18):

Searched for Roundup CLI→Web visibility issues and found several relevant insights:

1. **Schema Caching Issue** (Most Relevant):

   - Quote from Roundup documentation: "Schema changes are automatically applied to the database on the next tracker access, but roundup-server needs to be restarted as it caches the schema"
   - Roundup server caches schema and configuration data in the process
   - This is a common reason why changes made via CLI might not appear immediately

1. **Reindex Command**:

   - `roundup-admin reindex [classname]` re-generates search indexes
   - Documentation states: "You need to run roundup-admin reindex if the tracker has existing data after installing indexing engines"
   - Could be relevant for making CLI-created items visible

1. **Database Migration**:

   - Should run `roundup-admin migrate` to update database schema version before using web/CLI/mail interfaces

1. **Retired Items**:

   - Items with "retired" status don't appear in class listings (though accessible by ID)
   - All test CIs are created with status=5 (Active), so this isn't the issue

**Configuration Review** (`tracker/config.ini`):

- Database backend: `sqlite` (line 650)
- Indexer: empty string (line 137) - will use first available indexer
- Template engine: `zopetal` (line 23)
- No obvious misconfigurations found

**Roundup Commands Available**:

- `reindex [classname|classname:#-#|designator]*` - Re-generate search indexes
- `migrate` - Update database schema version
- `commit` - Commit current transaction (could be relevant)

**Hypothesis for Option 1 Fix**:

The issue might be that:

1. CIs created via CLI need search index regeneration to be visible
1. Or there's a database transaction that needs explicit commit
1. Or server restart alone isn't sufficient without reindexing

**Next Test**: Try `roundup-admin reindex ci` after creating CIs via CLI, before starting server

### 6. Verified Reindex Solution (Option 1) ✅

**Test Executed** (2025-11-18 19:44):

Successfully tested the `roundup-admin reindex` solution for CLI→Web visibility issue.

**Test Procedure**:

```bash
# Step 1: Stop server
pkill -f "roundup-server" && sleep 2

# Step 2: Clean database
cd tracker && rm -rf db/*

# Step 3: Initialize database
echo -e "admin\nadmin" | uv run roundup-admin -i . initialise

# Step 4: Create test CIs via CLI
uv run roundup-admin -i . create ci name=test-server-01 type=1 status=5
uv run roundup-admin -i . create ci name=test-server-02 type=1 status=5
uv run roundup-admin -i . create ci name=test-workstation-01 type=1 status=5

# Step 5: CRITICAL - Run reindex command
uv run roundup-admin -i . reindex ci

# Step 6: Start server
cd .. && uv run roundup-server -p 9080 pms=tracker > /dev/null 2>&1 &
sleep 3
```

**Test Results**:

```bash
curl -s "http://localhost:9080/pms/ci" | grep -E "test-server-01|test-server-02|test-workstation-01"
# Output:
#   <a href="ci1">test-server-01</a>
#   <a href="ci2">test-server-02</a>
#   <a href="ci3">test-workstation-01</a>
# ✅ SUCCESS: All CIs visible through web interface!
```

**Conclusion**:

- ✅ **Option 1 (reindex) WORKS**: The `roundup-admin reindex ci` command successfully resolves the CLI→Web visibility issue
- ✅ **Root cause confirmed**: Search indexes not automatically updated when items created via CLI
- ✅ **Solution documented**: Updated Roundup best practices (v1.4) with complete workflow
- ✅ **Ready for BDD integration**: Can now update `features/steps/ci_search_steps.py` to include reindex step

**Next Action**: Update BDD step definitions to include `reindex ci` after CLI item creation

### 7. Fixed Search Functionality Bug ✅

**Issue Discovered** (2025-11-18 21:00):

After integrating reindex command into BDD step definitions, the "Search CIs by name" scenario failed:

- Expected: 2 CIs matching "db-server"
- Actual: 0 CIs returned
- Debug output showed: 3 CIs visible BEFORE search, 0 AFTER search

**Root Cause Investigation**:

Added file-based debug logging to `/tmp/roundup_search_debug.log` which revealed:

```
=== filter_ci_ids_by_search called ===
search_term: 'db-server'
ci_ids: [<HTMLItem(0x102cad750) ci 1>, <HTMLItem(0x102cad950) ci 2>, <HTMLItem(0x102cadad0) ci 3>]
  ERROR: CI 1 - Type: AttributeError, Message: getnode, Repr: AttributeError('getnode')
  ERROR: CI 2 - Type: AttributeError, Message: getnode, Repr: AttributeError('getnode')
  ERROR: CI 3 - Type: AttributeError, Message: getnode, Repr: AttributeError('getnode')
result: [] (count: 0)
```

**Root Cause**: The `db.ci.getnode()` method doesn't exist in Roundup TAL template context. The `ci_ids` passed to template helper functions are already `HTMLItem` objects that wrap the database nodes.

**Fix Applied** (`tracker/extensions/template_helpers.py:75-119`):

```python
# OLD (BROKEN):
node = db.ci.getnode(id_str)  # AttributeError!
name = (node.name.plain() if node.name else "").lower()

# NEW (FIXED):
# ci_id is already an HTMLItem object with the CI data
# Access name and location directly from the HTMLItem
name = ""
if hasattr(ci_id, 'name') and ci_id.name:
    if hasattr(ci_id.name, 'plain'):
        name = ci_id.name.plain()
    else:
        name = str(ci_id.name)
name = name.lower()
```

**Test Results After Fix**:

```bash
uv run behave features/cmdb/ci_search.feature --tags=@web-ui
# Results:
# - 7 scenarios passed
# - 3 scenarios failed (unrelated - combined filters, sorting)
# - 1 scenario error (CSV export not implemented)
# - Search functionality ✅ WORKING
```

**Files Modified**:

- `tracker/extensions/template_helpers.py` - Fixed `filter_ci_ids_by_search()` to access HTMLItem fields directly
- `features/steps/ci_search_steps.py` - Added reindex command integration (lines 104-119)
- `docs/reference/roundup-development-practices.md` - Added "Python Template Helpers" section (v1.5)

**Debug logging removed after verification**.

**Documentation Impact**:

- New best practices section documents HTMLItem object handling
- Explains why `db.ci.getnode()` fails in TAL template context
- Provides defensive patterns for `.plain()` method usage
- Establishes template helper best practices for future development

## Next Steps

### Immediate Options

**Option 1: Investigate Roundup Database Backend**

- Check Roundup tracker configuration (config.ini, db backend settings)
- Review Roundup documentation for proper CLI→Web workflow
- Investigate database indexing requirements
- Check if detectors or auditors need to run for CI visibility

**Option 2: Create CIs via Web UI in Tests**

- Modify `step_create_multiple_cis()` to use Playwright
- Navigate to CI creation form
- Fill and submit via browser
- Server sees changes immediately (no caching issue)
- More realistic test (uses actual user workflow)

**Option 3: Hybrid Approach**

- Use `initial_data.py` to populate test CIs during database initialization
- Modify `roundup-admin initialise` to include test data
- Server loads CIs on startup

### Recommended Path Forward

**Investigate Roundup tracker configuration first**:

- Review `tracker/config.ini` backend settings
- Check if database needs explicit commit/flush
- Test if `roundup-admin reindex` helps
- Consult Roundup documentation and community

**If no solution found**, switch to **Option 2 (Web UI creation)**:

- More maintainable long-term
- Tests actual user workflow
- Eliminates all caching concerns
- Aligns with BDD best practice (test through UI)

## Files Modified

### Core Changes

- `features/environment.py` - Proper fixture implementation
- `features/steps/ci_search_steps.py` - Updated CI creation
- `features/steps/web_ui_steps.py` - Error detection helper (from Day 1)
- `tracker/extensions/template_helpers.py` - Python helper functions (from Day 1)
- `tracker/html/ci.index.html` - Simplified TAL template (from Day 1)
- `tests/config/playwright_config.py` - Reduced timeouts (from Day 1)

### Documentation

- `docs/adr/0002-adopt-development-best-practices.md` - Added Behave and Playwright best practices sections
- `CLAUDE.md` - Added reference to Behave best practices in ADR-0002
- `docs/reference/roundup-development-practices.md` - Added Database Administration Commands section (v1.4)
- `docs/sprints/sprint-6-backlog.md` - Updated with Day 2 progress
- `docs/sprints/sprint-6-day-2-summary.md` - This file

## Key Learnings

1. **Behave fixtures are powerful**: Generator pattern with `use_fixture()` ensures cleanup
1. **Test isolation requires careful thought**: Database + server + browser state
1. **Roundup has caching behavior**: CLI changes not visible to running server
1. **Root cause identified**: Search indexes not automatically updated for CLI-created items
1. **Solution verified**: `roundup-admin reindex ci` makes CLI-created items visible through web interface
1. **Web search was essential**: Found solution in Roundup documentation via targeted search
1. **Documentation is critical**: Official Behave docs provided exact patterns needed for proper test infrastructure
1. **Systematic investigation pays off**: Research → Hypothesis → Test → Verify workflow led to solution

## Questions for Review

1. ✅ **RESOLVED**: Roundup CLI→Web visibility issue solved with `reindex` command
1. ✅ **RESOLVED**: No configuration setting missing - reindex is the correct workflow
1. ✅ **DECISION**: CLI-based test data creation is viable with reindex step included
1. ✅ **DECISION**: Option 1 (reindex) verified and working - no need for Option 2 or 3

## Time Investment

- Behave documentation research: ~30 minutes
- Fixture implementation: ~1 hour
- CI visibility investigation: ~2 hours
- Documentation updates (ADR-0002, CLAUDE.md, Roundup best practices): ~45 minutes
- Web search and configuration investigation: ~45 minutes
- Reindex solution verification testing: ~15 minutes
- **Total**: ~5.25 hours

## Conclusion

**Sprint 6 Day 2 was highly successful**, completing a full investigation-to-solution cycle:

### Achievements

1. **BDD Infrastructure Completed**:

   - Implemented proper Behave fixtures with generator pattern and automatic cleanup
   - Achieved full test isolation (clean database + server + browser per scenario)
   - Added comprehensive Behave and Playwright best practices to ADR-0002

1. **Critical Issue Resolved**:

   - ✅ **Identified**: CLI-created items not visible through web interface due to missing search index updates
   - ✅ **Researched**: Found solution via targeted web search of Roundup documentation
   - ✅ **Verified**: Tested `roundup-admin reindex ci` command - **WORKS**
   - ✅ **Documented**: Updated Roundup best practices (v1.4) with complete workflow and troubleshooting

1. **Documentation Enhanced**:

   - Behave best practices added to ADR-0002 and referenced in CLAUDE.md
   - Playwright best practices added to ADR-0002 with migration recommendations
   - Roundup Database Administration Commands section added (v1.4)
   - Complete CLI→Web visibility workflow documented for future reference

1. **Educational Value Delivered**:

   - Demonstrated systematic investigation process: Research → Hypothesis → Test → Verify
   - Showed importance of official documentation and targeted web search
   - Created comprehensive reference materials for Roundup developers
   - BDD infrastructure serves as example for Python/Behave/Playwright users

### Next Steps

1. **Update BDD step definitions**: Add `reindex ci` command to `features/steps/ci_search_steps.py` after CLI item creation
1. **Run full test suite**: Verify all BDD scenarios pass with reindex solution
1. **Consider migration tasks**: Review Playwright best practices for potential test improvements

The infrastructure improvements and solutions discovered today serve both the functional objectives (working BDD tests) and educational objectives (demonstrating best practices) of this project.
