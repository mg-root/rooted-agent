import requests
import json
from core.system import PATHS, load_json

def _ollama_generate_without_tools(messages: list):
    config = load_json(PATHS["DEFAULT"])

    url = "http://localhost:11434/api/chat"
    payload = {
        "model": config["model"],
        "messages": messages,
        "options": {"temperature": config["temperature"]},
        "stream": True
    }

    response = requests.post(url, json=payload, stream=True)
    response.raise_for_status()

    for line in response.iter_lines():
        if not line:
            continue
        data = json.loads(line.decode("utf-8"))
        yield data.get("message", {}).get("content", "")

def _ollama_generate_include_tools(messages: list):
    config = load_json(PATHS["DEFAULT"])
    tools_api = load_json(PATHS["TOOLS_API"])

    url = "http://localhost:11434/api/chat"
    payload = {
        "model": config["model"],
        "messages": messages,
        "options": {"temperature": config["temperature"]},
        "tools": tools_api,
        "stream": False
    }

    response = requests.post(url, json=payload, stream=False)
    response.raise_for_status()

    data = response.json()

    msg = data.get("message", {})

    if "tool_calls" in msg:
        return msg
    else:
        return msg.get("content", "")
    
def _ollama_generate(messages: list):
    config = load_json(PATHS["DEFAULT"])

    url = "http://localhost:11434/api/chat"
    payload = {
        "model": config["model"],
        "messages": messages,
        "options": {"temperature": config["temperature"]},
        "stream": False
    }

    response = requests.post(url, json=payload, stream=False)
    response.raise_for_status()

    data = response.json()
    content = data.get("message", {}).get("content", "")

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return content

def ollama_generate(messages: list, include_tools: bool = False, force_no_stream: bool = False):
    if force_no_stream:
        return _ollama_generate(messages)

    if include_tools:
        return _ollama_generate_include_tools(messages)
    else:
        return _ollama_generate_without_tools(messages)
