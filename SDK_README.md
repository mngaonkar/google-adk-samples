# Declarative Agent SDK

A powerful, declarative SDK for creating Google ADK (Agent Development Kit) agents using YAML-based configuration. This SDK simplifies agent creation by providing factories, registries, and utilities that reduce boilerplate code and make agent development more maintainable.

## Features

✨ **YAML-Based Configuration**: Define agents declaratively using YAML files instead of writing repetitive code

🔧 **Skills-Based Architecture**: Reusable components with auto-discovered tools and instructions

📦 **Registry System**: Centralized registries for tools, skills, and workflows

🔄 **Workflow Factory**: Create complex LangGraph workflows from YAML configuration

🎯 **Type-Safe**: Built with Pydantic for robust type checking and validation

## Installation

```bash
pip install declarative-agent-sdk
```

### Development Installation

To install in development mode with dev dependencies:

```bash
git clone https://github.com/yourusername/declarative-agent-sdk.git
cd declarative-agent-sdk
pip install -e ".[dev]"
```

## Quick Start

### 1. Create a Agent with YAML

Create a YAML configuration file `my_agent.yaml`:

```yaml
name: my_agent
description: A helpful assistant agent
model: gemini-2.5-flash
instruction_file: prompts/instructions.md
skills:
  - research
  - writing
```

### 2. Load and Run the Agent

```python
from sdk import AgentFactory

# Create agent from YAML configuration
agent = AgentFactory.from_yaml_file('my_agent.yaml')

# Run the agent
response = await agent.run("What are the latest trends in AI?")
print(response)
```

### 3. Define Skills

Create reusable skills in a `skills/` directory:

```
skills/
  research/
    SKILL.md              # Instructions for the skill
    scripts/
      search_web.py       # Auto-discovered tools
      analyze_data.py
```

## Core Components

### AgentFactory

Create agents from YAML configuration files:

```python
from sdk import AgentFactory

agent = AgentFactory.from_yaml_file('config/agent.yaml')
```

### ToolRegistry

Register and manage tools for your agents:

```python
from sdk import ToolRegistry

# Register a function as a tool
@ToolRegistry.register('calculate_sum')
def add_numbers(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

# Get a registered tool
tool_func = ToolRegistry.get('calculate_sum')
```

### SkillRegistry

Organize related tools and instructions into skills:

```python
from sdk import SkillRegistry

# Register a skill directory
SkillRegistry.register('research', 'skills/research')

# Get skill tools and instructions
tools = SkillRegistry.get_tools('research')
instructions = SkillRegistry.get_instructions('research')
```

### WorkflowFactory

Create LangGraph workflows from YAML:

```python
from sdk import WorkflowFactory, WorkflowRegistry

# Register workflow functions
WorkflowRegistry.register('process_data', process_data_function)
WorkflowRegistry.register('analyze_results', analyze_function)

# Compile workflow from YAML
graph = WorkflowFactory.compile_from_yaml('workflows/my_workflow.yaml')

# Run the workflow
result = graph.invoke({"input": "data"})
```

## YAML Configuration Examples

### Agent Configuration

```yaml
name: chapter_agent
description: Generates book chapter content
model: gemini-2.5-flash
instruction_file: prompts/chapter_instructions.md
skills:
  - research
  - writing
  - formatting
input_key_map:
  chapter_number: number
  chapter_title: title
```

### Workflow Configuration

```yaml
workflow:
  name: book_generation_workflow
  nodes:
    - name: toc_agent
      type: function
    - name: chapter_agent_parallel
      type: function
    - name: collation_agent
      type: function
  edges:
    - from: START
      to: toc_agent
    - from: toc_agent
      to: chapter_agent_parallel
      condition: route_after_toc
    - from: chapter_agent_parallel
      to: collation_agent
    - from: collation_agent
      to: END
```

## Requirements

- Python >= 3.9
- google-adk >= 0.1.0
- google-genai >= 0.1.0
- pydantic >= 2.0.0
- pyyaml >= 6.0
- langgraph >= 0.1.0

## Documentation

For full documentation, examples, and API reference, see the [SDK README](sdk/README.md) in the repository.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues, questions, or contributions, please visit the [GitHub repository](https://github.com/yourusername/declarative-agent-sdk).
