# Changelog

All notable changes to Boardroom Ear are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

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
