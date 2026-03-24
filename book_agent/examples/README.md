# Book Agent Examples

This directory contains example scripts to test and demonstrate the book agent system.

## Available Examples

### test_toc_agent.py

Test script for the Table of Contents (TOC) Agent. This agent creates comprehensive book table of contents based on a given topic.

#### Usage

**Test with default topic:**
```bash
python test_toc_agent.py
```

**Test with custom topic:**
```bash
python test_toc_agent.py --topic "Your Book Topic Here"
```

**Run multiple test cases:**
```bash
python test_toc_agent.py --multiple
```

#### Examples

```bash
# Generate TOC for a Python programming book
python test_toc_agent.py --topic "Python Programming for Data Science"

# Generate TOC for an AI book
python test_toc_agent.py --topic "Deep Learning with PyTorch"

# Run automated tests with multiple topics
python test_toc_agent.py --multiple
```

#### Requirements

- TOC agent configuration at: `toc_agent/configs/toc_agent.yaml`
- vLLM server running (if using vLLM provider) at the endpoint specified in config
- TAVILY_API_KEY environment variable set (for web search functionality)

#### Expected Output

The script will:
1. Load the TOC agent from YAML configuration
2. Send the topic to the agent
3. Display the generated table of contents in YAML format
4. Show any output_key data if configured
5. Display the session ID

## Environment Setup

Before running examples, ensure you have:

1. **Installed SDK dependencies:**
   ```bash
   pip install -e /path/to/sdk
   ```

2. **Set environment variables** (in `.env` file or shell):
   ```bash
   TAVILY_API_KEY=your_tavily_api_key
   # For vLLM provider:
   OPENAI_API_KEY=sk-dummy-key  # Any value for local vLLM
   ```

3. **Started vLLM server** (if using vLLM provider):
   ```bash
   python -m vllm.entrypoints.openai.api_server \
     --model Qwen/Qwen3-4B-Thinking-2507-FP8 \
     --enable-auto-tool-choice \
     --tool-call-parser hermes \
     --host 0.0.0.0 \
     --port 8000
   ```

## Troubleshooting

### vLLM Tool Calling Error
If you see: `Error code: 400 - 'auto' tool choice requires --enable-auto-tool-choice`

**Solution:** Restart vLLM with tool calling enabled (see step 3 above)

### Import Errors
If you see: `ModuleNotFoundError: No module named 'sdk'`

**Solution:** Install the SDK package or add to PYTHONPATH:
```bash
export PYTHONPATH=/path/to/google-adk-samples:$PYTHONPATH
```

### Tavily Search Not Available
If you see: `Tool 'tavily_search' not found in registry`

**Solution:** 
1. Install langchain-community: `pip install langchain-community`
2. Set TAVILY_API_KEY in your environment
3. Restart the script

## Adding New Examples

To add new agent tests:

1. Create a new Python file: `test_<agent_name>.py`
2. Follow the pattern in `test_toc_agent.py`
3. Load agent from YAML configuration using `AgentFactory`
4. Create test cases with different inputs
5. Document usage in this README

## Support

For issues or questions, check:
- Main README: `/path/to/google-adk-samples/README.md`
- SDK Documentation: `/path/to/google-adk-samples/sdk/README.md`
- Agent configurations: `/path/to/google-adk-samples/book_agent/*/configs/`
