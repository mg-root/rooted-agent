def convert_memory(memory: dict) -> str:
    out = []
    for section, content in memory.items():
        out.append(f"{section}:")
        if isinstance(content, dict):
            for subsection, item in content.items():
                out.append(f"- {subsection}: {item}")
        elif isinstance(content, list):
            for item in content:
                out.append(f"- {item}")
        else:
            out.append(f"- {content}")
        out.append("")

    return "\n".join(out)