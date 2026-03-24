import os
from litellm import completion

# Set API key for local vLLM server (can be any value for local servers)
os.environ["OPENAI_API_KEY"] = "sk-dummy-key"

response = completion(
    model="openai/Qwen/Qwen3-4B-Thinking-2507-FP8",           # Format: openai/<your-served-model-name>
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user",   "content": "Explain how vLLM works in simple terms."}
    ],
    api_base="http://10.0.0.147:8000/v1",   # ← Point to your vLLM server
    temperature=0.7,
    max_tokens=1024,
)

print(response.choices[0].message.content)