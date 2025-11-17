import os
from core.system import confirm

def make_file(path: str, content: str):

    # Confirmation utilisateur
    confirm(f"Create file : {path} ?")

    # Création du dossier parent si non existant
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    return f"[OK] File created: {path}"
