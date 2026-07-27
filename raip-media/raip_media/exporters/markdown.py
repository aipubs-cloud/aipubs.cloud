"""Export transcript as Markdown."""
from pathlib import Path


def export(transcript_path: Path, out_dir: Path, title: str = "Transcript") -> Path:
    text = transcript_path.read_text(encoding="utf-8")
    md = f"# {title}\n\n{text}\n"
    out = out_dir / "transcript.md"
    out.write_text(md, encoding="utf-8")
    return out
