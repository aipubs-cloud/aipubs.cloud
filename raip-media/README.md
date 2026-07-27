# RAIP Media Intelligence Suite — MVP

A provenance-aware media processing tool that produces RAIP-signed artifact bundles from video and audio files.

## Features

- **Integrity-first pipeline** — SHA-256 ACF computed before any processing
- **Transcription** — Whisper backend (or deterministic stub when Whisper not installed)
- **RAIP provenance** — every output gets an ACF, lifecycle chain, and Ed25519 attestation
- **Rich console dashboard** — live TUI progress display during processing
- **Exporters** — plain text, Markdown, SRT subtitles
- **Batch processing** — process entire directories of media files

## Installation

```bash
# Core (no AI models)
pip install -e .

# With Whisper transcription
pip install -e ".[whisper]"
```

`ffmpeg` must be in `PATH` for audio extraction. Without it, the pipeline runs with a stub transcript.

## Quick start

```bash
# Transcribe a video and generate RAIP provenance
raip-media transcribe lecture.mp4

# Show console dashboard for a completed bundle
raip-media dashboard lecture/

# Verify artifact integrity
raip-media verify lecture/manifest.json

# Export all formats
raip-media export lecture/ --all

# Process an entire directory
raip-media batch ./videos/ --out ./bundles/
```

## Output bundle structure

```
lecture/
├── audio.wav               ← extracted audio (if ffmpeg available)
├── transcript.txt          ← transcription
├── words.json              ← word-level timings
├── keywords.json           ← extracted keywords
├── checksum.sha256         ← SHA-256 checksums for all files
├── manifest.json           ← artifact registry (type, ACF, parent_acf)
└── provenance.raip.json    ← RAIP envelope (ACF + ALC + SIGN)
```

## RAIP integration

Every output file is registered in `manifest.json` with:

- **`acf`** — SHA-256 fingerprint
- **`parent_acf`** — lineage back to the source media
- **`type`** — artifact type (source_media, transcript, words, keywords)

`provenance.raip.json` contains the full RAIP envelope:

```json
{
  "artifact": { "acf": "sha256:..." },
  "lifecycle": {
    "events": [{ "type": "CREATED", "timestamp": "...", "actor": "raip-media" }],
    "current_hash": "sha256:..."
  },
  "attestation": {
    "algorithm": "Ed25519",
    "public_key": "...",
    "signature": "..."
  }
}
```

## Key management

By default, an ephemeral Ed25519 keypair is generated per run. For persistent signing:

```bash
raip init          # generate .raip/private.pem
raip-media transcribe lecture.mp4 --key .raip/private.pem
```

## Architecture

```
raip-media transcribe lecture.mp4
        │
        ▼
  Integrity Check (ACF)
        │
        ▼
  Audio Extraction (ffmpeg / stub)
        │
        ▼
  Transcription (Whisper / stub)
        │
        ▼
  Keyword Extraction
        │
        ▼
  Provenance Generation
  ┌─────────────────────────────┐
  │  manifest.json  (artifact   │
  │  registry with ACFs)        │
  │  provenance.raip.json       │
  │  (RAIP envelope)            │
  └─────────────────────────────┘
        │
        ▼
  Signature (Ed25519)
        │
        ▼
  Archive (checksum.sha256)
```

## Future modules (RAIP v2.0+)

- `RAIP-SID` — Semantic Identity Descriptor (topological fingerprinting)
- `RAIP-ALC-DAG` — DAG lifecycle for parallel/branching provenance
- `RAIP-ZK` — Zero-knowledge attestations for private artifacts
- `RAIP-STREAM` — Continuous provenance for evolving artifacts
