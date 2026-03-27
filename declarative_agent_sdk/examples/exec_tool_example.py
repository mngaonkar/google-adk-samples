"""
Example: Using the exec_command builtin tool

This example demonstrates how to use the exec_command tool to execute
shell commands and processes from within agents.
"""

from declarative_agent_sdk import builtin_tools, setup_logging

# Setup logging
setup_logging(level='INFO')

def example_basic_command():
    """Execute a simple command"""
    print("\n=== Example 1: Basic Command ===")
    
    result = builtin_tools.exec_command("ls -la /tmp")
    
    if result['success']:
        print(f"✓ Command succeeded (exit code: {result['exit_code']})")
        print(f"Output:\n{result['stdout']}")
    else:
        print(f"✗ Command failed (exit code: {result['exit_code']})")
        print(f"Error: {result['error']}")
        print(f"Stderr: {result['stderr']}")


def example_with_timeout():
    """Execute command with timeout"""
    print("\n=== Example 2: Command with Timeout ===")
    
    # This will timeout if sleep duration > timeout
    result = builtin_tools.exec_command(
        "sleep 2",
        timeout=1  # 1 second timeout
    )
    
    if result['timed_out']:
        print("✓ Command timed out as expected")
        print(f"Error: {result['error']}")
    else:
        print(f"Command completed: {result['success']}")


def example_shell_features():
    """Use shell features like pipes"""
    print("\n=== Example 3: Shell Features (Pipes) ===")
    
    result = builtin_tools.exec_command(
        "ps aux | grep python | head -5",
        shell=True
    )
    
    if result['success']:
        print("✓ Shell command succeeded")
        print(f"Output:\n{result['stdout']}")


def example_working_directory():
    """Execute command in specific directory"""
    print("\n=== Example 4: Working Directory ===")
    
    # Show current directory
    result1 = builtin_tools.exec_command("pwd")
    print(f"Default directory: {result1['stdout'].strip()}")
    
    # Execute in different directory
    result2 = builtin_tools.exec_command(
        "pwd",
        cwd="/tmp"
    )
    print(f"Changed directory: {result2['stdout'].strip()}")


def example_with_input():
    """Send input to command"""
    print("\n=== Example 5: Command with Input ===")
    
    result = builtin_tools.exec_command(
        "cat",  # cat reads from stdin
        input_data="Hello from exec_command!\nThis is line 2.\n"
    )
    
    if result['success']:
        print("✓ Command succeeded")
        print(f"Output:\n{result['stdout']}")


def example_environment_variables():
    """Set environment variables for command"""
    print("\n=== Example 6: Environment Variables ===")
    
    import os
    
    # Merge custom env vars with current environment
    custom_env = os.environ.copy()
    custom_env['MY_VAR'] = 'Hello from env!'
    
    result = builtin_tools.exec_command(
        "echo $MY_VAR",
        shell=True,
        env=custom_env
    )
    
    if result['success']:
        print(f"Environment variable output: {result['stdout'].strip()}")


def example_async_process():
    """Start a background process"""
    print("\n=== Example 7: Async Process ===")
    
    result = builtin_tools.exec_async(
        "sleep 10",
        stdout_file="/tmp/async_out.log",
        stderr_file="/tmp/async_err.log"
    )
    
    if result['success']:
        print(f"✓ Process started with PID: {result['pid']}")
        print(f"Output will be written to /tmp/async_out.log")
        
        # You can check if process is still running
        import subprocess
        try:
            subprocess.run(["ps", "-p", str(result['pid'])], check=True, capture_output=True)
            print(f"Process {result['pid']} is still running")
        except subprocess.CalledProcessError:
            print(f"Process {result['pid']} has finished")


def example_error_handling():
    """Handle command errors"""
    print("\n=== Example 8: Error Handling ===")
    
    # Command not found
    result1 = builtin_tools.exec_command("nonexistent_command")
    print(f"Command not found - Error: {result1['error']}")
    
    # Command with non-zero exit
    result2 = builtin_tools.exec_command("ls /nonexistent/path")
    print(f"Exit code: {result2['exit_code']}")
    print(f"Stderr: {result2['stderr'].strip()}")


def example_python_script():
    """Execute a Python script"""
    print("\n=== Example 9: Execute Python Script ===")
    
    # Create a temporary Python script
    script = """
import sys
print("Hello from Python!")
print("Arguments:", sys.argv[1:])
for i in range(3):
    print(f"Line {i+1}")
"""
    
    # Write script to temp file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(script)
        script_path = f.name
    
    try:
        result = builtin_tools.exec_command(
            f"python {script_path} arg1 arg2",
            timeout=5
        )
        
        if result['success']:
            print("✓ Python script executed")
            print(f"Output:\n{result['stdout']}")
    finally:
        # Cleanup
        import os
        os.unlink(script_path)


def example_agent_usage():
    """Example of using exec_command in an agent"""
    print("\n=== Example 10: Agent Usage ===")
    
    from declarative_agent_sdk import ToolRegistry
    import tempfile
    
    # Register the exec tool
    ToolRegistry.register('exec_command', builtin_tools.exec_command)
    
    # Create a temporary instruction file
    instruction = """You are a system administration agent.
You can execute shell commands using the exec_command tool.
Always check command results and report errors."""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(instruction)
        instruction_file = f.name
    
    try:
        from declarative_agent_sdk import AIAgent
        
        # Create agent with exec tool
        agent = AIAgent(
            name="SystemAgent",
            instruction_file=instruction_file,
            description="Agent that can execute system commands",
            model="gemini-2.0-flash-exp",
            tools=['exec_command']
        )
        
        print(f"✓ Created agent '{agent.name}' with exec_command tool")
        print(f"Available tools: {ToolRegistry.list_available()}")
    finally:
        # Cleanup
        import os
        os.unlink(instruction_file)


if __name__ == '__main__':
    print("Exec Tool Examples\n" + "=" * 60)
    
    # Run all examples
    example_basic_command()
    example_with_timeout()
    example_shell_features()
    example_working_directory()
    example_with_input()
    example_environment_variables()
    example_async_process()
    example_error_handling()
    example_python_script()
    example_agent_usage()
    
    print("\n" + "=" * 60)
    print("All examples completed!")
