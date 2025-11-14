import requests
import json
from core.system import PATHS, load_json

def _ollama_generate_stream(messages):
    config = load_json(PATHS["DEFAULT"])

    url = "http://localhost:11434/api/chat"
    payload = {
        "model": config["model"],
        "prompt": messages,
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

def _ollama_generate_nostream(messages):
    url = "http://localhost:11434/api/chat"
    payload = {
        "model": "llama3.1",
        "messages": messages,
        "options": {"temperature": 0.2},
        "stream": False
    }

    response = requests.post(url, json=payload)
    response.raise_for_status()

    data = response.json()
    return data.get("message", {}).get("content", "")

def ollama_generate(messages, stream=True):
    if stream:
        return _ollama_generate_stream(messages)
    else:
        return _ollama_generate_nostream(messages)
