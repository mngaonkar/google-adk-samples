"""
Execute Tool - Execute shell commands and processes

This tool allows agents to execute system commands and processes.
Use with caution as it provides shell access.
"""

import subprocess
import shlex
from typing import Dict, Optional, List, Union
from declarative_agent_sdk.agent_logging import get_logger

logger = get_logger(__name__)


def exec_command(
    command: str,
    shell: bool = False,
    timeout: Optional[int] = 30,
    cwd: Optional[str] = None,
    env: Optional[Dict[str, str]] = None,
    capture_output: bool = True,
    input_data: Optional[str] = None,
    encoding: str = 'utf-8'
) -> Dict[str, Union[str, int, bool]]:
    """
    Execute a shell command or process.
    
    Args:
        command: Command to execute. If shell=False, can be a string or list of arguments.
                If shell=True, should be a complete shell command string.
        shell: If True, execute command through the shell (enables pipes, redirection, etc.)
               If False (default), execute directly (safer, no shell injection risk)
        timeout: Maximum time in seconds to wait for command to complete (default: 30)
                Set to None for no timeout
        cwd: Working directory for the command (default: current directory)
        env: Environment variables dict to set for the command (default: inherit parent env)
        capture_output: If True, capture stdout and stderr (default: True)
        input_data: Optional string to send to command's stdin
        encoding: Character encoding for input/output (default: utf-8)
        
    Returns:
        Dictionary containing:
            - success: bool - Whether command completed successfully (exit code 0)
            - exit_code: int - Process exit code
            - stdout: str - Standard output (if capture_output=True)
            - stderr: str - Standard error (if capture_output=True)
            - timed_out: bool - Whether command exceeded timeout
            - error: str - Error message if execution failed
            
    Example:
        # Simple command (safe, no shell)
        result = exec_command("ls -la /tmp")
        print(result['stdout'])
        
        # With shell features (pipes, redirection)
        result = exec_command("ps aux | grep python", shell=True)
        
        # With timeout and working directory
        result = exec_command(
            "npm install",
            timeout=300,
            cwd="/path/to/project"
        )
        
        # With input data
        result = exec_command(
            "python script.py",
            input_data="hello\\nworld\\n"
        )
        
    Security Note:
        When shell=False (default), command arguments are safely parsed and shell
        injection is prevented. When shell=True, be very careful with untrusted input
        as it can lead to command injection vulnerabilities.
    """
    result = {
        'success': False,
        'exit_code': None,
        'stdout': '',
        'stderr': '',
        'timed_out': False,
        'error': None
    }
    
    try:
        # Parse command if not using shell
        if not shell:
            if isinstance(command, str):
                # Safely parse command string into arguments
                cmd_args = shlex.split(command)
            elif isinstance(command, list):
                cmd_args = command
            else:
                raise ValueError(f"command must be str or list, got {type(command)}")
        else:
            # Shell mode: command is a string
            cmd_args = command
        
        logger.debug(f"Executing command: {command} (shell={shell}, timeout={timeout}, cwd={cwd})")
        
        # Prepare subprocess arguments
        subprocess_kwargs = {
            'shell': shell,
            'timeout': timeout,
            'cwd': cwd,
            'env': env,
        }
        
        # Add capture settings
        if capture_output:
            subprocess_kwargs['stdout'] = subprocess.PIPE
            subprocess_kwargs['stderr'] = subprocess.PIPE
            subprocess_kwargs['text'] = True
            subprocess_kwargs['encoding'] = encoding
        
        # Add input if provided
        if input_data is not None:
            subprocess_kwargs['input'] = input_data
        
        # Execute the command
        proc = subprocess.run(cmd_args, **subprocess_kwargs)
        
        # Populate result
        result['exit_code'] = proc.returncode
        result['success'] = (proc.returncode == 0)
        
        if capture_output:
            result['stdout'] = proc.stdout or ''
            result['stderr'] = proc.stderr or ''
        
        if result['success']:
            logger.info(f"Command executed successfully: {command}")
        else:
            logger.warning(f"Command exited with code {proc.returncode}: {command}")
            
    except subprocess.TimeoutExpired as e:
        result['timed_out'] = True
        result['error'] = f"Command timed out after {timeout} seconds"
        
        # Capture any partial output
        if capture_output:
            result['stdout'] = e.stdout.decode(encoding) if e.stdout else ''
            result['stderr'] = e.stderr.decode(encoding) if e.stderr else ''
        
        logger.error(f"Command timed out: {command}")
        
    except FileNotFoundError as e:
        result['error'] = f"Command not found: {e.filename}"
        logger.error(f"Command not found: {command} - {e}")
        
    except PermissionError as e:
        result['error'] = f"Permission denied: {e}"
        logger.error(f"Permission denied executing: {command} - {e}")
        
    except Exception as e:
        result['error'] = f"Execution error: {str(e)}"
        logger.error(f"Error executing command: {command} - {e}", exc_info=True)
    
    return result


def exec_async(
    command: str,
    shell: bool = False,
    cwd: Optional[str] = None,
    env: Optional[Dict[str, str]] = None,
    stdout_file: Optional[str] = None,
    stderr_file: Optional[str] = None
) -> Dict[str, Union[int, str]]:
    """
    Execute a command asynchronously (non-blocking).
    
    This starts a process and returns immediately without waiting for completion.
    Useful for long-running processes like servers or daemons.
    
    Args:
        command: Command to execute
        shell: If True, execute through shell
        cwd: Working directory
        env: Environment variables
        stdout_file: Optional file path to redirect stdout
        stderr_file: Optional file path to redirect stderr
        
    Returns:
        Dictionary containing:
            - pid: int - Process ID of started process
            - success: bool - Whether process started successfully
            - error: str - Error message if failed to start
            
    Example:
        # Start a web server
        result = exec_async("python -m http.server 8000")
        print(f"Server started with PID: {result['pid']}")
        
        # Start with output redirection
        result = exec_async(
            "npm run dev",
            stdout_file="server.log",
            stderr_file="server.error.log"
        )
    """
    result = {
        'success': False,
        'pid': None,
        'error': None
    }
    
    try:
        # Parse command if not using shell
        if not shell:
            if isinstance(command, str):
                cmd_args = shlex.split(command)
            else:
                cmd_args = command
        else:
            cmd_args = command
        
        # Prepare subprocess arguments
        subprocess_kwargs = {
            'shell': shell,
            'cwd': cwd,
            'env': env,
        }
        
        # Set up file redirects if specified
        if stdout_file:
            subprocess_kwargs['stdout'] = open(stdout_file, 'w')
        else:
            subprocess_kwargs['stdout'] = subprocess.DEVNULL
            
        if stderr_file:
            subprocess_kwargs['stderr'] = open(stderr_file, 'w')
        else:
            subprocess_kwargs['stderr'] = subprocess.DEVNULL
        
        # Start process asynchronously
        proc = subprocess.Popen(cmd_args, **subprocess_kwargs)
        
        result['success'] = True
        result['pid'] = proc.pid
        
        logger.info(f"Started async process (PID {proc.pid}): {command}")
        
    except Exception as e:
        result['error'] = f"Failed to start process: {str(e)}"
        logger.error(f"Error starting async process: {command} - {e}", exc_info=True)
    
    return result
