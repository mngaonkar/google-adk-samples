"""
Test script for TOC Agent

This script tests the Table of Contents agent by creating a TOC 
for different book topics.
"""

import sys
import os
import asyncio
from pathlib import Path

# Add parent directory to path to import sdk
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sdk import AgentFactory, setup_logging
from sdk.logging_config import get_logger

# Setup logging
setup_logging(level="DEBUG")
logger = get_logger(__name__)


async def test_toc_agent(topic: str):
    """
    Test the TOC agent with a given book topic.
    
    Args:
        topic: The book topic to generate a table of contents for
    """
    logger.info(f"Testing TOC Agent with topic: {topic}")
    logger.info("=" * 80)
    
    # Path to TOC agent configuration
    config_path = Path(__file__).parent.parent / "toc_agent" / "configs" / "toc_agent.yaml"
    
    if not config_path.exists():
        logger.error(f"Config file not found: {config_path}")
        return
    
    try:
        # Create agent from YAML configuration
        logger.info(f"Loading agent configuration from: {config_path}")
        agent = AgentFactory.from_yaml_file(str(config_path))
        logger.info(f"Agent '{agent.name}' loaded successfully")
        
        # Run the agent
        logger.info(f"\nGenerating table of contents for: {topic}")
        logger.info("-" * 80)
        
        result = await agent.run(
            input_text=f"Create a comprehensive table of contents for a book about: {topic}",
            user_id="test_user"
        )
        
        # Display results
        logger.info("\n" + "=" * 80)
        logger.info("AGENT RESPONSE:")
        logger.info("=" * 80)
        print("\n" + result["final_response"])
        
        # Display output_key data if available
        if result.get("output_key_data"):
            logger.info("\n" + "=" * 80)
            logger.info("OUTPUT KEY DATA (toc_agent_response):")
            logger.info("=" * 80)
            print(result["output_key_data"])
        
        logger.info("\n" + "=" * 80)
        logger.info(f"Session ID: {result['session_id']}")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"Error testing TOC agent: {e}", exc_info=True)


async def run_multiple_tests():
    """Run multiple test cases for the TOC agent."""
    test_topics = [
        "Python Programming for Beginners",
        "Artificial Intelligence and Machine Learning",
        "Sustainable Energy Solutions",
        "Modern Web Development",
        "Financial Independence and Investing"
    ]
    
    logger.info("Running multiple TOC agent tests...")
    logger.info(f"Total topics to test: {len(test_topics)}\n")
    
    for i, topic in enumerate(test_topics, 1):
        logger.info(f"\n{'#' * 80}")
        logger.info(f"TEST {i}/{len(test_topics)}")
        logger.info(f"{'#' * 80}\n")
        
        await test_toc_agent(topic)
        
        # Add delay between tests to avoid rate limiting
        if i < len(test_topics):
            logger.info("\nWaiting 5 seconds before next test...\n")
            await asyncio.sleep(5)


def main():
    """Main entry point for the test script."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test the TOC Agent")
    parser.add_argument(
        "--topic",
        type=str,
        help="Book topic to generate TOC for (if not specified, runs multiple tests)"
    )
    parser.add_argument(
        "--multiple",
        action="store_true",
        help="Run multiple test cases"
    )
    
    args = parser.parse_args()
    
    if args.topic:
        # Test single topic
        asyncio.run(test_toc_agent(args.topic))
    elif args.multiple:
        # Run multiple test cases
        asyncio.run(run_multiple_tests())
    else:
        # Default: single test with a sample topic
        default_topic = "Cloud Computing and DevOps Practices"
        logger.info(f"No topic specified, using default: {default_topic}")
        logger.info("Use --topic 'Your Topic' to test with a custom topic")
        logger.info("Use --multiple to run multiple test cases\n")
        asyncio.run(test_toc_agent(default_topic))


if __name__ == "__main__":
    main()
