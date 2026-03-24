# Quick Start: Using declarative-agent-sdk

This guide will help you quickly get started with the declarative-agent-sdk.

## Installation

```bash
pip install declarative-agent-sdk
```

Or for local development:

```bash
# From the google-adk-samples directory
pip install -e .
```

## Basic Usage

### 1. Simple Agent Creation

```python
from sdk import AgentFactory

# Create an agent from YAML
agent = AgentFactory.from_yaml_file('config/my_agent.yaml')

# Run the agent
response = await agent.run({
    "input": "Tell me about quantum computing"
})
print(response)
```

### 2. Using Tool Registry

```python
from sdk import ToolRegistry

# Register a custom tool
@ToolRegistry.register('calculate')
def calculate(expression: str) -> float:
    """Safely evaluate a mathematical expression."""
    # Implementation here
    return eval(expression)

# Use the tool in your agent
tools = [ToolRegistry.get('calculate')]
```

### 3. Creating Skills

Create a skill directory structure:

```
skills/
  data_analysis/
    SKILL.md
    scripts/
      load_data.py
      analyze_data.py
      visualize.py
```

Then register and use the skill:

```python
from sdk import SkillRegistry

# Register the skill
SkillRegistry.register('data_analysis', 'skills/data_analysis')

# Get all tools from the skill
tools = SkillRegistry.get_tools('data_analysis')
instructions = SkillRegistry.get_instructions('data_analysis')
```

### 4. Building Workflows

Create a workflow YAML file:

```yaml
# workflows/data_pipeline.yaml
workflow:
  name: data_processing_workflow
  nodes:
    - name: load_data
      type: function
    - name: process_data
      type: function
    - name: save_results
      type: function
  edges:
    - from: START
      to: load_data
    - from: load_data
      to: process_data
    - from: process_data
      to: save_results
    - from: save_results
      to: END
```

Then compile and run:

```python
from sdk import WorkflowFactory, WorkflowRegistry

# Register workflow functions
WorkflowRegistry.register('load_data', load_data_func)
WorkflowRegistry.register('process_data', process_func)
WorkflowRegistry.register('save_results', save_func)

# Compile and run
graph = WorkflowFactory.compile_from_yaml('workflows/data_pipeline.yaml')
result = graph.invoke({"input_file": "data.csv"})
```

## YAML Configuration

### Agent YAML Example

```yaml
name: research_agent
description: An agent that conducts research and writes reports
model: gemini-2.5-flash
instruction_file: prompts/research_instructions.md
skills:
  - web_search
  - data_analysis
  - report_writing
input_key_map:
  topic: research_topic
  depth: analysis_depth
```

### Skill Directory Structure

```
skills/
  skill_name/
    SKILL.md              # Markdown instructions for the agent
    scripts/
      tool1.py            # Python file with tool functions
      tool2.py
      utils/
        helper.py
```

## Examples

See the `book_agent` directory for a complete example of:
- Multi-agent workflows
- Skill-based architecture
- YAML-based configuration
- LangGraph integration

## API Reference

### AgentFactory

- `from_yaml_file(yaml_path)` - Create agent from YAML file
- `from_yaml_dict(config_dict)` - Create agent from dictionary

### ToolRegistry

- `register(name, func)` - Register a tool function
- `get(name)` - Get a registered tool
- `register_from_directory(path)` - Auto-register tools from directory
- `list_tools()` - List all registered tools

### SkillRegistry

- `register(name, path)` - Register a skill directory
- `get_tools(skill_name)` - Get all tools from a skill
- `get_instructions(skill_name)` - Get skill instructions
- `list_skills()` - List all registered skills

### WorkflowFactory

- `compile_from_yaml(yaml_path)` - Compile LangGraph from YAML
- `compile_from_dict(config)` - Compile from dictionary

### WorkflowRegistry

- `register(name, func)` - Register a workflow function
- `get(name)` - Get a registered function
- `list_workflows()` - List all registered workflows

## Best Practices

1. **Organize by Skills**: Group related tools and instructions into skills
2. **Use YAML for Configuration**: Keep agent definitions declarative
3. **Version Your Agents**: Track changes to YAML configurations
4. **Document Tools**: Add clear docstrings to all tool functions
5. **Test Workflows**: Validate workflow YAML before deployment

## Troubleshooting

### Import Errors

If you get import errors:
```bash
# Verify installation
pip show declarative-agent-sdk

# Reinstall if needed
pip install --force-reinstall declarative-agent-sdk
```

### Tool Registration Issues

Tools must be registered before creating agents that use them:
```python
# Wrong order
agent = AgentFactory.from_yaml_file('agent.yaml')  # ✗ Tools not registered yet
ToolRegistry.register('my_tool', tool_func)

# Correct order
ToolRegistry.register('my_tool', tool_func)  # ✓ Register first
agent = AgentFactory.from_yaml_file('agent.yaml')
```

### Skill Discovery

Ensure skill directories have the correct structure:
- Must contain `SKILL.md` file
- Tool scripts must be in `scripts/` subdirectory
- Tool functions must have proper docstrings

## Next Steps

- Read the full [SDK Documentation](sdk/README.md)
- Check out [Build and Install Guide](BUILD_AND_INSTALL.md)
- Explore the [Book Agent Example](book_agent/README.md)
- Review example workflows in `book_agent/examples/`

## Support

- File issues on GitHub
- Check the documentation
- See examples in the repository
