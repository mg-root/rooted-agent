from typing import Dict, Callable
from tools.diagram import render_mermaid

def fake_web_search(query: str) -> str:
    return f"[FAKE SEARCH RESULT]\nRésultat fictif pour la recherche : **{query}**\n"

TOOLS: Dict[str, Callable] = {
    "fake_web_search": fake_web_search,
    "diagram_mermaid": render_mermaid
}

def execute_tool(tool: dict) -> str:
    tool_name = tool["function"]["name"]
    args = tool["function"]["arguments"]

    if tool_name not in TOOLS:
        return f"[red][ERROR] Tool '{tool_name}' not found.[/red]"

    func = TOOLS[tool_name]

    try:
        result = func(**args)
        return result
    except Exception as e:
        return f"[TOOL EXECUTION ERROR] {str(e)}"