import os
from core.system import confirm
from docx import Document
from reportlab.pdfgen import canvas
from odf.opendocument import OpenDocumentText

def make_file(path: str):
    confirm(f"Create file: {path} ?")

    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    ext = os.path.splitext(path)[1].lower()

    if ext in [".txt", ".md", ".py", ".js", ".cpp", ".c", ".hpp", ".html", ".css", ".java", ".ts", ".php", ".cs", ".json"]:
        with open(path, "w", encoding="utf-8") as f:
            if ext == ".json":
                f.write("{}")
            else:
                f.write("")
        return f"[OK] Empty text file created: {path}"

    if ext == ".docx":
        doc = Document()
        doc.add_paragraph("")
        doc.save(path)
        return f"[OK] Empty DOCX file created: {path}"

    if ext == ".odt":
        odt = OpenDocumentText()
        odt.save(path)
        return f"[OK] Empty ODT file created: {path}"

    if ext == ".pdf":
        c = canvas.Canvas(path)
        c.drawString(50, 800, "")
        c.save()
        return f"[OK] Empty PDF file created: {path}"

    with open(path, "w", encoding="utf-8") as f:
        f.write("")
    return f"[OK] Empty file created (unknown type): {path}"
