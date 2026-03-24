# Building and Installing the Declarative Agent SDK

This guide explains how to build, install, and publish the `declarative-agent-sdk` Python package.

## Table of Contents

- [Local Development Installation](#local-development-installation)
- [Building the Package](#building-the-package)
- [Installing from Built Package](#installing-from-built-package)
- [Publishing to PyPI](#publishing-to-pypi)
- [Installing from PyPI](#installing-from-pypi)
- [Verifying Installation](#verifying-installation)

## Local Development Installation

For local development, install the package in editable mode:

```bash
# From the workspace root (google-adk-samples/)
pip install -e .
```

This allows you to make changes to the SDK and immediately see them reflected without reinstalling.

### With Development Dependencies

```bash
pip install -e ".[dev]"
```

This installs additional tools like pytest, black, mypy, and ruff for development.

## Building the Package

### Prerequisites

Install build tools:

```bash
pip install build twine
```

### Build the Distribution

From the workspace root directory:

```bash
# Build both wheel and source distribution
python -m build
```

This creates:
- `dist/declarative_agent_sdk-0.1.0-py3-none-any.whl` (wheel file)
- `dist/declarative-agent-sdk-0.1.0.tar.gz` (source distribution)

### Clean Build

To ensure a clean build, remove old build artifacts first:

```bash
# Remove old builds
rm -rf build/ dist/ *.egg-info sdk/*.egg-info

# Build fresh
python -m build
```

## Installing from Built Package

### Install from Wheel

```bash
pip install dist/declarative_agent_sdk-0.1.0-py3-none-any.whl
```

### Install from Source Distribution

```bash
pip install dist/declarative-agent-sdk-0.1.0.tar.gz
```

### Install from Local Directory

```bash
# From workspace root
pip install .
```

## Publishing to PyPI

### Test on TestPyPI First

1. **Create TestPyPI account** at https://test.pypi.org/account/register/

2. **Create API token** at https://test.pypi.org/manage/account/token/

3. **Upload to TestPyPI**:

```bash
python -m twine upload --repository testpypi dist/*
```

4. **Test installation from TestPyPI**:

```bash
pip install --index-url https://test.pypi.org/simple/ declarative-agent-sdk
```

### Publish to Production PyPI

1. **Create PyPI account** at https://pypi.org/account/register/

2. **Create API token** at https://pypi.org/manage/account/token/

3. **Upload to PyPI**:

```bash
python -m twine upload dist/*
```

4. **Verify the upload** at https://pypi.org/project/declarative-agent-sdk/

### Using .pypirc for Authentication

Create `~/.pypirc` to avoid entering credentials each time:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-your-api-token-here

[testpypi]
username = __token__
password = pypi-your-test-api-token-here
```

Make it readable only by you:

```bash
chmod 600 ~/.pypirc
```

## Installing from PyPI

Once published, users can install with:

```bash
pip install declarative-agent-sdk
```

### Specific Version

```bash
pip install declarative-agent-sdk==0.1.0
```

### Upgrade to Latest

```bash
pip install --upgrade declarative-agent-sdk
```

## Verifying Installation

### Check Installation

```bash
pip show declarative-agent-sdk
```

### Test Import

```python
# Test basic import
import sdk
print(sdk.__version__)

# Test specific imports
from sdk import AgentFactory, ToolRegistry, WorkflowFactory
print("All imports successful!")
```

### Run Quick Test

```python
from sdk import AgentFactory, ToolRegistry

# Register a simple tool
@ToolRegistry.register('greet')
def greet(name: str) -> str:
    """Greet someone by name."""
    return f"Hello, {name}!"

# Test the tool
greet_func = ToolRegistry.get('greet')
result = greet_func('World')
print(result)  # Should print: Hello, World!
```

## Version Management

### Updating Version

To release a new version:

1. **Update version** in `sdk/__version__.py`:
   ```python
   __version__ = "0.2.0"
   ```

2. **Update version** in `pyproject.toml`:
   ```toml
   version = "0.2.0"
   ```

3. **Rebuild and publish**:
   ```bash
   rm -rf dist/
   python -m build
   python -m twine upload dist/*
   ```

## Troubleshooting

### Import Errors After Installation

If you get import errors, ensure the package is installed:

```bash
pip list | grep declarative-agent-sdk
```

### Build Errors

If build fails, check:
- setuptools is up to date: `pip install --upgrade setuptools wheel build`
- pyproject.toml syntax is valid
- All required files exist (README, LICENSE, etc.)

### Upload Errors

If upload to PyPI fails:
- Check that the package name isn't already taken
- Verify your API token is correct
- Ensure the version number hasn't been published before

## Development Workflow

Recommended workflow for contributors:

```bash
# 1. Clone repository
git clone https://github.com/yourusername/declarative-agent-sdk.git
cd declarative-agent-sdk

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install in development mode
pip install -e ".[dev]"

# 4. Make changes to the code

# 5. Run tests (when available)
pytest

# 6. Format code
black sdk/
ruff check sdk/

# 7. Build and test locally
python -m build
pip install dist/*.whl --force-reinstall

# 8. Push changes and create PR
```

## Additional Resources

- [Python Packaging Guide](https://packaging.python.org/)
- [setuptools Documentation](https://setuptools.pypa.io/)
- [Twine Documentation](https://twine.readthedocs.io/)
- [PyPI Help](https://pypi.org/help/)

## Support

For issues or questions:
- Open an issue on GitHub
- Check existing documentation
- Contact the maintainers
