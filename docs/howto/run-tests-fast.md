<!--
SPDX-FileCopyrightText: 2025 Georges Martin <jrjsmrtn@gmail.com>
SPDX-License-Identifier: MIT
-->

# How to Run Tests Fast

## Overview

This guide explains how to run BDD tests with optimal performance using parallel execution and database optimizations.

**Time Required**: 5 minutes setup
**Difficulty**: Beginner
**Prerequisites**: PMS installed, tests passing

## Quick Start

### Fast Local Testing (Single Database)

The fastest way to run tests locally is to use the same optimization as CI: shared database with no cleanup between scenarios.

```bash
# Start server once
./scripts/reset-test-db.sh admin
uv run roundup-server -p 9080 pms=tracker > /dev/null 2>&1 &

# Run tests with optimization
export CLEANUP_TEST_DATA="false"
export HEADLESS="true"
uv run behave features/issue_tracking/

# Stop server when done
pkill -f roundup-server
```

**Performance**: ~13 seconds for issue_tracking features (vs ~2-3 minutes with database cleanup)

### Parallel Testing (Multiple Workers)

For even faster execution, run feature sets in parallel:

```bash
# Run all features in parallel (4 workers)
./scripts/run-tests-parallel.sh 4

# Run specific feature set (2 workers)
./scripts/run-tests-parallel.sh 2 features/cmdb
```

**Performance**: 40-60% faster than sequential execution

## Understanding the Optimizations

### Database Cleanup Optimization

**Problem**: The default test setup reinitializes the database for every scenario:

```
For each of 129 scenarios:
  1. Stop server
  2. Delete database
  3. Reinitialize database
  4. (Test creates data)
  5. Start server
  6. Run test
```

This takes 2-5 seconds per scenario = **4-10 minutes total overhead**!

**Solution**: Share database across scenarios by setting `CLEANUP_TEST_DATA="false"`:

```
Once:
  1. Initialize database
  2. Start server

For each scenario:
  1. Run test (scenarios create their own test data)
```

**Tradeoff**: Tests must be written to handle existing data (create unique entities, don't assume empty database).

### Parallel Execution

**Approach**: Run different feature files simultaneously using multiple workers.

**Architecture**:

- Each worker gets its own database (tracker-worker-N)
- Each worker gets its own server port (9080+N)
- GNU `parallel` distributes feature files across workers

**Example**: 20 feature files with 4 workers

```
Worker 1: features 1, 5, 9, 13, 17
Worker 2: features 2, 6, 10, 14, 18
Worker 3: features 3, 7, 11, 15, 19
Worker 4: features 4, 8, 12, 16, 20
```

All run simultaneously → ~4x faster!

## CI/CD Parallel Strategy

GitHub Actions runs tests in parallel using matrix strategy:

```yaml
matrix:
  python-version: ['3.9', '3.10', '3.11']
  feature-set: ['issue_tracking', 'change_mgmt', 'cmdb']
```

This creates **9 parallel jobs**:

- Python 3.9 + issue_tracking
- Python 3.9 + change_mgmt
- Python 3.9 + cmdb
- Python 3.10 + issue_tracking
- ... (9 total)

Each job runs ~1-2 minutes, all in parallel = **total CI time ~1-2 minutes** (vs ~10+ minutes sequential).

## Performance Comparison

### Before Optimization (Sequential, Database Cleanup)

```
Issue Tracking: ~2 minutes
Change Management: ~3 minutes
CMDB: ~4 minutes
Total: ~9 minutes
```

### After Optimization (Parallel, Shared Database)

**CI (9 parallel jobs)**:

```
All jobs run simultaneously: ~1.5 minutes
Speedup: 6x faster (83% improvement)
```

**Local (4 workers)**:

```
Issue Tracking: ~7 seconds
Change Management: ~12 seconds
CMDB: ~15 seconds
Total: ~15 seconds (parallelized)
Speedup: 36x faster (97% improvement)
```

## Best Practices

### When to Use Shared Database

✅ **Good for**:

- Local development iteration
- CI/CD pipelines
- Smoke testing
- Quick feedback loops

❌ **Not suitable for**:

- Tests that rely on empty database state
- Tests that check exact counts without filters
- Integration tests for database initialization

### When to Use Parallel Execution

✅ **Good for**:

- Running full test suite
- CI/CD pipelines
- Pre-commit verification
- Release validation

❌ **Not suitable for**:

- Debugging single scenarios
- Writing new tests
- Investigating test failures

### Writing Parallel-Safe Tests

**Create unique test data**:

```python
# Bad: Assumes specific IDs
Then I should see issue "1"

# Good: Uses created data
Then I should see the created issue
```

**Use filters, not counts**:

```python
# Bad: Assumes empty database
Then I should see 3 issues

# Good: Filters for test data
Then I should see 3 issues with tag "test-run-12345"
```

**Clean up critical resources**:

```python
# Good: Each scenario creates unique CIs
Given I create CI "server-{timestamp}"
```

## Troubleshooting

### Tests Fail with CLEANUP_TEST_DATA="false"

**Problem**: Tests assume empty database

**Solution**: Either:

1. Update tests to be parallel-safe (preferred)
1. Run with cleanup enabled: `unset CLEANUP_TEST_DATA`

### Parallel Script Fails to Start Workers

**Problem**: Ports already in use

**Solution**:

```bash
# Kill all roundup servers
pkill -f roundup-server

# Clean up worker databases
rm -rf tracker-worker-*

# Try again
./scripts/run-tests-parallel.sh 4
```

### GNU Parallel Not Found

**Problem**: `parallel` command not available

**Solution**:

```bash
# macOS with MacPorts
sudo port install parallel

# macOS with Homebrew (alternative)
brew install parallel

# Linux
sudo apt-get install parallel  # Debian/Ubuntu
sudo yum install parallel      # RHEL/CentOS
```

## Advanced Usage

### Custom Worker Count

Adjust based on your CPU cores:

```bash
# Use all CPU cores
WORKERS=$(sysctl -n hw.ncpu)  # macOS
WORKERS=$(nproc)               # Linux
./scripts/run-tests-parallel.sh $WORKERS
```

### Selective Feature Execution

```bash
# Run only CMDB tests in parallel
./scripts/run-tests-parallel.sh 2 features/cmdb

# Run only web-ui tagged scenarios
export BEHAVE_TAGS="web-ui"
uv run behave features/issue_tracking/
```

### Integration with Pre-commit

Add to `.git/hooks/pre-push`:

```bash
#!/bin/bash
echo "Running fast test suite..."
export CLEANUP_TEST_DATA="false"
export HEADLESS="true"

./scripts/reset-test-db.sh admin >/dev/null 2>&1
uv run roundup-server -p 9080 pms=tracker >/dev/null 2>&1 &
SERVER_PID=$!

uv run behave features/issue_tracking/ --format=progress

kill $SERVER_PID
```

## Summary

✅ Use `CLEANUP_TEST_DATA="false"` for 10-20x speedup locally
✅ Use parallel execution for additional 3-4x speedup
✅ CI runs 9 parallel jobs for maximum efficiency
✅ Write parallel-safe tests for best results

## Next Steps

- **Reference**: [BDD Testing Best Practices](../reference/bdd-testing-best-practices.md)
- **How-to**: [Debugging BDD Scenarios](./debugging-bdd-scenarios.md)
- **Tutorial**: [Getting Started](../tutorials/getting-started.md)

## Related

- [GitHub Actions Workflow](.github/workflows/ci.yml)
- [Behave Environment](features/environment.py)
- [Parallel Test Script](scripts/run-tests-parallel.sh)
