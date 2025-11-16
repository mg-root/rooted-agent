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

def select_workspace():
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

def select_files(workspace: str, path: str = None, multiple: bool = False, authorized_hidden_files: bool = False, authorized_files_extension: list = [".txt"]):
    if not path:
        path = workspace
    
    files_selected = []
    
    title = "Select your file(s):"
    dirs, files = listdir(path, authorized_hidden_files, authorized_files_extension)
    options = dirs + files
    index = 0

    if path != workspace:
        options.insert(0, "..")

    def render_menu():
        table = Table(show_header=False, box=None, expand=True)
        for i, opt in enumerate(options):
            prefix = escape("[x] " if opt in files_selected else "[ ] ")
            if i == index:
                table.add_row(f"[bold green]>> {prefix if opt in files else ""}{os.path.basename(opt)}[/bold green]")
            else:
                table.add_row(f"   {prefix if opt in files else ""}{os.path.basename(opt)}")
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
            elif key == readchar.key.SPACE:
                if options[index] in files:
                    if multiple:
                        full_path = os.path.join(path, options[index])
                        files_selected.append(full_path) if full_path not in files_selected else files_selected.remove(options[index])
                    elif len(files_selected) == 0:
                        full_path = os.path.join(path, options[index])
                        files_selected.append(full_path) if full_path not in files_selected else files_selected.remove(options[index])
                elif options[index] in dirs:
                    child = os.path.join(path, options[index])
                    live.update(None)
                    live.stop()
                    return select_files(workspace, child, multiple, authorized_hidden_files, authorized_files_extension)
                elif options[index] == "..":
                    parent = os.path.abspath(os.path.join(path, os.pardir))
                    if parent.startswith(workspace):
                        live.update(None)
                        live.stop()
                        return select_files(workspace, parent, multiple, authorized_hidden_files, authorized_files_extension)
            elif key == readchar.key.BACKSPACE:
                parent = os.path.abspath(os.path.join(path, os.pardir))
                if parent.startswith(workspace):
                    live.update(None)
                    live.stop()
                    return select_files(workspace, parent, multiple, authorized_hidden_files, authorized_files_extension)
            elif key.lower() == "q":
                live.update(None)
                live.stop()
                indicate("File(s) selection: canceled.")
                return False

            live.update(render_menu())

def listdir(path: str, authorized_hidden_files: bool = False, authorized_files_extension: list = [".txt"]) -> dict:
    if not os.path.exists(path):
        return ValueError("Path doesn't exist.")

    dirs = []
    files = []

    for elt in os.listdir(path):
        if os.path.isdir(os.path.join(path, elt)):
            if elt.startswith(".") and not authorized_hidden_files:
                continue
            dirs.append(os.path.join(path, elt))
        else:
            name, extension = os.path.splitext(elt)
            if extension not in authorized_files_extension:
                continue
            files.append(os.path.join(path, elt))

    return dirs, files