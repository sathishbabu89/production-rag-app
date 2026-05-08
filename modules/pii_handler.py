import re


class PIIHandler:

    PATTERNS = {
        "EMAIL": r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
        "PHONE": r"\b\d{10}\b",
        "AADHAAR": r"\b\d{4}\s\d{4}\s\d{4}\b",
        "PAN": r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b"
    }

    @staticmethod
    def redact(text: str) -> str:
        redacted_text = text

        for pii_type, pattern in PIIHandler.PATTERNS.items():
            redacted_text = re.sub(
                pattern,
                f"[REDACTED_{pii_type}]",
                redacted_text
            )

        return redacted_text