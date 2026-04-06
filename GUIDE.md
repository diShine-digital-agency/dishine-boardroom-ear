# diShine Boardroom Ear - Operational Guide 🕵️‍♂️
**Strategic Local Intelligence Platform**

This guide provides deep technical and operational instructions for using the `Boardroom Ear` effectively in high-stakes environments.

---

## 🛠 Prerequisites

- **Python 3.9+**: Ideally installed via Homebrew or directly from Python.org.
- **FFmpeg**: Required to decode audio files. `setup.sh` will try to install it via Homebrew (`brew install ffmpeg`).
- **RAM**: Large Whisper models (like `medium` or `large-v3`) require at least 8GB of free RAM. For standard laptops, we recommend the `small` or `base` models for efficiency.

---

## 🧭 Operational Workflow

### 1. Preparation
Ensure your Mac has the necessary models downloaded before an "Air-Gapped" session. You can do this by running a test transcription on any short audio file while connected to the internet. Whisper models will be cached locally in `~/.cache/whisper`.

### 2. High-Confidentiality Sessions
If you work in a boardroom, you can disconnect your Wi-Fi entirely. The core transcription logic (`Boardroom_Ear.py`) will function without any external network dependency.

### 3. The "Strategic Action Plan" (Optional)
If you wish to convert your transcript into a structured consultant's report:
- Ensure `anthropic_api_key` is set in `config.yaml`.
- The system will automatically **Scrub (Anonymize)** the transcript. 
- It replaces entities like names and company titles with placeholders: `[PERSON_REDACTED]`, `[COMPANY_REDACTED]`.
- This scrubbed text is sent to Claude-3.5-Sonnet for high-level strategic reasoning.

---

## 🏗 Directory Structure

- `/core`: Transcription engine wrapper for CTranslate2.
- `/analysis`: NDA-compliance layer (scrubber) and AI Planner (Claude integration).
- `/drop_here`: Place your audio recordings here.
- `/transcripts`: Final text and markdown reports are saved here.
- `/models`: Local model cache (optional, default is ~/.cache).

---

## 🏎 Performance Tuning (`config.yaml`)

- **Max Speed**: `model_size: "tiny"` + `compute_type: "float32"`.
- **Max Accuracy**: `model_size: "large-v3"` + `compute_type: "float32"`.
- **The "diShine Sweet Spot"**: `model_size: "small"` balance of ~90% accuracy with instantaneous local response.

---

## ❓ Troubleshooting

- **"No audio files found"**: Ensure your recording is in `/drop_here` and has a valid extension (.mp3, .wav, .m4a, .mp4).
- **"ffmpeg not found"**: Manual install: `brew install ffmpeg`.
- **"Model load failed"**: This usually means you ran out of RAM. Try a smaller model (`base` or `tiny`) in `config.yaml`.

---

## 🏁 Author
**Kush @ diShine**
*Strategic Local Transcriber Tool v1.0*
