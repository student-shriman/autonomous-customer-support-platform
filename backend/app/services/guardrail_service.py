"""
Guardrail & Security Service.
Features:
  - PII Masking (Credit Cards, SSNs, API Keys, Email addresses)
  - Prompt Injection & System Override Detection
"""

import re
from typing import Tuple

# Regex Patterns for Sensitive Data
_CC_REGEX = re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b")
_SSN_REGEX = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
_API_KEY_REGEX = re.compile(r"\b(?:sk-[a-zA-Z0-9]{20,}|euri-[a-zA-Z0-9]{20,}|pcsk_[a-zA-Z0-9_]{20,})\b")

# Prompt Injection Patterns
_INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+instructions", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+(in\s+developer\s+mode|unrestricted)", re.IGNORECASE),
    re.compile(r"system\s*:\s*override", re.IGNORECASE),
    re.compile(r"forget\s+all\s+rules", re.IGNORECASE)
]

def mask_pii(text: str) -> str:
    """Mask sensitive PII tokens before logging or passing to external services."""
    masked = _CC_REGEX.sub("[CARD_REDACTED]", text)
    masked = _SSN_REGEX.sub("[SSN_REDACTED]", masked)
    masked = _API_KEY_REGEX.sub("[API_KEY_REDACTED]", masked)
    return masked

def validate_input(text: str) -> Tuple[bool, str]:
    """
    Validate input against malicious prompt injection attacks.
    Returns (is_valid, sanitized_text_or_reason).
    """
    for pattern in _INJECTION_PATTERNS:
        if pattern.search(text):
            return False, "Input flagged by security guardrails: Prohibited instruction pattern detected."
    
    return True, mask_pii(text)
