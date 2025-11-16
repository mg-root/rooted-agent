from rich.console import Console

console = Console()

def fake_web_search(query: str) -> str:
    return f"[FAKE SEARCH RESULT]\nRésultat fictif pour la recherche : **{query}**\n"