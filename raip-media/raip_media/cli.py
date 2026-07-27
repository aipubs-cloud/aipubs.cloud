"""raip-media CLI

Commands
--------
  raip-media transcribe <media>    Process media → transcript + provenance
  raip-media verify <manifest>     Verify artifact ACFs in a manifest
  raip-media dashboard <bundle>    Show console dashboard for a bundle
  raip-media export <bundle>       Export formats (--txt, --md, --srt)
  raip-media batch <dir>           Process every media file in a directory

Usage examples
--------------
  raip-media transcribe lecture.mp4
  raip-media transcribe lecture.mp4 --out out/lecture-bundle
  raip-media transcribe lecture.mp4 --model large
  raip-media verify out/lecture-bundle/manifest.json
  raip-media dashboard out/lecture-bundle
  raip-media export out/lecture-bundle --txt --md --srt
  raip-media batch ./videos/
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from rich.console import Console

console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="raip-media",
        description="RAIP Media Intelligence Suite — provenance-aware media processing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--version", action="version", version="raip-media 0.1.0")

    sub = parser.add_subparsers(dest="cmd", metavar="<command>")
    sub.required = True

    # transcribe
    p_t = sub.add_parser("transcribe", help="Transcribe a media file and generate RAIP provenance")
    p_t.add_argument("media", metavar="MEDIA", help="Path to media file (video or audio)")
    p_t.add_argument("--out", metavar="DIR", default=None, help="Output bundle directory")
    p_t.add_argument("--model", default="base", help="Whisper model name (default: base)")
    p_t.add_argument("--no-dashboard", action="store_true", help="Suppress live dashboard")
    p_t.add_argument("--key", metavar="PEM", default=None, help="Path to Ed25519 private key PEM")
    p_t.add_argument("--timestamp", metavar="ISO", default=None,
                     help="Deterministic timestamp (for test vectors)")

    # verify
    p_v = sub.add_parser("verify", help="Verify artifact ACFs in a bundle manifest")
    p_v.add_argument("manifest", metavar="MANIFEST", help="Path to manifest.json")
    p_v.add_argument("--json", dest="as_json", action="store_true", help="Output as JSON")

    # dashboard
    p_d = sub.add_parser("dashboard", help="Display console dashboard for a completed bundle")
    p_d.add_argument("bundle", metavar="BUNDLE", help="Path to bundle directory")

    # export
    p_e = sub.add_parser("export", help="Export transcript formats from a bundle")
    p_e.add_argument("bundle", metavar="BUNDLE", help="Path to bundle directory")
    p_e.add_argument("--txt", action="store_true", help="Export plain text")
    p_e.add_argument("--md", action="store_true", help="Export Markdown")
    p_e.add_argument("--srt", action="store_true", help="Export SRT subtitles")
    p_e.add_argument("--all", dest="all_formats", action="store_true", help="Export all formats")

    # batch
    p_b = sub.add_parser("batch", help="Process all media files in a directory")
    p_b.add_argument("dir", metavar="DIR", help="Directory containing media files")
    p_b.add_argument("--model", default="base", help="Whisper model name")
    p_b.add_argument("--out", metavar="DIR", default=None, help="Output base directory")

    args = parser.parse_args()

    try:
        if args.cmd == "transcribe":
            _cmd_transcribe(args)
        elif args.cmd == "verify":
            _cmd_verify(args)
        elif args.cmd == "dashboard":
            _cmd_dashboard(args)
        elif args.cmd == "export":
            _cmd_export(args)
        elif args.cmd == "batch":
            _cmd_batch(args)
    except KeyboardInterrupt:
        console.print("\n[yellow]Aborted.[/yellow]")
        sys.exit(130)
    except Exception as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        sys.exit(1)


# ---------------------------------------------------------------------------
# transcribe
# ---------------------------------------------------------------------------

_MEDIA_EXTS = {".mp4", ".mov", ".mkv", ".avi", ".webm", ".mp3", ".wav", ".m4a", ".flac", ".ogg"}


def _load_key(key_path: str | None):
    from raip_media.raip_core import generate_ephemeral_key, private_key_from_pem
    if key_path:
        pem = Path(key_path).read_bytes()
        return private_key_from_pem(pem)
    return generate_ephemeral_key()


def _cmd_transcribe(args: argparse.Namespace) -> None:
    from raip_media.extractor import extract_audio
    from raip_media.transcriber import transcribe
    from raip_media.provenance import produce_provenance
    from raip_media.dashboard import (
        PIPELINE_STAGES, run_pipeline_dashboard, PipelineCallback
    )
    from raip_media.raip_core import compute_acf

    media = Path(args.media).resolve()
    if not media.exists():
        console.print(f"[red]File not found: {media}[/red]")
        sys.exit(1)

    bundle_dir = Path(args.out).resolve() if args.out else Path(media.stem).resolve()
    bundle_dir.mkdir(parents=True, exist_ok=True)

    private_key = _load_key(getattr(args, "key", None))
    model_name = getattr(args, "model", "base")
    timestamp = getattr(args, "timestamp", None)

    if getattr(args, "no_dashboard", False):
        _run_pipeline(media, bundle_dir, private_key, model_name, timestamp)
    else:
        def runner(name: str, cb: "PipelineCallback") -> None:
            _run_pipeline(media, bundle_dir, private_key, model_name, timestamp, cb)

        run_pipeline_dashboard(media.name, PIPELINE_STAGES, runner)

    # Print summary
    manifest_path = bundle_dir / "manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        console.print(f"\n[bold green]Bundle written to:[/bold green] {bundle_dir}")
        console.print(f"  Artifacts : {len(manifest.get('artifacts', []))}")
        console.print(f"  manifest  : {manifest_path}")
        console.print(f"  provenance: {bundle_dir / 'provenance.raip.json'}")


def _run_pipeline(
    media: Path,
    bundle_dir: Path,
    private_key,
    model_name: str,
    timestamp: str | None,
    cb=None,
) -> None:
    """Execute the full pipeline, optionally updating a dashboard callback."""
    from raip_media.extractor import extract_audio
    from raip_media.transcriber import transcribe
    from raip_media.provenance import produce_provenance
    from raip_media.raip_core import compute_acf

    def _start(stage):
        if cb:
            cb.start_stage(stage)

    def _done(stage, detail=""):
        if cb:
            cb.complete_stage(stage, detail)

    def _fail(stage, detail=""):
        if cb:
            cb.fail_stage(stage, detail)

    # 1. Integrity Check
    _start("Integrity Check")
    source_acf = compute_acf(media.read_bytes())
    _done("Integrity Check", f"acf={source_acf[7:19]}...")

    # 2. Audio Extraction
    _start("Audio Extraction")
    audio_path = extract_audio(media, bundle_dir)
    _done("Audio Extraction", "ok" if audio_path else "skipped (no ffmpeg)")

    # 3. Transcription
    _start("Transcription")
    transcript_path, words_path = transcribe(audio_path, bundle_dir, model_name)
    _done("Transcription", f"{transcript_path.name}")

    # 4. Keyword Extraction (stub)
    _start("Keyword Extraction")
    keywords_path = bundle_dir / "keywords.json"
    _extract_keywords_stub(transcript_path, keywords_path)
    _done("Keyword Extraction", "keywords.json")

    # 5. Provenance Generation
    _start("Provenance Generation")
    artifact_files = [
        {"path": str(media), "type": "source_media", "parent_acf": None,
         "metadata": {"acf": source_acf}},
        {"path": str(transcript_path), "type": "transcript",
         "parent_acf": source_acf, "metadata": {"model": model_name}},
        {"path": str(words_path), "type": "words",
         "parent_acf": source_acf, "metadata": {}},
        {"path": str(keywords_path), "type": "keywords",
         "parent_acf": source_acf, "metadata": {}},
    ]
    result = produce_provenance(
        bundle_dir, artifact_files, private_key,
        generator="raip-media", generator_version="0.1.0",
        timestamp=timestamp,
    )
    _done("Provenance Generation", "manifest.json")

    # 6. Signature
    _start("Signature")
    _done("Signature", "Ed25519")

    # 7. Archive
    _start("Archive")
    _write_checksum_file(bundle_dir)
    _done("Archive", "checksum.sha256")

    if cb:
        cb.set_summary(result["manifest"])


def _extract_keywords_stub(transcript_path: Path, out_path: Path) -> None:
    """Very simple keyword extraction: top frequent non-stop-words."""
    import re
    stop = {
        "the", "a", "an", "is", "in", "of", "and", "to", "this", "that",
        "it", "for", "on", "are", "with", "was", "as", "at", "be", "by",
        "or", "not", "from", "we", "you", "i", "s", "t", "so", "if",
    }
    text = transcript_path.read_text(encoding="utf-8").lower()
    words = re.findall(r"[a-z]{3,}", text)
    freq: dict[str, int] = {}
    for w in words:
        if w not in stop:
            freq[w] = freq.get(w, 0) + 1
    top = sorted(freq, key=lambda k: freq[k], reverse=True)[:20]
    out_path.write_text(json.dumps(top, indent=2), encoding="utf-8")


def _write_checksum_file(bundle_dir: Path) -> None:
    lines = []
    for f in sorted(bundle_dir.iterdir()):
        if f.is_file() and f.suffix != ".sha256":
            from raip_media.utils import file_sha256
            lines.append(f"{file_sha256(f)}  {f.name}")
    (bundle_dir / "checksum.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# verify
# ---------------------------------------------------------------------------

def _cmd_verify(args: argparse.Namespace) -> None:
    from raip_media.raip_core import compute_acf

    manifest_path = Path(args.manifest).resolve()
    if not manifest_path.exists():
        console.print(f"[red]Manifest not found: {manifest_path}[/red]")
        sys.exit(2)

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    results = []
    overall = True
    pass_sym = "[green]✓[/green]"
    fail_sym = "[red]✗[/red]"

    for artifact in manifest.get("artifacts", []):
        p = Path(artifact["path"])
        expected_acf = artifact.get("acf", "")

        if not p.exists():
            results.append({"id": artifact["id"], "status": "MISSING", "path": str(p)})
            overall = False
            continue

        observed_acf = compute_acf(p.read_bytes())
        ok = observed_acf == expected_acf
        if not ok:
            overall = False
        results.append({
            "id": artifact["id"],
            "type": artifact.get("type"),
            "status": "PASS" if ok else "FAIL",
            "path": str(p),
            "expected_acf": expected_acf,
            "observed_acf": observed_acf,
        })

    if getattr(args, "as_json", False):
        print(json.dumps({"overall": overall, "artifacts": results}, indent=2))
    else:
        console.print()
        for r in results:
            sym = pass_sym if r["status"] == "PASS" else fail_sym
            console.print(f"  {sym} [{r['status']}] {r.get('type', '?')}  {Path(r['path']).name}")
        console.print()
        if overall:
            console.print("[bold green]VERIFICATION: PASS[/bold green]")
        else:
            console.print("[bold red]VERIFICATION: FAIL[/bold red]")
            sys.exit(1)


# ---------------------------------------------------------------------------
# dashboard
# ---------------------------------------------------------------------------

def _cmd_dashboard(args: argparse.Namespace) -> None:
    from raip_media.dashboard import show_bundle_dashboard
    bundle_dir = Path(args.bundle).resolve()
    if not bundle_dir.exists():
        console.print(f"[red]Bundle directory not found: {bundle_dir}[/red]")
        sys.exit(2)
    show_bundle_dashboard(bundle_dir)


# ---------------------------------------------------------------------------
# export
# ---------------------------------------------------------------------------

def _cmd_export(args: argparse.Namespace) -> None:
    bundle_dir = Path(args.bundle).resolve()
    if not bundle_dir.exists():
        console.print(f"[red]Bundle directory not found: {bundle_dir}[/red]")
        sys.exit(2)

    transcript_path = bundle_dir / "transcript.txt"
    words_path = bundle_dir / "words.json"
    do_all = getattr(args, "all_formats", False)

    if (getattr(args, "txt", False) or do_all) and transcript_path.exists():
        from raip_media.exporters.txt import export
        out = export(transcript_path, bundle_dir)
        console.print(f"[green]✓[/green] Exported plain text: {out.name}")

    if (getattr(args, "md", False) or do_all) and transcript_path.exists():
        from raip_media.exporters.markdown import export
        out = export(transcript_path, bundle_dir, title=bundle_dir.name)
        console.print(f"[green]✓[/green] Exported Markdown: {out.name}")

    if (getattr(args, "srt", False) or do_all) and words_path.exists():
        from raip_media.exporters.srt import export
        out = export(words_path, bundle_dir)
        console.print(f"[green]✓[/green] Exported SRT: {out.name}")

    if not any([
        getattr(args, "txt", False),
        getattr(args, "md", False),
        getattr(args, "srt", False),
        do_all,
    ]):
        console.print("[yellow]No format specified. Use --txt, --md, --srt, or --all.[/yellow]")


# ---------------------------------------------------------------------------
# batch
# ---------------------------------------------------------------------------

def _cmd_batch(args: argparse.Namespace) -> None:
    src_dir = Path(args.dir).resolve()
    if not src_dir.is_dir():
        console.print(f"[red]Not a directory: {src_dir}[/red]")
        sys.exit(2)

    media_files = [f for f in src_dir.iterdir() if f.suffix.lower() in _MEDIA_EXTS]
    if not media_files:
        console.print(f"[yellow]No media files found in {src_dir}[/yellow]")
        return

    base_out = Path(args.out).resolve() if args.out else src_dir / "_bundles"
    private_key = _load_key(None)
    model_name = getattr(args, "model", "base")

    console.print(f"Processing {len(media_files)} file(s) in {src_dir}")
    for media in sorted(media_files):
        bundle_dir = base_out / media.stem
        console.print(f"\n[cyan]→ {media.name}[/cyan]  →  {bundle_dir}")
        bundle_dir.mkdir(parents=True, exist_ok=True)
        try:
            _run_pipeline(media, bundle_dir, private_key, model_name, None)
            console.print(f"  [green]✓[/green] Done: {bundle_dir}")
        except Exception as exc:
            console.print(f"  [red]✗[/red] Failed: {exc}")


if __name__ == "__main__":
    main()
