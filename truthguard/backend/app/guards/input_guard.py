import re
from typing import Tuple, Optional

INJECTION_PATTERNS = [
    r'(?i)\bignore\s+(?:all\s+)?previous\s+instructions\b',
    r'(?i)\breveal\s+(?:the\s+)?system\s+prompt\b',
    r'(?i)\bjailbreak\b',
    r'(?i)\byou\s+are\s+now\s+DAN\b',
    r'(?i)\bdisregard\s+(?:all\s+)?safety\b',
    r'(?i)\bexecute\s+command\b',
    r'(?i)<script[\s\S]*?>',
    r'(?i)\bdrop\s+table\b'
]


def validate_user_input(question: str) -> Tuple[bool, Optional[str]]:
    """
    Validates user question against security rules, emptiness, and length limits.
    """
    if not question or not question.strip():
        return False, "Question cannot be empty or whitespace only."

    trimmed = question.strip()
    if len(trimmed) < 3:
        return False, "Question is too short (minimum 3 characters)."

    if len(trimmed) > 1000:
        return False, "Question exceeds maximum length limit of 1000 characters."

    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, trimmed):
            return False, "Question was rejected by security guardrail: potential adversarial prompt injection detected."

    return True, None
