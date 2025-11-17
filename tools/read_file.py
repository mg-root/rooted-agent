import os
import PyPDF2
from docx import Document
from odf.opendocument import load
from odf.text import P

accepted_file = {
    "utf8": [".txt", ".md", ".py", ".js", ".ts", ".cpp", ".c", ".cs", ".hpp", ".h", ".html", ".php", ".css", ".java"],
    "json": [".json", ".jsonc"],
    "docx": [".docx"],
    "odt": [".odt"],
    "pdf": [".pdf"]
}

def read_file(path: str):
    _, ext = os.path.splitext(path)

    ext = ext.lower()

    if ext in accepted_file["utf8"]:
        return _read_utf8(path)
    elif ext in accepted_file["json"]:
        return _read_json(path)
    elif ext in accepted_file["docx"]:
        return _read_docx(path)
    elif ext in accepted_file["odt"]:
        return _read_odt(path)
    elif ext in accepted_file["pdf"]:
        return _read_pdf(path)
    
    return _read_binary(path)
    
def _read_utf8(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
    
def _read_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
    
def _read_docx(path: str) -> str:
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs)

def _read_odt(path: str) -> str:
    odt = load(path)
    paragraphs = odt.getElementsByType(P)
    
    lines = []
    for p in paragraphs:
        text_content = "".join(node.data for node in p.childNodes if hasattr(node, "data"))
        lines.append(text_content)

    return "\n".join(lines)

def _read_pdf(path: str) -> str:
    text = ""
    with open(path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    return text.strip()

def _read_binary(path: str) -> str:
    size = os.path.getsize(path)
    return f"[BINARY FILE] {os.path.basename(path)} ({size} bytes)"