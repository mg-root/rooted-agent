from rich.console import Console

console = Console()

def indicate(text: str):
    return console.print(f"[yellow]# {text}[/yellow]\n")