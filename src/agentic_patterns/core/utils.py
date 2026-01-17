"""
Utility functions for context engineering.

Provides:
- PII redaction for protecting sensitive data
- Retry/fallback wrapper for resilient API calls
"""

import re
import time
from typing import Callable, Optional


# PII Detection patterns (simple regex-based)
PII_PATTERNS = {
    "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    "credit_card": r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
    "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
    "phone": r'\b(?:\+1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
}


def redact_pii(text: str) -> str:
    """Redact PII from text before processing.

    Args:
        text: Input text potentially containing PII

    Returns:
        Text with PII redacted

    Example:
        >>> redact_pii("Contact me at john@example.com")
        "Contact me at [REDACTED_EMAIL]"
    """
    result = text
    for pii_type, pattern in PII_PATTERNS.items():
        result = re.sub(pattern, f'[REDACTED_{pii_type.upper()}]', result)
    return result


def sanitize_query(query: str) -> str:
    """Sanitize user query by redacting PII.

    Context Engineering: Protects sensitive data from being
    processed by the knowledge base or logged.

    Args:
        query: User query potentially containing PII

    Returns:
        Sanitized query with PII redacted
    """
    return redact_pii(query)


def with_retry_and_fallback(
    primary_fn: Callable,
    fallback_fn: Optional[Callable] = None,
    max_retries: int = 2,
    backoff_factor: float = 2.0,
    initial_delay: float = 1.0,
):
    """Wrap a function with retry logic and optional fallback.

    Args:
        primary_fn: Primary function to call
        fallback_fn: Fallback function if primary exhausts retries
        max_retries: Maximum retry attempts
        backoff_factor: Multiplier for delay between retries
        initial_delay: Initial delay in seconds

    Returns:
        Wrapped function with retry/fallback behavior

    Example:
        >>> def primary():
        ...     return model.invoke(prompt)
        >>> def fallback():
        ...     return fallback_model.invoke(prompt)
        >>> wrapped = with_retry_and_fallback(primary, fallback)
        >>> result = wrapped()
    """
    def wrapper(*args, **kwargs):
        delay = initial_delay

        for attempt in range(max_retries + 1):
            try:
                return primary_fn(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries:
                    if fallback_fn:
                        try:
                            return fallback_fn(*args, **kwargs)
                        except Exception:
                            raise e  # Re-raise original if fallback fails
                    raise e
                time.sleep(delay)
                delay *= backoff_factor

    return wrapper
