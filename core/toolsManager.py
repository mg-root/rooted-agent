from typing import Dict, Callable
from tools.diagram import render_mermaid
from rich.console import Console
from tools.edit_file import edit_file
from tools.make_file import make_file

console = Console()

TOOLS: Dict[str, Callable] = {
    "edit_file": edit_file,
    "make_file": make_file,
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