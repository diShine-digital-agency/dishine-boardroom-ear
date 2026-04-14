"""Tests for analysis.scrubber.PII_Scrubber."""

import pytest
from analysis.scrubber import PII_Scrubber


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def scrubber():
    return PII_Scrubber()


@pytest.fixture
def blank_scrubber():
    return PII_Scrubber(redaction_mode="blank")


@pytest.fixture
def hash_scrubber():
    return PII_Scrubber(redaction_mode="hash")


# ---------------------------------------------------------------------------
# Email detection
# ---------------------------------------------------------------------------

class TestEmailScrubbing:
    def test_basic_email(self, scrubber):
        result = scrubber.scrub("Contact us at hello@example.com today.")
        assert "hello@example.com" not in result
        assert "[EMAIL_REDACTED]" in result

    def test_email_with_plus(self, scrubber):
        result = scrubber.scrub("Send to user+tag@domain.co.uk")
        assert "user+tag@domain.co.uk" not in result

    def test_no_false_positive_for_plain_text(self, scrubber):
        result = scrubber.scrub("This is a normal sentence.")
        assert result == "This is a normal sentence."


# ---------------------------------------------------------------------------
# Phone detection
# ---------------------------------------------------------------------------

class TestPhoneScrubbing:
    def test_us_phone_dashes(self, scrubber):
        result = scrubber.scrub("Call 555-867-5309 for details.")
        assert "555-867-5309" not in result

    def test_international_phone(self, scrubber):
        result = scrubber.scrub("Reach us at +39 02 1234 5678.")
        assert "+39 02 1234 5678" not in result


# ---------------------------------------------------------------------------
# IP address detection
# ---------------------------------------------------------------------------

class TestIPScrubbing:
    def test_ipv4(self, scrubber):
        result = scrubber.scrub("Server is at 192.168.1.100.")
        assert "192.168.1.100" not in result
        assert "[IP_REDACTED]" in result


# ---------------------------------------------------------------------------
# URL detection
# ---------------------------------------------------------------------------

class TestURLScrubbing:
    def test_https_url(self, scrubber):
        result = scrubber.scrub("Visit https://portal.acme.com/dashboard for more.")
        assert "https://portal.acme.com/dashboard" not in result
        assert "[URL_REDACTED]" in result

    def test_bare_www(self, scrubber):
        result = scrubber.scrub("Go to www.acme.com for info.")
        assert "www.acme.com" not in result


# ---------------------------------------------------------------------------
# Date detection
# ---------------------------------------------------------------------------

class TestDateScrubbing:
    def test_iso_date(self, scrubber):
        result = scrubber.scrub("The meeting is on 2024-01-15.")
        assert "2024-01-15" not in result
        assert "[DATE_REDACTED]" in result

    def test_us_date_slash(self, scrubber):
        result = scrubber.scrub("Deadline: 01/15/2024.")
        assert "01/15/2024" not in result

    def test_written_date(self, scrubber):
        result = scrubber.scrub("Join us January 15, 2024 in Milan.")
        assert "January 15, 2024" not in result


# ---------------------------------------------------------------------------
# Person name detection
# ---------------------------------------------------------------------------

class TestPersonScrubbing:
    def test_first_last(self, scrubber):
        result = scrubber.scrub("John Smith will lead the meeting.")
        assert "John Smith" not in result
        assert "[PERSON_REDACTED]" in result

    def test_three_part_name(self, scrubber):
        result = scrubber.scrub("Brief prepared by Anna Maria Rossi.")
        assert "Anna Maria Rossi" not in result


# ---------------------------------------------------------------------------
# Redaction modes
# ---------------------------------------------------------------------------

class TestRedactionModes:
    def test_blank_mode(self, blank_scrubber):
        result = blank_scrubber.scrub("Email john@example.com for info.")
        assert "john@example.com" not in result
        assert "[EMAIL_REDACTED]" not in result

    def test_hash_mode_consistent(self, hash_scrubber):
        text = "Email john@example.com twice: john@example.com"
        result = hash_scrubber.scrub(text)
        # The same address should produce the same hash token
        parts = [w for w in result.split() if w.startswith("[EMAIL_")]
        assert len(parts) == 2
        assert parts[0] == parts[1]

    def test_invalid_mode(self):
        with pytest.raises(ValueError, match="Invalid redaction_mode"):
            PII_Scrubber(redaction_mode="unknown")


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------

class TestInputValidation:
    def test_non_string_raises(self, scrubber):
        with pytest.raises(TypeError):
            scrubber.scrub(12345)

    def test_empty_string(self, scrubber):
        assert scrubber.scrub("") == ""


# ---------------------------------------------------------------------------
# Audit log
# ---------------------------------------------------------------------------

class TestAuditLog:
    def test_audit_log_written(self, tmp_path):
        log_file = str(tmp_path / "audit.log")
        s = PII_Scrubber(audit_log_path=log_file)
        s.scrub("Contact john.doe@acme.com or 192.168.0.1 for info.")
        assert (tmp_path / "audit.log").exists()
        content = (tmp_path / "audit.log").read_text()
        assert "EMAIL" in content
        assert "IP_ADDRESS" in content

    def test_no_audit_log_for_clean_text(self, tmp_path):
        log_file = str(tmp_path / "audit.log")
        s = PII_Scrubber(audit_log_path=log_file)
        s.scrub("this sentence has no personal information in it.")
        # No audit file should be created when nothing is redacted
        assert not (tmp_path / "audit.log").exists()


# ---------------------------------------------------------------------------
# Combined real-world sample
# ---------------------------------------------------------------------------

class TestCompanyScrubbing:
    def test_company_with_corp_suffix(self, scrubber):
        result = scrubber.scrub("Acme Corp signed the deal.")
        assert "Acme Corp" not in result
        assert "[COMPANY_REDACTED]" in result

    def test_company_with_llc_suffix(self, scrubber):
        result = scrubber.scrub("Contact Holdings LLC for info.")
        assert "Holdings LLC" not in result

    def test_no_false_positive_for_common_acronyms(self, scrubber):
        """Common all-caps words must NOT be treated as company names."""
        phrases = [
            "The NDA protects all parties involved.",
            "The CEO announced new strategy.",
            "PII data must be scrubbed.",
            "ONLY scrubbed text is sent to the API.",
            "This is NOT acceptable.",
        ]
        for phrase in phrases:
            result = scrubber.scrub(phrase)
            assert "[COMPANY_REDACTED]" not in result, (
                f"False positive: '{phrase}' became '{result}'"
            )


class TestRealWorldSample:
    def test_full_boardroom_sample(self, scrubber):
        raw = (
            "John Smith from Acme Corp discussed the merger on January 15, 2024. "
            "Contact him at john.smith@acme.com or +1 (555) 867-5309. "
            "The deal portal is at https://portal.acme.com/deal/42. "
            "Internal server: 192.168.1.100. Project lead: Jane Doe."
        )
        result = scrubber.scrub(raw)

        assert "john.smith@acme.com" not in result
        assert "192.168.1.100" not in result
        assert "https://portal.acme.com/deal/42" not in result
        assert "January 15, 2024" not in result
