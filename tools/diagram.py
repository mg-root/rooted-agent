import os
import subprocess
import shutil

def has_cmd(cmd: str) -> bool:
    return shutil.which(cmd) is not None

def render_mermaid(mermaid_text: str, output_path: str = "diagram.png"):
    """Rend un diagramme Mermaid via mmdc (si dispo)."""
    if not has_cmd("mmdc"):
        raise RuntimeError("Mermaid CLI (mmdc) introuvable. Installez-le : npm i -g @mermaid-js/mermaid-cli")
    
    tmp = output_path + ".mmd"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(mermaid_text)
    
    # Force l'utilisation de Chromium système
    env = os.environ.copy()
    env["PUPPETEER_EXECUTABLE_PATH"] = "/usr/bin/chromium"

    try:
        subprocess.run(
            ["mmdc", "-i", tmp, "-o", output_path],
            check=True,
            env=env
        )
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)
    
    return output_path

def render_graphviz(dot_text: str, output_path: str = "graph.png"):
    """Rend un diagramme Graphviz via dot (si dispo)."""
    if not has_cmd("dot"):
        raise RuntimeError("Graphviz 'dot' introuvable. Installez-le : sudo apt-get install graphviz")
    tmp = output_path + ".dot"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(dot_text)
    subprocess.run(["dot", "-Tpng", tmp, "-o", output_path], check=True)
    os.remove(tmp)
    return output_path