# Boardroom Ear - Operational Guide 🕵️‍♂️
**Strategic Local Stranscription Solution**

This guide provides deep operational instructions for using `Boardroom Ear` effectively in high-stakes environments.

---

## 🛠 Prerequisites

- **Python 3.9+**: Ideally installed via Homebrew.
- **FFmpeg**: Required to decode audio files. `setup.sh` will auto-install it via Homebrew (`brew install ffmpeg`) on macOS.
- **RAM**: Large Whisper models (like `medium` or `large-v3`) require at least 8GB of free RAM. For standard laptops, we recommend the `small` or `base` models for efficiency.

---

## 🧭 Operational Workflow

### 1. Air-Gapped Session Preparation
If you plan to use `Boardroom Ear` in a strictly air-gapped environment (no Wi-Fi), you must cache the models first.
1. Run a test transcription on a 5-second audio file while connected to Wi-Fi.
2. The core Whisper model will download to `~/.cache/huggingface/hub` (standard path).
3. Once downloaded, you can disconnect your internet and perform full board-level transcriptions entirely offline.

### 2. High-Confidentiality Audio Handling
1. **Source**: For maximum quality, use a high-fidelity omnidirectional mic in the center of the table.
2. **Format**: Use `.mp3` (128kbps+) or `.wav` for the best balance of size and quality.
3. **Location**: Drop the file into `/drop_here`.

### 3. Executing the Strategic Plan
To convert raw text into a consultant's executive summary:
- Add your `anthropic_api_key` to `config.yaml`.
- Ensure `auto_anonymize` is set to `true` (it is by default).
- The system will scrub the transcript locally before sending a sanitized version to Claude-3.5-Sonnet.

---

## 🏗 Directory Deep-Dive

- `/core`: Contains the `faster-whisper` integration and model loaders.
- `/analysis`: Contains the `PII-Scrubber` (regex-based) and the `StrategicPlanner` (Claude integration).
- `/drop_here`: Input folder for raw recordings.
- `/transcripts`: Output folder for final TXT and Markdown reports.

---

## 🏎 Performance Tuning (`config.yaml`)

- **Max Quality**: Use `model_size: "large-v3"`. Best for multi-speaker boardroom settings.
- **Max Efficiency**: Use `model_size: "small"`. Fast, accurate (~90%), and low RAM footprint.
- **Auto-Device**: On Mac, set `device: "auto"`. It will automatically attempt to use `MPS` (Metal Performance Shaders) if available.

---

## 🏁 Author
**Kevin Escoda @ diShine**
*Strategic Local Transcriber Tool v1.0*
