# Contributing to Locust Flow

Thank you for contributing! This guide will help you get started.

## Quick Start

```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/locust-flow.git
cd locust-flow

# Setup
make install-dev
make install-hooks

# Make changes and test
make test
make lint
make format
```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

Branch prefixes: `feature/`, `fix/`, `docs/`, `refactor/`, `test/`

### 2. Make Changes

- Write tests for new functionality
- Follow existing code patterns
- Keep functions small and focused
- Add docstrings for public APIs

### 3. Test Your Changes

```bash
make test          # Run tests
make coverage      # Check coverage
make lint          # Check code style
make format        # Format code
make ci            # Run all checks
```

### 4. Commit

Use conventional commit format:

```bash
git commit -m "feat: add custom retry delays"
git commit -m "fix: handle empty validation list"
git commit -m "docs: update plugin examples"
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `perf`

### 5. Submit Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a PR on GitHub with:
- Clear title and description
- Reference to related issues
- Screenshots (if applicable)

## Code Style

We use:
- **Black** for formatting (line length: 127)
- **flake8** for linting
- **isort** for import sorting

Run `make format` before committing.

## Testing

Place tests in `tests/` directory with `test_` prefix:

```python
def test_feature_works(self):
    """Test that feature works as expected."""
    result = function_under_test(config)
    self.assertEqual(result, expected_value)
```

## Reporting Issues

### Bug Reports

Include:
- Clear description
- Steps to reproduce
- Expected vs actual behavior
- Environment (Python version, OS)
- Minimal config example
- Error messages/logs

### Feature Requests

Include:
- Use case and motivation
- Proposed solution
- Example usage

## Pull Request Checklist

- [ ] Tests pass (`make test`)
- [ ] Code formatted (`make format`)
- [ ] Linting passes (`make lint`)
- [ ] Tests added for new features
- [ ] Documentation updated
- [ ] Commit messages follow convention

## Project Structure

```
locust-flow/
├── framework/           # Core code
│   ├── config_loader.py
│   ├── config_validator.py
│   ├── flow_executor.py
│   └── plugins/        # Plugin system
├── tests/              # Test suite
├── configs/            # Examples
└── main.py             # Entry point
```

## Questions?

- Check existing issues
- Read README.md
- Open a new issue with "question" label

## License

By contributing, you agree your contributions will be licensed under the MIT License.

---

Thank you for contributing!
