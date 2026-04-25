# diShine Boardroom Ear — Technical Infrastructure

Boardroom Ear is built on a privacy-first (edge) architecture. It uses optimised transformer implementations to run resource-heavy AI workloads locally on consumer hardware (MacBooks, Linux laptops).

---

## Technology stack

- **Core engine**: [faster-whisper](https://github.com/SYSTRAN/faster-whisper)
- **Runtime**: [CTranslate2](https://github.com/OpenNMT/CTranslate2) (C++ inference engine)
- **Quantisation**: INT8 / float16 / float32 (CPU-optimised)
- **Strategic AI**: Anthropic Claude 3.5 Sonnet (optional, opt-in)
- **NDA layer**: regex-based PII scrubber (fully local)
- **Language**: Python 3.9+

---

## Inference architecture: `faster-whisper`

Standard OpenAI Whisper is memory-intensive and slow on CPUs. Boardroom Ear uses `faster-whisper`, a re-implementation of Whisper built on CTranslate2.

### Benefits (as reported by the faster-whisper README)
- Roughly **4× faster** than the reference `openai/whisper` implementation at equivalent accuracy.
- Roughly **2× lower memory footprint** at the same model size, thanks to CTranslate2's memory-efficient inference and INT8 quantisation.
- **Quantisation support**: `int8`, `int8_float16`, `float16`, `float32` — allows large-v3-quality transcription on CPU-only laptops.

Numbers vary by hardware, model, and audio length. See the [faster-whisper benchmarks](https://github.com/SYSTRAN/faster-whisper#benchmark) for the source figures.

---

## Security & privacy workflow

The design is focused on data sovereignty.

1. **Local transcription loop**
   Audio → `faster-whisper` (in memory) → text.
   Audio files are never written to temporary cloud storage.

2. **The scrubber (anonymiser)**
   A dedicated Python module (`analysis/scrubber.py`) parses the raw transcript. It uses regex patterns for seven entity types (person, email, phone, IP, URL, date, company) to replace sensitive data with `[TYPE_REDACTED]` placeholders, whitespace, or hash tokens depending on the selected redaction mode.

3. **Strategic export**
   Only the anonymised text is passed to the `StrategicPlanner` module. Even if the Anthropic API were compromised, the transmitted data would be contextually useful but individually unidentifiable.

---

## Hardware acceleration

### Apple Silicon (M1–M4)
CTranslate2 **does not use Apple Metal / MPS**. On Apple Silicon, transcription runs on the CPU, and speed comes from CTranslate2's highly optimised ARM NEON kernels combined with INT8 quantisation. In practice this delivers real-time or faster-than-real-time transcription for the `small` and `medium` models on an M-series chip with no GPU involvement.

Verify acceleration is active by checking the startup banner — it prints the resolved `device` and `compute_type`. On Apple Silicon you should see `device=cpu` with a quantised `compute_type` (e.g. `int8` or `int8_float16`).

### Intel Macs and Linux x64
CTranslate2 uses OpenMP to parallelise across all available CPU cores. On Linux with a CUDA-capable GPU, set `device: cuda` to offload inference to the GPU.

---

## Project files

- `Boardroom_Ear.py` — CLI controller and config orchestrator.
- `core/boardroom_ear.py` — Whisper model manager.
- `analysis/scrubber.py` — PII regex engine.
- `analysis/strategic_planner.py` — Anthropic API client.
- `core/__init__.py`, `analysis/__init__.py` — intentionally empty so that `--help` and `--health-check` run before heavy dependencies are installed.

---

## Author

Developed by [diShine](https://dishine.it) — Milan, IT.
Kevin Escoda.
