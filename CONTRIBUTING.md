# Contributing to PVOutput Tariff Uploader

Thank you for your interest in contributing to PVOutput Tariff Uploader! This document provides guidelines and information for contributors.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Submitting Changes](#submitting-changes)
- [Review Process](#review-process)
- [Release Process](#release-process)

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/). By participating, you are expected to uphold this code.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- pipenv (for dependency management)
- Docker (optional, for container testing)

### Setting Up Your Development Environment

1. **Fork the repository** on GitHub
2. **Clone your fork:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/pvoutput-tariff.git
   cd pvoutput-tariff
   ```

3. **Add the upstream remote:**
   ```bash
   git remote add upstream https://github.com/adampetrovic/pvoutput-tariff.git
   ```

4. **Set up the development environment:**
   ```bash
   make install-dev
   ```

5. **Verify the setup:**
   ```bash
   make check
   ```

## Development Workflow

### Branch Strategy

We use a simplified Git flow:

- `main` - Stable release branch
- `develop/*` - Development branches for upcoming releases
- `feature/*` - Feature development branches
- `fix/*` - Bug fix branches
- `hotfix/*` - Critical fixes for production

### Creating a Feature Branch

```bash
# Update your local main branch
git checkout main
git pull upstream main

# Create a feature branch
git checkout -b feature/your-feature-name

# Make your changes
# ...

# Push to your fork
git push origin feature/your-feature-name
```

### Keeping Your Branch Updated

```bash
# Fetch latest changes from upstream
git fetch upstream

# Rebase your branch on the latest main
git rebase upstream/main

# Force push if needed (be careful with shared branches)
git push --force-with-lease origin feature/your-feature-name
```

## Coding Standards

### Python Code Style

We follow [PEP 8](https://pep8.org/) with some modifications enforced by our tools:

- **Line length**: 88 characters (Black default)
- **String quotes**: Double quotes preferred
- **Import sorting**: Use isort with Black profile
- **Type hints**: Required for all public functions and methods

### Code Quality Tools

Run these commands to ensure code quality:

```bash
# Format code
make format

# Check formatting
make format-check

# Lint code
make lint

# Type checking
make type-check

# Security scanning
make security

# Run all checks
make check
```

### Commit Convention

We use [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Test changes
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `style`: Code style changes
- `chore`: Maintenance tasks
- `ci`: CI/CD changes

**Examples:**
```bash
feat: add support for dynamic tariff pricing
fix: handle timezone conversion edge cases
docs: update configuration examples
test: add tests for seasonal tariff calculation
```

### Code Structure

```python
# Example function with proper documentation and type hints
def calculate_current_tariff(
    tariff_config: Dict[str, Any],
    current_time: datetime,
    public_holidays: Optional[Dict[str, Any]] = None
) -> float:
    """Calculate the current tariff rate based on time and configuration.
    
    Args:
        tariff_config: Dictionary containing tariff configuration
        current_time: Current datetime for tariff calculation
        public_holidays: Optional public holiday configuration
        
    Returns:
        Current tariff rate in cents per kWh
        
    Raises:
        ValueError: If tariff configuration is invalid
    """
    # Implementation here
    pass
```

## Testing Guidelines

### Test Structure

- Tests are located in the `test/` directory
- Test files should be named `test_*.py`
- Use descriptive test names that explain what is being tested

### Writing Tests

```python
import unittest
from datetime import datetime

class TestTariffCalculation(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.sample_config = {
            "peak": {"price": 45.87, "times": [{"start": "14:00", "end": "20:00"}]},
            "offpeak": {"price": 25.43, "times": []}
        }

    def test_peak_time_calculation(self):
        """Test that peak rates are correctly applied during peak hours."""
        test_time = datetime(2024, 6, 15, 15, 30)  # 3:30 PM
        result = get_current_tariff(self.sample_config, {}, test_time)
        self.assertEqual(result, 45.87)

    def test_offpeak_fallback(self):
        """Test that off-peak rates are used when no other tariff matches."""
        test_time = datetime(2024, 6, 15, 10, 30)  # 10:30 AM
        result = get_current_tariff(self.sample_config, {}, test_time)
        self.assertEqual(result, 25.43)
```

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test file
pipenv run pytest test/test_tariffs.py

# Run with verbose output
make test-verbose

# Run only failed tests
make test-failed
```

### Test Coverage

- Aim for >90% test coverage
- All new features must include tests
- Bug fixes should include regression tests
- Use `make test-cov` to generate coverage reports

## Submitting Changes

### Before Submitting

1. **Run all quality checks:**
   ```bash
   make check
   ```

2. **Validate configurations:**
   ```bash
   make validate
   ```

3. **Update documentation** if needed

4. **Add tests** for new functionality

5. **Update CHANGELOG.md** if applicable

### Pull Request Process

1. **Create a pull request** from your feature branch to `main`

2. **Fill out the PR template** with:
   - Description of changes
   - Type of change (bug fix, feature, etc.)
   - Testing performed
   - Checklist completion

3. **Ensure CI passes:**
   - All tests must pass
   - Code quality checks must pass
   - Security scans must pass

4. **Request review** from maintainers

5. **Address feedback** and update your PR as needed

### Pull Request Template

```markdown
## Description
Brief description of the changes and why they were made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Added tests for new functionality
- [ ] Manual testing performed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review of code completed
- [ ] Code is commented, particularly in hard-to-understand areas
- [ ] Documentation updated if needed
- [ ] No new warnings introduced
```

## Review Process

### Review Criteria

- **Functionality**: Does the code work as intended?
- **Tests**: Are there adequate tests with good coverage?
- **Code Quality**: Is the code clean, readable, and maintainable?
- **Performance**: Are there any performance implications?
- **Security**: Are there any security concerns?
- **Documentation**: Is the code properly documented?

### Review Timeline

- Initial review: Within 2-3 business days
- Follow-up reviews: Within 1-2 business days
- Emergency fixes: Within 24 hours

### Addressing Review Comments

1. **Read all comments** carefully
2. **Ask for clarification** if needed
3. **Make requested changes** in new commits
4. **Respond to comments** explaining your changes
5. **Request re-review** when ready

## Release Process

### Version Management

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (v2.0.0): Breaking changes
- **MINOR** (v1.1.0): New features, backwards compatible
- **PATCH** (v1.0.1): Bug fixes, backwards compatible

### Creating a Release

Releases are automated through GitHub Actions:

```bash
# Create and push a version tag
git tag v1.2.3
git push origin v1.2.3
```

This triggers:
- Automated testing
- Security scanning
- Docker image building
- GitHub release creation
- Documentation updates

## Development Tips

### Useful Commands

```bash
# Quick development setup
make dev

# Run quick checks during development
make quick-check

# Clean temporary files
make clean

# Show all available commands
make help
```

### IDE Setup

For VS Code users:
```bash
make vscode  # Creates .vscode/settings.json
```

### Debugging

```bash
# Run with verbose logging
export PYTHONPATH=.
python -m pdb uploader.py --config test/config.yaml

# Profile performance
make profile
```

### Environment Information

```bash
# Show environment details
make env-info

# Check dependency status
make deps-outdated
```

## Getting Help

- **Documentation**: Check the README and code comments
- **Issues**: Search existing issues or create a new one
- **Discussions**: Use GitHub Discussions for questions
- **Security**: Report security issues privately via email

## Recognition

Contributors will be acknowledged in:
- Release notes
- README contributors section
- Git commit history

Thank you for contributing to PVOutput Tariff Uploader! 🎉