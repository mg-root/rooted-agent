import json
import re
from typing import Dict, Callable
from tools.diagram import render_mermaid

def fake_web_search(query: str) -> str:
    return f"[FAKE SEARCH RESULT]\nRésultat fictif pour la recherche : '{query}'\n"


TOOLS: Dict[str, Callable] = {
    "fake_web_search": fake_web_search,
    "diagram_mermaid": render_mermaid
}

def detect_tool_call(output: str):
    """
    Détecte un appel de tool même si le modèle ajoute une phrase avant.
    Extrait le PREMIER objet JSON valide contenant {tool, args}.
    Retourne un dict {"tool": ..., "args": {...}} si valide, sinon None.
    """

    if not output or not isinstance(output, str):
        return None

    # Nettoyage des caractères parasites
    cleaned = (
        output.replace("\ufeff", "")
              .replace("\u200b", "")
              .strip()
    )

    # Chercher le premier objet JSON avec une regex robuste
    match = re.search(r"\{[\s\S]*\}", cleaned)
    if not match:
        return None

    json_text = match.group(0).strip()

    # TENTER de parser le JSON
    try:
        data = json.loads(json_text)
    except Exception:
        return None

    # Vérifier que c'est bien un tool call strict
    if not isinstance(data, dict):
        return None

    if set(data.keys()) != {"tool", "args"}:
        return None

    if not isinstance(data["args"], dict):
        return None

    return data

def execute_tool(tool_call: dict) -> str:
    tool_name = tool_call.get("tool")
    args = tool_call.get("args", {})

    if tool_name not in TOOLS:
        return f"[ERROR] Tool '{tool_name}' not found."

    func = TOOLS[tool_name]

    try:
        result = func(**args)
        return result
    except Exception as e:
        return f"[TOOL EXECUTION ERROR] {str(e)}"