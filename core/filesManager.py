import os
import readchar
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.markup import escape
from core.system import PATHS, load_json
from core.notifications import indicate

console = Console()

def select_workspace() -> list:
    config = load_json(PATHS["DEFAULT"])

    title = "Select your whitelist workspace:"
    options = [workspace for workspace in config["whitelist_workspaces"] if os.path.exists(workspace)]
    index = 0

    def render_menu():
        table = Table(show_header=False, box=None, expand=True)
        for i, opt in enumerate(options):
            if i == index:
                table.add_row(f"[bold green]>> {opt}[/bold green]")
            else:
                table.add_row(f"   {opt}")
        return Panel(table, title=f"[bold magenta]{title}[/bold magenta]", border_style="magenta")

    with Live(render_menu(), refresh_per_second=30, console=console, screen=False) as live:
        while True:
            key = readchar.readkey()

            if key == readchar.key.UP:
                index = (index - 1) % len(options)
            elif key == readchar.key.DOWN:
                index = (index + 1) % len(options)
            elif key == readchar.key.ENTER:
                live.update(None)
                return options[index]
            elif key.lower() == "q":
                live.update(None)
                live.stop()
                indicate("Workspace selection: canceled.")
                return False

            live.update(render_menu())

def select_files(workspace: str, multiple: bool = False, hidden_files: bool = False, authorized_files: list = [".txt"]):
    files_selected = []
    
    title = "Select your file(s):"
    options = [elt for elt in os.listdir(workspace) if (hidden_files or not elt.startswith('.')) or (os.path.isfile() and os.path.splitext(elt)[1] in authorized_files)]
    index = 0

    def render_menu():
        table = Table(show_header=False, box=None, expand=True)
        for i, opt in enumerate(options):
            prefix = escape("[x] " if opt in files_selected else "[ ] ")
            if i == index:
                table.add_row(f"[bold green]>> {prefix}{opt}[/bold green]")
            else:
                table.add_row(f"   {prefix}{opt}")
        return Panel(table, title=f"[bold magenta]{title}[/bold magenta]", border_style="magenta")

    with Live(render_menu(), refresh_per_second=30, console=console, screen=False) as live:
        while True:
            key = readchar.readkey()

            if key == readchar.key.UP:
                index = (index - 1) % len(options)
            elif key == readchar.key.DOWN:
                index = (index + 1) % len(options)
            elif key == readchar.key.ENTER:
                live.update(None)
                return files_selected
            elif key == readchar.key.SPACE and multiple:
                files_selected.append(options[index]) if options[index] not in files_selected else files_selected.remove(options[index])
            elif key.lower() == "q":
                live.update(None)
                live.stop()
                indicate("File(s) selection: canceled.")
                return False

            live.update(render_menu())
