"""
Example: Using SDK Logging Configuration

This example demonstrates how to use the centralized logging configuration
in the declarative-agent-sdk.
"""

from declarative_agent_sdk import setup_logging, get_logger, set_log_level, SkillRegistry
import logging


def example_basic_logging():
    """Example 1: Basic logging with defaults"""
    print("\n=== Example 1: Basic Logging ===")
    
    # Logging is auto-configured, but you can customize it
    setup_logging(level='INFO')
    
    logger = get_logger(__name__)
    logger.info("This is an info message")
    logger.debug("This debug message won't show (level is INFO)")
    logger.warning("This is a warning")
    logger.error("This is an error")


def example_debug_mode():
    """Example 2: Enable debug mode"""
    print("\n=== Example 2: Debug Mode ===")
    
    # Switch to debug level
    setup_logging(level='DEBUG', force=True)
    
    logger = get_logger(__name__)
    logger.debug("Now debug messages are visible!")
    logger.info("Info still works")


def example_with_file():
    """Example 3: Log to file"""
    print("\n=== Example 3: File Logging ===")
    
    # Configure with file output
    setup_logging(
        level='INFO',
        log_file='example_sdk.log',
        force=True
    )
    
    logger = get_logger(__name__)
    logger.info("This message goes to console AND file")
    print("Check example_sdk.log for the log file output")


def example_environment_vars():
    """Example 4: Using environment variables"""
    print("\n=== Example 4: Environment Variables ===")
    
    import os
    
    # Set environment variable
    os.environ['SDK_LOG_LEVEL'] = 'WARNING'
    
    # Configure will pick up the environment variable
    setup_logging(force=True)
    
    logger = get_logger(__name__)
    logger.info("This won't show (below WARNING level)")
    logger.warning("This warning will show")
    logger.error("This error will show")


def example_runtime_level_change():
    """Example 5: Change log level at runtime"""
    print("\n=== Example 5: Runtime Level Change ===")
    
    setup_logging(level='INFO', force=True)
    logger = get_logger(__name__)
    
    logger.info("Starting with INFO level")
    logger.debug("This won't show")
    
    # Change to DEBUG
    set_log_level('DEBUG')
    logger.debug("Now debug messages show after level change!")


def example_with_sdk_components():
    """Example 6: SDK components use the same logging"""
    print("\n=== Example 6: SDK Components ===")
    
    setup_logging(level='INFO', force=True)
    
    # All SDK components now use centralized logging
    # This will log using the configured setup
    SkillRegistry.register(
        'example_skill',
        directory='./skills/example',
        description='Example skill',
        category='test'
    )
    
    logger = get_logger(__name__)
    logger.info(f"Registered skills: {SkillRegistry.list_available()}")


def example_custom_format():
    """Example 7: Custom log format"""
    print("\n=== Example 7: Custom Format ===")
    
    setup_logging(
        level='INFO',
        format_string='[%(levelname)s] %(name)s: %(message)s',
        force=True
    )
    
    logger = get_logger(__name__)
    logger.info("This uses a simpler format")
    logger.warning("Without timestamps")


def main():
    """Run all examples"""
    print("=" * 60)
    print("SDK Logging Configuration Examples")
    print("=" * 60)
    
    example_basic_logging()
    example_debug_mode()
    example_with_file()
    example_environment_vars()
    example_runtime_level_change()
    example_with_sdk_components()
    example_custom_format()
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
