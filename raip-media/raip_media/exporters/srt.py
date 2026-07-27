"""Export words JSON as SRT subtitles."""
import json
from pathlib import Path


def _fmt_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def export(words_path: Path, out_dir: Path, words_per_line: int = 8) -> Path:
    words = json.loads(words_path.read_text(encoding="utf-8"))
    out = out_dir / "subtitles.srt"
    lines = []
    idx = 1
    i = 0
    while i < len(words):
        chunk = words[i : i + words_per_line]
        start = chunk[0]["start"]
        end = chunk[-1]["end"]
        text = " ".join(w["word"] for w in chunk)
        lines.append(str(idx))
        lines.append(f"{_fmt_time(start)} --> {_fmt_time(end)}")
        lines.append(text)
        lines.append("")
        idx += 1
        i += words_per_line
    out.write_text("\n".join(lines), encoding="utf-8")
    return out
