# diShine Boardroom Ear

**100% NDA-Compliant Local Transcriber & Strategic Analyst for Confidential Boardrooms.**

Board meetings, M&A discussions, and legal strategies are too sensitive for cloud recording bots. `diShine Boardroom Ear` is a portable, security-first intelligence tool that runs 100% locally on your MacBook. It transforms raw audio into structured strategic assets without a single byte leaving your device.

Built by [diShine](https://dishine.it) | Kevin Escoda.

---

## Why this exists

Standard tools like Otter.ai or Fireflies are convenient, but they represent a massive liability in highly confidential environments. `Boardroom Ear` was built to provide the power of AI transcription and strategic analysis while maintaining a **Zero Trust** relationship with the cloud.

It’s specifically designed for:
- **Board of Directors**: Capturing strategic intent without risking data leaks.
- **M&A Advisors**: Analyzing deal rooms and negotiation sessions locally.
- **Legal Strategy**: Transcribing depositions or strategy sessions with absolute privacy.
- **Consultants**: Providing high-value summaries directly on-site from a USB or local drive.

---

## What's included

| Component | Logic | What it provides |
|-----------|-------|------------------|
| **Local Transcriber** | `faster-whisper` | 100% offline audio-to-text with INT8 quantization. |
| **NDA Scrubber** | `PII-Scrubber` | Automatic redaction of names, emails, and entities. |
| **Strategic Planner** | `Claude-3.5-Sonnet` | Professional action plans and executive summaries. |
| **Edge Intelligence** | `Metal/MPS` | Optimized for Apple Silicon (M1/M2/M3/M4) performance. |

---

## Getting started

### 1. Preparation (One-time setup)
Ensure you have Python 3.9+ and FFmpeg. Then run the installer:
```bash
./setup.sh
```

### 2. Operational Workflow
1. Drop your `.mp3` or `.m4a` files into the `drop_here/` folder.
2. Double-click `Boardroom_Ear.command` (or run `python3 Boardroom_Ear.py`).
3. Transcripts and Strategic Plans will be generated in `transcripts/`.

---

## Directory Structure

```text
dishine-boardroom-ear/
├── Boardroom_Ear.command  # Quick-launch script for Mac
├── Boardroom_Ear.py       # Core application hub
├── config.yaml            # Model settings and API credentials
├── setup.sh               # Dependency installer
├── core/                  # Optimized Whisper engine wrappers
├── analysis/              # Scrubber and Strategic Planner modules
├── drop_here/             # Place audio files here
└── transcripts/           # Output folder (Transcripts + MD Reports)
```

---

## Platform Support

| Platform | Local Transcription | Strategic AI | Privacy Level |
|----------|---------------------|--------------|---------------|
| macOS (M1-M4) | Full (Metal) | Optional | 100% NDA-Complient |
| macOS (Intel) | Full (CPU) | Optional | 100% NDA-Complient |
| Linux (x64) | Full (CPU) | Optional | 100% NDA-Complient |

---

## Security & NDA Compliance

The tool follows a "Local-First" architecture:
1. **Raw Audio Storage**: Stays on the local drive. Never uploaded.
2. **Transcription**: Happens in local memory using CTranslate2.
3. **Anonymization**: A regex-based scrubber replaces PII with tokens (e.g., `[PERSON_REDACTED]`) before any external analysis.
4. **Cloud Opt-in**: Strategic analysis via Anthropic is strictly opt-in and ONLY uses anonymized text.

---

## About diShine

[diShine](https://dishine.it) is a creative tech agency based in Milan. We build boutique AI tools for digital consultants and help businesses navigate complex technology stacks with pragmatic, business-first solutions.

- Web: [dishine.it](https://dishine.it)
- GitHub: [github.com/diShine-digital-agency](https://github.com/diShine-digital-agency)

Copyright (c) 2026 [diShine](https://dishine.it). All rights reserved.
