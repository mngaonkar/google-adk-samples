"""
Example: Using Token Truncation with AgentFactory

This example demonstrates how to configure and use automatic token truncation
to prevent ContextWindowExceededError when working with models that have
limited context windows.
"""

import asyncio
from sdk import AgentFactory, get_logger

logger = get_logger(__name__)


async def example_with_yaml_config():
    """Example 1: Using YAML configuration with token truncation enabled"""
    
    # Create agent from YAML with truncation enabled
    agent = AgentFactory.from_yaml_file(
        "book_agent/examples/chapter_agent_with_truncation_example.yaml"
    )
    
    # Create a very long input that would normally exceed context window
    long_input = """
    Write a chapter about artificial intelligence.
    
    Context (this would be very long in a real scenario):
    """ + "Lorem ipsum dolor sit amet. " * 5000  # Simulate long context
    
    # The agent will automatically truncate this to fit within the context window
    # No ContextWindowExceededError will be raised
    result = await agent.run(long_input)
    
    logger.info(f"Response: {result['final_response'][:200]}...")
    return result


async def example_with_dict_config():
    """Example 2: Using dictionary configuration"""
    
    config = {
        "name": "truncating_agent",
        "description": "Agent with automatic input truncation",
        "instruction_file": "book_agent/chapter_agent/SKILL.md",
        "model": "Qwen/Qwen3-4B-Thinking-2507-FP8",
        "provider": "vllm",
        "endpoint": {
            "url": "http://10.0.0.147:8000/v1",
            "max_tokens": 3000,
            "temperature": 0.8
        },
        # Token management configuration
        "enable_truncation": True,
        "context_window": 20384,  # Qwen3-4B context size
        "truncate_strategy": "end",  # Keep beginning, truncate end
        "safety_margin": 100,
        "skills": ["skills/chapter"],
        "output_key": "chapter_response"
    }
    
    agent = AgentFactory.from_dict(config)
    
    # Test with long input
    result = await agent.run("Write about machine learning" + " context..." * 1000)
    
    logger.info(f"Response received: {len(result['final_response'])} chars")
    return result


async def example_without_truncation():
    """Example 3: Agent without truncation (may fail on large inputs)"""
    
    config = {
        "name": "regular_agent",
        "instruction_file": "book_agent/chapter_agent/SKILL.md",
        "model": "Qwen/Qwen3-4B-Thinking-2507-FP8",
        "provider": "vllm",
        "endpoint": {
            "url": "http://10.0.0.147:8000/v1",
            "max_tokens": 3000
        },
        "enable_truncation": False,  # Disabled
        "skills": ["skills/chapter"]
    }
    
    agent = AgentFactory.from_dict(config)
    
    # Small input - should work fine
    result = await agent.run("Write a short paragraph about AI")
    
    logger.info("Success with normal-sized input")
    return result


async def example_truncation_strategies():
    """Example 4: Demonstrating different truncation strategies"""
    
    strategies = {
        "end": "Keep the beginning (prompt), truncate end (good for prompts)",
        "start": "Keep the end, truncate beginning (good for chat history)",
        "middle": "Keep both ends, truncate middle (balanced approach)"
    }
    
    for strategy, description in strategies.items():
        logger.info(f"\nTesting strategy: {strategy}")
        logger.info(f"Description: {description}")
        
        config = {
            "name": f"agent_{strategy}",
            "instruction_file": "book_agent/chapter_agent/SKILL.md",
            "model": "Qwen/Qwen3-4B-Thinking-2507-FP8",
            "provider": "vllm",
            "endpoint": {
                "url": "http://10.0.0.147:8000/v1",
                "max_tokens": 3000
            },
            "enable_truncation": True,
            "context_window": 20384,
            "truncate_strategy": strategy,
            "skills": ["skills/chapter"]
        }
        
        agent = AgentFactory.from_dict(config)
        
        # Create input with clear beginning, middle, and end markers
        long_input = (
            "BEGINNING: Write about AI. Important instructions here.\n\n"
            + "MIDDLE: " + ("Context data. " * 2000) + "\n\n"
            + "END: Make sure to include these final points."
        )
        
        result = await agent.run(long_input)
        logger.info(f"Strategy '{strategy}' completed successfully")


async def example_manual_configuration():
    """Example 5: Understanding the token budget calculation"""
    
    # Token budget breakdown:
    # Total context window: 20384 tokens (Qwen3-4B)
    # Reserved for output: 3000 tokens (max_tokens)
    # Safety margin: 100 tokens
    # Available for input: 20384 - 3000 - 100 = 17284 tokens
    
    logger.info("Token Budget Calculation:")
    logger.info("=" * 50)
    logger.info("Total context window: 20384 tokens")
    logger.info("Reserved for output: 3000 tokens")
    logger.info("Safety margin: 100 tokens")
    logger.info("Available for input: 17284 tokens")
    logger.info("=" * 50)
    
    config = {
        "name": "budget_aware_agent",
        "instruction_file": "book_agent/chapter_agent/SKILL.md",
        "model": "Qwen/Qwen3-4B-Thinking-2507-FP8",
        "provider": "vllm",
        "endpoint": {
            "url": "http://10.0.0.147:8000/v1",
            "max_tokens": 3000
        },
        "enable_truncation": True,
        "context_window": 20384,
        "safety_margin": 100,
        "skills": ["skills/chapter"]
    }
    
    agent = AgentFactory.from_dict(config)
    
    # Input will be automatically truncated to fit 17284 tokens
    result = await agent.run("Generate content" + " context..." * 5000)
    logger.info("Agent successfully handled large input with automatic truncation")


async def main():
    """Run all examples"""
    
    logger.info("=" * 70)
    logger.info("Token Truncation Examples")
    logger.info("=" * 70)
    
    try:
        logger.info("\n1. YAML Configuration Example")
        logger.info("-" * 70)
        await example_with_yaml_config()
        
        logger.info("\n2. Dictionary Configuration Example")
        logger.info("-" * 70)
        await example_with_dict_config()
        
        logger.info("\n3. Without Truncation Example")
        logger.info("-" * 70)
        await example_without_truncation()
        
        logger.info("\n4. Truncation Strategies Example")
        logger.info("-" * 70)
        await example_truncation_strategies()
        
        logger.info("\n5. Manual Configuration Example")
        logger.info("-" * 70)
        await example_manual_configuration()
        
        logger.info("\n" + "=" * 70)
        logger.info("All examples completed successfully!")
        logger.info("=" * 70)
        
    except Exception as e:
        logger.error(f"Error in examples: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
