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
from core.notifications import indicate

import requests
from rich.console import Console

from core.filesManager import select_workspace, select_files

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
def chat(include_tools: bool = False):
    """
    Start a new chat with Agent Rooted.
    """

    os.system('clear')
    indicate("Rooted is ready to help you !")
    
    history = []
    tmp = []

    while True:
        prompt = config['promptDisplayed']

        if len(tmp) > 0:
            prompt = f"[Files: [green]{" [/green]/[green] ".join([str(file[0]) for file in tmp])}[/green]]" + prompt

        user_input = Prompt.ask(prompt)
        if user_input.lower() == f"{config["prefix"]}exit":
            console.print("[red]End of chat.[/red]")
            break
        elif user_input.lower() == f"{config["prefix"]}load":
            workspace = select_workspace()
            files = select_files(workspace, multiple=True)
            for file in files:
                with open(file, "r", encoding="utf-8") as f:
                    content = f.read()
                file_name = os.path.basename(file)
                console.print(f"[[green]File loaded[/green]] {file_name}\n")
                tmp.append([file_name, content])
            continue
        elif user_input.lower() == f"{config["prefix"]}history":
            console.print(history)
            continue
        elif user_input.lower().startswith(f'{config["prefix"]}save '):
            name = user_input.replace(f"{config["prefix"]}save ", "").strip()
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

        for file in tmp:
            history.append({
                "role": "system",
                "content": f"[File loaded: {file[0]}]\n{file[1]}"
            })

        history.append({
            "role": "user",
            "content": user_input
        })

        if include_tools:
            try:
                response = ollama_generate(build_chat(history), include_tools)
                if isinstance(response, dict):                  
                    for tool in response["tool_calls"]:
                        tool_call_id = tool["id"]
                        tool_output = execute_tool(tool)

                        history.append({
                            "role": "tool",
                            "rool_call_id": tool_call_id,
                            "content": tool_output
                        })

                    final_response = ollama_generate(build_chat(history), include_tools)

                    history.append({
                        "role": "assistant",
                        "content": final_response
                    })

                    console.print(Markdown(final_response + "\n"))
                else:
                    history.append({
                        "role": 'assistant',
                        "content": response
                    })

                    tmp = []

                    console.print(Markdown(response + "\n"))
            except Exception as e:
                console.print(f"\n[red]Error 111:[/red] {e}")
        else:
            try:
                response = ""
                with Live(console=console, refresh_per_second=20) as live:
                    for token in ollama_generate(build_chat(history), include_tools):
                        response += token
                        live.update(Markdown(response))
                print()
                
                history.append({
                    "role": 'assistant',
                    "content": response
                })

                tmp = []
            except Exception as e:
                console.print(f"\n[red]Error:[/red] {e}")

if __name__ == "__main__":
    app()
