from rich.console import Console

console = Console()

def informate(text: str):
    return console.print(f"[magenta]# {text}[/magenta]\n")

def indicate(text: str):
    return console.print(f"[yellow]# {text}[/yellow]\n")