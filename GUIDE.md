# User Guide for diShine Boardroom Ear

## Table of Contents
1. [Quick Start Guide](#quick-start-guide)
2. [Configuration Guide](#configuration-guide)
3. [Real-World Scenarios](#real-world-scenarios)
4. [Advanced Topics](#advanced-topics)
5. [Troubleshooting FAQs](#troubleshooting-faqs)
6. [Best Practices](#best-practices)
7. [Additional Documentation Links](#additional-documentation-links)

## Quick Start Guide

### Installation Steps for macOS
1. Open Terminal.
2. Install Python and FFmpeg: `brew install python ffmpeg`.
3. Clone the repository, run `./setup.sh`, and follow the prompts.

See [INSTALLATION.md](INSTALLATION.md) for detailed instructions.

### Installation Steps for Linux
1. Open a terminal window.
2. Install prerequisites: `sudo apt install python3 python3-venv python3-pip ffmpeg`.
3. Clone the repository, run `./setup.sh`, and follow the prompts.

### First Run
1. Place an audio file (`.mp3`, `.wav`, or `.m4a`) into `drop_here/`.
2. Run `python3 Boardroom_Ear.py`.
3. Find your transcript in `transcripts/`.

## Configuration Guide

### Model Recommendations
- **Quick tests**: `tiny` — fastest, lowest accuracy (~85%). Good for verifying setup.
- **Standard use**: `small` — recommended for most users. Good balance of speed and accuracy (~91%).
- **High accuracy**: `medium` — slower but more accurate (~94%). Best for multi-speaker meetings.
- **Maximum accuracy**: `large-v3` — slowest, highest accuracy (~97%). Requires ≥10 GB RAM.

### Configuration File (`config.yaml`)

All settings can be controlled via `config.yaml`, environment variables (`.env`), or CLI flags. CLI flags always take precedence. See [USAGE.md](USAGE.md) for the full reference.

## Real-World Scenarios

### Board Meetings
- Use `--model small` or `--model medium` for clear multi-speaker audio.
- Run with `--anonymization basic` (default) to scrub names, emails, and dates before generating a strategic plan.
- Review `transcripts/audit.log` after each session to confirm redaction counts.

### M&A (Mergers and Acquisitions)
- Use `--anonymization full` for maximum confidentiality — all PII is replaced with blank spaces.
- For air-gapped environments, skip the strategic plan with `--no-plan` to prevent any outbound connections.
- Store `drop_here/` and `transcripts/` on an encrypted volume (FileVault, VeraCrypt, LUKS).

### Legal Depositions
- Ensure permission from all parties before recording.
- Use `--no-plan` to guarantee zero external API calls.
- Use `--model large-v3` for maximum transcription accuracy.
- Securely erase source audio after processing with `srm` (macOS) or `shred` (Linux).

## Advanced Topics

### Batch Processing
- Use `--batch --input-dir /path/to/recordings/` to process an entire folder of audio files in one run.
- The tool shares the loaded Whisper model across all files in the batch, saving startup time.

### Air-Gapped Setup
1. On a connected machine, run the tool once with your chosen model to trigger the download.
2. Copy `~/.cache/huggingface/hub` to the offline machine.
3. Set the `HF_HOME` environment variable to point to the copied cache.
4. Use `--no-plan` to prevent any outbound connections.

See [SECURITY.md](SECURITY.md) for full details.

## Troubleshooting FAQs
1. **Why does the application not start?**
   - Run `python3 Boardroom_Ear.py --health-check` to diagnose. Common causes: missing Python 3.9+, missing FFmpeg, or missing dependencies.
2. **How do I reset my configuration?**
   - Delete `config.yaml` and run `./setup.sh` to regenerate it from the sample.
3. **What to do if I encounter errors during installation?**
   - Check system requirements in [INSTALLATION.md](INSTALLATION.md). Enable debug logging with `--log-level DEBUG` and review the output.
4. **Transcription is too slow?**
   - Use a smaller model (`--model tiny` or `--model base`). Ensure `device: auto` is set to use GPU acceleration on Apple Silicon.
5. **Strategic Plan generation fails?**
   - Verify your `ANTHROPIC_API_KEY` in `.env`. Check your Anthropic account for rate limits or billing issues.

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for more solutions.

## Best Practices
- Always store audio and transcripts on encrypted volumes.
- Use `--anonymization full` for maximum PII removal before any external analysis.
- Review `transcripts/audit.log` after every session to verify redaction completeness.
- Securely delete source audio after processing.
- For the most sensitive environments, use `--no-plan` to guarantee zero cloud contact.

## Additional Documentation Links

| Document | Contents |
|----------|----------|
| [INSTALLATION.md](INSTALLATION.md) | Step-by-step setup for macOS and Linux |
| [USAGE.md](USAGE.md) | CLI reference, workflow examples, configuration guide |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | Common issues and solutions |
| [API.md](API.md) | Python API reference for developers |
| [SECURITY.md](SECURITY.md) | NDA compliance details, privacy guarantees, audit trails |
| [CHANGELOG.md](CHANGELOG.md) | Version history and release notes |

---

This document provides users of all technical backgrounds with step-by-step instructions tailored for security compliance environments.
