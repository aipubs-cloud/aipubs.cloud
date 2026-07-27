"""Export transcript as plain text."""
from pathlib import Path


def export(transcript_path: Path, out_dir: Path) -> Path:
    text = transcript_path.read_text(encoding="utf-8")
    out = out_dir / "transcript_export.txt"
    out.write_text(text, encoding="utf-8")
    return out
