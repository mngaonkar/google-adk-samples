"""
Example usage of ModelFactory for creating model objects.

This demonstrates how to use ModelFactory to create model objects
for different LLM providers (Google Gemini, vLLM, etc.).
"""

from declarative_agent_sdk import ModelFactory

def example_google_gemini():
    """Example: Create a Google Gemini model (default provider)."""
    print("=" * 60)
    print("Example 1: Google Gemini Model (Default)")
    print("=" * 60)
    
    # Simple model name - returns the name as-is for Google
    model = ModelFactory.create_model("gemini-2.0-flash-exp")
    print(f"Model: {model}")
    print(f"Type: {type(model)}\n")
    
    # Explicitly specify Google provider
    model2 = ModelFactory.create_model(
        model_name="gemini-1.5-pro",
        provider="google"
    )
    print(f"Model 2: {model2}")
    print(f"Type: {type(model2)}\n")


def example_vllm_local():
    """Example: Create a vLLM model with local endpoint."""
    print("=" * 60)
    print("Example 2: vLLM Model with Local Endpoint")
    print("=" * 60)
    
    try:
        model = ModelFactory.create_model(
            model_name="Qwen/Qwen3-4B-Thinking-2507-FP8",
            provider="vllm",
            endpoint_url="http://localhost:8000/v1"
        )
        print(f"Model: {model}")
        print(f"Type: {type(model)}\n")
        
        # Test calling the model
        print("Testing model call...")
        # Uncomment if you have a running vLLM server:
        # response = model(messages=[
        #     {"role": "user", "content": "Hello, what is 2+2?"}
        # ])
        # print(f"Response: {response.choices[0].message.content}")
        
    except ImportError as e:
        print(f"Error: {e}")
        print("Install litellm with: pip install litellm\n")


def example_with_custom_config():
    """Example: Create vLLM model with custom configuration."""
    print("=" * 60)
    print("Example 3: vLLM Model with Custom Configuration")
    print("=" * 60)
    
    try:
        model = ModelFactory.create_model(
            model_name="Qwen/Qwen3-4B",
            provider="vllm",
            endpoint_url="http://10.0.0.147:8000/v1",
            temperature=0.8,
            max_tokens=2048
        )
        print(f"Model: {model}")
        print(f"Type: {type(model)}")
        print("Note: Custom config (temperature=0.8, max_tokens=2048) passed to LiteLLM\n")
        
    except ImportError as e:
        print(f"Error: {e}\n")


def example_error_handling():
    """Example: Error handling for invalid configurations."""
    print("=" * 60)
    print("Example 4: Error Handling")
    print("=" * 60)
    
    # Missing endpoint_url for vLLM
    try:
        model = ModelFactory.create_model(
            model_name="Qwen/Qwen3-4B",
            provider="vllm"
            # Missing endpoint_url!
        )
    except ValueError as e:
        print(f"Expected error: {e}\n")
    
    # Unsupported provider
    try:
        model = ModelFactory.create_model(
            model_name="some-model",
            provider="unsupported_provider"
        )
    except ValueError as e:
        print(f"Expected error: {e}\n")


def example_usage_in_agent():
    """Example: How ModelFactory is used with AgentFactory."""
    print("=" * 60)
    print("Example 5: Usage with AgentFactory (Conceptual)")
    print("=" * 60)
    
    # This is how AgentFactory uses ModelFactory internally
    config = {
        'name': 'my_agent',
        'instruction_file': 'instructions.md',
        'model': 'Qwen/Qwen3-4B',
        'provider': 'vllm',
        'endpoint': {
            'url': 'http://localhost:8000/v1'
        }
    }
    
    # AgentFactory extracts these fields and calls:
    model_name = config.get('model', 'gemini-2.0-flash-exp')  # Provide default
    provider = config.get('provider')
    endpoint_url = config.get('endpoint', {}).get('url')
    
    print(f"Config: {config}")
    print(f"\nModelFactory would be called with:")
    print(f"  model_name: {model_name}")
    print(f"  provider: {provider}")
    print(f"  endpoint_url: {endpoint_url}")
    
    try:
        model = ModelFactory.create_model(
            model_name=model_name,
            provider=provider,
            endpoint_url=endpoint_url
        )
        print(f"\nCreated model: {model}")
        print(f"Type: {type(model)}\n")
    except ImportError:
        print(f"\nNote: litellm not installed, but would create LiteLLM model\n")


if __name__ == "__main__":
    # Run all examples
    example_google_gemini()
    example_vllm_local()
    example_with_custom_config()
    example_error_handling()
    example_usage_in_agent()
    
    print("=" * 60)
    print("All examples completed!")
    print("=" * 60)
