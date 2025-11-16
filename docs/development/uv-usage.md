# Using `uv` for Development

This project uses [uv](https://github.com/astral-sh/uv) for fast, reliable Python package management.

## Why `uv`?

- **10-100x faster** than pip for dependency installation
- **Deterministic** dependency resolution with lock files
- **Drop-in replacement** for pip and venv
- **Modern tooling** with excellent developer experience

## Installation

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with MacPorts
sudo port install uv
```

## Common Commands

### Initial Setup

```bash
# Create virtual environment and install dependencies
# Note: Use --no-install-project since this is not a distributable package
uv sync --no-install-project

# Install with dev dependencies
uv sync --no-install-project --dev
```

**Note**: This project is a Roundup configuration project, not a distributable Python package.
Always use `--no-install-project` with `uv sync` to skip installing the project itself.

### Adding Dependencies

```bash
# Add a runtime dependency
uv add roundup

# Add a dev dependency
uv add --dev pytest

# Add a dependency with version constraint
uv add 'behave>=1.2.6'
```

### Removing Dependencies

```bash
# Remove a dependency
uv remove playwright
```

### Running Commands

```bash
# Run in the virtual environment
uv run behave features/

# Run a script
uv run python -m roundup.scripts.roundup_server

# Run tests
uv run pytest
```

### Updating Dependencies

```bash
# Update all dependencies
uv lock --upgrade

# Sync after lock file update
uv sync
```

### Managing Python Versions

```bash
# Use specific Python version
uv python install 3.11
uv venv --python 3.11

# Pin Python version
uv python pin 3.11
```

## Integration with Existing Workflow

### Virtual Environment

`uv` creates a virtual environment in `.venv/` by default. You can still activate it traditionally:

```bash
source .venv/bin/activate
```

Or use `uv run` for one-off commands without activation.

### requirements.txt (Legacy Support)

While we've migrated to `pyproject.toml`, you can still generate `requirements.txt`:

```bash
uv pip compile pyproject.toml -o requirements.txt
```

### CI/CD

GitHub Actions workflows can use `uv` for faster installations:

```yaml
- name: Install dependencies
  run: |
    curl -LsSf https://astral.sh/uv/install.sh | sh
    uv sync --dev
```

## Lock File

The `uv.lock` file ensures reproducible installs across all environments:

- **Commit it** to version control
- **Never edit manually** - use `uv add`/`uv remove`
- **Update regularly** with `uv lock --upgrade`

## Comparison with Other Tools

| Feature      | uv                | pip      | poetry     |
| ------------ | ----------------- | -------- | ---------- |
| Speed        | ⚡️ 10-100x faster | Baseline | ~2x faster |
| Lock files   | ✅ Yes            | ❌ No    | ✅ Yes     |
| Resolver     | ✅ Modern         | ⚠️ Basic | ✅ Good    |
| Installation | Simple            | Built-in | Complex    |

## Troubleshooting

### Clear cache

```bash
uv cache clean
```

### Regenerate lock file

```bash
rm uv.lock
uv lock
```

### Use different Python

```bash
uv venv --python /path/to/python
```

## Migration Checklist

- [x] Created `pyproject.toml` with dependencies
- [x] Generated `uv.lock` file
- [x] Updated `.gitignore` for uv cache
- [ ] Update CI workflows to use `uv`
- [ ] Document in README

## Resources

- [uv Documentation](https://docs.astral.sh/uv/)
- [uv GitHub](https://github.com/astral-sh/uv)
- [Migration Guide](https://docs.astral.sh/uv/guides/integration/)
