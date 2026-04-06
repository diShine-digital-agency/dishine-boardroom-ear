# diShine Boardroom Ear - Technical Infrastructure

`Boardroom Ear` is built with a "Privacy-First" (Edge) architecture. It leverages optimized transformer implementations to run resource-heavy AI workloads locally on consumer hardware (MacBooks).

---

## 🏗 Technology Stack

- **Core Engine**: [faster-whisper](https://github.com/guillaumekln/faster-whisper)
- **Runtime**: CTranslate2 (C++ Inference Engine)
- **Quantization**: INT8 / Float32 (optimized for CPU/Metal)
- **Strategic AI**: Anthropic Claude-3.5-Sonnet (via API)
- **NDA Layer**: Regex-based PII Scrubber (Local)
- **Language**: Python 3.9+ 

---

## ⚡ Inference Architecture: `faster-whisper`

Standard OpenAI Whisper is memory-intensive and slow on CPUs. `Boardroom Ear` uses `faster-whisper`, a re-implementation of Whisper using [CTranslate2](https://github.com/OpenNMT/CTranslate2).

### Key Benefits:
- **Up to 4x Speedup**: Compared to the standard Whisper implementation.
- **Lower Memory Footprint**: Uses 2x less RAM for the same model accuracy.
- **Quantization Support**: Runs `int8` weights, allowing high-quality transcription on laptops without high-end GPUs.

---

## 🔒 Security & Privacy Workflow

The design is focused on **"Data Sovereignty."**

1. **Local Transcription Loop**:
   Audio -> `faster-whisper` (In-Memory) -> Text.
   *Encryption note: Audio files are never written to temporary cloud storage.*

2. **The Scrubber (Anonymizer)**:
   A dedicated Python layer (`analysis/scrubber.py`) parses the raw transcript.
   *It uses hard-coded regex patterns and entity recognition candidates (Names, Emails, Company Suffixes) to replace sensitive data with `<REDACTED>` placeholders.*

3. **Strategic Export**:
   ONLY the anonymized text is passed to the `StrategicPlanner` module.
   *This ensures that even if the Claude API is compromised, the data sent is contextually useful but individually unidentifiable.*

---

## 🏎 Hardware Optimization

On Apple Silicon (M1/M2/M3/M4):
- The tool defaults to using **MPS (Metal Performance Shaders)** if the backend supports it, offloading computation to the Mac's GPU.
- For Intel-based Macs, it uses **OpenMP** to parallelize across all available CPU cores.

---

## 🛠 Project Files

- `Boardroom_Ear.py`: CLI controller and config orchestrator.
- `core/boardroom_ear.py`: Whisper Model manager.
- `analysis/scrubber.py`: PII regex engine.
- `analysis/strategic_planner.py`: Anthropic API client.

---

## 🏁 Author
**Developed by diShine (Milan, IT)**
*Kevin Escoda*
