# Agent Factory - YAML-Based Agent Configuration

## Overview

The Agent Factory provides a clean, declarative way to define and instantiate AIAgent objects using YAML configuration files. This makes agent management more maintainable and reduces code duplication.

**Key Features:**
- **Skills-Based Architecture**: Agents can reference skills that auto-discover tools and instructions
- **Instance-Level Tool Registry**: Each agent has its own isolated tool namespace
- **Auto-Discovery**: Functions in skill directories are automatically registered as tools
- **Combined Instructions**: SKILL.md files from all referenced skills are appended to agent instructions
- **Declarative Configuration**: Define agents entirely in YAML without boilerplate code

## Quick Start

### 1. Define Your Skills

Skills are reusable components with their own instructions and tools. Each skill should have:
- `SKILL.md` - Instructions for the agent
- `scripts/` folder - Python files with tool functions

Example skill structure:
```
skills/
  toc/
    SKILL.md
    scripts/
      validate_yaml.py  # Contains validate_yaml() function
      format_toc.py     # Contains format_toc() function
```

### 2. Create YAML Configuration

Create a YAML file (e.g., `configs/agents/my_agent.yaml`):

```yaml
name: my_agent
description: A helpful agent that does something useful
instruction_file: my_agent/SKILL.md  # Optional if using skills
skills:
  - toc  # Auto-discovers tools from skills/toc/scripts/
  - chapter
tools:
  - google_search  # From global registry
  - toc_validate_yaml  # Auto-discovered from skills/toc/scripts/
output_key: my_agent_response
model: gemini-2.0-flash-exp
```

### 3. Load Agent from YAML

```python
from sdk.agent_factory import AgentFactory

# Load from file
agent = AgentFactory.from_yaml_file('configs/agents/my_agent.yaml')

# Agent now has:
# - Combined instructions from my_agent/SKILL.md + all skills' SKILL.md files
# - Auto-discovered tools from skills/toc/scripts/ and skills/chapter/scripts/
# - Instance-level tool registry (isolated from other agents)
```

## YAML Configuration Schema

### Required Fields

- **name** (string): Unique identifier for the agent

### Optional Fields

- **instruction_file** (string): Path to the main SKILL.md file containing agent instructions
  - If not specified, instructions will be built from skills' SKILL.md files
  - Combined with SKILL.md from all referenced skills
  
- **skills** (list): List of skill directories to include
  - Default: None
  - Each skill directory is relative to `SKILLS_DIRECTORY` constant
  - Automatically discovers tools from `{skill_dir}/scripts/` folders
  - Appends each skill's SKILL.md to agent instructions
  - Example: `['toc', 'chapter']` references `skills/toc/` and `skills/chapter/`
  
- **description** (string): Human-readable description of what the agent does
  - Default: empty string
  
- **tools** (list): List of tool names to provide to the agent
  - Default: empty list
  - Can reference tools from:
    - Global ToolRegistry (manually registered tools)
    - Instance registry (auto-discovered from skills)
  - Tool names from skills are prefixed: `{skill_name}_{function_name}`
  
- **output_key** (string): Key name for the agent's output in the result
  - Default: None
  
- **model** (string): LLM model to use
  - Default: Value from `GEMINI_MODEL` constant

## Complete Example

### Example: TOC Agent with Skills

**File: configs/agents/toc_agent.yaml**
```yaml
name: toc_agent
description: An agent to create a table of contents for a book based on user provided topic.
instruction_file: toc_agent/SKILL.md
skills:
  - toc  # Auto-discovers from skills/toc/scripts/
tools:
  - google_search  # From global registry
  - toc_validate_yaml  # Auto-discovered from skills/toc/scripts/
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

# Load agent from YAML - automatically includes:
# - Instructions from toc_agent/SKILL.md
# - Instructions from skills/toc/SKILL.md (appended)
# - Tools from skills/toc/scripts/ (auto-discovered with 'toc_' prefix)
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

### Skill Directory Structure

```
skills/
  toc/
    SKILL.md                      # Instructions for TOC generation
    scripts/
      validate_yaml.py            # Contains validate_yaml() function
      format_toc.py               # Contains format_toc() function
```

**What happens automatically:**
1. `skills/toc/SKILL.md` is appended to agent instructions
2. Functions in `scripts/` are registered as tools with `toc_` prefix
3. Agent can use `toc_validate_yaml()` and `toc_format_toc()` tools

## Registry Architecture

The SDK uses a three-tier registry system for managing skills, tools, and workflows:

### Tool Registry

Stores callable functions and tools. Used for:
- **Global tools**: Manually registered tools available to all agents
- **Instance tools**: Auto-discovered from skills, isolated per agent

#### Auto-Discovery from Skills

When an agent specifies `skills`, the ToolRegistry automatically:
1. Scans `{skill_dir}/scripts/` for Python files
2. Discovers all user-defined functions
3. Registers them with prefix: `{skill_name}_{function_name}`
4. Stores them in the agent's instance registry (isolated)

```python
# Auto-discovery happens automatically via YAML
# But you can also use it manually:
from sdk.tool_registry import ToolRegistry

count = ToolRegistry.register_from_scripts_folder(
    'skills/toc/scripts',
    prefix='toc_'
)
print(f"Registered {count} tools")
```

#### Manual Tool Registration

For global tools not in skills:

```python
from sdk.tool_registry import ToolRegistry

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

#### Listing Available Tools

```python
from sdk.tool_registry import ToolRegistry

# List global registry
available_tools = ToolRegistry.list_available()
print(f"Available tools: {available_tools}")

# Access agent's instance registry
agent = AgentFactory.from_yaml_file('configs/agents/my_agent.yaml')
instance_tools = agent.tool_registry.list_available()
print(f"Agent instance tools: {instance_tools}")
```

### Skill Registry

Stores skill metadata and directory paths (not callables).

```python
from sdk.skill_registry import SkillRegistry

# Register a skill
SkillRegistry.register(
    'toc_agent',
    directory='skills/toc',
    description='Generate table of contents',
    category='agent'
)

# Get skill directory
directory = SkillRegistry.get_directory('toc_agent')

# List all skills
skills = SkillRegistry.list_available()
```

### Instance-Level Tool Isolation

Each AIAgent instance has its own ToolRegistry, preventing namespace conflicts:

```yaml
# agent_a.yaml
name: agent_a
skills:
  - skill_x  # Has function foo() -> registered as skill_x_foo

# agent_b.yaml  
name: agent_b
skills:
  - skill_y  # Also has function foo() -> registered as skill_y_foo
```

Both agents can have a `foo()` function without conflicts because each has an isolated registry.

## Benefits

1. **Declarative Configuration**: Agent configuration is separate from code
2. **Reduced Boilerplate**: 90%+ reduction in agent initialization code
3. **Auto-Discovery**: Tools are automatically discovered from skill directories
4. **Instance Isolation**: Each agent has its own tool namespace, preventing conflicts
5. **Composable Skills**: Reusable skill components with instructions and tools
6. **Combined Instructions**: SKILL.md files from all skills are automatically appended
7. **Easy Maintenance**: Update agent properties without touching code
8. **Version Control Friendly**: YAML files clearly show configuration changes
9. **Validation**: Factory validates required fields and skill availability
10. **Prefix Management**: Auto-generated prefixes prevent tool name collisions

## Advanced Usage

### How Skills Work

When you specify `skills: ['toc', 'chapter']` in your YAML:

1. **Instruction Appending**:
   - Main `instruction_file` content is loaded first
   - Each `skills/{skill_name}/SKILL.md` is appended with header: `# Skill: {skill_name}`
   - Final instruction is the concatenation of all

2. **Tool Auto-Discovery**:
   - Scans `skills/{skill_name}/scripts/` for `.py` files
   - Extracts all user-defined functions (not imports)
   - Registers each as `{skill_name}_{function_name}`
   - Stored in agent's instance registry

3. **Tool Resolution**:
   - Tools listed in YAML can be:
     - Global registry tools (e.g., `google_search`)
     - Instance registry tools (e.g., `toc_validate_yaml`)
   - Factory tries global first, then passes names to instance registry

### Creating Skills

**Step 1: Create Skill Directory**
```
skills/
  my_skill/
    SKILL.md
    scripts/
      tool_a.py
      tool_b.py
```

**Step 2: Write SKILL.md**
```markdown
# My Skill

You have access to two tools for processing data:
- my_skill_process_data: Process raw data
- my_skill_validate_data: Validate processed data

Use these tools when the user asks for data processing.
```

**Step 3: Create Tool Functions**

File: `skills/my_skill/scripts/tool_a.py`
```python
def process_data(input_data: str) -> str:
    """Process the input data."""
    return f"Processed: {input_data}"

def validate_data(data: str) -> bool:
    """Validate the data."""
    return len(data) > 0
```

**Step 4: Reference in Agent YAML**
```yaml
name: my_agent
skills:
  - my_skill
# Tools are auto-discovered: my_skill_process_data, my_skill_validate_data
```

### Agent Without Instruction File

You can create agents entirely from skills:

```yaml
name: composed_agent
description: Agent built entirely from skills
skills:
  - toc
  - chapter
  - validation
# No instruction_file needed - will use skills' SKILL.md files
```

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

# Each agent has its own isolated tool registry
print(f"Agent A tools: {agents['agent_a'].tool_registry.list_available()}")
print(f"Agent B tools: {agents['agent_b'].tool_registry.list_available()}")
```

### Loading from Environment-Specific Configs

```python
import os
from sdk.agent_factory import AgentFactory

env = os.getenv('ENVIRONMENT', 'dev')
config_file = f'configs/agents/my_agent.{env}.yaml'
agent = AgentFactory.from_yaml_file(config_file)
```

### Programmatic Agent Creation

```python
from sdk.agent_factory import AgentFactory

config = {
    'name': 'dynamic_agent',
    'description': 'Created at runtime',
    'skills': ['toc', 'chapter'],
    'tools': ['google_search'],
    'output_key': 'result'
}
agent = AgentFactory.from_dict(config)
```

## Error Handling

The factory provides clear error messages for common issues:

```python
# Missing required field
ValueError: Agent 'name' is required in configuration

# No instructions
ValueError: Agent does not have any instruction text. Please provide an instruction_file or ensure SKILL.md files are included in skills directories.

# Skill directory not found
FileNotFoundError: Skill directory not found: /path/to/skills/missing_skill

# Missing tool (warning, not error)
WARNING: Tool 'unknown_tool' not found in instance registry, skipping

# YAML file not found
FileNotFoundError: YAML file not found: configs/agents/missing.yaml
```

## Architecture Overview

```
Agent YAML Config
       ↓
AgentFactory.from_yaml_file()
       ↓
Creates AIAgent with:
  ├─ Instance ToolRegistry (isolated)
  │    ├─ Auto-discovers from skills/*/scripts/
  │    └─ Registers with {skill_name}_ prefix
  │
  ├─ Combined Instructions
  │    ├─ Main instruction_file
  │    └─ All skills' SKILL.md (appended)
  │
  └─ Resolved Tools
       ├─ From global ToolRegistry
       └─ From instance ToolRegistry
```

## Migration Guide

### From Manual Agent Creation

**Before:**
```python
from sdk.ai_agent import AIAgent
from sdk.utils import read_from_file

instruction = read_from_file('toc_agent/SKILL.md')
agent = AIAgent(
    name='toc_agent',
    description='Creates table of contents',
    instruction_file='toc_agent/SKILL.md',
    tools=[google_search, validate_yaml],
    output_key='toc_response',
    model='gemini-2.0-flash-exp'
)
```

**After:**
```yaml
# configs/agents/toc_agent.yaml
name: toc_agent
description: Creates table of contents
instruction_file: toc_agent/SKILL.md
skills:
  - toc
tools:
  - google_search
output_key: toc_response
model: gemini-2.0-flash-exp
```

```python
from sdk.agent_factory import AgentFactory

agent = AgentFactory.from_yaml_file('configs/agents/toc_agent.yaml')
```

**Benefits**: 90% less code, auto-discovery of tools, combined instructions
