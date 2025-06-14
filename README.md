# PVOutput Tariff Uploader

[![CI/CD Pipeline](https://github.com/adampetrovic/pvoutput-tariff/actions/workflows/ci.yml/badge.svg)](https://github.com/adampetrovic/pvoutput-tariff/actions/workflows/ci.yml)
[![Docker Build](https://github.com/adampetrovic/pvoutput-tariff/actions/workflows/docker.yml/badge.svg)](https://github.com/adampetrovic/pvoutput-tariff/actions/workflows/docker.yml)
[![Security Scan](https://github.com/adampetrovic/pvoutput-tariff/actions/workflows/security.yml/badge.svg)](https://github.com/adampetrovic/pvoutput-tariff/actions/workflows/security.yml)
[![codecov](https://codecov.io/gh/adampetrovic/pvoutput-tariff/branch/main/graph/badge.svg)](https://codecov.io/gh/adampetrovic/pvoutput-tariff)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

A Python-based utility that automatically calculates and uploads electricity tariff prices to [PVOutput](https://pvoutput.org/) based on time-of-use rates, seasonal variations, and public holidays.

## ✨ Features

- 🕐 **Time-of-Use Pricing**: Supports complex tariff structures with multiple time periods
- 📅 **Seasonal Tariffs**: Different pricing for specific date ranges
- 🏖️ **Holiday Support**: Automatic public holiday detection with regional support
- 🔄 **Automated Uploads**: Regular uploads to PVOutput extended parameters
- 🐳 **Docker Support**: Easy deployment with multi-architecture containers
- 🔒 **Security First**: Comprehensive security scanning and validation
- ⚡ **High Performance**: Efficient execution with minimal resource usage

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Development](#-development)
- [Docker Usage](#-docker-usage)
- [Release Process](#-release-process)
- [Contributing](#-contributing)
- [Security](#-security)
- [License](#-license)

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Pull the latest image
docker pull ghcr.io/adampetrovic/pvoutput-tariff:latest

# Run with your configuration
docker run -it --rm \
  -v /path/to/your/config.yaml:/config/config.yaml \
  -e PVOUTPUT_API_KEY=your_api_key \
  -e PVOUTPUT_SYSTEM_ID=your_system_id \
  -e TZ=Australia/Sydney \
  ghcr.io/adampetrovic/pvoutput-tariff:latest
```

### Using Python

```bash
# Clone the repository
git clone https://github.com/adampetrovic/pvoutput-tariff.git
cd pvoutput-tariff

# Install dependencies
pip install pipenv
pipenv install

# Run the application
pipenv run python uploader.py \
  --config config.yaml \
  --api-key your_api_key \
  --system-id your_system_id \
  --timezone Australia/Sydney
```

## 📦 Installation

### Prerequisites

- Python 3.10 or higher
- [pipenv](https://pipenv.pypa.io/en/latest/) for dependency management
- [Docker](https://docker.com/) (optional, for containerized deployment)

### Local Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/adampetrovic/pvoutput-tariff.git
   cd pvoutput-tariff
   ```

2. **Install dependencies:**
   ```bash
   pip install pipenv
   pipenv install
   ```

3. **Activate the virtual environment:**
   ```bash
   pipenv shell
   ```

### Docker Installation

```bash
# Pull the latest stable release
docker pull ghcr.io/adampetrovic/pvoutput-tariff:latest

# Or pull a specific version
docker pull ghcr.io/adampetrovic/pvoutput-tariff:v1.2.3
```

## ⚙️ Configuration

Create a `config.yaml` file with your tariff structure. See [example config](test/config.yaml) for a complete example.

### Basic Configuration

```yaml
pvoutput:
  extended_param: "v12"  # PVOutput extended parameter (v1-v12)

tariffs:
  peak:
    price: 45.87  # Price in cents per kWh
    times:
      - start: "14:00"
        end: "20:00"
    weekdays_only: true  # Optional: only apply on weekdays
    
  offpeak:
    price: 25.43
    times: []  # Empty times = fallback tariff

public_holidays:  # Optional
  country: "AU"
  region: "NSW"
```

### Advanced Configuration

```yaml
pvoutput:
  extended_param: "v12"

tariffs:
  # Summer peak rates (seasonal)
  summer_peak:
    price: 55.20
    start_date: 2024-12-01
    end_date: 2024-02-28
    weekdays_only: true
    times:
      - start: "14:00"
        end: "20:00"
      
  # Shoulder rates
  shoulder:
    price: 35.10
    times:
      - start: "07:00"
        end: "14:00"
      - start: "20:00"
        end: "22:00"
        
  # Off-peak (fallback)
  offpeak:
    price: 22.50
    times: []

public_holidays:
  country: "AU"
  region: "NSW"
```

### Configuration Validation

The application includes comprehensive configuration validation:

```bash
# Validate your configuration
pipenv run python -c "
from config_schema import validate_config
import yaml
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)
validate_config(config)
print('✅ Configuration is valid')
"
```

## 🎯 Usage

### Command Line Interface

```bash
python uploader.py [OPTIONS]

Options:
  --config PATH          Path to configuration YAML file [default: /config/config.yaml]
  --api-key TEXT         PVOutput API key (or set PVOUTPUT_API_KEY env var)
  --system-id TEXT       PVOutput System ID (or set PVOUTPUT_SYSTEM_ID env var)
  --timezone TEXT        Timezone for calculations [default: Australia/Sydney]
  --help                 Show this message and exit
```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `PVOUTPUT_API_KEY` | Your PVOutput API key | Yes |
| `PVOUTPUT_SYSTEM_ID` | Your PVOutput system ID | Yes |
| `TZ` | Timezone (e.g., `Australia/Sydney`) | No |

### Examples

```bash
# Basic usage
python uploader.py --config config.yaml --api-key abc123 --system-id 12345

# Using environment variables
export PVOUTPUT_API_KEY=abc123
export PVOUTPUT_SYSTEM_ID=12345
export TZ=Australia/Sydney
python uploader.py --config config.yaml

# Custom timezone
python uploader.py --config config.yaml --timezone Europe/London

# Using different config file
python uploader.py --config tariffs/summer.yaml
```

## 🛠️ Development

### Setting Up Development Environment

1. **Clone and setup:**
   ```bash
   git clone https://github.com/adampetrovic/pvoutput-tariff.git
   cd pvoutput-tariff
   pipenv install --dev
   pipenv shell
   ```

2. **Install pre-commit hooks:**
   ```bash
   pipenv run pre-commit install
   ```

### Development Workflow

#### Code Quality Tools

```bash
# Run all quality checks
make check

# Individual tools
pipenv run flake8 uploader.py test/          # Linting
pipenv run black uploader.py test/           # Formatting  
pipenv run isort uploader.py test/           # Import sorting
pipenv run mypy uploader.py                  # Type checking
pipenv run bandit -r uploader.py             # Security scanning
```

#### Testing

```bash
# Run all tests
pipenv run pytest

# Run with coverage
pipenv run pytest --cov=uploader --cov-report=html

# Run specific test file
pipenv run pytest test/test_tariffs.py

# Run with verbose output
pipenv run pytest -v

# Run only failed tests
pipenv run pytest --lf
```

#### Security and Dependencies

```bash
# Check for security vulnerabilities
pipenv run safety check

# Audit dependencies
pipenv run pip-audit

# Check licenses
pipenv run pip-licenses

# Update dependencies
pipenv update
```

### Project Structure

```
pvoutput-tariff/
├── .github/workflows/     # GitHub Actions workflows
├── test/                  # Test files and test configs
├── uploader.py           # Main application
├── config_schema.py      # Configuration validation
├── Dockerfile           # Container definition
├── Pipfile              # Python dependencies
├── pyproject.toml       # Project configuration
└── README.md           # This file
```

### Adding New Features

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Write tests first:**
   ```bash
   # Add tests in test/
   pipenv run pytest test/test_your_feature.py
   ```

3. **Implement the feature:**
   ```bash
   # Make your changes
   pipenv run pytest  # Ensure tests pass
   ```

4. **Run quality checks:**
   ```bash
   pipenv run flake8 uploader.py test/
   pipenv run black uploader.py test/
   pipenv run mypy uploader.py
   ```

5. **Commit and push:**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   git push origin feature/your-feature-name
   ```

## 🐳 Docker Usage

### Building Images

```bash
# Build locally
docker build -t pvoutput-tariff .

# Multi-platform build
docker buildx build --platform linux/amd64,linux/arm64 -t pvoutput-tariff .
```

### Running Containers

```bash
# Basic run
docker run --rm \
  -v $(pwd)/config.yaml:/config/config.yaml \
  -e PVOUTPUT_API_KEY=your_key \
  -e PVOUTPUT_SYSTEM_ID=your_id \
  ghcr.io/adampetrovic/pvoutput-tariff:latest

# With custom timezone
docker run --rm \
  -v $(pwd)/config.yaml:/config/config.yaml \
  -e PVOUTPUT_API_KEY=your_key \
  -e PVOUTPUT_SYSTEM_ID=your_id \
  -e TZ=Europe/London \
  ghcr.io/adampetrovic/pvoutput-tariff:latest

# As non-root user
docker run --rm --user 1000:1000 \
  -v $(pwd)/config.yaml:/config/config.yaml \
  -e PVOUTPUT_API_KEY=your_key \
  -e PVOUTPUT_SYSTEM_ID=your_id \
  ghcr.io/adampetrovic/pvoutput-tariff:latest

# With cron (run every 5 minutes)
docker run -d --name pvoutput-tariff \
  -v $(pwd)/config.yaml:/config/config.yaml \
  -e PVOUTPUT_API_KEY=your_key \
  -e PVOUTPUT_SYSTEM_ID=your_id \
  --restart unless-stopped \
  ghcr.io/adampetrovic/pvoutput-tariff:latest
```

### Docker Compose

```yaml
version: '3.8'
services:
  pvoutput-tariff:
    image: ghcr.io/adampetrovic/pvoutput-tariff:latest
    environment:
      - PVOUTPUT_API_KEY=your_key
      - PVOUTPUT_SYSTEM_ID=your_id
      - TZ=Australia/Sydney
    volumes:
      - ./config.yaml:/config/config.yaml:ro
    restart: unless-stopped
```

## 📦 Release Process

### Automated Releases

Releases are automatically created when you push a version tag:

```bash
# Create and push a version tag
git tag v1.2.3
git push origin v1.2.3
```

This triggers the release workflow which:
- ✅ Validates the release
- 🏗️ Builds Python packages and Docker images
- 🔒 Runs security scans
- 📝 Generates release notes
- 🚀 Publishes to GitHub Releases and container registry

### Manual Release

You can also trigger releases manually via GitHub Actions:

1. Go to **Actions** → **Release Management**
2. Click **Run workflow**
3. Enter the version (e.g., `v1.2.3`)
4. Choose if it's a pre-release
5. Click **Run workflow**

### Release Types

- **Stable Release**: `v1.2.3` (semantic versioning)
- **Pre-release**: `v1.2.3-alpha.1`, `v1.2.3-beta.1`, `v1.2.3-rc.1`
- **Development**: Automatic builds from `main` branch

### Version Management

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (`v2.0.0`): Breaking changes
- **MINOR** (`v1.1.0`): New features, backwards compatible
- **PATCH** (`v1.0.1`): Bug fixes, backwards compatible

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Quick Contribution Guide

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and add tests
4. **Run quality checks**: `pipenv run flake8 && pipenv run pytest`
5. **Commit your changes**: `git commit -m 'feat: add amazing feature'`
6. **Push to your branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

### Commit Convention

We use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `test:` Test changes
- `refactor:` Code refactoring
- `chore:` Maintenance tasks

## 🔒 Security

### Security Features

- 🔍 **Automated Security Scanning**: CodeQL, Bandit, Semgrep, Trivy
- 🔐 **Container Signing**: Images signed with cosign
- 📋 **SBOM Generation**: Software Bill of Materials included
- 🛡️ **Dependency Scanning**: Regular vulnerability checks
- 🔑 **Secret Detection**: Prevents accidental secret commits

### Reporting Security Issues

Please report security vulnerabilities to [security@example.com](mailto:security@example.com) or use GitHub's security advisory feature.

### Security Best Practices

- Always use the latest version
- Verify container image signatures
- Keep dependencies updated
- Use environment variables for secrets
- Run containers as non-root user

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📖 **Documentation**: Check this README and code comments
- 🐛 **Bug Reports**: [Open an issue](https://github.com/adampetrovic/pvoutput-tariff/issues)
- 💡 **Feature Requests**: [Open an issue](https://github.com/adampetrovic/pvoutput-tariff/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/adampetrovic/pvoutput-tariff/discussions)

## 🙏 Acknowledgments

- [PVOutput](https://pvoutput.org/) for providing the API
- [holidays](https://github.com/dr-prodigy/python-holidays) library for holiday support
- All contributors who help improve this project

---

**Made with ❤️ for the solar community**