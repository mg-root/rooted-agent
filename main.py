import typer
import os
from rich.console import Console
from rich.live import Live
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown
from core.llm import ollama_generate
from core.system import PATHS, load_json, save_chat
from core.chatBuilder import build_chat
from core.toolsManager import execute_tool
from core.notifications import informate

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
    informate("Rooted is ready to help you !")
    
    history = []
    tmp = []
    context = {
        "workspace": "",
        "files": []
    }

    while True:
        prompt = config['promptDisplayed']

        if len(tmp) > 0:
            prompt = f"[Files: [green]{" [/green]/[green] ".join([str(file[0]) for file in tmp])}[/green]]" + prompt

        user_input = Prompt.ask(prompt)

        # Exit
        if user_input.lower() == f"{config["prefix"]}exit":
            console.print("[red bold]End of the chat.[/red bold]")
            break

        # Load
        elif user_input.lower() == f"{config["prefix"]}load":
            workspace = select_workspace()
            files = select_files(workspace, multiple=True)
            for file in files:
                with open(file, "r", encoding="utf-8") as f:
                    content = f.read()
                file_name = os.path.basename(file)
                console.print(f"[[green]+[/green]] File loaded [green bold]{file_name}[/greenbold]\n")
                tmp.append([file_name, content])
            continue

        # Context
        elif user_input.lower() == f"{config["prefix"]}context" or user_input.lower() == f"{config["prefix"]}ctx":
            workspace = select_workspace()

            if not workspace:
                continue

            selectSpecificFiles = Confirm.ask("Do you want to select specific files ?", show_default=True, default=True)
            if selectSpecificFiles:
                last_current_files = context["files"].copy()
                result = select_files(workspace, multiple=True, authorized_files_extension=[".txt", ".pdf", ".docx"], current_files=context["files"])
                
                if result == False:
                    continue
                elif result == [] and last_current_files != []:
                    console.print(f"[[red bold]-[/red bold]] Context removed.\n")
                    continue

                context["files"] = result
                context["workspace"] = ""

                if last_current_files != [] and last_current_files != context["files"]:
                    removed = []
                    added = []
                    for file in last_current_files:
                        if file not in context["files"]:
                            removed.append(file)

                    if removed:
                        console.print(f"[[red bold]-[/red bold]] File(s) removed from context:\n{"\n".join([f" • [red bold]{os.path.basename(file)}[/red bold]" for file in removed])}\n")

                    for file in context["files"]:
                        if file not in last_current_files:
                            added.append(file)

                    if added:
                        console.print(f"[[green bold]+[/green bold]] File(s) added into context:\n{"\n".join([f" • [green bold]{os.path.basename(file)}[/green bold]" for file in added])}\n")
                else:   
                    console.print(f"[[green bold]+[/green bold]] File(s) added into context:\n{"\n".join([f" • [green bold]{os.path.basename(file)}[/green bold]" for file in context["files"]])}\n")
            else:
                context["workspace"] = workspace
                console.print(f"[[green bold]+[/green bold]] Workspace added into context: [green bold]{workspace}[/green bold]\n")
            continue

        # Get Context
        elif user_input.lower() == f"{config["prefix"]}context -get" or user_input.lower() == f"{config["prefix"]}ctx -get":
            if context["workspace"]:
                console.print(f"[[magenta bold]Workspace[/magenta bold]] [magenta bold]{context["workspace"]}[/magenta bold]\n")
            elif context["files"]:
                console.print(f"[[magenta bold]File{"s" if len(context['files']) > 1 else ""}[/magenta bold]]\n{"\n".join([f" • [magenta bold]{os.path.basename(file)}[/magenta bold]" for file in context["files"]])}\n")
            else:
                console.print(f"[[red bold]![/red bold]] [red]No defined context.[/red]\n")
            continue

        # Remove Context
        elif user_input.lower() == f"{config["prefix"]}context -remove" or user_input.lower() == f"{config["prefix"]}ctx -remove":
            console.print(context["workspace"])
            console.print(context["files"])
            if context["workspace"] == "" and context["files"] == []:
                console.print(f"[[red bold]![/red bold]] [red]No defined context.[/red]\n")
            else:
                context = {
                    "workspace": "",
                    "files": []
                }
                console.print(f"[[red bold]-[/red bold]] Context removed.\n")
            continue
        
        # History
        elif user_input.lower() == f"{config["prefix"]}history":
            console.print(history)
            continue

        # Save (decapreted)
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
