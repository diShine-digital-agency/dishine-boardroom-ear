# diShine Boardroom Ear (v1.0) 🎧
**100% NDA-Compliant Local Transcriber & Strategic Analyst**

The `diShine Boardroom Ear` is a portable, security-first transcription tool designed specifically for high-stakes environments: M&A discussions, board meetings, and confidential legal strategy sessions. 

Unlike cloud-based competitors (Otter, Fireflies, etc.), **Boardroom Ear runs 100% locally on your machine.** No audio ever leaves your device during transcription.

---

## 🚀 Key Features

- **Local-First Transcription**: Powered by `faster-whisper`, a highly optimized version of OpenAI's Whisper model.
- **Privacy-Centric**: Designed for "Air-Gapped" or high-confidentiality use. Zero internet required for transcription.
- **Strategic Action Plan**: Optionally generates a professional executive summary and action items using Claude (after local PII scrubbing).
- **NDA Compliance Layer**: Built-in automatic PII (Personally Identifiable Information) scrubber to protect entity names before any cloud analysis.
- **Mac-Native Experience**: One-click `.command` launcher for effortless operation.

---

## 🛠 Quick Start

1. **Setup**: Run `setup.sh` to initialize the environment and dependencies.
   ```bash
   ./setup.sh
   ```
2. **Drop Audio**: Put your `.mp3`, `.wav`, or `.m4a` files into the `/drop_here` folder.
3. **Run**: Double-click `Boardroom_Ear.command` (or run `python3 Boardroom_Ear.py`).
4. **Result**: Your transcript will appear in the `/transcripts` folder.

---

## ⚙️ Configuration (`config.yaml`)

- `model_size`: Choose from `tiny`, `base`, `small` (recommended for speed), `medium`, or `large-v3` (maximum accuracy).
- `anthropic_api_key`: Add your Claude API key to unlock the **Strategic Action Plan** feature.
- `auto_anonymize`: Set to `true` to ensure transcripts are scrubbed before being sent for AI analysis.

---

## 🔒 Security Guarantee
This tool is built on the philosophy of **"Edge Intelligence."** Your raw audio files are never uploaded. The optional "Strategic Action Plan" feature uses a local scrubbing layer to replace sensitive names/companies with placeholders (e.g., `[PERSON_REDACTED]`) before communicating with external LLMs.

---

## 🖋 Author
Developed for **diShine** by Kush.
