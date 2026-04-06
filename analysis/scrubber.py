import re
import os

class PII_Scrubber:
    def __init__(self):
        # Basic patterns for names, companies, and dates
        self.patterns = {
            "NAMES": r"\b([A-Z][a-z]+ [A-Z][a-z]+)\b", # Basic First Last
            "EMAILS": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "PHONES": r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
            "COMPANIES": r"\b([A-Z]{2,}|[A-Z][a-z]+ (Inc\.|Corp\.|Ltd\.|LLC))\b"
        }

    def scrub(self, text):
        scrubbed_text = text
        
        # In a real boardroom tool, you'd use a more sophisticated NER model
        # For this version, we use robust regex and a placeholder system
        
        placeholders = {
            "NAMES": "[PERSON_REDACTED]",
            "EMAILS": "[EMAIL_REDACTED]",
            "PHONES": "[PHONE_REDACTED]",
            "COMPANIES": "[COMPANY_REDACTED]"
        }
        
        for key, pattern in self.patterns.items():
            scrubbed_text = re.sub(pattern, placeholders[key], scrubbed_text)
            
        return scrubbed_text

if __name__ == "__main__":
    test_text = "John Doe from Acme Corp discussed the merger at 555-0123. Email me at john@acme.com."
    scrubber = PII_Scrubber()
    print(f"Original: {test_text}")
    print(f"Scrubbed: {scrubber.scrub(test_text)}")
