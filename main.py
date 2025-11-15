import typer
import os
from rich.console import Console
from rich.live import Live
from rich.prompt import Prompt
from rich.markdown import Markdown
from core.llm import ollama_generate
from core.system import PATHS, load_json, save_chat
from core.chatBuilder import build_chat
from core.toolsManager import execute_tool

import requests
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

app = typer.Typer(help="Agent IA - Rooted ready to support you.")
console = Console()
config = load_json(PATHS["DEFAULT"])

OLLAMA_API = "http://localhost:11434/api"
MODEL_NAME = config["model"]

def is_model_loaded(model_name: str) -> bool:
    try:
        resp = requests.get(f"{OLLAMA_API}/ps")
        resp.raise_for_status()
        loaded = [m["name"] for m in resp.json().get("models", [])]
        return model_name in loaded
    except Exception:
        return False

def load_model_with_progress(model_name: str):
    console.print(f"[magenta]Chargement du modèle {model_name}...[/magenta]")

@app.command()
def chat(include_tools: bool = True):
    """
    Start a new chat with Agent Rooted.
    """

    console.print("[bold magenta]Rooted is ready to help you ![/bold magenta]\n")
    
    history = []
    tmp = []

    while True:
        prompt = config['promptDisplayed']

        if len(tmp) > 0:
            prompt = f"[Files: [green]{" [/green]/[green] ".join([str(file[0]) for file in tmp])}[/green]]" + prompt

        user_input = Prompt.ask(prompt)
        if user_input.lower() == "#exit":
            console.print("[red]End of chat.[/red]")
            break
        elif user_input.lower().startswith("#load "):
            path = user_input.replace("#load ", "").strip()
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as file:
                    content = file.read()
                console.print(f"[[green]File loaded[/green]] {path.split("/")[-1]}\n")
                tmp.append([path.split("/")[-1], content])
            else:
                console.print(f"[[red]File undefined[/red]] {path.split("/")[-1]}\n")
            continue
        elif user_input.lower() == "#history":
            console.print(history)
            continue
        elif user_input.lower().startswith('#save '):
            name = user_input.replace("#save ", "").strip()
            success = save_chat(name, history)
            if success:
                console.print(f"[[green]Chat saved[/green]] {os.path.join(PATHS["LOGS"], name)}\n")
            else:
                console.print(f"[[red]Error save[/red]]\n")
            continue

        if not user_input:
            continue

        if not is_model_loaded(MODEL_NAME):
            load_model_with_progress(MODEL_NAME)

        history.append({
            "role": "user",
            "content": user_input
        })

        if include_tools:
            try:
                response = ollama_generate(build_chat(history), include_tools)
                if isinstance(response, dict):                  
                    for tool in response["tool_calls"]:
                        tool_name = tool["function"]["name"]
                        tool_call_id = tool["id"]
                        tool_output = execute_tool(tool)

                        history.append({
                            "role": "tool",
                            "rool_call_id": tool_call_id,
                            "content": tool_output
                        })

                        console.print(f"[[green]+[/green]] Tool: {tool_name} has been called.\n")

                    final_response = ollama_generate(build_chat(history), include_tools)

                    history.append({
                        "role": "assistant",
                        "content": final_response
                    })

                    console.print(Markdown(final_response))
                else:
                    history.append({
                        "role": 'assistant',
                        "content": response
                    })

                    tmp = []

                    console.print(Markdown(response))
            except Exception as e:
                console.print(f"\n[red]Error 111:[/red] {e}")
        else:
            try:
                response = ""
                with Live(console=console, refresh_per_second=20) as live:
                    for token in ollama_generate(build_chat(history), include_tools):
                        response += token
                        live.update(Markdown(response))
                
                history.append({
                    "role": 'assistant',
                    "content": response
                })

                tmp = []
            except Exception as e:
                console.print(f"\n[red]Error:[/red] {e}")

if __name__ == "__main__":
    app()
