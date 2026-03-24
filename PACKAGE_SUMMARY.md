# Declarative Agent SDK - Package Summary

## Package Overview

**Package Name**: `declarative-agent-sdk`  
**Import Name**: `sdk`  
**Version**: 0.1.0  
**Python**: >= 3.9

The Declarative Agent SDK provides a YAML-based, declarative approach to building Google ADK agents with built-in support for skills, tools, and workflows.

## Installation

### For Users

```bash
pip install declarative-agent-sdk
```

### For Developers

```bash
# Clone and install in editable mode
git clone <repository-url>
cd google-adk-samples
pip install -e .

# Or with dev dependencies
pip install -e ".[dev]"
```

## Package Structure

```
google-adk-samples/
├── sdk/                          # Main package directory
│   ├── __init__.py              # Package exports
│   ├── __version__.py           # Version info
│   ├── ai_agent.py              # Extended Agent class
│   ├── agent_factory.py         # YAML-based agent creation
│   ├── tool_registry.py         # Tool registration system
│   ├── skill_registry.py        # Skill management
│   ├── workflow_factory.py      # LangGraph workflow builder
│   ├── workflow_registry.py     # Workflow function registry
│   ├── utils.py                 # Utility functions
│   ├── constants.py             # Package constants
│   └── README.md                # SDK documentation
├── pyproject.toml               # Modern package configuration
├── setup.py                     # Legacy setup script
├── MANIFEST.in                  # Package file inclusion rules
├── SDK_README.md                # PyPI package description
├── LICENSE                      # MIT License
├── BUILD_AND_INSTALL.md         # Build/publish instructions
├── QUICKSTART.md                # Quick start guide
└── validate_package.py          # Package validation script
```

## Core Components

### 1. AIAgent
Extended Agent class with convenient initialization:
- YAML-based configuration
- Skill integration
- Custom tool support
- Input key mapping

### 2. AgentFactory
Create agents from YAML files:
```python
from sdk import AgentFactory
agent = AgentFactory.from_yaml_file('config/agent.yaml')
```

### 3. ToolRegistry
Centralized tool management:
```python
from sdk import ToolRegistry

@ToolRegistry.register('tool_name')
def my_tool(arg: str) -> str:
    return arg.upper()
```

### 4. SkillRegistry
Organize tools into reusable skills:
```python
from sdk import SkillRegistry
SkillRegistry.register('skill_name', 'skills/skill_name')
```

### 5. WorkflowFactory
Build LangGraph workflows from YAML:
```python
from sdk import WorkflowFactory
graph = WorkflowFactory.compile_from_yaml('workflow.yaml')
```

### 6. WorkflowRegistry
Register workflow functions:
```python
from sdk import WorkflowRegistry
WorkflowRegistry.register('function_name', function)
```

## Dependencies

- **google-adk** >= 0.1.0 - Core ADK framework
- **google-genai** >= 0.1.0 - Google Generative AI
- **pydantic** >= 2.0.0 - Data validation
- **pyyaml** >= 6.0 - YAML parsing
- **langgraph** >= 0.1.0 - Workflow graphs

## Building the Package

### 1. Validate Structure
```bash
python validate_package.py
```

### 2. Install Build Tools
```bash
pip install build twine
```

### 3. Build Distribution
```bash
# Clean previous builds
rm -rf build/ dist/ *.egg-info

# Build wheel and source distribution
python -m build
```

This creates:
- `dist/declarative_agent_sdk-0.1.0-py3-none-any.whl`
- `dist/declarative-agent-sdk-0.1.0.tar.gz`

### 4. Test Installation
```bash
# Install from wheel
pip install dist/declarative_agent_sdk-0.1.0-py3-none-any.whl

# Or development mode
pip install -e .
```

### 5. Verify Installation
```python
import sdk
print(sdk.__version__)  # Should print: 0.1.0
```

## Publishing

### TestPyPI (Recommended First)
```bash
python -m twine upload --repository testpypi dist/*
pip install --index-url https://test.pypi.org/simple/ declarative-agent-sdk
```

### Production PyPI
```bash
python -m twine upload dist/*
```

## Usage

### Basic Agent Creation
```python
from sdk import AgentFactory

agent = AgentFactory.from_yaml_file('agent.yaml')
response = await agent.run({"query": "Hello"})
```

### With Custom Tools
```python
from sdk import ToolRegistry, AgentFactory

@ToolRegistry.register('greet')
def greet(name: str) -> str:
    return f"Hello, {name}!"

agent = AgentFactory.from_yaml_file('agent.yaml')
```

### With Skills
```python
from sdk import SkillRegistry, AgentFactory

SkillRegistry.register('research', 'skills/research')
agent = AgentFactory.from_yaml_file('agent.yaml')
```

### Workflows
```python
from sdk import WorkflowFactory, WorkflowRegistry

WorkflowRegistry.register('step1', step1_function)
WorkflowRegistry.register('step2', step2_function)

graph = WorkflowFactory.compile_from_yaml('workflow.yaml')
result = graph.invoke({"input": "data"})
```

## Example Project: book_agent

The `book_agent` directory demonstrates a complete multi-agent system:

- **TOC Agent**: Creates table of contents
- **Chapter Agent**: Writes chapter content (parallel execution)
- **Collation Agent**: Combines chapters into a book

Key features demonstrated:
- Multi-agent workflows
- Skill-based architecture
- YAML configuration
- LangGraph integration
- Parallel agent execution

## File Checklist

Before building, ensure these files exist:

- [x] `pyproject.toml` - Package configuration
- [x] `setup.py` - Setup script
- [x] `sdk/__init__.py` - Package initialization
- [x] `sdk/__version__.py` - Version information
- [x] `SDK_README.md` - Package description for PyPI
- [x] `LICENSE` - MIT License
- [x] `MANIFEST.in` - File inclusion rules
- [x] `.gitignore` - Ignore build artifacts

## Version Management

To release a new version:

1. Update `sdk/__version__.py`:
   ```python
   __version__ = "0.2.0"
   ```

2. Update `pyproject.toml`:
   ```toml
   version = "0.2.0"
   ```

3. Build and publish:
   ```bash
   rm -rf dist/
   python -m build
   python -m twine upload dist/*
   ```

## Documentation

- **SDK_README.md** - PyPI package page
- **sdk/README.md** - Detailed SDK documentation
- **BUILD_AND_INSTALL.md** - Build and publish guide
- **QUICKSTART.md** - Quick start guide
- **book_agent/README.md** - Example usage

## Development Workflow

```bash
# 1. Make changes to sdk/
# 2. Test locally
pip install -e .

# 3. Validate
python validate_package.py

# 4. Build
python -m build

# 5. Test installation
pip install dist/*.whl --force-reinstall

# 6. Publish (when ready)
python -m twine upload dist/*
```

## Key Features

✅ Declarative YAML configuration  
✅ Skill-based architecture  
✅ Auto-discovery of tools  
✅ Workflow orchestration  
✅ Type-safe with Pydantic  
✅ Extensible registry system  
✅ Compatible with Google ADK  
✅ LangGraph integration  

## Support & Resources

- **Repository**: https://github.com/yourusername/declarative-agent-sdk
- **Issues**: https://github.com/yourusername/declarative-agent-sdk/issues
- **Documentation**: See `sdk/README.md`
- **Examples**: See `book_agent/` directory

## License

MIT License - See LICENSE file

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

**Ready to build?** Run `python validate_package.py` to verify everything is in place!
