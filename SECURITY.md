# Security & NDA Compliance

This document explains how Boardroom Ear protects confidential data and what guarantees it provides to users operating under NDAs or legal data-handling obligations.

---

## Architecture: Local-First

The tool is designed so that no audio or raw transcript text ever leaves your device unless you explicitly choose to generate a Strategic Action Plan.

```
┌───────────────────────────────────────────────────────────────┐
│                        Your Machine                           │
│                                                               │
│  Audio file → [Whisper / CTranslate2] → Raw Transcript        │
│                                              │                │
│                                    [PII Scrubber]             │
│                                              │                │
│                               Anonymised Transcript           │
│                                              │                │
│                       (ONLY this, opt-in) → [Anthropic API]   │
│                                              │                │
│                                    Strategic Plan (local)     │
└───────────────────────────────────────────────────────────────┘
```

The raw audio and raw transcript **never leave your machine**.

---

## Data Handling

| Data type | Where it lives | Sent externally? |
|-----------|---------------|-----------------|
| Raw audio | `drop_here/` (local) | Never |
| Raw transcript | `transcripts/` (local) | Never |
| Anonymised transcript | Memory only during API call | Only to Anthropic, only if you provide a key |
| Strategic Plan | `transcripts/` (local) | Never |
| Audit log | `transcripts/audit.log` | Never |

---

## PII Scrubber

Before any text is sent to an external API, the `PII_Scrubber` applies regex patterns to detect and replace:

| Entity type | Pattern approach |
|-------------|-----------------|
| Person names | Capitalised First Last / three-part names |
| Email addresses | RFC-5321 compliant regex |
| Phone numbers | International formats, US formats |
| IP addresses | IPv4 dotted-decimal |
| URLs | http, https, ftp, bare `www.` |
| Dates | ISO 8601, US slashes, written month names |
| Company names | Suffix-based (Inc., Corp., LLC, GmbH, etc.) |

### Redaction Modes

- **`basic` (default)**: Replaces with typed placeholders (`[EMAIL_REDACTED]`, `[PERSON_REDACTED]`, …). Easy to audit.
- **`full`**: Replaces with whitespace. No trace of the entity type in output.
- **`hash`**: Replaces with a deterministic SHA-256 prefix. The same entity always maps to the same token within one document, useful for cross-reference analysis without revealing the original value.

### Limitations

The scrubber uses regex patterns and does not perform NLP-based Named Entity Recognition (NER). It may miss:
- Unusual name formats (single names, non-Western names).
- Company names without common suffixes.
- Contextual references ("the CEO", "our partner").

For environments requiring certified anonymisation, consider running the output through an additional NER layer before external processing.

---

## Audit Trail

When `audit_log` is set in `config.yaml` (or `BOARDROOM_AUDIT_LOG` in `.env`), a sanitised log entry is written after every `PII_Scrubber.scrub()` call. The audit log contains **only counts**, never the original text.

Example entry:

```
[2024-01-15T09:45:12Z] PII scrub completed.
  EMAIL: 3 instance(s) redacted
  PERSON: 5 instance(s) redacted
  PHONE: 1 instance(s) redacted
```

The audit log is suitable for compliance reviews without exposing sensitive content.

---

## Anthropic API Usage

If Strategic Plan generation is enabled:

1. The transcript is anonymised locally first (see above).
2. Only the anonymised text is transmitted to Anthropic.
3. Anthropic's data handling is governed by their [Privacy Policy](https://www.anthropic.com/privacy) and [Usage Policy](https://www.anthropic.com/usage-policy).
4. Anthropic offers enterprise data agreements — consult [https://www.anthropic.com](https://www.anthropic.com) for details.

If your NDA prohibits sending any derivative content externally, use `--no-plan` to skip this step entirely.

---

## Secure Temp File Handling

- No temporary files are created during transcription. The Whisper engine processes audio in memory.
- Output files are written atomically. Partial writes are not left behind on failure.
- The `transcripts/` and `drop_here/` directories are excluded from git via `.gitignore`.

---

## Recommendations for High-Security Environments

1. **Air-gapped operation**: Download the Whisper model on a connected machine, then copy `~/.cache/huggingface/hub` to the offline device. Use `--no-plan` to avoid any outbound connections.
2. **Full anonymisation**: Use `--anonymization full` to strip all entity tokens from output.
3. **Encrypted storage**: Store `drop_here/` and `transcripts/` on an encrypted volume (macOS FileVault, VeraCrypt, LUKS).
4. **Secure deletion**: After processing, securely erase source audio with `srm` (macOS) or `shred` (Linux).
5. **Audit review**: Review `transcripts/audit.log` after each session to confirm redaction counts match expectations.

---

## Supported versions

| Version | Supported |
|---------|-----------|
| 1.3.x   | Yes       |
| 1.2.x   | Security fixes only |
| < 1.2   | No        |

---

## Reporting a vulnerability

If you find a security or privacy issue in Boardroom Ear, please report it responsibly.

**Do not open a public issue.** Instead, email [hello@dishine.it](mailto:hello@dishine.it) with:

- A description of the issue.
- Steps to reproduce.
- The impact you believe it has.

We will acknowledge receipt within 48 hours and aim to release a fix within 7 days for critical issues.
