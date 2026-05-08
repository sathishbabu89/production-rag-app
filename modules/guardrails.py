class Guardrails:

    SUSPICIOUS_PATTERNS = [
        "ignore previous instructions",
        "ignore all instructions",
        "system prompt",
        "developer message",
        "act as",
        "jailbreak",
        "override",
        "bypass",
        "simulate",
        "pretend to be"
    ]

    @staticmethod
    def validate_query(query: str):
        lower_query = query.lower()

        for pattern in Guardrails.SUSPICIOUS_PATTERNS:
            if pattern in lower_query:
                raise ValueError(
                    f"Potential prompt injection detected: '{pattern}'"
                )

    @staticmethod
    def sanitize_context(context: str) -> str:
        cleaned_context = context

        for pattern in Guardrails.SUSPICIOUS_PATTERNS:
            cleaned_context = cleaned_context.replace(pattern, "[FILTERED]")

        return cleaned_context