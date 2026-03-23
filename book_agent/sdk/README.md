# Agent Factory - YAML-Based Agent Configuration

## Overview

The Agent Factory provides a clean, declarative way to define and instantiate AIAgent objects using YAML configuration files. This makes agent management more maintainable and reduces code duplication.

## Quick Start

### 1. Register Your Tools

Before creating agents, register any custom tools you want to use:

```python
from sdk.agent_factory import ToolRegistry, AgentFactory
from collation_agent.scripts.create_pdf_file import create_pdf_file

# Register custom tools
ToolRegistry.register('create_pdf_file', create_pdf_file)
```

Common tools (like `google_search`) are auto-registered when the module is imported.

### 2. Create YAML Configuration

Create a YAML file (e.g., `configs/agents/my_agent.yaml`):

```yaml
name: my_agent
description: A helpful agent that does something useful
instruction_file: my_agent/SKILL.md
tools:
  - google_search
  - my_custom_tool
output_key: my_agent_response
model: gemini-2.0-flash-exp
```

### 3. Load Agent from YAML

```python
from sdk.agent_factory import AgentFactory

# Load from file
agent = AgentFactory.from_yaml_file('configs/agents/my_agent.yaml')

# Or load from dictionary
config = {
    'name': 'my_agent',
    'description': 'A helpful agent',
    'instruction_file': 'my_agent/SKILL.md',
    'tools': ['google_search'],
    'output_key': 'my_agent_response'
}
agent = AgentFactory.from_dict(config)
```

## YAML Configuration Schema

### Required Fields

- **name** (string): Unique identifier for the agent
- **instruction_file** (string): Path to the SKILL.md file containing agent instructions

### Optional Fields

- **description** (string): Human-readable description of what the agent does
  - Default: empty string
- **tools** (list): List of tool names to provide to the agent
  - Default: empty list
  - Tool names must be registered in ToolRegistry
- **output_key** (string): Key name for the agent's output in the result
  - Default: None
- **model** (string): LLM model to use
  - Default: Value from `GEMINI_MODEL` constant

## Complete Example

### Example: TOC Agent

**File: configs/agents/toc_agent.yaml**
```yaml
name: toc_agent
description: An agent to create a table of contents for a book based on user provided topic.
instruction_file: toc_agent/SKILL.md
tools:
  - google_search
output_key: toc_agent_response
model: gemini-2.0-flash-exp
```

**File: toc_agent/agent.py**
```python
from sdk.agent_factory import AgentFactory
from sdk.utils import save_to_file
from agent_state import AgentState
import logging

logger = logging.getLogger(__name__)

# Load agent from YAML
agent = AgentFactory.from_yaml_file('configs/agents/toc_agent.yaml')
logger.info("Table of Contents agent initialized from YAML config.")

TOC_OUTPUT_FILE = "workspace/toc_response.yaml"

def toc_agent(state: AgentState) -> AgentState:
    result = agent.run_sync(state["topic_description"])
    save_to_file(result["final_response"], TOC_OUTPUT_FILE)
    logger.info(f"TOC agent response saved to {TOC_OUTPUT_FILE}")
    state["toc_location"] = TOC_OUTPUT_FILE
    return state
```

## Tool Registry

### Registering Custom Tools

```python
from sdk.agent_factory import ToolRegistry

# Register a single tool
ToolRegistry.register('my_tool', my_tool_function)

# Register multiple tools
tools = {
    'tool_1': tool_1_function,
    'tool_2': tool_2_function,
}
for name, tool in tools.items():
    ToolRegistry.register(name, tool)
```

### Listing Available Tools

```python
from sdk.agent_factory import ToolRegistry

available_tools = ToolRegistry.list_available()
print(f"Available tools: {available_tools}")
```

## Benefits

1. **Declarative Configuration**: Agent configuration is separate from code
2. **Reduced Boilerplate**: No need to repeat `AIAgent()` initialization code
3. **Easy Maintenance**: Update agent properties without touching code
4. **Version Control Friendly**: YAML files clearly show configuration changes
5. **Reusability**: Same agent config can be used in multiple contexts
6. **Validation**: Factory validates required fields and tool availability

## Advanced Usage

### Creating Multiple Agents from Config Directory

```python
from pathlib import Path
from sdk.agent_factory import AgentFactory

config_dir = Path('configs/agents')
agents = {}

for yaml_file in config_dir.glob('*.yaml'):
    agent = AgentFactory.from_yaml_file(str(yaml_file))
    agents[agent.name] = agent

print(f"Loaded {len(agents)} agents: {list(agents.keys())}")
```

### Loading from Environment-Specific Configs

```python
import os
from sdk.agent_factory import AgentFactory

env = os.getenv('ENVIRONMENT', 'dev')
config_file = f'configs/agents/my_agent.{env}.yaml'
agent = AgentFactory.from_yaml_file(config_file)
```

## Error Handling

The factory provides clear error messages:

```python
# Missing required field
ValueError: Agent 'name' is required in configuration

# Missing tool registration
ValueError: Tool 'unknown_tool' not found in registry. Available tools: ['google_search']

# File not found
FileNotFoundError: YAML file not found: configs/agents/missing.yaml
```
