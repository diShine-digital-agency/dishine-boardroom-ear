# Release Notes — v1.2.0

Released 2026-04-14.

## Bug fix

- **Company-name regex false positives** — The PII scrubber's COMPANY pattern included a catch-all `[A-Z]{2,}` branch that treated any uppercase word (NDA, CEO, API, FBI, …) as a company name, replacing it with `[COMPANY_REDACTED]`. This corrupted transcripts with false redactions. The pattern now matches company names only when followed by a legal suffix (Inc., Corp., LLC, GmbH, etc.). Three new tests guard against regression.

## Documentation overhaul

- **README** — Removed duplicate content left over from the v1.0→v1.1 merge (paragraphs, tables, and headings were stacked twice). Fixed "NDA-Complient" and "reffer" typos. Added a competitive analysis section with a factual comparison to Otter.ai, Fireflies.ai, whisper.cpp, and MacWhisper.
- **GUIDE** — Replaced generic placeholder text with concrete model recommendations, scenario-specific guidance (board meetings, M&A, legal depositions), and working CLI examples.
- **INFRASTRUCTURE** — Corrected the scrubber placeholder description to match the actual `[TYPE_REDACTED]` output format.
- **SECURITY** — Removed stale "all-caps acronyms" reference from the company-name detection description.
- **CHANGELOG** — Added a complete v1.2.0 entry following Keep a Changelog format.