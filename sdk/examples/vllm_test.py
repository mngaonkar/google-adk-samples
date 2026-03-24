import os
from litellm import completion
from google.genai.types import Content, Part
from google.adk.models.lite_llm import LiteLlm
from google.adk.models.llm_request import LlmRequest
import asyncio

# Set API key for local vLLM server (can be any value for local servers)
os.environ["OPENAI_API_KEY"] = "sk-dummy-key"

def test_vllm_model():
    response = completion(
        model="openai/Qwen/Qwen3-4B-Thinking-2507-FP8",           # Format: openai/<your-served-model-name>
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user",   "content": "Explain how vLLM works in simple terms."}
        ],
        api_base="http://10.0.0.147:8000/v1",   # ← Point to your vLLM server
        temperature=0.7,
        # max_tokens=2048,
    )

    print(response.choices[0].message.content)

async def test_lite_llm_model():
    model = LiteLlm(
        model="openai/Qwen/Qwen3-4B-Thinking-2507-FP8",  # Format: openai/<your-served-model-name>
        api_base="http://10.0.0.147:8000/v1",   # ← Point to your vLLM server
        temperature=0.7,
        # max_tokens=2048,
    )

    # generate_content_async returns an async generator for streaming
    response_generator = model.generate_content_async(
        llm_request=LlmRequest(
            contents=[
                Content(
                    role="system",
                    parts=[Part(text="You are a helpful assistant.")]
                ),
                Content(
                    role="user",
                    parts=[Part(text="Explain how vLLM works in simple terms.")]
                )
            ]
        )
    )

    # Iterate through the async generator to get the response
    final_response = None
    async for response in response_generator:
        final_response = response
    
    # Print the final response - LlmResponse uses LiteLLM format
    if final_response:        
        # Try to extract text from the response
        if hasattr(final_response, 'text'):
            print(final_response.text)
        elif hasattr(final_response, 'choices'):
            print(final_response.choices[0].message.content)
        else:
            print(final_response.content.parts[0].text)
    else:
        print("No response generated")

def main():
    # print("Testing vLLM model with direct completion call:")
    # test_vllm_model()
    
    print("\nTesting vLLM model with LiteLlm wrapper:")
    asyncio.run(test_lite_llm_model())

if __name__ == "__main__":
    main()