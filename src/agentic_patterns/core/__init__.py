"""
Core module - Shared infrastructure for agentic patterns.

Provides:
- Model initialization (get_model)
- Checkpointer setup (get_memory_checkpointer)
- Middleware preset factories for each pattern
- Utility functions (PII redaction, retry/fallback helpers)
"""

from agentic_patterns.core.config import get_model, DEFAULT_MODEL, DEFAULT_MODEL_PROVIDER
from agentic_patterns.core.checkpointer import get_memory_checkpointer
from agentic_patterns.core.middleware import (
    create_subagent_middleware,
    create_supervisor_middleware,
    create_support_middleware,
    create_skills_middleware,
)
from agentic_patterns.core.utils import (
    redact_pii,
    sanitize_query,
    with_retry_and_fallback,
    PII_PATTERNS,
)

__all__ = [
    # Config
    "get_model",
    "DEFAULT_MODEL",
    "DEFAULT_MODEL_PROVIDER",
    # Checkpointer
    "get_memory_checkpointer",
    # Middleware
    "create_subagent_middleware",
    "create_supervisor_middleware",
    "create_support_middleware",
    "create_skills_middleware",
    # Utils
    "redact_pii",
    "sanitize_query",
    "with_retry_and_fallback",
    "PII_PATTERNS",
]
