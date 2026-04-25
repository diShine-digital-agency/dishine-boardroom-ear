# Installing Boardroom Ear

This guide covers installation on macOS (Apple Silicon and Intel) and Linux (x64). Windows is not officially supported.

---

## Requirements

| Dependency | Minimum version | Notes |
|------------|----------------|-------|
| Python     | 3.9             | 3.11 recommended |
| FFmpeg     | 4.x             | Required to decode audio |
| RAM        | 4 GB            | 8 GB recommended for `medium`/`large` models |
| Disk       | 2 GB free       | Model cache lives in `~/.cache/huggingface/hub` |

---

## macOS — Apple Silicon (M1 / M2 / M3 / M4)

### 1. Install Homebrew (if not already installed)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. Install Python and FFmpeg

```bash
brew install python ffmpeg
```

### 3. Clone and run setup

```bash
git clone https://github.com/diShine-digital-agency/dishine-boardroom-ear.git
cd dishine-boardroom-ear
chmod +x setup.sh
./setup.sh
```

The setup script will:
- Verify Python 3.9+
- Install FFmpeg if missing
- Create a `venv` virtual environment
- Install all Python dependencies from `requirements.txt`
- Create `drop_here/` and `transcripts/` directories
- Copy `.env.example` → `.env` and `tests/sample_config.yaml` → `config.yaml`

### 4. (Optional) Add your Anthropic API key

Open `.env` in a text editor and set:

```
ANTHROPIC_API_KEY=sk-ant-...
```

Leave it blank if you only need local transcription.

---

## macOS — Intel

The steps are identical to Apple Silicon. The tool falls back to CPU compute automatically. Set these values in `config.yaml` for best results on Intel:

```yaml
device: "cpu"
compute_type: "float32"
```

---

## Linux (Ubuntu / Debian)

### 1. Install Python and FFmpeg

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip ffmpeg
```

### 2. Clone and run setup

```bash
git clone https://github.com/diShine-digital-agency/dishine-boardroom-ear.git
cd dishine-boardroom-ear
chmod +x setup.sh
./setup.sh
```

---

## Air-Gapped / Offline Setup

If you need to run in an environment without internet access:

1. On a connected machine, run the tool once to trigger model download.
2. The model cache is stored in `~/.cache/huggingface/hub`.
3. Copy that directory to the offline machine and set the `HF_HOME` environment variable to point to it.

---

## Verifying the installation

```bash
python3 Boardroom_Ear.py --health-check
```

All checks should show ✔. See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) if any fail.

The health check and `--help` are deliberately kept independent of `faster-whisper` and `anthropic`, so you can run them *before* `./setup.sh` to see exactly what is missing.

---

## Running the tests

From the repository root, with the dev dependencies installed:

```bash
pip install -r requirements-dev.txt
pytest tests/
```

`pyproject.toml` adds the repo root to `sys.path`, so no editable install or `PYTHONPATH=.` is required. The scrubber suite (24 tests) does not depend on `faster-whisper` or `anthropic` and runs with just `pytest`, `pyyaml`, `python-dotenv`, and `rich`.
