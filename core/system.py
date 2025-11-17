import os
import sys
import json
import time
import shutil
from datetime import datetime
from typing import Callable, Any, Optional

from rich.prompt import Confirm
from rich.console import Console

console = Console()

PATHS = {
    "LOG": os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "logs", "actions.jsonl"),
    "DEFAULT": os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "default.json"),
    "SYSTEM_MESSAGES": os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "systemMessages.json"),
    "DEVELOPER_INSTRUCTIONS": os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "developerInstructions.json"),
    "MEMORY": os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "memory.json"),   
    "TOOLS_API": os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "toolsAPI.json"),

    "SPECIALIZATION/CODE_EXPERT": os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "specializations", "codeExpert.json"),

    "LOGS": os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "logs")
}

def load_json(path: str) -> dict:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        ValueError(f"{path} doesn't exist.")

def save_chat(name: str, messages: list) -> bool:
    full_path = os.path.exists(os.path.join(PATHS["LOGS"], name))
    if os.path.exists(full_path):
        return False
    
    with open(full_path + ".json", "+w", encoding="utf-8") as f:
        f.write(json.dumps(messages, indent=2, ensure_ascii=False))
    return True

def is_path_allowed(path: str, whitelist: list[str]) -> bool:
    try:
        ap = os.path.abspath(path)
        for w in whitelist:
            if os.path.commonpath([ap, os.path.abspath(w)]) == os.path.abspath(w):
                return True
        return False
    except Exception:
        return False

def confirm(message: str) -> bool:
    console.print(f"[bold yellow][CONFIRM][/bold yellow] {message}")
    ans = Confirm.ask("Proceed ?", default=False)
    return bool(ans)

def backup_file(path: str) -> Optional[str]:
    if not os.path.exists(path):
        return None
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    root, ext = os.path.splitext(path)
    backup_path = f"{root}.backup_{ts}{ext}"
    shutil.copy2(path, backup_path)
    return backup_path

def safe_action(message: str, action_name: str, func: Callable[..., Any], *args, **kwargs):
    cfg = load_json(PATHS["DEFAULT"])
    # Path whitelist enforcement for any str arg that looks like a path
    whitelist = cfg.get("workdir_whitelist", ["./"])

    # Quick path scan
    paths = []
    for a in list(args) + list(kwargs.values()):
        if isinstance(a, str) and ("/" in a or a.endswith(".docx") or a.endswith(".png") or a.endswith(".mmd")):
            paths.append(a)

    # Check whitelist
    for p in paths:
        if not is_path_allowed(p, whitelist):
            console.print(f"[bold red]Chemin interdit par la whitelist:[/bold red] {p}")
            return None

    # Confirmation
    if not confirm(message):
        console.print("[dim]Action annulée.[/dim]")
        return None

    # Backups pour docx cibles
    for p in paths:
        if p.endswith(".docx") and os.path.exists(p):
            bp = backup_file(p)
            if bp:
                console.print(f"[green]Backup créé[/green] → {bp}")