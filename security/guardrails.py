import re
from typing import Optional

INJECTION_PATTERNS = [
    r"ignore previous instructions",
    r"ignore all instructions",
    r"you are now",
    r"act as",
    r"forget your",
    r"system prompt",
    r"jailbreak",
    r"disregard",
]

PII_PATTERNS = [
    r"\b\d{3}-\d{2}-\d{4}\b",        # SSN
    r"\b\d{16}\b",                     # Credit card
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email
]

MAX_INPUT_LENGTH = 2000

def validate_input(text: str) -> tuple[bool, Optional[str]]:
    if not text or not text.strip():
        return False, "Input cannot be empty"

    if len(text) > MAX_INPUT_LENGTH:
        return False, f"Input too long — max {MAX_INPUT_LENGTH} characters"

    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return False, "Input contains disallowed instructions"

    return True, None

def scrub_pii(text: str) -> str:
    for pattern in PII_PATTERNS:
        text = re.sub(pattern, "[REDACTED]", text)
    return text

def validate_agent_output(output: str, agent_name: str) -> tuple[bool, Optional[str]]:
    if not output or not output.strip():
        return False, f"{agent_name} returned empty output"

    if len(output) > 10000:
        return False, f"{agent_name} output exceeds size limit"

    return True, None

def enforce_clinical_guardrail(ranked_treatments: list) -> list:
    safe = []
    for t in ranked_treatments:
        if t.get("ml_score", 0) < 0.3:
            continue  # Filter out very low confidence recommendations
        safe.append(t)
    return safe