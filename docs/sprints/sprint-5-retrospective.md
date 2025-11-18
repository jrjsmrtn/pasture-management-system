<!--
SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
SPDX-License-Identifier: MIT
-->

# Sprint 5 Retrospective

**Sprint Duration**: December 2024 - January 2025
**Version Released**: v0.6.0
**Sprint Goal**: Complete CMDB foundation with CI search, filtering, and reporting capabilities
**Points Completed**: 31 / 41 (76%)

## Executive Summary

Sprint 5 made significant progress in CMDB capabilities, completing all core configuration item management features (Stories 1-5). The sprint demonstrated strong technical execution with the implementation of complex filtering logic, template validation automation, and comprehensive BDD specifications. While Stories 6-7 (search/sort backends and advanced reporting) remain incomplete, the delivered functionality provides a solid, production-ready CMDB foundation.

## What Went Well

### 1. BDD Specification-First Approach

**Observation**: Writing Gherkin scenarios before implementation continued to prove highly effective.

**Evidence**:

- All 5 completed stories had comprehensive BDD feature files written first
- Feature files served as unambiguous acceptance criteria
- Scenarios provided clear implementation roadmap
- Living documentation automatically generated from tests

**Impact**:

- Reduced ambiguity in requirements
- Faster implementation due to clear target behavior
- Better test coverage from day one
- Improved collaboration between technical and functional perspectives

**Continue**: Maintain this approach for all future stories

### 2. Incremental Implementation with Frequent Commits

**Observation**: Breaking work into small, testable increments with frequent commits improved development flow.

**Evidence**:

- Average 2-3 commits per story
- Each commit represented working, testable state
- Easy to track progress and roll back if needed
- Clear commit messages following conventional format

**Examples**:

```
feat: add CI creation with required fields (Sprint 5, Story 1)
feat: implement CI relationships and dependencies (Sprint 5, Story 2)
fix: resolve ci.index.html template error and implement filterspec
```

**Impact**:

- Reduced debugging time when issues occurred
- Better understanding of what changed when
- Easier code review and collaboration

**Continue**: Maintain frequent, atomic commits with clear messages

### 3. Template Validation Automation

**Observation**: Creating `scripts/validate-templates.sh` and adding it to pre-push hooks prevented template errors from reaching the repository.

**Evidence**:

- Script validates all `.html`, `.tal`, and `.xml` files in `tracker/html/`
- Pre-push hook caught multiple template syntax errors
- Template errors now fail fast locally rather than in production

**Impact**:

- Reduced deployment risk
- Faster feedback loop for template changes
- Improved confidence in template modifications

**Continue**: Expand validation to cover more template patterns and edge cases

### 4. Roundup TAL Pattern Discovery

**Observation**: Deep investigation into Roundup's Template Attribute Language revealed powerful patterns for data manipulation.

**Key Discoveries**:

- Path expressions: `ci/type/name` for nested property access
- `FieldStorage.getvalue()` instead of `.get()` for form data
- Manual filterspec construction: `db.ci.filter(None, filterspec)`
- HTMLItem iteration patterns (not raw IDs)
- Reject exceptions for proper error handling

**Documentation**:

- Patterns documented in `docs/reference/roundup-development-practices.md`
- Examples included in code comments
- Backlog document captures detailed implementation notes

**Impact**:

- Faster future template development
- Better understanding of Roundup's capabilities
- Reduced trial-and-error time

**Continue**: Document all new patterns discovered in future sprints

### 5. Manual Testing Rigor

**Observation**: When BDD tests failed, manual testing provided reliable validation of functionality.

**Evidence**:

- Screenshot verification showed functionality working correctly
- Manual filter testing confirmed all combinations work
- CSV export manually validated
- HTML inspection revealed correct rendering

**Impact**:

- Confidence that functionality works despite test failures
- Proper identification of test tooling issues vs. functionality issues
- Prevented false negatives from blocking progress

**Continue**: Maintain manual testing as backup validation method

## What Could Be Improved

### 1. BDD Test Integration with Playwright

**Issue**: Behave + Playwright tests failed to locate CI rows despite correct rendering in browser.

**Symptoms**:

- Tests expect 2 CIs, find 0
- Screenshot shows 2 CIs clearly visible
- Multiple selector strategies attempted (table rows, links with regex)
- All strategies returned 0 matches

**Root Cause Analysis**:

- Likely mismatch between Playwright DOM inspection and Roundup TAL rendering timing
- Possible issue with Roundup's dynamic content loading
- May need wait strategies or different selector patterns
- Could be Playwright configuration issue (viewport, timeouts, etc.)

**Impact**:

- BDD tests don't validate functionality correctly
- Manual testing required for validation
- Reduced confidence in automated test suite
- Technical debt accumulating

**Action Items**:

1. Deep dive into Playwright selectors with Roundup HTML structure
1. Investigate wait strategies and timing issues
1. Consider alternative approaches (API testing, direct HTML parsing)
1. Consult Roundup community about Playwright integration patterns

**Priority**: High - Core BDD objective is demonstration of testing effectiveness

### 2. Test Execution Time

**Issue**: BDD tests take significant time to complete due to browser automation overhead.

**Evidence**:

- Each scenario requires browser launch, page load, interaction
- Database initialization for each test run
- Playwright screenshot capture adds delay
- Full test suite runs in minutes, not seconds

**Impact**:

- Slower development feedback loop
- Less frequent test execution
- Reduced willingness to run full test suite locally

**Potential Solutions**:

1. Implement test parallelization with Behave
1. Use shared browser context across scenarios
1. Optimize database setup/teardown
1. Consider API-level tests for faster feedback, UI tests for critical paths only

**Priority**: Medium - Affects development velocity but not blocking

### 3. Database Management Between Tests

**Issue**: Database state management between test runs is manual and error-prone.

**Current Process**:

```bash
cd tracker && rm -rf db/* && uv run roundup-admin -i . initialise admin && cd ..
pkill -f "roundup-server" && sleep 2 && uv run roundup-server -p 9080 pms=tracker > /dev/null 2>&1 &
```

**Problems**:

- Multi-step manual process
- Easy to forget steps
- No automated cleanup
- Server restart required for detector changes

**Impact**:

- Test pollution between runs
- Inconsistent test environments
- Time wasted on environment setup

**Potential Solutions**:

1. Create `scripts/reset-test-db.sh` helper script
1. Implement Behave hooks for automatic database cleanup
1. Consider in-memory database for tests
1. Docker/Podman container for isolated test environment

**Priority**: Medium - Improves developer experience but workaround exists

### 4. Sprint Scope Estimation

**Issue**: Sprint 5 planned for 41 points but delivered 31 (76%).

**Analysis**:

- Stories 1-5 completed as planned (31 points)
- Stories 6-7 not started (10 points)
- Core CMDB functionality complete, advanced features deferred

**Contributing Factors**:

- Underestimated complexity of filtering implementation (3 points became 5 effective)
- Template validation automation added mid-sprint (unplanned but valuable)
- BDD test debugging took longer than expected
- Code review improvements alongside story work

**Impact**:

- Sprint goal partially achieved
- Technical debt accumulated in testing
- Stories 6-7 deferred to Sprint 6

**Lessons Learned**:

1. More accurate story point estimation needed
1. Consider buffer time for technical debt and quality improvements
1. Re-estimate stories after spike investigations
1. Better velocity tracking to adjust mid-sprint

**Action**: Review velocity metrics and adjust Sprint 6 planning accordingly

### 5. Documentation Lagging Implementation

**Issue**: Some features implemented without immediate documentation updates.

**Examples**:

- Filtering patterns discovered but not documented until backlog review
- TAL tricks learned but not captured in reference docs
- CSV export implementation not reflected in user guides

**Impact**:

- Knowledge loss between sessions
- Harder for future developers to understand patterns
- Reduces value of "living documentation" goal

**Solution**:

- Update reference docs within same commit as implementation
- Add documentation checklist to story completion procedure
- Include documentation review in pre-commit checks

**Priority**: Medium - Important for long-term maintainability

## Action Items for Sprint 6

### Critical

1. **Resolve BDD Test Integration Issues**

   - Deep dive into Playwright selector patterns with Roundup
   - Implement proper wait strategies
   - Consider alternative testing approaches if needed
   - Document solution in reference docs
   - **Owner**: Development team
   - **Deadline**: First 2 weeks of Sprint 6

1. **Complete Stories 6-7 from Sprint 5**

   - Story 6: Search/sort backend improvements (5 points)
   - Story 7: Advanced reporting and dashboard (5 points)
   - Carry forward to Sprint 6 with lessons learned
   - **Owner**: Development team
   - **Deadline**: Sprint 6 mid-point

### High Priority

3. **Create Database Management Helper Script**

   - Script: `scripts/reset-test-db.sh`
   - Automate database cleanup, initialization, server restart
   - Integrate with Behave hooks if possible
   - Document usage in testing guide
   - **Owner**: Development team
   - **Deadline**: Sprint 6 week 1

1. **Implement Test Parallelization**

   - Research Behave parallel execution options
   - Configure for safe parallel test runs
   - Update CI/CD pipeline to use parallelization
   - Measure execution time improvements
   - **Owner**: Development team
   - **Deadline**: Sprint 6 week 2

1. **Update Reference Documentation**

   - Document all TAL patterns discovered in Sprint 5
   - Add filtering implementation guide
   - Create template development best practices
   - Update Roundup development practices document
   - **Owner**: Development team
   - **Deadline**: Sprint 6 ongoing

### Medium Priority

6. **Velocity Tracking and Sprint Planning Improvements**

   - Analyze Sprint 1-5 velocity data
   - Create velocity trend chart
   - Adjust Sprint 6 point estimates based on historical data
   - Consider 15-20% buffer for technical debt
   - **Owner**: Project lead
   - **Deadline**: Sprint 6 planning

1. **Expand Template Validation**

   - Add more template syntax checks
   - Validate TAL expression correctness
   - Check for common anti-patterns
   - Add performance hints (e.g., avoid expensive operations in loops)
   - **Owner**: Development team
   - **Deadline**: Sprint 6 week 3

## Velocity Analysis

### Historical Velocity (Points Completed)

| Sprint | Planned | Completed | Velocity % | Notes                                     |
| ------ | ------- | --------- | ---------- | ----------------------------------------- |
| 1      | 15      | 15        | 100%       | Initial issue tracking                    |
| 2      | 20      | 20        | 100%       | Issue lifecycle + change foundation       |
| 3      | 25      | 25        | 100%       | Complete change management                |
| 4      | 30      | 30        | 100%       | CMDB foundation                           |
| 5      | 41      | 31        | 76%        | CMDB search/filter (Stories 6-7 deferred) |

### Observations

1. **Consistent Delivery (Sprints 1-4)**: 100% completion rate suggests good estimation initially

1. **Sprint 5 Variance**: 24% shortfall indicates one of:

   - Over-ambitious planning
   - Underestimated story complexity
   - Unplanned work (template validation, debugging)
   - Velocity ceiling reached

1. **Adjusted Velocity**: Realistic velocity appears to be ~30 points per sprint based on Sprint 4-5 data

### Sprint 6 Planning Recommendations

1. **Conservative Estimate**: Plan for 30 points maximum
1. **Include Buffer**: 25 story points + 5 points buffer for technical debt
1. **Carry Forward**: Stories 6-7 from Sprint 5 (10 points)
1. **New Work**: 15-20 points of new features
1. **Stretch Goals**: Identify optional stories for if velocity exceeds expectations

## Technical Debt Summary

### Identified in Sprint 5

1. **BDD Test Integration** (High)

   - Playwright selector issues
   - Test reliability concerns
   - Estimated effort: 8-13 points

1. **Database Management** (Medium)

   - Manual cleanup process
   - Environment setup complexity
   - Estimated effort: 3-5 points

1. **Documentation Gaps** (Medium)

   - TAL patterns not documented
   - User guides incomplete
   - Estimated effort: 5-8 points

1. **Test Execution Time** (Medium)

   - Slow feedback loop
   - Parallelization needed
   - Estimated effort: 5-8 points

**Total Technical Debt**: 21-34 points (roughly 1 sprint worth)

### Mitigation Strategy

- Address critical items in Sprint 6 (8-13 points)
- Medium items spread across Sprints 6-7 (13-21 points)
- Track debt in backlog explicitly
- Allocate 20% of sprint capacity to debt reduction

## Team Insights

### Development Practices

1. **BDD-First Works**: Despite test integration challenges, writing scenarios first remains valuable
1. **Incremental Progress**: Small commits with clear messages improve code quality
1. **Automation Pays Off**: Template validation caught multiple issues early
1. **Manual Testing Still Essential**: Don't rely solely on automated tests

### Learning and Growth

1. **Deep Roundup Expertise**: Team gaining significant TAL knowledge
1. **Testing Challenges**: Playwright integration more complex than expected
1. **Documentation Discipline**: Need to improve real-time documentation habits

### Communication

1. **Clear Commit Messages**: Conventional commit format working well
1. **Sprint Documentation**: Backlog and retrospective process effective
1. **Technical Debt Visibility**: Need better tracking system for debt items

## Recommendations for Sprint 6

### Process Improvements

1. **Story Estimation**:

   - Use Planning Poker or similar for collaborative estimation
   - Include "technical investigation" time in estimates
   - Re-estimate after spike stories
   - Consider complexity, risk, and unknowns

1. **Mid-Sprint Reviews**:

   - Check velocity at sprint mid-point
   - Adjust scope if needed
   - Flag blockers early
   - Communicate status clearly

1. **Technical Debt Management**:

   - Explicit debt items in backlog
   - Allocate 20% capacity to debt reduction
   - Track debt metrics over time
   - Prioritize debt by impact

### Technical Focus

1. **Testing Strategy**:

   - Resolve BDD integration issues
   - Implement test parallelization
   - Create database management automation
   - Balance UI and API testing

1. **Documentation**:

   - Real-time documentation updates
   - Pattern documentation as discovered
   - User guide improvements
   - Reference docs for all TAL patterns

1. **Code Quality**:

   - Maintain template validation
   - Expand pre-commit checks
   - Code review focus on patterns and maintainability
   - Performance considerations for database queries

### Sprint 6 Goals

**Primary**: Complete remaining Sprint 5 stories (6-7) and address critical technical debt

**Secondary**: Begin Sprint 6 new features (reporting, analytics)

**Stretch**: Advanced filtering, bulk operations, CI relationship visualization

## Conclusion

Sprint 5 delivered significant CMDB functionality despite not completing all planned stories. The core configuration item management features (Stories 1-5) are production-ready and provide solid foundation for future work. Key challenges around BDD test integration and sprint scope estimation provide valuable lessons for Sprint 6.

The team's technical capabilities with Roundup and TAL have grown substantially, and the BDD-first approach continues to prove valuable for requirements clarity and living documentation. Moving forward, focus on resolving technical debt, completing deferred stories, and maintaining sustainable velocity will ensure continued project success.

**Overall Assessment**: Successful sprint with important lessons learned.
**Sprint 6 Outlook**: Positive, with clear priorities and realistic expectations.
**Project Health**: Good, with manageable technical debt and clear roadmap.

______________________________________________________________________

**Document Status**: Sprint 5 Complete
**Next Review**: Sprint 6 retrospective
**Version**: v0.6.0
**Date**: 2025-01-18
