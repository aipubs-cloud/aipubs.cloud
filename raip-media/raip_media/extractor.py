"""raip_media.extractor

Audio extraction from media files.  Uses ffmpeg if available in PATH;
falls back gracefully to a placeholder stub so the pipeline still runs
without a media processing installation.
"""

import shutil
import subprocess
from pathlib import Path
from typing import Optional


def ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None


def extract_audio(media_path: Path, out_dir: Path) -> Optional[Path]:
    """Extract a 16 kHz mono WAV from *media_path* into *out_dir*.

    Returns the path to the WAV file, or ``None`` if ffmpeg is unavailable
    or extraction fails.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    out_audio = out_dir / "audio.wav"

    if not ffmpeg_available():
        stub = out_dir / "audio_stub.txt"
        stub.write_text(
            "audio extraction skipped — ffmpeg not found in PATH", encoding="utf-8"
        )
        return None

    cmd = [
        "ffmpeg", "-y", "-i", str(media_path),
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        str(out_audio),
    ]
    result = subprocess.run(
        cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    if result.returncode == 0 and out_audio.exists():
        return out_audio
    return None
