import typer
import os
from rich.console import Console
from rich.live import Live
from rich.prompt import Prompt
from rich.markdown import Markdown
from core.llmEngine import ollama_generate
from core.system import PATHS, load_json
from core.chatBuilder import build_chat
from core.toolsManager import execute_tool
from core.notifications import informate
from tools.read_file import read_file
from core.commandHandler import CommandHandler

import requests

app = typer.Typer(help="Agent IA - Rooted ready to support you.")
console = Console()
config = load_json(PATHS["DEFAULT"])
handler = CommandHandler(config, console)

################################################################################
OLLAMA_API = config["ollama_api"]
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
################################################################################

@app.command()
def chat(include_tools: bool = False):
    """
    Start a new chat with Agent Rooted.
    """

    os.system('clear')
    informate("Rooted is ready to help you !")
    
    history = []

    while handler.state["running"]:
        prompt = config['promptDisplayed']

        if len(handler.state["tmp"]) > 0:
            prompt = f"[Files: [green]{" [/green]/[green] ".join([str(file[0]) for file in handler.state["tmp"]])}[/green]]" + prompt

        user_input = Prompt.ask(prompt)

        if handler.dispatch(user_input):
            continue

        if not user_input:
            continue

        if not is_model_loaded(MODEL_NAME):
            load_model_with_progress(MODEL_NAME)

        for file in handler.state["tmp"]:
            history.append({
                "role": "system",
                "content": f"[File: {file[0]}]\n{file[1]}\n"
            })

        history.append({
            "role": "user",
            "content": user_input
        })

        # Workspace
        if handler.state["workspace"]["files"]:
            tmp_messages = []
            tmp_messages.append({
                "role": "system",
                "content": (
                    "You are an assistant whose ONLY responsibility is to select which files are relevant "
                    "to the user's last message.\n\n"

                    "Below is the list of files available in the workspace:\n"
                    f"{chr(10).join([f' - {file}' for file in handler.state["workspace"]["files"]])}\n\n"

                    "YOUR RULES (STRICT):\n"
                    "1. You MUST NOT answer the user's question.\n"
                    "2. You MUST NOT provide, suggest, or execute shell commands (no 'touch', 'echo', 'ls', "
                    "'cat', 'mkdir', 'rm', or any other shell command or script).\n"
                    "3. You MUST NOT summarize, inspect, or interpret the content of any file.\n"
                    "4. You MUST NOT explain your reasoning.\n"
                    "5. You MUST NOT open or analyze files.\n"
                    "6. You MUST ONLY return the list of file paths that are relevant to the user's request.\n"
                    "7. You MUST answer with the required format ONLY, and nothing else.\n\n"

                    "EXPECTED OUTPUT FORMAT (MANDATORY):\n"
                    "[\"/full/path/to/file.ext\", ...]\n\n"

                    "SELECTION RULES:\n"
                    "- If the user explicitly mentions a file name, return ONLY that file (if it exists in the workspace).\n"
                    "- If no file corresponds to the user's request, return an empty list: [].\n"
                    "- If you are unsure whether a file may be relevant, INCLUDE IT in the list.\n"
                    "- NEVER return anything other than a pure JSON array of file paths.\n"
                    "- DO NOT add extra sentences, comments, explanations, or formatting.\n"
                )
            })

            tmp_messages.append({
                "role": "user",
                "content": user_input
            })
            
            response = ollama_generate(tmp_messages, force_no_stream=True)

            if isinstance(response, list) and len(response) > 0:
                for file in response:
                    if os.path.exists(file):
                        content = read_file(file)
                    else:
                        content = "[EMPTY FILE — DOES NOT EXIST YET]"

                    history.insert(-2, {
                        "role": "system",
                        "content": f"[File: {file}]\n{content}\n"
                    })

        # Tools
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

                    try:
                        console.print(Markdown(final_response + "\n"))
                    except Exception as e:
                        console.print(final_response)
                        console.print(f"\n[red]Error tools -> print final tools reponse:[/red] {e}")
                else:
                    history.append({
                        "role": 'assistant',
                        "content": response
                    })

                    handler.state["tmp"] = []

                    try:
                        console.print(Markdown(response + "\n"))
                    except Exception as e:
                        console.print(response)
                        console.print(f"\n[red]Error tools -> print response:[/red] {e}")
            except Exception as e:
                console.print(f"\n[red]Error tools:[/red] {e}")

        # Without tools
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

                handler.state["tmp"] = []
            except Exception as e:
                console.print(f"\n[red]Error without tools:[/red] {e}")

if __name__ == "__main__":
    app()
