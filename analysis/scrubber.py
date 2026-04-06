import re
import os
import logging
import datetime

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# PII / NDA Scrubber
# ---------------------------------------------------------------------------

# Patterns ordered so more-specific ones come first.
_PATTERNS = [
    # Emails — must come before URL so user@host doesn't get swallowed by URL
    ("EMAIL", r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"),
    # URLs  (http/https/ftp or bare www.)
    ("URL", r"https?://[^\s\"'>)]+|ftp://[^\s\"'>)]+|\bwww\.[^\s\"'>)]+"),
    # IPv4 addresses
    ("IP_ADDRESS", r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    # ISO / common date formats: 2024-01-15, 15/01/2024, January 15 2024, etc.
    # DATE must come before PHONE so numeric date-like strings are caught first.
    (
        "DATE",
        r"\b(?:\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}|\d{4}[\/\-\.]\d{1,2}[\/\-\.]\d{1,2}"
        r"|(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?"
        r"|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
        r"\.?\s+\d{1,2},?\s+\d{4})\b",
    ),
    # International phone numbers: +39 02 1234 5678, (555) 867-5309, etc.
    (
        "PHONE",
        r"\b(?:\+?\d{1,3}[\s\-.])?(?:\(\d{1,4}\)[\s\-.]?)?\d{2,5}[\s\-.]\d{2,5}(?:[\s\-.]\d{1,5})?\b",
    ),
    # Company suffixes: "Acme Corp.", "XYZ Inc", "Holdings LLC", "BIGCO" (all-caps ≥2 chars)
    (
        "COMPANY",
        r"\b(?:[A-Z][A-Za-z0-9&\s]{1,40}?\s+(?:Inc\.?|Corp\.?|Ltd\.?|LLC|LLP|GmbH|S\.A\.|S\.p\.A\.|SRL|AG)|[A-Z]{2,})\b",
    ),
    # Person names: First Last (both capitalised, not all-caps acronym)
    ("PERSON", r"\b([A-Z][a-z]{1,20}\s+[A-Z][a-z]{1,20}(?:\s+[A-Z][a-z]{1,20})?)\b"),
]

_PLACEHOLDERS = {
    "EMAIL": "[EMAIL_REDACTED]",
    "URL": "[URL_REDACTED]",
    "IP_ADDRESS": "[IP_REDACTED]",
    "PHONE": "[PHONE_REDACTED]",
    "DATE": "[DATE_REDACTED]",
    "COMPANY": "[COMPANY_REDACTED]",
    "PERSON": "[PERSON_REDACTED]",
}

_COMPILED = [(label, re.compile(pattern), _PLACEHOLDERS[label]) for label, pattern in _PATTERNS]


class PII_Scrubber:
    """Regex-based PII scrubber for NDA-compliant transcript anonymisation.

    Supported entity types: PERSON, EMAIL, PHONE, IP_ADDRESS, URL, DATE, COMPANY.

    Parameters
    ----------
    audit_log_path : str or None
        If provided, a sanitised audit log entry (counts only, no raw text) is
        appended to this file after each :meth:`scrub` call.
    redaction_mode : str
        ``"token"``  – replace with ``[TYPE_REDACTED]`` placeholder (default).
        ``"blank"``  – replace with an empty string.
        ``"hash"``   – replace with a deterministic SHA-256 hex prefix so the
                       same entity maps to the same token within one document.
    """

    def __init__(self, audit_log_path=None, redaction_mode="token"):
        if redaction_mode not in ("token", "blank", "hash"):
            raise ValueError(
                f"Invalid redaction_mode '{redaction_mode}'. Use 'token', 'blank', or 'hash'."
            )
        self.audit_log_path = audit_log_path
        self.redaction_mode = redaction_mode
        self._patterns = _COMPILED

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def scrub(self, text: str) -> str:
        """Return *text* with all detected PII replaced according to *redaction_mode*.

        Parameters
        ----------
        text : str
            Raw transcript text.

        Returns
        -------
        str
            Anonymised transcript text.
        """
        if not isinstance(text, str):
            raise TypeError(f"Expected str, got {type(text).__name__}.")

        scrubbed = text
        counts: dict[str, int] = {}

        for label, compiled, placeholder in self._patterns:
            if self.redaction_mode == "blank":
                replacement = " "
            elif self.redaction_mode == "hash":
                import hashlib

                def _hash_replace(m, _lbl=label):
                    digest = hashlib.sha256(m.group(0).encode()).hexdigest()[:8]
                    return f"[{_lbl}_{digest}]"

                new_text, n = compiled.subn(_hash_replace, scrubbed)
            else:
                replacement = placeholder

            if self.redaction_mode != "hash":
                new_text, n = compiled.subn(replacement, scrubbed)

            counts[label] = counts.get(label, 0) + n
            scrubbed = new_text

        if self.audit_log_path and any(counts.values()):
            self._write_audit_entry(counts)

        total = sum(counts.values())
        logger.debug("Scrubbed %d PII entities: %s", total, counts)

        return scrubbed

    # ------------------------------------------------------------------
    # Audit logging (counts only – no raw PII)
    # ------------------------------------------------------------------

    def _write_audit_entry(self, counts: dict):
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
        lines = [f"[{timestamp}] PII scrub completed."]
        for label, count in sorted(counts.items()):
            if count:
                lines.append(f"  {label}: {count} instance(s) redacted")
        lines.append("")

        try:
            log_dir = os.path.dirname(self.audit_log_path)
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)
            with open(self.audit_log_path, "a", encoding="utf-8") as fh:
                fh.write("\n".join(lines) + "\n")
            logger.debug("Audit entry written to %s", self.audit_log_path)
        except OSError as exc:
            logger.warning("Could not write audit log to '%s': %s", self.audit_log_path, exc)


if __name__ == "__main__":
    _SAMPLE = (
        "John Smith from Acme Corp discussed the merger on January 15, 2024. "
        "Contact him at john.smith@acme.com or +1 (555) 867-5309. "
        "The deal dashboard lives at https://portal.acme.com/deal/42. "
        "Internal server: 192.168.1.100. Founded by Jane Doe in 2009."
    )
    scrubber = PII_Scrubber(audit_log_path="/tmp/boardroom_audit.log")
    print("Original :", _SAMPLE)
    print("Scrubbed :", scrubber.scrub(_SAMPLE))
