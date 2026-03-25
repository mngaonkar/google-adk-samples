# Building Production-Ready AI Agents: A Declarative SDK for Google ADK

> **TL;DR:** Learn how to build, configure, and deploy production-grade AI agents using a declarative YAML-based SDK that supports multiple LLM providers, automatic token management, skills-based architecture, and zero-boilerplate agent creation.

---

## The Challenge: AI Agent Complexity at Scale

Building a single AI agent is straightforward. Building a dozen agents—each with different models, tools, skills, and context window constraints—quickly becomes a maintenance nightmare. You end up with:

- **Boilerplate everywhere**: The same initialization code copied across multiple agent files
- **Hardcoded configurations**: Model names, API keys, and parameters scattered throughout your codebase
- **Tool namespace conflicts**: Multiple agents trying to use functions with the same name
- **Context window errors**: Runtime failures when inputs exceed model token limits
- **Provider lock-in**: No easy way to switch between Google Gemini, OpenAI, or local vLLM servers

What if you could define agents declaratively in YAML, automatically manage token budgets, and compose reusable skills like building blocks?

**Enter the Declarative Agent SDK.**

---

## What Is This SDK?

The **Declarative Agent SDK** is a production-ready framework built on top of Google's Agent Development Kit (ADK). It provides:

🎯 **Zero-boilerplate agent creation** via YAML configuration  
🔧 **Skills-based architecture** with auto-discovery of tools  
🌐 **Multi-provider support** (Google Gemini, vLLM, OpenAI)  
⚡ **Automatic token management** to prevent context window errors  
🔒 **Instance-level isolation** preventing tool namespace conflicts  
📊 **Centralized logging** with configurable outputs  
🔄 **Hot-swappable configurations** without code changes  
🔀 **Multi-agent workflows** using LangGraph StateGraph in YAML

---

## Key Features

### 1. Declarative YAML Configuration

Define your entire agent in a YAML file—no Python boilerplate required.

```yaml
name: chapter_agent
description: Generates book chapters with web research capabilities
model: Qwen/Qwen3-4B-Thinking-2507-FP8
provider: vllm

endpoint:
  url: http://localhost:8000/v1
  max_tokens: 3000
  temperature: 0.8

# Auto-discover tools from skill directories
skills:
  - chapter
  - research

# Add global tools
tools:
  - tavily_search

# Automatic token management (NEW!)
enable_truncation: true
context_window: 20384
truncate_strategy: end
safety_margin: 100

output_key: chapter_response
```

Load it in one line:

```python
from sdk import AgentFactory

agent = AgentFactory.from_yaml_file('configs/chapter_agent.yaml')
```

**That's it.** Your agent is ready with tools, skills, instructions, and token management configured.

---

### 2. Multi-Provider Model Support

Switch between Google Gemini, OpenAI, or local vLLM servers without changing your code.

#### Google Gemini (Default)

```yaml
name: gemini_agent
model: gemini-2.0-flash-exp
# provider defaults to 'google'
```

#### vLLM (Local Inference)

```yaml
name: local_agent
model: Qwen/Qwen3-4B-Thinking-2507-FP8
provider: vllm
endpoint:
  url: http://10.0.0.147:8000/v1
  max_tokens: 3000
```

The `ModelFactory` handles provider-specific configurations automatically:

```python
from sdk import ModelFactory

# Create a Google Gemini model
gemini = ModelFactory.create_model(
    model_name="gemini-2.0-flash-exp",
    provider="google"
)

# Create a vLLM model
vllm = ModelFactory.create_model(
    model_name="Qwen/Qwen3-4B",
    provider="vllm",
    endpoint_url="http://localhost:8000/v1",
    max_tokens=2048
)
```

---

### 3. Automatic Token Management ⚡ NEW!

The most common runtime error in production AI systems? **Context window exceeded.**

The SDK now includes intelligent token management that automatically truncates inputs to fit within your model's limits.

#### The Problem

```python
# Your model has a 20,384 token context window
# You request 4,096 tokens for output
# Your input is 17,000 tokens

# Result: ERROR - ContextWindowExceededError 💥
# 17,000 + 4,096 = 21,096 > 20,384
```

#### The Solution

Enable automatic truncation in your YAML:

```yaml
enable_truncation: true
context_window: 20384       # Qwen3-4B total context
max_tokens: 3000            # Reserved for output
truncate_strategy: end      # Keep beginning, truncate end
safety_margin: 100          # Buffer for overhead
```

**What happens:**

```python
# SDK calculates: 20,384 - 3,000 - 100 = 17,284 tokens available
# Your input: 17,000 tokens → ✅ Fits perfectly
# Your input: 25,000 tokens → 🔧 Auto-truncated to 17,284 tokens
# Result: No runtime errors, ever
```

#### Truncation Strategies

Choose how to handle oversized inputs:

- **`end`**: Keep the beginning (important instructions), truncate the end
- **`start`**: Keep the end (recent messages), truncate the beginning  
- **`middle`**: Keep both ends, truncate the middle

**Production Use Case:**

```python
# Generate a chapter from a long research document
agent = AgentFactory.from_yaml_file('configs/chapter_agent.yaml')

# This document is 50,000 tokens (way over budget!)
long_research = load_research_document()

# Agent automatically truncates to fit, keeping the important parts
result = await agent.run(f"Write chapter about AI:\n\n{long_research}")
# ✅ Works without errors
```

---

### 4. Skills-Based Architecture

**Skills** are reusable components that bundle instructions and tools together.

#### Skill Directory Structure

```
skills/
  research/
    SKILL.md              # Instructions for web research
    scripts/
      search.py           # search_web(query) tool
      summarize.py        # summarize_results(text) tool
      
  chapter/
    SKILL.md              # Instructions for chapter writing
    scripts/
      outline.py          # create_outline(topic) tool
      format.py           # format_markdown(text) tool
```

#### Auto-Discovery Magic

When you add `skills: ['research', 'chapter']` to your YAML:

1. **Instructions are combined**: Each `SKILL.md` is appended to your agent's system prompt
2. **Tools are auto-discovered**: All functions in `scripts/` become available tools
3. **Namespaces are prefixed**: `search_web()` becomes `research_search_web()`
4. **Isolation is automatic**: Each agent gets its own tool registry

```yaml
name: writer_agent
skills:
  - research  # Auto-discovers: research_search_web, research_summarize
  - chapter   # Auto-discovers: chapter_create_outline, chapter_format
```

**Zero manual tool registration required.**

---

### 5. Instance-Level Tool Isolation

Each agent has its own isolated tool registry, preventing namespace conflicts.

```yaml
# agent_a.yaml
skills:
  - skill_x  # Has function process()

# agent_b.yaml
skills:
  - skill_y  # Also has function process()
```

**No conflicts!** Agent A gets `skill_x_process()`, Agent B gets `skill_y_process()`.

---

## Quick Start: Build Your First Agent in 5 Minutes

### Step 1: Create a Skill

```bash
mkdir -p skills/calculator/scripts
```

**File:** `skills/calculator/SKILL.md`
```markdown
# Calculator Skill

You have access to mathematical tools:
- calculator_add: Add two numbers
- calculator_multiply: Multiply two numbers

Use these when the user asks for calculations.
```

**File:** `skills/calculator/scripts/math_tools.py`
```python
def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b

def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b
```

### Step 2: Create Agent YAML

**File:** `configs/calculator_agent.yaml`
```yaml
name: calculator_agent
description: An agent that performs mathematical calculations
model: gemini-2.0-flash-exp
skills:
  - calculator
output_key: result
```

### Step 3: Run Your Agent

```python
from sdk import AgentFactory
import asyncio

async def main():
    agent = AgentFactory.from_yaml_file('configs/calculator_agent.yaml')
    
    result = await agent.run("What is 25 times 17?")
    print(result['final_response'])
    # Output: "425"

asyncio.run(main())
```

**Done!** You built an agent with zero boilerplate code.

---

## Advanced Use Cases

### Multi-Agent Workflows with Token Management

```python
from sdk import AgentFactory

# Research agent with large context window (processes long documents)
researcher = AgentFactory.from_yaml_file('configs/research_agent.yaml')

# Writer agent with token constraints (uses truncation)
writer = AgentFactory.from_yaml_file('configs/writer_agent.yaml')

# Workflow: Research → Write
research_data = await researcher.run("Research AI trends")

# This might be huge! But writer truncates automatically
chapter = await writer.run(f"Write chapter using: {research_data}")
```

### Environment-Specific Configurations

```python
import os
from sdk import AgentFactory

env = os.getenv('ENVIRONMENT', 'dev')

# Load dev, staging, or prod configs
agent = AgentFactory.from_yaml_file(f'configs/agent.{env}.yaml')
```

**Development:** Use fast local models  
**Production:** Use powerful cloud models

### Dynamic Agent Creation

```python
from sdk import AgentFactory

# Create agents programmatically
config = {
    'name': 'dynamic_agent',
    'model': 'gemini-2.0-flash-exp',
    'skills': ['research', 'writing'],
    'enable_truncation': True,
    'context_window': 1000000,
    'max_tokens': 8000
}

agent = AgentFactory.from_dict(config)
```

---

## YAML Configuration Reference

### Complete Schema

```yaml
# === REQUIRED ===
name: string                    # Unique agent identifier

# === OPTIONAL ===
description: string             # Human-readable description
instruction_file: string        # Path to main SKILL.md
model: string                   # Model name (default: gemini-2.0-flash-exp)
provider: string                # 'google' or 'vllm' (default: google)

# === ENDPOINT CONFIG ===
endpoint:
  url: string                   # API endpoint URL (vLLM only)
  max_tokens: integer          # Output token limit
  temperature: float           # Sampling temperature (0.0-1.0)

# === SKILLS & TOOLS ===
skills:                        # List of skill directories
  - skill_name_1
  - skill_name_2

tools:                         # Additional tool names
  - tool_name_1
  - tool_name_2

# === TOKEN MANAGEMENT ===
enable_truncation: boolean     # Auto-truncate inputs (default: false)
context_window: integer        # Total context size (e.g., 20384)
truncate_strategy: string      # 'end', 'start', or 'middle'
safety_margin: integer         # Extra token buffer (default: 100)

# === OUTPUT ===
output_key: string             # Session state output key
```

### Token Budget Calculation

```
Available Input Tokens = context_window - max_tokens - safety_margin

Example (Qwen3-4B):
  20,384 - 3,000 - 100 = 17,284 tokens available for input
```

---

## Production Best Practices

### 1. Always Enable Truncation for Variable-Length Inputs

```yaml
# ✅ Good: Handles unpredictable input sizes
enable_truncation: true
context_window: 20384
```

```yaml
# ⚠️ Risky: May crash on large inputs
enable_truncation: false
```

### 2. Use Skills for Reusability

```
# ✅ Good: Reusable across agents
skills/
  common/
    scripts/
      email.py
      format.py

# ❌ Bad: Duplicated across agents
agent_a/scripts/email.py
agent_b/scripts/email.py
```

### 3. Environment Variables for Secrets

```yaml
# ✅ Good: Use environment variables
endpoint:
  url: ${VLLM_ENDPOINT_URL}

# ❌ Bad: Hardcoded secrets
endpoint:
  url: http://secret-server:8000
```

### 4. Monitor Token Usage

```python
from sdk import get_logger

logger = get_logger(__name__)

# SDK logs token info automatically when truncation occurs:
# INFO: Context window: 20384 tokens
# INFO: Available for input: 17284 tokens
# WARNING: Input size (25000 tokens) exceeds budget, truncating...
```

### 5. Version Your Configurations

```
configs/
  agents/
    v1/
      research_agent.yaml
    v2/
      research_agent.yaml  # Breaking changes
```

---

## Architecture Overview

### Component Diagram

#### Single Agent Architecture

```
┌─────────────────────────────────────────────────┐
│      Agent YAML Configuration                   │
│   (agents, skills, tools, token management)     │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│           AgentFactory                          │
│  • Parses YAML                                  │
│  • Validates configuration                      │
│  • Creates model via ModelFactory               │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│           AIAgent Instance                      │
│  ┌─────────────────────────────────┐            │
│  │  Instance ToolRegistry          │            │
│  │  • Auto-discovered tools        │            │
│  │  • Prefixed namespace           │            │
│  └─────────────────────────────────┘            │
│  ┌─────────────────────────────────┐            │
│  │  Combined Instructions          │            │
│  │  • Main SKILL.md                │            │
│  │  • All skills' SKILL.md         │            │
│  └─────────────────────────────────┘            │
│  ┌─────────────────────────────────┐            │
│  │  Token Management               │            │
│  │  • Auto-truncation              │            │
│  │  • Budget calculation           │            │
│  └─────────────────────────────────┘            │
└─────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│         ModelFactory (Multi-Provider)           │
│  • Google Gemini                                │
│  • vLLM (local inference)                       │
│  • OpenAI (future)                              │
└─────────────────────────────────────────────────┘
```

#### Multi-Agent Workflow Architecture

```
┌─────────────────────────────────────────────────┐
│      Workflow YAML Configuration                │
│   (nodes, edges, conditional routing)           │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│         WorkflowRegistry                        │
│  • Agent functions (toc_agent, etc.)            │
│  • Router functions (route_after_toc)           │
│  • Helper functions                             │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│         WorkflowFactory                         │
│  • Parses workflow YAML                         │
│  • Resolves functions from registry             │
│  • Builds LangGraph StateGraph                  │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│      Compiled Workflow (LangGraph)              │
│  ┌──────────────────────────────┐               │
│  │  Nodes (Agent Executions)    │               │
│  │  • toc_agent                 │               │
│  │  • chapter_agent_parallel    │               │
│  │  • collation_agent           │               │
│  └──────────────────────────────┘               │
│  ┌──────────────────────────────┐               │
│  │  Edges (Flow Control)        │               │
│  │  • Simple: A → B             │               │
│  │  • Conditional: A → router() │               │
│  └──────────────────────────────┘               │
│  ┌──────────────────────────────┐               │
│  │  State Management            │               │
│  │  • Shared state across nodes │               │
│  │  • Parallel execution        │               │
│  └──────────────────────────────┘               │
└─────────────────────────────────────────────────┘
```

### Data Flow

#### Agent Creation Flow

```
1. Load YAML → Parse configuration
2. Extract skills → Auto-discover tools → Register with prefix
3. Combine SKILL.md → Build instruction text
4. Create model → ModelFactory handles provider
5. Validate token config → Setup truncation
6. Initialize agent → Return ready-to-use instance
```

#### Workflow Execution Flow

```
1. Load Workflow YAML → Parse nodes, edges, routers
2. Resolve functions → Lookup in WorkflowRegistry
3. Build graph → Create LangGraph StateGraph
4. Compile → Optimize execution plan
5. Invoke → Execute workflow with initial state
6. Route → Apply conditional logic at decision points
7. Complete → Return final state
```

---

## Multi-Agent Workflows with LangGraph

Beyond single agents, the SDK provides **WorkflowFactory** and **WorkflowRegistry** for building complex multi-agent workflows using LangGraph's StateGraph—all defined in YAML.

### Why Multi-Agent Workflows?

Complex tasks often require **multiple specialized agents** working together:

- **Book Writing**: TOC Agent → Chapter Agents (parallel) → Collation Agent
- **Research Pipeline**: Data Collector → Analyzer → Report Writer
- **Customer Support**: Classifier → Specialist Agents → Response Generator

Instead of hardcoding the workflow graph, define it declaratively in YAML.

---

### Quick Start: Your First Workflow

#### Step 1: Define Your State

```python
from typing import TypedDict

class BookState(TypedDict):
    topic: str
    toc: str
    chapters: list[str]
    final_pdf: str
```

#### Step 2: Create Agent Functions

```python
def toc_agent(state: BookState) -> BookState:
    """Generate table of contents."""
    # Your agent logic here
    state['toc'] = generate_toc(state['topic'])
    return state

def chapter_agent(state: BookState) -> BookState:
    """Generate chapters."""
    state['chapters'] = generate_chapters(state['toc'])
    return state

def collation_agent(state: BookState) -> BookState:
    """Create final PDF."""
    state['final_pdf'] = create_pdf(state['chapters'])
    return state

def route_after_toc(state: BookState) -> str:
    """Router function - decide next step based on state."""
    if validate_toc(state['toc']):
        return "chapter_agent"
    else:
        return "toc_agent"  # Retry TOC
```

#### Step 3: Register Workflow Functions

```python
from sdk import WorkflowRegistry

# Register all workflow nodes and routers
WorkflowRegistry.register("toc_agent", toc_agent)
WorkflowRegistry.register("chapter_agent", chapter_agent)
WorkflowRegistry.register("collation_agent", collation_agent)
WorkflowRegistry.register("route_after_toc", route_after_toc)

# Or register multiple at once
WorkflowRegistry.register_multiple({
    "toc_agent": toc_agent,
    "chapter_agent": chapter_agent,
    "collation_agent": collation_agent,
    "route_after_toc": route_after_toc
})
```

#### Step 4: Define Workflow in YAML

**File:** `configs/book_workflow.yaml`

```yaml
name: book_generation_workflow
description: Multi-agent workflow for book creation

# Define workflow nodes (steps)
nodes:
  - name: toc_agent
    function: toc_agent
    description: Generate table of contents
    
  - name: chapter_agent
    function: chapter_agent
    description: Generate all chapters
    
  - name: collation_agent
    function: collation_agent
    description: Create final PDF

# Define simple edges (direct connections)
edges:
  - from: START
    to: toc_agent
    
  - from: chapter_agent
    to: collation_agent
    
  - from: collation_agent
    to: END

# Define conditional edges (routing logic)
conditional_edges:
  - from: toc_agent
    router_function: route_after_toc
    description: Validate TOC and route accordingly
```

#### Step 5: Compile and Run

```python
from sdk import WorkflowFactory

# Compile workflow from YAML
workflow = WorkflowFactory.compile_from_yaml(
    'configs/book_workflow.yaml',
    BookState
)

# Run the workflow
initial_state = {"topic": "AI in 2024"}
result = workflow.invoke(initial_state)

print(result['final_pdf'])  # Path to generated PDF
```

**That's it!** Your multi-agent workflow is running with zero hardcoded graph logic.

---

### Workflow Execution Flow

The example above creates this execution graph:

```
START
  ↓
toc_agent
  ↓ (conditional: route_after_toc)
  ├─→ chapter_agent (if TOC valid)
  │     ↓
  │   collation_agent
  │     ↓
  │    END
  │
  └─→ toc_agent (if TOC invalid - retry)
```

---

### WorkflowRegistry API

The **WorkflowRegistry** stores the mapping between function names (used in YAML) and actual Python functions.

#### Register Functions

```python
from sdk import WorkflowRegistry

# Register individual function
WorkflowRegistry.register('my_agent', my_agent_function)

# Register multiple functions
WorkflowRegistry.register_multiple({
    'agent_1': agent_1_func,
    'agent_2': agent_2_func,
    'router': router_func
})
```

#### Retrieve Functions

```python
# Get a registered function
func = WorkflowRegistry.get('my_agent')

# Check if registered
if WorkflowRegistry.is_registered('my_agent'):
    print("Function exists")

# List all registered functions
all_funcs = WorkflowRegistry.list_available()
print(all_funcs)  # ['agent_1', 'agent_2', 'router']
```

#### Clear Registry (Testing)

```python
# Clear all registered functions (useful for tests)
WorkflowRegistry.clear()
```

---

### WorkflowFactory API

The **WorkflowFactory** builds LangGraph StateGraph workflows from YAML configuration.

#### Create from YAML File

```python
from sdk import WorkflowFactory
from my_state import MyState

# Load and compile workflow
workflow = WorkflowFactory.compile_from_yaml(
    'configs/my_workflow.yaml',
    MyState
)

# Run it
result = workflow.invoke({"input": "data"})
```

#### Create from Dictionary

```python
config = {
    'name': 'dynamic_workflow',
    'nodes': [
        {'name': 'step1', 'function': 'process_data'},
        {'name': 'step2', 'function': 'analyze_data'}
    ],
    'edges': [
        {'from': 'START', 'to': 'step1'},
        {'from': 'step1', 'to': 'step2'},
        {'from': 'step2', 'to': 'END'}
    ]
}

workflow = WorkflowFactory.from_dict(config, MyState)
compiled = workflow.compile()
```

#### Manual Compilation

```python
# If you need the graph before compiling
graph = WorkflowFactory.from_yaml_file(
    'configs/workflow.yaml',
    MyState
)

# Inspect or modify the graph
print(graph.nodes)

# Then compile when ready
compiled_workflow = graph.compile()
```

---

### YAML Workflow Schema

#### Complete Configuration Format

```yaml
# Workflow metadata
name: string                    # Workflow identifier
description: string             # Human-readable description

# Workflow nodes (processing steps)
nodes:
  - name: string               # Node identifier
    function: string           # Registered function name
    description: string        # Optional description

# Simple edges (direct connections)
edges:
  - from: string               # Source node (or START)
    to: string                 # Target node (or END)
    type: simple               # Optional, defaults to simple

# Conditional edges (routing logic)
conditional_edges:
  - from: string               # Source node
    router_function: string    # Registered router function name
    description: string        # Optional description
```

#### Special Node Names

- **`START`**: Entry point of the workflow
- **`END`**: Exit point of the workflow

---

### Real-World Example: Book Generation

This example shows a production workflow with parallel execution, validation, and error recovery.

**File:** `configs/book_workflow.yaml`

```yaml
name: book_generation_workflow
description: Multi-agent book generation with parallel chapter creation

nodes:
  - name: toc_agent
    function: toc_agent
    description: Generate and validate table of contents
    
  - name: chapter_agent_parallel
    function: chapter_agent_parallel
    description: Generate all chapters in parallel using Send API
    
  - name: collation_agent
    function: collation_agent
    description: Combine chapters into final PDF

edges:
  - from: START
    to: toc_agent
    
  - from: chapter_agent_parallel
    to: collation_agent
    
  - from: collation_agent
    to: END

conditional_edges:
  - from: toc_agent
    router_function: route_after_toc
    description: |
      Validates TOC YAML format and content.
      If valid: proceed to chapter_agent_parallel
      If invalid: retry toc_agent
```

**Python Implementation:**

```python
from typing import Literal
from sdk import WorkflowRegistry, WorkflowFactory

# Define router with type hints for LangGraph
def route_after_toc(state: BookState) -> Literal["chapter_agent_parallel", "toc_agent"]:
    """Validate TOC and route to next step or retry."""
    toc_file = state.get('toc_location')
    
    if not toc_file or not os.path.exists(toc_file):
        return "toc_agent"  # Retry
    
    try:
        with open(toc_file) as f:
            toc_data = yaml.safe_load(f)
        
        # Validate TOC structure
        if validate_toc_structure(toc_data):
            return "chapter_agent_parallel"  # Proceed
        else:
            return "toc_agent"  # Retry
            
    except Exception as e:
        logger.error(f"TOC validation failed: {e}")
        return "toc_agent"  # Retry

# Parallel chapter generation using LangGraph Send API
def chapter_agent_parallel(state: BookState):
    """Generate multiple chapters in parallel."""
    from langgraph.types import Send
    
    toc = load_toc(state['toc_location'])
    
    # Create parallel Send commands for each chapter
    return [
        Send("generate_chapter", {"chapter": ch})
        for ch in toc['chapters']
    ]

# Register everything
WorkflowRegistry.register_multiple({
    "toc_agent": toc_agent,
    "chapter_agent_parallel": chapter_agent_parallel,
    "generate_chapter": generate_single_chapter,
    "collation_agent": collation_agent,
    "route_after_toc": route_after_toc
})

# Compile and run
workflow = WorkflowFactory.compile_from_yaml(
    'configs/book_workflow.yaml',
    BookState
)

result = workflow.invoke({
    "topic": "The Future of AI",
    "toc_location": "",
    "chapters": [],
    "final_pdf": ""
})
```

---

### Advanced Workflow Patterns

#### Pattern 1: Retry with Max Attempts

```python
def route_with_retry(state: MyState) -> str:
    """Retry up to 3 times before giving up."""
    attempts = state.get('attempts', 0)
    
    if attempts >= 3:
        return "error_handler"
    
    if validate(state):
        return "next_step"
    else:
        state['attempts'] = attempts + 1
        return "retry_step"
```

#### Pattern 2: Dynamic Branching

```python
def dynamic_router(state: MyState) -> str:
    """Route based on data type."""
    data_type = state.get('data_type')
    
    routing = {
        'text': 'text_processor',
        'image': 'image_processor',
        'audio': 'audio_processor'
    }
    
    return routing.get(data_type, 'unknown_handler')
```

#### Pattern 3: Parallel Fan-Out/Fan-In

```yaml
nodes:
  - name: split_task
    function: split_into_subtasks
    
  - name: process_parallel
    function: process_subtasks  # Returns Send() list
    
  - name: merge_results
    function: combine_results

edges:
  - from: START
    to: split_task
    
  - from: split_task
    to: process_parallel
    
  - from: process_parallel
    to: merge_results
    
  - from: merge_results
    to: END
```

```python
def process_subtasks(state):
    """Fan-out to parallel processing."""
    from langgraph.types import Send
    
    return [
        Send("worker", {"task": task})
        for task in state['subtasks']
    ]
```

---

### Benefits of Workflow YAML Configuration

| Feature | Manual LangGraph | YAML Workflow |
|---------|-----------------|---------------|
| **Code Lines** | 50-100+ lines | 20-30 lines YAML |
| **Readability** | Python graph API | Declarative, visual |
| **Modifications** | Code changes | Config changes |
| **Version Control** | Diff complex code | Diff simple YAML |
| **Testing** | Mock graph objects | Swap function registry |
| **Documentation** | Inline comments | Self-documenting YAML |
| **Non-Developers** | Can't modify | Can modify workflow |

---

### Error Handling & Validation

#### Function Not Registered

```python
# Error message if function not found:
ValueError: Function 'my_agent' not found in registry.
Available functions: ['toc_agent', 'chapter_agent', 'collation_agent']
```

**Solution:**

```python
# Ensure function is registered before creating workflow
WorkflowRegistry.register('my_agent', my_agent_function)
```

#### Invalid YAML Structure

```python
# Error if node missing required fields:
ValueError: Node must have 'name' and 'function': {'name': 'my_node'}
```

**Solution:**

```yaml
nodes:
  - name: my_node
    function: my_function  # Required!
```

#### Router Function Returns Invalid Node

If your router function returns a node name that doesn't exist in the graph, LangGraph will raise an error at runtime.

**Solution:**

```python
def safe_router(state) -> Literal["valid_node_1", "valid_node_2"]:
    """Use Literal type hints to enforce valid routes."""
    if condition:
        return "valid_node_1"
    else:
        return "valid_node_2"
```

---

### Testing Workflows

#### Unit Testing Individual Nodes

```python
import pytest

def test_toc_agent():
    state = {"topic": "Test Topic"}
    result = toc_agent(state)
    
    assert 'toc_location' in result
    assert os.path.exists(result['toc_location'])

def test_router():
    # Test valid TOC
    state_valid = {"toc_location": "valid_toc.yaml"}
    assert route_after_toc(state_valid) == "chapter_agent_parallel"
    
    # Test invalid TOC
    state_invalid = {"toc_location": ""}
    assert route_after_toc(state_invalid) == "toc_agent"
```

#### Integration Testing Workflow

```python
def test_complete_workflow():
    workflow = WorkflowFactory.compile_from_yaml(
        'configs/book_workflow.yaml',
        BookState
    )
    
    initial_state = {
        "topic": "Test Book",
        "toc_location": "",
        "chapters": [],
        "final_pdf": ""
    }
    
    result = workflow.invoke(initial_state)
    
    # Verify output
    assert result['final_pdf'] != ""
    assert os.path.exists(result['final_pdf'])
    assert len(result['chapters']) > 0
```

#### Mock Functions for Testing

```python
@pytest.fixture
def mock_workflow():
    # Clear registry
    WorkflowRegistry.clear()
    
    # Register mock functions
    def mock_agent(state):
        state['processed'] = True
        return state
    
    WorkflowRegistry.register('mock_agent', mock_agent)
    
    # Create test workflow
    config = {
        'name': 'test_workflow',
        'nodes': [{'name': 'agent', 'function': 'mock_agent'}],
        'edges': [
            {'from': 'START', 'to': 'agent'},
            {'from': 'agent', 'to': 'END'}
        ]
    }
    
    return WorkflowFactory.from_dict(config, dict).compile()

def test_with_mocks(mock_workflow):
    result = mock_workflow.invoke({"input": "test"})
    assert result['processed'] is True
```

---

### Migration Guide: Manual Graph → YAML Workflow

**Before (Manual LangGraph):**

```python
from langgraph.graph import StateGraph, START, END

# Create graph
workflow = StateGraph(BookState)

# Add nodes
workflow.add_node("toc_agent", toc_agent)
workflow.add_node("chapter_agent", chapter_agent)
workflow.add_node("collation_agent", collation_agent)

# Add edges
workflow.add_edge(START, "toc_agent")
workflow.add_conditional_edges("toc_agent", route_after_toc)
workflow.add_edge("chapter_agent", "collation_agent")
workflow.add_edge("collation_agent", END)

# Compile
compiled = workflow.compile()
```

**After (YAML Workflow):**

```yaml
# configs/book_workflow.yaml
name: book_generation_workflow

nodes:
  - name: toc_agent
    function: toc_agent
  - name: chapter_agent
    function: chapter_agent
  - name: collation_agent
    function: collation_agent

edges:
  - from: START
    to: toc_agent
  - from: chapter_agent
    to: collation_agent
  - from: collation_agent
    to: END

conditional_edges:
  - from: toc_agent
    router_function: route_after_toc
```

```python
from sdk import WorkflowRegistry, WorkflowFactory

# Register functions
WorkflowRegistry.register_multiple({
    "toc_agent": toc_agent,
    "chapter_agent": chapter_agent,
    "collation_agent": collation_agent,
    "route_after_toc": route_after_toc
})

# One-line compilation
compiled = WorkflowFactory.compile_from_yaml(
    'configs/book_workflow.yaml',
    BookState
)
```

**Benefits:**
- **80% less code**: From 15+ lines to 1 line
- **Visual clarity**: YAML shows structure clearly
- **Easy modifications**: Change workflow without code changes
- **Version control**: Cleaner diffs in YAML

---

## Registries: The Three-Tier System

### ToolRegistry

Manages callable functions and tools.

```python
from sdk import ToolRegistry

# Manual registration (global tools)
def my_custom_tool(query: str) -> str:
    return f"Result for: {query}"

ToolRegistry.register('custom_search', my_custom_tool)

# Auto-discovery (from skills)
count = ToolRegistry.register_from_scripts_folder(
    'skills/research/scripts',
    prefix='research_'
)
print(f"Registered {count} tools")

# List available tools
tools = ToolRegistry.list_available()
```

### SkillRegistry

Stores skill metadata and directories.

```python
from sdk import SkillRegistry

# Register a skill
SkillRegistry.register(
    'research',
    directory='skills/research',
    description='Web research capabilities',
    category='utility'
)

# Get skill directory
directory = SkillRegistry.get_directory('research')

# List all skills
skills = SkillRegistry.list_available()
```

### WorkflowRegistry

Stores workflow functions and routers for multi-agent workflows.

```python
from sdk import WorkflowRegistry

# Register workflow functions
def my_agent(state):
    # Process state
    return state

def my_router(state):
    # Route to next node
    return "next_node"

WorkflowRegistry.register('my_agent', my_agent)
WorkflowRegistry.register('my_router', my_router)

# Register multiple at once
WorkflowRegistry.register_multiple({
    'agent_1': agent_1_func,
    'agent_2': agent_2_func,
    'router': router_func
})

# Get registered function
func = WorkflowRegistry.get('my_agent')

# Check if registered
if WorkflowRegistry.is_registered('my_agent'):
    print("Function is registered")

# List all registered functions
functions = WorkflowRegistry.list_available()

# Clear registry (useful for testing)
WorkflowRegistry.clear()
```

**See the [Multi-Agent Workflows](#multi-agent-workflows-with-langgraph) section for complete workflow examples.**

---

## Token Management Deep Dive

### Why Token Management Matters

**Real-world scenario:**

```python
# You're building a book writing system
# Each chapter agent processes:
#   - Book outline (500 tokens)
#   - Previous chapters (10,000 tokens)
#   - Research data (15,000 tokens)
#   - Instructions (500 tokens)
# Total: 26,000 tokens

# Your model (Qwen3-4B) has a 20,384 token limit
# Result: CRASH 💥
```

### The Solution: Automatic Truncation

```yaml
# Config
enable_truncation: true
context_window: 20384
max_tokens: 3000
truncate_strategy: end
safety_margin: 100
```

```python
# SDK automatically:
# 1. Calculates: 20,384 - 3,000 - 100 = 17,284 tokens available
# 2. Counts input tokens: 26,000 tokens
# 3. Truncates to fit: Keeps first 17,284 tokens
# 4. Processes without error ✅
```

### When to Use Which Strategy

| Strategy | Use Case | Example |
|----------|----------|---------|
| `end` | Important instructions at start | Prompts with context at the end |
| `start` | Recent messages more important | Chat history |
| `middle` | Both ends contain critical info | Instructions + final requirements |

### Model Context Windows Reference

| Model | Context Window | Token Management Needed? |
|-------|----------------|-------------------------|
| **Qwen3-4B** | 20,384 | ✅ Yes |
| **GPT-3.5 Turbo** | 16,385 | ✅ Yes |
| **GPT-4** | 8,192 | ✅ Yes |
| **GPT-4 Turbo** | 128,000 | ⚠️ Sometimes |
| **Gemini 2.0 Flash** | 1,000,000 | ❌ Rarely |
| **Gemini 1.5 Pro** | 2,000,000 | ❌ Almost never |

---

## Error Handling & Validation

The SDK provides clear, actionable error messages:

### Configuration Errors

```python
# Missing required field
ValueError: Agent 'name' is required in configuration

# Invalid token configuration
ValueError: Invalid context window configuration: 
max_context_tokens (20384) - max_output_tokens (25000) 
- safety_margin (100) = -4716 <= 0.
Reduce max_output_tokens or increase max_context_tokens.

# Skill not found
FileNotFoundError: Skill directory not found: /path/to/skills/missing
```

### Runtime Warnings

```python
# Incomplete truncation config
WARNING: Incomplete context window configuration: 
max_context_tokens=None, max_output_tokens=3000. 
Both must be provided for truncation. Returning input unchanged.

# Tool not found (non-fatal)
WARNING: Tool 'unknown_tool' not found in instance registry, skipping
```

### Token Management Errors

```python
# Truncation disabled but input too large
ContextWindowExceededError: Input exceeds context window

# Fix: Enable truncation
enable_truncation: true
context_window: 20384
```

---

## Migration Guide

### Migrating from Manual Agent Creation

**Before (Manual):**

```python
from sdk.ai_agent import AIAgent
from sdk.utils import read_from_file
from sdk.tool_registry import ToolRegistry

# Register tools manually
ToolRegistry.register('search', search_tool)
ToolRegistry.register('validate', validate_tool)

# Read instruction
instruction = read_from_file('agent/SKILL.md')

# Create agent with all parameters
agent = AIAgent(
    name='my_agent',
    description='Does something useful',
    instruction_file='agent/SKILL.md',
    tools=[search_tool, validate_tool],
    output_key='result',
    model='gemini-2.0-flash-exp'
)

# Manually handle token limits
if len(input_text) > 10000:
    input_text = input_text[:10000]  # Crude truncation
```

**After (Declarative):**

```yaml
# configs/my_agent.yaml
name: my_agent
description: Does something useful
skills:
  - utility  # Auto-discovers search and validate tools
output_key: result
model: gemini-2.0-flash-exp

# Automatic token management
enable_truncation: true
context_window: 1000000
max_tokens: 8192
```

```python
from sdk import AgentFactory

# One line!
agent = AgentFactory.from_yaml_file('configs/my_agent.yaml')
```

**Benefits:**
- **90% less code**: From 40+ lines to 1 line
- **Auto-discovery**: No manual tool registration
- **Token safety**: Intelligent truncation built-in
- **Easy updates**: Change configs without code changes

---

## Real-World Examples

### Example 1: Book Writing System

```yaml
# research_agent.yaml
name: research_agent
model: gemini-1.5-pro  # Large context for research
skills:
  - web_research
  - summarization
tools:
  - tavily_search
enable_truncation: false  # Large context, no truncation needed
```

```yaml
# chapter_agent.yaml
name: chapter_agent
model: Qwen/Qwen3-4B-Thinking-2507-FP8  # Fast local inference
provider: vllm
endpoint:
  url: http://localhost:8000/v1
  max_tokens: 3000
skills:
  - chapter_writing
  - formatting
enable_truncation: true
context_window: 20384
truncate_strategy: end  # Keep instructions, truncate context
```

```python
# Workflow
researcher = AgentFactory.from_yaml_file('configs/research_agent.yaml')
writer = AgentFactory.from_yaml_file('configs/chapter_agent.yaml')

# Research (large input, large output)
research = await researcher.run("Research AI trends 2024")

# Write (auto-truncated input, constrained output)
chapter = await writer.run(f"Write chapter:\n{research}")
```

### Example 2: Customer Support with Local Models

```yaml
# support_agent.yaml
name: support_agent
description: Customer support with local vLLM
model: Meta-Llama-3-8B-Instruct
provider: vllm
endpoint:
  url: http://gpu-server:8000/v1
  max_tokens: 1024
  temperature: 0.7
skills:
  - customer_support
  - knowledge_base
enable_truncation: true
context_window: 8192  # Llama-3-8B context
truncate_strategy: middle  # Keep recent + instructions
safety_margin: 200
```

### Example 3: Multi-Environment Setup

```yaml
# agent.dev.yaml (Development)
name: dev_agent
model: gemini-2.0-flash-exp  # Fast, cheap
endpoint:
  max_tokens: 1024
```

```yaml
# agent.prod.yaml (Production)
name: prod_agent
model: Qwen/Qwen3-4B-Thinking-2507-FP8
provider: vllm
endpoint:
  url: ${VLLM_ENDPOINT}  # Environment variable
  max_tokens: 3000
enable_truncation: true
context_window: 20384
```

```python
import os
from sdk import AgentFactory

env = os.getenv('ENV', 'dev')
agent = AgentFactory.from_yaml_file(f'configs/agent.{env}.yaml')
```

---

## Centralized Logging

Configure logging across all SDK components.

```python
from sdk import setup_logging, get_logger
import logging

# Setup at application start
setup_logging(
    level=logging.INFO,
    log_file='agent.log',
    log_format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Or use environment variables
# export SDK_LOG_LEVEL=DEBUG
# export SDK_LOG_FILE=/var/log/agents.log
# export SDK_LOG_FORMAT='[%(levelname)s] %(message)s'

# Get logger in any module
logger = get_logger(__name__)
logger.info("Agent started")
logger.warning("Token limit approaching")
```

**See [LOGGING.md](LOGGING.md) for complete documentation.**

---

## Performance Tips

### 1. Use Local Models for Development

```yaml
# Fast iteration with local vLLM
provider: vllm
model: Qwen/Qwen3-4B  # Free, fast, local
```

### 2. Cache Agent Instances

```python
# Good: Load once, reuse
agent = AgentFactory.from_yaml_file('config.yaml')
for task in tasks:
    await agent.run(task)

# Bad: Reload every time
for task in tasks:
    agent = AgentFactory.from_yaml_file('config.yaml')  # Slow!
    await agent.run(task)
```

### 3. Optimize Token Usage

```yaml
# Reserve only what you need
max_tokens: 1024  # Don't default to 4096 if you only need 1024
safety_margin: 50  # Smaller margin = more input capacity
```

### 4. Batch Similar Requests

```python
# Process multiple items with same agent
batch = ["Task 1", "Task 2", "Task 3"]
results = await asyncio.gather(*[agent.run(task) for task in batch])
```

---

## Security Best Practices

### 1. Use Environment Variables for Secrets

```yaml
# ✅ Good
endpoint:
  url: ${VLLM_ENDPOINT_URL}
  api_key: ${VLLM_API_KEY}

# ❌ Bad
endpoint:
  url: http://secret-server:8000
  api_key: sk-1234567890abcdef
```

### 2. Validate Input Before Processing

```python
def safe_run(agent, user_input):
    # Validate input
    if len(user_input) > 100000:  # 100k chars
        raise ValueError("Input too large")
    
    # Sanitize
    clean_input = sanitize(user_input)
    
    # Run agent
    return agent.run_sync(clean_input)
```

### 3. Limit Tool Capabilities

```python
# Give agents only necessary tools
skills:
  - read_only_tools  # Safe for untrusted input

# Don't give unnecessary permissions
# ❌ skills: [file_system, database, admin]
```

---

## Testing Your Agents

### Unit Testing

```python
import pytest
from sdk import AgentFactory

@pytest.fixture
def test_agent():
    return AgentFactory.from_yaml_file('configs/test_agent.yaml')

def test_agent_response(test_agent):
    result = test_agent.run_sync("Test input")
    assert result['final_response'] is not None
    assert len(result['final_response']) > 0

def test_token_truncation(test_agent):
    # Create oversized input
    huge_input = "Test " * 50000
    
    # Should not raise ContextWindowExceededError
    result = test_agent.run_sync(huge_input)
    assert result['final_response'] is not None
```

### Integration Testing

```python
async def test_multi_agent_workflow():
    researcher = AgentFactory.from_yaml_file('configs/researcher.yaml')
    writer = AgentFactory.from_yaml_file('configs/writer.yaml')
    
    # End-to-end workflow
    research = await researcher.run("Research topic")
    chapter = await writer.run(f"Write using: {research}")
    
    assert len(chapter['final_response']) > 1000
```

---

## Troubleshooting

### Issue: Context Window Errors Still Occur

**Symptoms:**
```
ContextWindowExceededError: Input exceeds context window
```

**Solutions:**

1. **Check configuration:**
   ```yaml
   enable_truncation: true  # Must be true
   context_window: 20384    # Must match your model
   ```

2. **Verify logs:**
   ```
   # Look for these messages
   WARNING: Incomplete context window configuration
   INFO: Token truncation enabled
   ```

3. **Increase safety margin:**
   ```yaml
   safety_margin: 500  # Larger buffer
   ```

### Issue: Tools Not Found

**Symptoms:**
```
WARNING: Tool 'my_tool' not found in instance registry
```

**Solutions:**

1. **Check skill directory structure:**
   ```
   skills/my_skill/
     SKILL.md ✅
     scripts/
       my_tool.py ✅  # File exists
       def my_tool(): ✅  # Function defined
   ```

2. **Verify function is not private:**
   ```python
   # ✅ Good: Public function
   def my_tool():
       pass
   
   # ❌ Bad: Private (ignored)
   def _my_tool():
       pass
   ```

3. **Check YAML configuration:**
   ```yaml
   skills:
     - my_skill  # Skill must be listed
   ```

### Issue: Model Connection Fails

**Symptoms:**
```
ConnectionError: Failed to connect to vLLM endpoint
```

**Solutions:**

1. **Verify vLLM server is running:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Check endpoint URL:**
   ```yaml
   endpoint:
     url: http://localhost:8000/v1  # Include /v1
   ```

3. **Test with simple request:**
   ```python
   import requests
   response = requests.post(
       "http://localhost:8000/v1/completions",
       json={"model": "Qwen/Qwen3-4B", "prompt": "test"}
   )
   print(response.status_code)
   ```

---

## Roadmap & Future Features

### Recently Added ✨

- [x] **Multi-agent workflows**: WorkflowFactory and WorkflowRegistry for LangGraph workflows in YAML
- [x] **Automatic token management**: Built-in truncation to prevent context window errors
- [x] **Multi-provider support**: Google Gemini, vLLM with ModelFactory
- [x] **Skills-based architecture**: Auto-discovery of tools from skill directories

### Planned Features

- [ ] **More providers**: OpenAI, Anthropic, Cohere
- [ ] **Automatic retries**: Built-in retry logic with exponential backoff
- [ ] **Streaming support**: Real-time token streaming
- [ ] **Cost tracking**: Monitor API costs per agent
- [ ] **A/B testing**: Compare different configurations
- [ ] **Model routing**: Automatic fallback to cheaper/faster models
- [ ] **Caching layer**: Cache frequent requests
- [ ] **Workflow visualization**: Generate diagrams from YAML workflows

### Contributing

Contributions welcome! Areas of interest:

- New model providers (Anthropic Claude, Cohere, etc.)
- Enhanced token management strategies
- Additional tool discovery mechanisms
- Performance optimizations
- Documentation improvements

---

## Conclusion

The **Declarative Agent SDK** transforms AI agent development from code-heavy to config-driven. By combining:

✅ **Zero-boilerplate YAML configuration**  
✅ **Automatic token management**  
✅ **Multi-provider model support**  
✅ **Skills-based architecture**  
✅ **Instance-level isolation**  
✅ **Multi-agent workflows** with WorkflowFactory

You can build production-ready AI systems that are:

- **Maintainable**: Change configs, not code
- **Scalable**: Add agents without duplication
- **Reliable**: Automatic error prevention
- **Flexible**: Switch models and providers easily
- **Testable**: Clear separation of concerns
- **Orchestratable**: Complex multi-agent workflows in YAML

### Getting Started

1. **Clone the repository**
2. **Create your first skill** in `skills/`
3. **Define an agent** in a YAML file
4. **Load and run** with `AgentFactory.from_yaml_file()`
5. **Build workflows** with `WorkflowFactory.compile_from_yaml()`

### Resources

- **Complete Examples**: [`/book_agent/examples/`](../book_agent/examples/)
- **Token Management Guide**: [`TOKEN_MANAGEMENT_GUIDE.md`](../book_agent/examples/TOKEN_MANAGEMENT_GUIDE.md)
- **Logging Documentation**: [`LOGGING.md`](LOGGING.md)
- **Skill Examples**: [`/skills/`](../skills/)
- **Workflow Examples**: [`/book_agent/configs/agents/book_workflow.yaml`](../book_agent/configs/agents/book_workflow.yaml)

---

**Built with ❤️ for production AI systems**

*Questions? Issues? Contributions? Let's build better agents together.*

---

## Appendix: Complete YAML Examples

### Minimal Configuration

```yaml
name: minimal_agent
model: gemini-2.0-flash-exp
```

### Full-Featured Configuration

```yaml
name: full_featured_agent
description: A comprehensive agent with all features enabled
instruction_file: agent/SKILL.md
model: Qwen/Qwen3-4B-Thinking-2507-FP8
provider: vllm

endpoint:
  url: http://10.0.0.147:8000/v1
  max_tokens: 3000
  temperature: 0.8

skills:
  - research
  - writing
  - validation

tools:
  - tavily_search
  - custom_tool

enable_truncation: true
context_window: 20384
truncate_strategy: end
safety_margin: 100

output_key: agent_response
```

### Production-Ready Configuration

```yaml
name: production_agent
description: Production agent with monitoring and safety
model: gemini-2.0-flash-exp

skills:
  - core_capabilities
  - safety_checks
  - logging

tools:
  - production_search
  - validation_tool

# Token safety
enable_truncation: true
context_window: 1000000
truncate_strategy: middle
safety_margin: 500

# Output configuration
output_key: production_response

# Environment-specific settings
endpoint:
  url: ${PROD_ENDPOINT_URL}
  max_tokens: ${PROD_MAX_TOKENS}
  temperature: 0.7
```

---

**End of Documentation**
