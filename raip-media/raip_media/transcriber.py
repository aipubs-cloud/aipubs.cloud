"""raip_media.transcriber

Transcription engine with two backends:

1. **Whisper** (optional) — uses ``openai-whisper`` if installed.
2. **Stub** — deterministic placeholder that always succeeds even without
   any AI models, so the provenance pipeline runs in CI and tests.

The active backend is chosen at call time based on availability.
"""

import json
import time
from pathlib import Path
from typing import Optional, Tuple


def _whisper_available() -> bool:
    try:
        import whisper  # noqa: F401
        return True
    except ImportError:
        return False


def transcribe(
    audio_path: Optional[Path],
    out_dir: Path,
    model_name: str = "base",
) -> Tuple[Path, Path]:
    """Transcribe *audio_path* and write ``transcript.txt`` + ``words.json``.

    Args:
        audio_path: Path to a WAV file, or ``None`` if audio extraction failed.
        out_dir: Directory where output files are written.
        model_name: Whisper model name (ignored by stub backend).

    Returns:
        ``(transcript_path, words_path)``
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    transcript_path = out_dir / "transcript.txt"
    words_path = out_dir / "words.json"

    if audio_path and audio_path.exists() and audio_path.suffix == ".wav":
        if _whisper_available():
            return _transcribe_whisper(audio_path, out_dir, model_name)

    return _transcribe_stub(audio_path, out_dir)


# ---------------------------------------------------------------------------
# Whisper backend
# ---------------------------------------------------------------------------

def _transcribe_whisper(
    audio_path: Path, out_dir: Path, model_name: str
) -> Tuple[Path, Path]:
    import whisper  # type: ignore

    transcript_path = out_dir / "transcript.txt"
    words_path = out_dir / "words.json"

    model = whisper.load_model(model_name)
    result = model.transcribe(str(audio_path), word_timestamps=True)

    transcript_path.write_text(result["text"].strip(), encoding="utf-8")

    words = []
    for segment in result.get("segments", []):
        for w in segment.get("words", []):
            words.append({
                "word": w.get("word", "").strip(),
                "start": round(w.get("start", 0.0), 3),
                "end": round(w.get("end", 0.0), 3),
                "probability": round(w.get("probability", 1.0), 4),
            })

    words_path.write_text(json.dumps(words, indent=2, ensure_ascii=False), encoding="utf-8")
    return transcript_path, words_path


# ---------------------------------------------------------------------------
# Stub backend
# ---------------------------------------------------------------------------

def _transcribe_stub(
    audio_path: Optional[Path], out_dir: Path
) -> Tuple[Path, Path]:
    transcript_path = out_dir / "transcript.txt"
    words_path = out_dir / "words.json"

    stem = audio_path.stem if audio_path else "unknown"
    text = (
        f"[RAIP Media Suite — transcript stub]\n\n"
        f"Source: {stem}\n\n"
        f"This is a placeholder transcript produced by the deterministic stub\n"
        f"backend. Install openai-whisper and provide an audio file to obtain\n"
        f"a real transcription.\n\n"
        f"Replace raip_media/transcriber.py with your preferred engine.\n"
    )
    transcript_path.write_text(text, encoding="utf-8")

    tokens = text.split()
    t = 0.0
    words = []
    for tok in tokens:
        words.append({"word": tok, "start": round(t, 2), "end": round(t + 0.4, 2)})
        t += 0.4

    words_path.write_text(json.dumps(words, indent=2, ensure_ascii=False), encoding="utf-8")
    return transcript_path, words_path
