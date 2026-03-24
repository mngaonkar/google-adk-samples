#!/usr/bin/env python3
"""
Validate the package structure for declarative-agent-sdk
"""

import os
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists and report status."""
    exists = os.path.exists(filepath)
    status = "✓" if exists else "✗"
    print(f"{status} {description}: {filepath}")
    return exists

def validate_package_structure():
    """Validate that all necessary files exist for the package."""
    print("=" * 60)
    print("Validating declarative-agent-sdk Package Structure")
    print("=" * 60)
    print()
    
    workspace_root = Path(__file__).parent
    os.chdir(workspace_root)
    
    all_valid = True
    
    # Check essential packaging files
    print("Essential Packaging Files:")
    print("-" * 60)
    all_valid &= check_file_exists("pyproject.toml", "Build configuration")
    all_valid &= check_file_exists("setup.py", "Setup script")
    all_valid &= check_file_exists("SDK_README.md", "Package README")
    all_valid &= check_file_exists("LICENSE", "License file")
    all_valid &= check_file_exists("MANIFEST.in", "Manifest file")
    print()
    
    # Check SDK package files
    print("SDK Package Files:")
    print("-" * 60)
    all_valid &= check_file_exists("sdk/__init__.py", "Package init")
    all_valid &= check_file_exists("sdk/__version__.py", "Version file")
    all_valid &= check_file_exists("sdk/ai_agent.py", "AI Agent module")
    all_valid &= check_file_exists("sdk/agent_factory.py", "Agent Factory module")
    all_valid &= check_file_exists("sdk/tool_registry.py", "Tool Registry module")
    all_valid &= check_file_exists("sdk/skill_registry.py", "Skill Registry module")
    all_valid &= check_file_exists("sdk/workflow_factory.py", "Workflow Factory module")
    all_valid &= check_file_exists("sdk/workflow_registry.py", "Workflow Registry module")
    all_valid &= check_file_exists("sdk/utils.py", "Utilities module")
    all_valid &= check_file_exists("sdk/constants.py", "Constants module")
    print()
    
    # Check documentation
    print("Documentation:")
    print("-" * 60)
    check_file_exists("BUILD_AND_INSTALL.md", "Build instructions")
    check_file_exists("sdk/README.md", "SDK documentation")
    print()
    
    # Validate pyproject.toml
    print("Validating pyproject.toml:")
    print("-" * 60)
    try:
        import tomli
    except ImportError:
        try:
            import tomllib as tomli
        except ImportError:
            print("⚠ Cannot validate TOML (tomli/tomllib not available)")
            print()
        else:
            validate_toml(tomli)
    else:
        validate_toml(tomli)
    
    # Final status
    print("=" * 60)
    if all_valid:
        print("✓ All essential files present!")
        print()
        print("Next steps:")
        print("1. Install build tools: pip install build twine")
        print("2. Build package: python -m build")
        print("3. Install locally: pip install -e .")
        print("4. Or install from wheel: pip install dist/*.whl")
    else:
        print("✗ Some essential files are missing!")
        print("Please create the missing files before building.")
    print("=" * 60)

def validate_toml(tomli):
    """Validate the pyproject.toml file."""
    try:
        with open("pyproject.toml", "rb") as f:
            config = tomli.load(f)
        
        project = config.get("project", {})
        print(f"✓ Package name: {project.get('name', 'N/A')}")
        print(f"✓ Version: {project.get('version', 'N/A')}")
        print(f"✓ Python requires: {project.get('requires-python', 'N/A')}")
        
        deps = project.get("dependencies", [])
        print(f"✓ Dependencies: {len(deps)} packages")
        for dep in deps:
            print(f"  - {dep}")
        print()
    except Exception as e:
        print(f"⚠ Could not validate pyproject.toml: {e}")
        print()

if __name__ == "__main__":
    validate_package_structure()
