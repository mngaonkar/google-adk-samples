# Token Management in AgentFactory

The AgentFactory now supports automatic input truncation to prevent `ContextWindowExceededError` when working with models that have limited context windows.

## Features

- **Automatic Truncation**: Inputs are automatically truncated to fit within the model's context window
- **Multiple Strategies**: Choose how to truncate (beginning, end, or middle)
- **YAML Configuration**: Easy setup through YAML config files
- **Safety Margins**: Built-in safety buffer to account for tokenization overhead

## Quick Start

Add these parameters to your agent YAML configuration:

```yaml
name: my_agent
model: Qwen/Qwen3-4B-Thinking-2507-FP8
provider: vllm

endpoint:
  url: http://localhost:8000/v1
  max_tokens: 3000

# Token Management Configuration
enable_truncation: true       # Enable automatic truncation
context_window: 20384         # Total tokens available (model-specific)
truncate_strategy: end        # How to truncate: "end", "start", or "middle"
safety_margin: 100            # Extra tokens for overhead
```

## Configuration Parameters

### `enable_truncation` (bool, default: false)
Enables automatic input truncation. When true, inputs exceeding the context window will be automatically truncated.

**Important**: If `enable_truncation` is `true` but `context_window` is not provided, truncation will be **silently skipped** and inputs will be passed unchanged. Both `context_window` and `max_tokens` (from endpoint) must be configured for truncation to work.

### `context_window` (int, optional)
The total number of tokens available in the model's context window. Examples:
- Qwen3-4B: 20384 tokens
- Gemini 2.0 Flash: 1,000,000 tokens
- GPT-4: 8,192 tokens (older) or 128,000 tokens (turbo)

### `truncate_strategy` (str, default: "end")
Determines how the input is truncated:
- `"end"`: Keep the beginning, remove from the end (recommended for prompts)
- `"start"`: Keep the end, remove from the beginning (useful for chat history)
- `"middle"`: Keep both beginning and end, remove from the middle

### `safety_margin` (int, default: 100)
Number of tokens to reserve as a safety buffer to account for tokenization differences and overhead.

## Token Budget Calculation

The token budget is calculated as:

```
Available Input Tokens = context_window - max_tokens - safety_margin
```

Example with Qwen3-4B:
```
Available Input = 20384 - 3000 - 100 = 17,284 tokens
```

## Usage Examples

### Example 1: Basic YAML Configuration

```yaml
name: chapter_agent
instruction_file: chapter_agent/SKILL.md
model: Qwen/Qwen3-4B-Thinking-2507-FP8
provider: vllm

endpoint:
  url: http://10.0.0.147:8000/v1
  max_tokens: 3000

enable_truncation: true
context_window: 20384
truncate_strategy: end
```

### Example 2: Dictionary Configuration

```python
from declarative_agent_sdk import AgentFactory

config = {
    "name": "my_agent",
    "instruction_file": "path/to/instructions.md",
    "model": "Qwen/Qwen3-4B-Thinking-2507-FP8",
    "provider": "vllm",
    "endpoint": {
        "url": "http://localhost:8000/v1",
        "max_tokens": 3000
    },
    "enable_truncation": True,
    "context_window": 20384,
    "truncate_strategy": "end",
    "safety_margin": 100
}

agent = AgentFactory.from_dict(config)
```

### Example 3: Running with Large Inputs

```python
import asyncio
from declarative_agent_sdk import AgentFactory

async def main():
    agent = AgentFactory.from_yaml_file("config.yaml")
    
    # Long input that would normally exceed context window
    very_long_input = "Your prompt here" + " context..." * 10000
    
    # Automatically truncated to fit within context window
    result = await agent.run(very_long_input)
    print(result['final_response'])

asyncio.run(main())
```

## Truncation Strategies Explained

### "end" Strategy (Recommended for Prompts)
Keeps the beginning of the input, truncates from the end.

```
Input:  [Important instructions] [Context data...] [More context...]
Output: [Important instructions] [Context data...]
```

**Use when**: Your important instructions are at the beginning.

### "start" Strategy
Keeps the end of the input, truncates from the beginning.

```
Input:  [Old context] [Recent context] [Latest message]
Output:                [Recent context] [Latest message]
```

**Use when**: Recent messages/context are more important (chat history).

### "middle" Strategy
Keeps both beginning and end, truncates from the middle.

```
Input:  [Instructions] [Middle context...] [Final requirements]
Output: [Instructions]                      [Final requirements]
```

**Use when**: Both the start and end contain critical information.

## When to Use Token Truncation

### ✅ Good Use Cases

- **Long document processing**: Extracting information from large texts
- **Batch operations**: Processing multiple items where individual size varies
- **Production systems**: Preventing runtime errors from unexpected input sizes
- **Multi-agent workflows**: Where context accumulates across agents

### ⚠️ Considerations

- **Information loss**: Truncation removes content, which may affect quality
- **Testing needed**: Verify that truncated inputs still produce acceptable results
- **Alternative approaches**: Consider chunking, summarization, or retrieval instead

## Model Context Windows

Common models and their context windows:

| Model | Context Window | Notes |
|-------|----------------|-------|
| Qwen3-4B | 20,384 tokens | Local vLLM |
| Gemini 1.5 Pro | 2,000,000 tokens | Very large, rarely needs truncation |
| Gemini 2.0 Flash | 1,000,000 tokens | Large context |
| GPT-4 Turbo | 128,000 tokens | Large context |
| GPT-3.5 Turbo | 16,385 tokens | May need truncation |

## What Happens When Parameters Are Missing?

The token truncation is **gracefully optional**. Here's the behavior:

### Scenario 1: Both parameters provided + truncation enabled
```yaml
enable_truncation: true
context_window: 20384
endpoint:
  max_tokens: 3000
```
✅ **Result**: Full truncation active. Inputs exceeding budget are automatically truncated.

### Scenario 2: Truncation enabled but missing context_window
```yaml
enable_truncation: true
# context_window: not provided
endpoint:
  max_tokens: 3000
```
⚠️ **Result**: Truncation **silently disabled**. Input passed unchanged. You may still get `ContextWindowExceededError` on large inputs.

### Scenario 3: Truncation enabled but missing max_tokens
```yaml
enable_truncation: true
context_window: 20384
# max_tokens: not provided
```
⚠️ **Result**: Truncation **silently disabled**. Input passed unchanged.

### Scenario 4: Truncation disabled
```yaml
enable_truncation: false  # or not specified
context_window: 20384
endpoint:
  max_tokens: 3000
```
✅ **Result**: No truncation applied (expected behavior). Input passed as-is.

### Scenario 5: No truncation configuration at all
```yaml
# No truncation parameters
```
✅ **Result**: No truncation applied. Works like traditional agent behavior.

**Best Practice**: If you enable truncation, always provide both `context_window` and `max_tokens` to ensure it actually works.

## Troubleshooting

### Still getting ContextWindowExceededError

1. **Check configuration**: Ensure `enable_truncation: true` is set
2. **Verify context_window**: Make sure it matches your model's actual limit AND is actually configured in YAML
3. **Check max_tokens**: Ensure `max_tokens` is set in the `endpoint` section (or at root level)
4. **Check logs**: Look for warnings like "Incomplete context window configuration" or "No context window constraints provided"
5. **Increase safety_margin**: Try a larger buffer (200-500 tokens)
6. **Reduce max_tokens**: Lower the output reservation

### Truncation removes important content

1. **Use "middle" strategy**: Keeps both beginning and end
2. **Increase context_window**: Use a model with larger context
3. **Implement chunking**: Split input into smaller, focused pieces
4. **Summarize first**: Pre-process long inputs with a summarization step

### Wrong token counts

The system uses `tiktoken` with GPT-4 tokenization by default. This is approximate for other models but generally safe due to the safety margin.

## See Also

- [token_truncation_example.py](../sdk/examples/token_truncation_example.py) - Complete examples
- [chapter_agent_with_truncation_example.yaml](chapter_agent_with_truncation_example.yaml) - YAML example
- [token_utils.py](../../sdk/token_utils.py) - Low-level token utilities
