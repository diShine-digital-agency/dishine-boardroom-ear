# Changelog

All notable changes to Boardroom Ear are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [1.3.0] — 2026-04-24

### Fixed

- **`--help` and `--health-check` worked only after the full dependency set was installed.** `core/__init__.py` and `analysis/__init__.py` eagerly re-exported the heavy classes, so importing either package forced `faster-whisper` (core) or `anthropic` (analysis) to load. `Boardroom_Ear.py` imported both at module level, meaning the diagnostic that is meant to run *before* install actually crashed at import time with `ModuleNotFoundError`. Both package `__init__.py` files are now empty, and the heavy imports in `Boardroom_Ear.py` are deferred to the call sites that need them. Running `--help` and `--health-check` now works on a fresh clone with only `rich`, `PyYAML`, and `python-dotenv` present — and the health check correctly reports which dependencies are still missing.
- **`pytest tests/` failed on a fresh clone** with `ModuleNotFoundError: No module named 'analysis'`, because there was no pytest configuration to add the repo root to `sys.path`. Added a `pyproject.toml` with `[tool.pytest.ini_options] pythonpath = ["."]`, so `pytest tests/` now works from the repo root without `PYTHONPATH=.` or an editable install.
- **Scrubber-only use required `anthropic`.** Importing `analysis.scrubber` pulled in `analysis/__init__.py`, which pulled in `strategic_planner`, which required the `anthropic` SDK even if the caller never touched the cloud path. The eager re-export has been removed; `from analysis.scrubber import PII_Scrubber` now works standalone.
- **`--health-check` crashed on Python 3.12+** with `module 'importlib' has no attribute 'util'`. The submodule is no longer auto-imported in modern Python; now imported explicitly as `importlib.util`.
- **Banner showed a hardcoded `v1.2`** and would have stayed on 1.2 forever regardless of release. Replaced with a `__version__` module constant that `pyproject.toml` and the banner both reference.

### Changed

- **`config.yaml` sample now matches the documented default.** The sample and the USAGE/GUIDE docs converge on `model_size: "small"`. The sample previously shipped `tiny`, which silently contradicted every doc that listed `small` as the default.
- **TROUBLESHOOTING — removed misleading PyTorch MPS advice.** Boardroom Ear runs on CTranslate2, not PyTorch, so `torch.backends.mps.is_available()` is irrelevant to whether transcription is hardware-accelerated. The Apple Silicon entry now explains what `device: auto` actually does and how to verify CPU-level acceleration.
- **README — softened the overclaim of "Metal/MPS" support.** CTranslate2 (the inference engine under faster-whisper) does not support Apple Metal / MPS; Apple Silicon performance comes from its optimised ARM NEON CPU kernels. The platform table and feature copy now reflect that accurately.
- **GUIDE — fixed heading hierarchy.** "Best Practices for Confidential Meetings" was nested as H3 under "Troubleshooting FAQs"; promoted to its own H2 section to match the Table of Contents.
- **README** — fixed three image alt-text typos ("Boardroam Ear" → "Boardroom Ear"), removed the empty-href Location badge, and added a Python version badge.
- **`RELEASE_NOTES.md` removed.** Duplicated CHANGELOG and inevitably drifted. CHANGELOG is now the single source of truth.
- **`--device mps` no longer advertised.** The CLI choice, the `VALID_DEVICES` set in `core/boardroom_ear.py`, and the device tables in USAGE.md, API.md, and TROUBLESHOOTING.md previously listed `mps` as an option. CTranslate2 has no Metal/MPS backend, so selecting it would have produced confusing runtime errors. `mps` is now removed from the accepted values and docs.
- **INFRASTRUCTURE.md** — rewritten to reflect the actual Apple Silicon path (ARM NEON CPU kernels, not GPU/MPS), cite the faster-whisper benchmarks rather than asserting unsourced performance numbers, and match the project's overall typography (em-dash separators, sentence-case headings).
- **Repo cleanup** — removed committed `__pycache__` artefacts, a 1-byte `Pictures/test` placeholder, and six unreferenced image files (three pre-revision screenshots and three unused `revised_` variants).

### Added

- `pyproject.toml` — version, pytest config (`pythonpath`, `testpaths`), and ruff line-length.
- **TROUBLESHOOTING** — new entries for the `pytest` import failure, running the scrubber without `anthropic`, and interpreting a pre-install `--health-check` report.
- **INSTALLATION** — "Running the tests" section explaining that `pyproject.toml` removes the `PYTHONPATH=.` requirement and that the 24-test scrubber suite runs without `faster-whisper` or `anthropic`.

## [1.2.0] — 2026-04-14

### Fixed
- **COMPANY regex false positives**: The PII scrubber's company-name pattern previously included a catch-all `[A-Z]{2,}` branch that matched any uppercase word of two or more letters (e.g. NDA, CEO, API, FBI). This corrupted transcripts by replacing common acronyms with `[COMPANY_REDACTED]`. The pattern now only matches names followed by a legal suffix (Inc., Corp., LLC, GmbH, etc.).

### Changed
- **README.md**: Removed duplicate paragraphs, tables, and section headings left over from the v1.0-to-v1.1 merge. Fixed "NDA-Complient" and "reffer" typos. Added a competitive analysis section comparing Boardroom Ear to cloud-based alternatives and other local tools.
- **GUIDE.md**: Replaced generic placeholder text (`<application-name>`, `[Model A]`) with concrete Boardroom Ear instructions, model recommendations, and scenario-specific guidance.
- **INFRASTRUCTURE.md**: Corrected the scrubber placeholder description from `<REDACTED>` to `[TYPE_REDACTED]` to match the actual code output.
- **SECURITY.md**: Removed stale "all-caps acronyms" reference from the company-name pattern description, reflecting the regex fix above.
- **RELEASE_NOTES.md**: Updated for v1.2.0.

### Added
- Three new unit tests covering company-name detection: suffix-based match, LLC match, and a false-positive guard for common acronyms (24 tests total).

---

## [1.1.0] — 2026-04-06

### Added
- **CLI arguments**: `--model`, `--device`, `--compute-type`, `--input`, `--input-dir`, `--output-dir`, `--anonymization`, `--batch`, `--dry-run`, `--no-plan`, `--log-level`, `--config`, `--timeout`
- **Batch processing mode**: Process an entire folder of audio files in one run (`--batch`)
- **Dry-run mode**: Validate setup and inputs without transcribing (`--dry-run`)
- **Health check**: `--health-check` flag prints a diagnostics summary
- **Auto-directory creation**: `drop_here/` and `transcripts/` are now created on startup if missing
- **Input validation**: Audio file existence, format, and size checks before starting transcription
- **Transcription timeout**: Configurable SIGALRM-based timeout protects against infinite hangs (`--timeout`)
- **Disk space check**: Warns when available space in the output directory drops below 100 MB
- **Comprehensive error handling**: Descriptive error messages for all failure modes with actionable guidance
- **`.env` support**: `python-dotenv` integration — all settings can be set via environment variables
- **Config validation on startup**: Invalid `model_size`, `device`, or `compute_type` values raise clear errors
- **Enhanced PII scrubber**: Added detection for URLs, IP addresses, dates (ISO 8601, written, US), and improved company/phone patterns
- **Redaction modes**: `token` (default), `blank`, and `hash` redaction modes in `PII_Scrubber`
- **Audit logging**: Sanitised redaction-count log written to `transcripts/audit.log` (configurable)
- **Structured application logging**: `logging.yaml` configuration with rotating file handler and console handler
- **`requirements.txt`**: Pinned dependency versions for reproducible installs
- **`requirements-dev.txt`**: Development dependencies (pytest, ruff)
- **`.env.example`**: Template for environment configuration
- **`logging.yaml`**: Logging configuration file
- **`analysis/__init__.py`** and **`core/__init__.py`**: Package init files
- **`tests/test_scrubber.py`**: Unit tests for the PII scrubber (28 tests)
- **`tests/sample_config.yaml`**: Reference configuration for CI and testing
- **Documentation**: `INSTALLATION.md`, `USAGE.md`, `TROUBLESHOOTING.md`, `API.md`, `SECURITY.md`
- **`setup.sh` improvements**: Python version check, Linux apt support, coloured output, directory creation, `.env` and `config.yaml` scaffolding

### Changed
- `core/boardroom_ear.py`: Rewrote with validation, error handling, logging, and timeout support
- `analysis/scrubber.py`: Complete rewrite with expanded patterns, redaction modes, and audit logging
- `analysis/strategic_planner.py`: Added input validation, structured logging, and configurable model/token parameters
- `Boardroom_Ear.py`: Replaced monolithic `main()` with modular CLI, config loader, and per-file processor
- `setup.sh`: Upgraded to full validation, cross-platform support, and verbose feedback
- `README.md`: Updated to reflect v1.1 features, accurate directory structure, and corrected typos

### Fixed
- `transcripts/` directory was not auto-created, causing `FileNotFoundError` on first run
- Strategic plan was saved without checking if `transcripts/` existed
- No error shown when audio file was missing or corrupted
- Scrubber silently accepted non-string input
- `StrategicPlanner` accepted empty transcripts, resulting in meaningless API calls
- Typo: "NDA-Complient" → "NDA-Compliant" in README

---

## [1.0.0] — 2026-01-15

### Added
- Initial release of diShine Boardroom Ear
- Local transcription via `faster-whisper` with Apple Silicon MPS support
- Basic PII scrubber (names, emails, phones, company names)
- Strategic Action Plan generation via Anthropic Claude 3.5 Sonnet
- `config.yaml` for model and API configuration
- `Boardroom_Ear.command` for one-click macOS launch
- `setup.sh` for dependency installation
- `GUIDE.md` for operational instructions
