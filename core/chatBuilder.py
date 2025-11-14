import json
from core.system import PATHS, load_json
from core.memoryManager import convert_memory

def build_chat(history: list = None) -> list:
    history = history or []

    system_messages = load_json(PATHS["SYSTEM_MESSAGES"])
    specialization = load_json(PATHS["SPECIALIZATION/CODE_EXPERT"])
    developer_instructions = load_json(PATHS["DEVELOPER_INSTRUCTIONS"])
    memory = convert_memory(load_json(PATHS["MEMORY"]))
    tools = load_json(PATHS["TOOLS_API"])

    messages = [
        { "role": "system", "content": "[INFORMATION]\n" + system_messages["default"] + "\n\n" + specialization["prompt"] },
        { "role": "system", "content": "[DEVELOPER INSTRUCTIONS]\n" + developer_instructions["default"] },
        { "role": "system", "content": "[MEMORY]\n" + memory },
        { "role": "system", "content": "[TOOLS API]\n" + json.dumps(tools, indent=2, ensure_ascii=False) }
    ]

    return messages + history