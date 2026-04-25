# API Reference

This document describes the public Python API for developers who want to integrate Boardroom Ear into their own scripts or pipelines.

---

## `core.boardroom_ear.BoardroomEar`

The transcription engine wrapping `faster-whisper`.

```python
from core.boardroom_ear import BoardroomEar
```

### Constructor

```python
BoardroomEar(
    model_size: str = "base",
    device: str = "cpu",
    compute_type: str = "int8",
    timeout: int = 3600
)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `model_size` | `str` | Whisper model: `tiny`, `base`, `small`, `medium`, `large`, `large-v2`, `large-v3` |
| `device` | `str` | Compute device: `cpu`, `cuda`, `auto` (no `mps` — CTranslate2 runs on CPU on Apple Silicon) |
| `compute_type` | `str` | Precision: `int8`, `float16`, `float32`, `int8_float16` |
| `timeout` | `int` | Max transcription seconds before `TranscriptionTimeoutError` is raised |

**Raises:** `ValueError` for invalid parameter values.

### `load_model()`

```python
ear.load_model() -> None
```

Explicitly loads the Whisper model into memory. Called automatically by `transcribe()` if not already loaded.

**Raises:** `RuntimeError` if the model cannot be loaded.

### `transcribe()`

```python
ear.transcribe(
    audio_path: str,
    output_dir: str = "transcripts",
    dry_run: bool = False
) -> str
```

Transcribes *audio_path* and saves the result to *output_dir*.

| Parameter | Type | Description |
|-----------|------|-------------|
| `audio_path` | `str` | Path to the audio file |
| `output_dir` | `str` | Directory where the `.txt` transcript will be saved |
| `dry_run` | `bool` | If `True`, validates inputs but skips actual transcription |

**Returns:** `str` — full transcript text (empty string in dry-run mode).

**Raises:**
- `FileNotFoundError` — audio file not found
- `ValueError` — unsupported format or empty/corrupted file
- `OSError` — cannot create output directory or save transcript
- `RuntimeError` — transcription engine failure
- `TranscriptionTimeoutError` — timeout exceeded (Unix only)

### Example

```python
ear = BoardroomEar(model_size="small", device="auto", compute_type="float32")
transcript = ear.transcribe("drop_here/meeting.mp3", output_dir="transcripts")
print(transcript[:200])
```

---

## `analysis.scrubber.PII_Scrubber`

Regex-based PII scrubber for NDA-compliant anonymisation.

```python
from analysis.scrubber import PII_Scrubber
```

### Constructor

```python
PII_Scrubber(
    audit_log_path: str | None = None,
    redaction_mode: str = "token"
)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `audit_log_path` | `str \| None` | If set, appends a sanitised audit entry (entity counts only) to this file after each scrub |
| `redaction_mode` | `str` | `"token"` — replace with `[TYPE_REDACTED]` (default); `"blank"` — replace with space; `"hash"` — deterministic per-entity hash token |

**Raises:** `ValueError` for invalid `redaction_mode`.

### `scrub()`

```python
scrubber.scrub(text: str) -> str
```

Returns *text* with all detected PII replaced according to *redaction_mode*.

**Detected entity types:** `PERSON`, `EMAIL`, `PHONE`, `IP_ADDRESS`, `URL`, `DATE`, `COMPANY`

**Raises:** `TypeError` if *text* is not a string.

### Example

```python
scrubber = PII_Scrubber(audit_log_path="transcripts/audit.log", redaction_mode="token")
clean = scrubber.scrub("John Smith — john@acme.com — +1 555-867-5309")
# clean → "[PERSON_REDACTED] — [EMAIL_REDACTED] — [PHONE_REDACTED]"
```

---

## `analysis.strategic_planner.StrategicPlanner`

Generates a structured executive action plan from an anonymised transcript via the Anthropic API.

```python
from analysis.strategic_planner import StrategicPlanner
```

### Constructor

```python
StrategicPlanner(
    api_key: str | None = None,
    model: str = "claude-3-5-sonnet-20241022",
    max_tokens: int = 2048
)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `api_key` | `str \| None` | Anthropic API key. Falls back to `ANTHROPIC_API_KEY` env var |
| `model` | `str` | Claude model identifier |
| `max_tokens` | `int` | Maximum tokens in the generated plan |

### `generate_plan()`

```python
planner.generate_plan(transcript_text: str) -> str | None
```

Calls the Claude API and returns a Markdown-formatted strategic action plan.

**Returns:** `str` with the plan, or `None` if the API key is missing or the call fails.

### Example

```python
planner = StrategicPlanner()  # reads ANTHROPIC_API_KEY from environment
plan = planner.generate_plan(anonymised_transcript)
if plan:
    with open("transcripts/plan.md", "w") as f:
        f.write(plan)
```

---

## Complete Pipeline Example

```python
import os
from core.boardroom_ear import BoardroomEar
from analysis.scrubber import PII_Scrubber
from analysis.strategic_planner import StrategicPlanner

# 1. Transcribe
ear = BoardroomEar(model_size="small", device="auto", compute_type="float32")
transcript = ear.transcribe("drop_here/board_session.mp3")

# 2. Anonymise
scrubber = PII_Scrubber(audit_log_path="transcripts/audit.log")
clean_transcript = scrubber.scrub(transcript)

# 3. Generate plan
planner = StrategicPlanner()
plan = planner.generate_plan(clean_transcript)

if plan:
    with open("transcripts/board_session_StrategicPlan.md", "w") as f:
        f.write(f"# Strategic Action Plan\n\n{plan}")
    print("Plan saved.")
```
