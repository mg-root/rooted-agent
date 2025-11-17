import os
import json
from docx import Document
from odf.opendocument import load as load_odt, OpenDocumentText
from odf.text import P
from core.system import confirm

accepted_file = {
    "utf8": [".txt", ".md", ".py", ".js", ".ts", ".cpp", ".c", ".cs", ".hpp", ".h", ".html", ".php", ".css", ".java"],
    "json": [".json", ".jsonc"],
    "docx": [".docx"],
    "odt": [".odt"],
    "pdf": [".pdf"]  # PDF editing not supported
}

def edit_file(path: str, content: str, modification_explained: str = None):
    _, ext = os.path.splitext(path)
    ext = ext.lower()

    print(modification_explained)
    confirm(f"Edit file {path} ?")

    if ext in accepted_file["utf8"]:
        return _edit_utf8(path, content)

    elif ext in accepted_file["json"]:
        return _edit_json(path, content)

    elif ext in accepted_file["docx"]:
        return _edit_docx(path, content)

    elif ext in accepted_file["odt"]:
        return _edit_odt(path, content)

    # PDF & binary: not editable
    return f"Cannot edit binary or PDF file: {path}"


# -------- UTF-8 (CODE / TEXTE) ---------
def _edit_utf8(path: str, content: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"[OK] File overwritten: {path}"


# -------- JSON ---------
def _edit_json(path: str, content: str):
    """
    content doit être un string JSON complet.
    On le valide avant d’écrire pour éviter les corruptions.
    """
    try:
        parsed = json.loads(content)  # validation
    except json.JSONDecodeError:
        return f"[ERROR] Invalid JSON content — file NOT modified: {path}"

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    return f"[OK] JSON file overwritten: {path}"


# -------- DOCX ---------
def _edit_docx(path: str, content: str):
    """
    content : texte brut envoyé par le modèle.
    On crée un nouveau fichier Word.
    """
    doc = Document()
    for line in content.split("\n"):
        doc.add_paragraph(line)

    doc.save(path)
    return f"[OK] DOCX file overwritten: {path}"


# -------- ODT ---------
def _edit_odt(path: str, content: str):
    """
    On recrée un fichier ODT avec du texte simple.
    """
    odt = OpenDocumentText()
    for line in content.split("\n"):
        p = P(text=line)
        odt.text.addElement(p)

    odt.save(path)
    return f"[OK] ODT file overwritten: {path}"
