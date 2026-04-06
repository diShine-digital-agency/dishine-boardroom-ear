# Troubleshooting

Quick solutions to the most common issues.

---

## Installation Issues

### `command not found: python3`
Python is not installed or not in your `PATH`.
- **macOS**: `brew install python`
- **Ubuntu/Debian**: `sudo apt install python3`

### `Error: Python 3.9+ required`
Your default `python3` is too old.
```bash
python3 --version          # check current version
brew install python        # macOS: installs latest Python 3
```

### `command not found: ffmpeg`
FFmpeg is missing. The setup script attempts to install it automatically. If it fails:
- **macOS**: `brew install ffmpeg`
- **Ubuntu**: `sudo apt install ffmpeg`
- **Manual**: https://ffmpeg.org/download.html

### `pip install` fails with SSL errors
Your system certificates may be outdated.
```bash
pip install --upgrade certifi
```

---

## Transcription Issues

### `FileNotFoundError: Audio file not found`
The file path is wrong. Check that:
- The file is in `drop_here/` (or that you passed the correct `--input` path).
- There are no typos in the filename.

### `Audio file appears corrupted`
The file is too small or unreadable. Re-export or re-download the audio file.

### `Transcription failed — unsupported codec`
FFmpeg cannot decode the file. Convert it first:
```bash
ffmpeg -i input.mkv -ar 16000 -ac 1 -c:a pcm_s16le output.wav
```

### `TranscriptionTimeoutError`
The audio is too long for the configured timeout.
- Increase `timeout` in `config.yaml` (seconds).
- Use a smaller model: `--model tiny` or `--model base`.
- Split the audio into smaller chunks.

### `RuntimeError: Failed to load Whisper model`
The model cannot be loaded. Common causes:
1. **Not enough RAM**: Use a smaller model (`tiny`, `base`).
2. **First run needs internet**: The model downloads on first use (~500 MB for `small`). Ensure you have a working internet connection.
3. **Corrupt cache**: Delete and redownload: `rm -rf ~/.cache/huggingface/hub`.

### Progress bar gets stuck at 0%
The audio may have a very long silence at the start. This is normal — Whisper skips silent segments. The transcript will contain everything that was spoken.

---

## Strategic Plan Issues

### `Warning: Anthropic API key not set`
Either:
- Add `ANTHROPIC_API_KEY=sk-ant-...` to your `.env` file.
- Or pass it interactively when prompted.
- Or use `--no-plan` to skip this step entirely.

### `Error calling Anthropic API: AuthenticationError`
Your API key is invalid or expired. Generate a new one at https://console.anthropic.com/.

### `Error calling Anthropic API: RateLimitError`
You've hit your Anthropic rate limit. Wait a minute and try again, or upgrade your Anthropic plan.

---

## Output Issues

### `OSError: Cannot create output directory`
The output path is on a read-only volume or you lack write permissions.
```bash
ls -la transcripts/   # check permissions
chmod 755 transcripts/
```

### `Low disk space warning`
Free up space on the disk where `transcripts/` is stored. The tool will still attempt to save files but may fail.

---

## macOS-Specific

### `venv/bin/activate: Permission denied`
```bash
chmod +x venv/bin/activate
```

### `Boardroom_Ear.command` not opening (security warning)
macOS Gatekeeper may block the script on first run:
```bash
xattr -d com.apple.quarantine Boardroom_Ear.command
```

### MPS (Metal) not being used on Apple Silicon
Check that `device: "auto"` is set in `config.yaml`. If Metal is still not used:
```bash
python3 -c "import torch; print(torch.backends.mps.is_available())"
```
If this prints `False`, update PyTorch: `pip install --upgrade torch`.

---

## Still stuck?

Run the health check first:
```bash
python3 Boardroom_Ear.py --health-check
```

Enable debug logging for more detail:
```bash
python3 Boardroom_Ear.py --log-level DEBUG --input your_file.mp3
```

Open an issue at [github.com/diShine-digital-agency/dishine-boardroom-ear](https://github.com/diShine-digital-agency/dishine-boardroom-ear) with the debug output.
