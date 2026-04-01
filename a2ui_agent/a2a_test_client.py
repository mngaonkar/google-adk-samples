import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_agent_card():
    url = "http://localhost:8000/.well-known/agent-card.json"
    response = requests.get(url)
    if response.status_code == 200:
        agent_card = response.json()
        logger.info(f"Agent Card: {agent_card}")
    else:
        logger.error(f"Failed to fetch agent card. Status code: {response.status_code}")

def invoke_agent(query):
    url = "http://localhost:8000/"
    payload = {
        "jsonrpc": "2.0",
        "id": "req-001",
        "method": "message/send",
        "params": {
            "message": {
            "role": "user",
            "parts": [
                {
                "kind": "text",
                "text": query
                }
            ],
            "messageId": "12345678-1234-1234-1234-123456789012"
            }
        }
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        result = response.json()
        logger.info(f"Agent Response: {result}")
    else:
        logger.error(f"Failed to invoke agent. Status code: {response.status_code}")

invoke_agent("steve wozniak")
