from typing import Dict, Callable
from tools.diagram import render_mermaid
from tools.fake_web import fake_web_search
from rich.console import Console

console = Console()

TOOLS: Dict[str, Callable] = {
    "fake_web_search": fake_web_search,
    "diagram_mermaid": render_mermaid
}

def execute_tool(tool: dict) -> str:
    tool_name = tool["function"]["name"]
    args = tool["function"]["arguments"]

    if tool_name not in TOOLS:
        return f"[red][ERROR] Tool '{tool_name}' not found.[/red]"

    console.print(f"[[green]+[/green]] Tool: {tool_name} has been called.\n")
    func = TOOLS[tool_name]

    try:
        result = func(**args)
        return result
    except Exception as e:
        return f"[TOOL EXECUTION ERROR] {str(e)}"