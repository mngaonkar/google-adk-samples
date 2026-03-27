"""
Example: Using AgentRegistry to manage agent instances

This example demonstrates how to use AgentRegistry to track and manage
agents created by AgentFactory or manually.
"""

from declarative_agent_sdk import (
    AgentFactory, 
    AgentRegistry, 
    AIAgent,
    setup_logging
)
import tempfile
import os

# Setup logging
setup_logging(level='INFO')


def example_basic_registration():
    """Register and retrieve an agent"""
    print("\n=== Example 1: Basic Registration ===")
    
    # Create a temporary instruction file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("You are a helpful assistant.")
        instruction_file = f.name
    
    try:
        # Create agent manually
        agent = AIAgent(
            name="helper_agent",
            instruction_file=instruction_file,
            description="A general purpose helper agent",
            model="gemini-2.0-flash-exp"
        )
        
        # Register agent
        AgentRegistry.register(agent, category='assistant')
        print(f"✓ Registered agent: {agent.name}")
        
        # Retrieve agent later
        retrieved = AgentRegistry.get('helper_agent')
        print(f"✓ Retrieved agent: {retrieved.name}")
        
        # Check if registered
        if AgentRegistry.is_registered('helper_agent'):
            print("✓ Agent is registered")
    finally:
        os.unlink(instruction_file)


def example_register_from_yaml():
    """Register agents from YAML files"""
    print("\n=== Example 2: Register from YAML ===")
    
    # Create temporary YAML config
    yaml_content = """
name: toc_agent
description: Generate table of contents
instruction_file: /tmp/toc_instructions.md
model: gemini-2.0-flash-exp
    """
    
    # Create instruction file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("Generate a table of contents for the given book content.")
        instruction_file = f.name
    
    # Update YAML with actual instruction file path
    yaml_content = yaml_content.replace('/tmp/toc_instructions.md', instruction_file)
    
    # Create YAML file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(yaml_content)
        yaml_file = f.name
    
    try:
        # Create agent from YAML
        agent = AgentFactory.from_yaml_file(yaml_file)
        
        # Register it
        AgentRegistry.register(
            agent,
            category='workflow',
            purpose='Book ToC generation'
        )
        print(f"✓ Registered agent from YAML: {agent.name}")
        
        # Get metadata
        metadata = AgentRegistry.get_metadata('toc_agent')
        print(f"Metadata: {metadata}")
    finally:
        os.unlink(yaml_file)
        os.unlink(instruction_file)


def example_list_agents():
    """List and categorize agents"""
    print("\n=== Example 3: List Agents ===")
    
    # Create and register multiple agents
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("Instructions")
        instruction_file = f.name
    
    try:
        agents = [
            ('agent1', 'workflow'),
            ('agent2', 'workflow'),
            ('agent3', 'tool'),
        ]
        
        for name, category in agents:
            agent = AIAgent(
                name=name,
                instruction_file=instruction_file,
                model="gemini-2.0-flash-exp"
            )
            AgentRegistry.register(agent, category=category)
        
        # List all agents
        all_agents = AgentRegistry.list_available()
        print(f"All agents: {all_agents}")
        
        # List by category
        workflow_agents = AgentRegistry.list_available(category='workflow')
        print(f"Workflow agents: {workflow_agents}")
        
        # Group by category
        by_category = AgentRegistry.list_by_category()
        print(f"By category: {by_category}")
        
        # Get registry info
        info = AgentRegistry.info()
        print(f"Registry info: {info}")
    finally:
        os.unlink(instruction_file)
        AgentRegistry.clear()


def example_register_multiple():
    """Register multiple agents at once"""
    print("\n=== Example 4: Register Multiple ===")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("Instructions")
        instruction_file = f.name
    
    try:
        # Create multiple agents
        agents = []
        for i in range(3):
            agent = AIAgent(
                name=f"agent_{i}",
                instruction_file=instruction_file,
                model="gemini-2.0-flash-exp"
            )
            agents.append(agent)
        
        # Register all at once
        count = AgentRegistry.register_multiple(agents, category='batch')
        print(f"✓ Registered {count} agents")
        
        # Verify
        print(f"Total agents: {len(AgentRegistry.list_available())}")
    finally:
        os.unlink(instruction_file)
        AgentRegistry.clear()


def example_register_from_yaml_files():
    """Register multiple agents from YAML files"""
    print("\n=== Example 5: Register from YAML Files ===")
    
    # Create temporary YAML files
    yaml_files = []
    instruction_files = []
    
    try:
        for i in range(3):
            # Create instruction file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                f.write(f"Instructions for agent {i}")
                instruction_file = f.name
                instruction_files.append(instruction_file)
            
            # Create YAML file
            yaml_content = f"""
name: yaml_agent_{i}
description: Agent {i} from YAML
instruction_file: {instruction_file}
model: gemini-2.0-flash-exp
            """
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                f.write(yaml_content)
                yaml_files.append(f.name)
        
        # Register all from YAML files
        count = AgentRegistry.register_from_yaml_files(
            yaml_files,
            category='yaml_batch'
        )
        print(f"✓ Registered {count} agents from YAML files")
        
        # List all
        agents = AgentRegistry.list_available()
        print(f"Registered agents: {agents}")
    finally:
        # Cleanup
        for f in yaml_files + instruction_files:
            if os.path.exists(f):
                os.unlink(f)
        AgentRegistry.clear()


def example_unregister():
    """Unregister agents"""
    print("\n=== Example 6: Unregister Agents ===")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("Instructions")
        instruction_file = f.name
    
    try:
        # Register agent
        agent = AIAgent(
            name="temp_agent",
            instruction_file=instruction_file,
            model="gemini-2.0-flash-exp"
        )
        AgentRegistry.register(agent)
        print(f"Registered: {AgentRegistry.list_available()}")
        
        # Unregister
        AgentRegistry.unregister('temp_agent')
        print(f"After unregister: {AgentRegistry.list_available()}")
        
        # Clear all
        agent2 = AIAgent(
            name="agent2",
            instruction_file=instruction_file,
            model="gemini-2.0-flash-exp"
        )
        AgentRegistry.register(agent2)
        print(f"After adding agent2: {AgentRegistry.list_available()}")
        
        AgentRegistry.clear()
        print(f"After clear: {AgentRegistry.list_available()}")
    finally:
        os.unlink(instruction_file)


def example_get_all_agents():
    """Get all agent instances"""
    print("\n=== Example 7: Get All Agents ===")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("Instructions")
        instruction_file = f.name
    
    try:
        # Register multiple agents
        for i in range(3):
            agent = AIAgent(
                name=f"agent_{i}",
                instruction_file=instruction_file,
                model="gemini-2.0-flash-exp"
            )
            AgentRegistry.register(agent, category=f"cat_{i % 2}")
        
        # Get all agent instances
        all_agents = AgentRegistry.get_all()
        print(f"Total agents: {len(all_agents)}")
        
        # Iterate and use agents
        for name, agent in all_agents.items():
            print(f"  - {name}: {agent.description}")
    finally:
        os.unlink(instruction_file)
        AgentRegistry.clear()


def example_with_metadata():
    """Register agents with custom metadata"""
    print("\n=== Example 8: Custom Metadata ===")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("Instructions")
        instruction_file = f.name
    
    try:
        agent = AIAgent(
            name="metadata_agent",
            instruction_file=instruction_file,
            model="gemini-2.0-flash-exp"
        )
        
        # Register with custom metadata
        AgentRegistry.register(
            agent,
            category='custom',
            purpose='Demonstrate metadata',
            version='1.0.0',
            tags=['demo', 'example'],
            owner='team_a'
        )
        
        # Retrieve metadata
        metadata = AgentRegistry.get_metadata('metadata_agent')
        print(f"Custom metadata: {metadata}")
    finally:
        os.unlink(instruction_file)
        AgentRegistry.clear()


if __name__ == '__main__':
    print("AgentRegistry Examples\n" + "=" * 60)
    
    # Run all examples
    example_basic_registration()
    example_register_from_yaml()
    example_list_agents()
    example_register_multiple()
    example_register_from_yaml_files()
    example_unregister()
    example_get_all_agents()
    example_with_metadata()
    
    print("\n" + "=" * 60)
    print("All examples completed!")
