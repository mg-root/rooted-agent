import os
from rich.prompt import Confirm
from core.filesManager import select_workspace, select_files

class CommandHandler:
    def __init__(self, config, console):
        self.config = config
        self.console = console
        self.state = {
            "workspace": {"path": "", "files": []},
            "tmp": [],
            "running": True
        }

    def exit(self, *args):
        self.console.print("[red bold]End of the chat.[/red bold]")
        self.state["running"] = False

    def load(self, *args):
        workspace = select_workspace()
        files = select_files(workspace, multiple=True)
        for file in files:
            with open(file, "r") as f:
                content = f.read()
            file_name = os.path.basename(file)
            self.console.print(f"[[green]+[/green]] File loaded [green bold]{file_name}[/greenbold]\n")
            self.state["tmp"].append([file_name, content])

    # -------------------------------------------------------------------------
    # WORKSPACE COMMAND
    # -------------------------------------------------------------------------
    def workspace(self, *args):
        # Sous-commandes : -get, -remove etc.
        if args:
            sub = args[0]

            if sub == "-get":
                return self._ws_get()

            if sub == "-remove":
                return self._ws_remove()

        # Sinon → sélection normale du workspace
        return self._ws_select()

    # -------------------------------------------------------------------------
    # Sous-fonction : afficher
    # -------------------------------------------------------------------------
    def _ws_get(self):
        ws = self.state["workspace"]
        if ws["path"]:
            self.console.print(
                f"[[magenta bold]Workspace[/magenta bold]] "
                f"[magenta bold]{ws['path']}[/magenta bold]\n"
            )
        elif ws["files"]:
            self.console.print(
                f"[[magenta bold]File{'s' if len(ws['files']) > 1 else ''}[/magenta bold]]\n" +
                "\n".join([f" • [magenta bold]{os.path.basename(f)}[/magenta bold]" for f in ws["files"]]) + "\n"
            )
        else:
            self.console.print(f"[[red bold]![/red bold]] [red]No defined workspace.[/red]\n")

    # -------------------------------------------------------------------------
    # Sous-fonction : supprimer
    # -------------------------------------------------------------------------
    def _ws_remove(self):
        ws = self.state["workspace"]

        if not ws["path"] and not ws["files"]:
            self.console.print(f"[[red bold]![/red bold]] [red]No defined workspace.[/red]\n")
            return

        self.state["workspace"] = {"path": "", "files": []}
        self.console.print(f"[[red bold]-[/red bold]] Workspace removed.\n")

    # -------------------------------------------------------------------------
    # Sous-fonction : sélectionner workspace ou fichiers
    # -------------------------------------------------------------------------
    def _ws_select(self):
        ws = self.state["workspace"]

        workspace = select_workspace()
        if not workspace:
            return

        select_specific = Confirm.ask("Do you want to select specific files ?", show_default=True, default=True)

        if select_specific:
            previous_files = ws["files"].copy()
            result = select_files(workspace, multiple=True, current_files=ws["files"])

            if result is False:
                return

            if result == [] and previous_files != []:
                self.console.print(f"[[red bold]-[/red bold]] Workspace removed.\n")
                ws["files"] = []
                return

            ws["files"] = result
            ws["path"] = ""

            # Fichiers retirés
            removed = [f for f in previous_files if f not in ws["files"]]
            if removed:
                self.console.print(
                    f"[[red bold]-[/red bold]] File(s) removed from workspace:\n" +
                    "\n".join([f" • [red bold]{os.path.basename(f)}[/red bold]" for f in removed]) + "\n"
                )

            # Fichiers ajoutés
            added = [f for f in ws["files"] if f not in previous_files]
            if added:
                self.console.print(
                    f"[[green bold]+[/green bold]] File(s) added into workspace:\n" +
                    "\n".join([f" • [green bold]{os.path.basename(f)}[/green bold]" for f in added]) + "\n"
                )

        else:
            ws["path"] = workspace
            ws["files"] = []
            self.console.print(
                f"[[green bold]+[/green bold]] Workspace added: [green bold]{workspace}[/green bold]\n"
            )

    # -------------------------------------------------------------------------
    # Command dispatcher
    # -------------------------------------------------------------------------
    def dispatch(self, user_input):
        if not user_input.startswith(self.config["prefix"]):
            return False

        parts = user_input[len(self.config["prefix"]):].split()
        cmd = parts[0]
        args = parts[1:]

        if hasattr(self, cmd):
            getattr(self, cmd)(*args)
            return True
        
        return False
