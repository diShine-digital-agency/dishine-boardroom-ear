# Using Boardroom Ear

This document covers day-to-day usage, CLI options, and configuration.

---

## Quick Start

1. Drop your audio file into `drop_here/`.
2. Launch:
   ```bash
   python3 Boardroom_Ear.py
   ```
3. Find your transcript in `transcripts/`.

---

## CLI Reference

```
python3 Boardroom_Ear.py [OPTIONS]
```

| Flag | Description | Default |
|------|-------------|---------|
| `--model` | Whisper model size: `tiny`, `base`, `small`, `medium`, `large`, `large-v2`, `large-v3` | `small` |
| `--device` | Compute device: `cpu`, `cuda`, `mps`, `auto` | `auto` |
| `--compute-type` | Precision: `int8`, `float16`, `float32`, `int8_float16` | `float32` |
| `--input FILE` | Process a specific audio file | — |
| `--input-dir DIR` | Scan a directory (use with `--batch`) | `drop_here/` |
| `--output-dir DIR` | Where to save transcripts | `transcripts/` |
| `--anonymization` | `none`, `basic` (token), `full` (blank) | `basic` |
| `--batch` | Process all audio files in the input directory | off |
| `--dry-run` | Validate setup without actually transcribing | off |
| `--no-plan` | Skip Strategic Action Plan even if an API key is set | off |
| `--log-level` | `DEBUG`, `INFO`, `WARNING`, `ERROR` | `INFO` |
| `--config FILE` | Path to a custom `config.yaml` | `config.yaml` |
| `--timeout SECONDS` | Max transcription time before aborting | `3600` |
| `--health-check` | Verify installation and exit | — |

---

## Workflow Examples

### Transcribe the latest file in drop_here/

```bash
python3 Boardroom_Ear.py
```

### Transcribe a specific file, skip the AI plan

```bash
python3 Boardroom_Ear.py --input recordings/board_q1.mp3 --no-plan
```

### Batch-process an entire folder

```bash
python3 Boardroom_Ear.py --batch --input-dir /Volumes/USB/recordings --output-dir ./transcripts
```

### Use the large-v3 model for maximum accuracy

```bash
python3 Boardroom_Ear.py --model large-v3 --device cpu --compute-type float32
```

### Full anonymisation (blank redaction instead of tokens)

```bash
python3 Boardroom_Ear.py --anonymization full
```

### Dry-run to validate without transcribing

```bash
python3 Boardroom_Ear.py --input meeting.mp3 --dry-run
```

---

## Configuration Guide (`config.yaml`)

The file is loaded on startup. CLI flags always override config file values.

```yaml
# Transcription
model_size: "small"       # tiny | base | small | medium | large | large-v3
device: "auto"            # cpu | cuda | mps | auto
compute_type: "float32"   # int8 | float16 | float32 | int8_float16

# Strategic Analysis
anthropic_api_key: ""     # Or set ANTHROPIC_API_KEY in .env
auto_anonymize: true

# Output
output_format: "markdown" # txt | markdown | both
output_dir: "transcripts"
drop_dir: "drop_here"
anonymization_level: "basic"  # none | basic | full

# Logging
log_level: "INFO"
log_file: ""              # leave blank for stdout only
audit_log: "transcripts/audit.log"

# Limits
timeout: 3600             # seconds
```

### Model Size vs. Speed Trade-off

| Model | VRAM | Speed (M2) | Accuracy |
|-------|------|-----------|----------|
| tiny  | ~1 GB | Very fast | ~85%    |
| base  | ~1 GB | Fast      | ~88%    |
| small | ~2 GB | Medium    | ~91%    |
| medium| ~5 GB | Slow      | ~94%    |
| large-v3 | ~10 GB | Very slow | ~97% |

For board meetings with multiple speakers, `small` or `medium` provide the best balance.

---

## Supported Audio Formats

`.mp3`, `.wav`, `.m4a`, `.mp4`, `.ogg`, `.flac`, `.aac`

For best accuracy: 16 kHz or higher sample rate, mono or stereo, minimal background noise.

---

## Output Files

After processing `drop_here/meeting.mp3`:

| File | Description |
|------|-------------|
| `transcripts/meeting_transcript.txt` | Raw transcript text |
| `transcripts/meeting_StrategicPlan.md` | AI-generated executive plan (if API key set) |
| `transcripts/audit.log` | PII redaction counts (no raw text) |
