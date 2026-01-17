"""
Agentic Patterns - Multi-agent patterns for LangChain/LangGraph 1.2.x
=====================================================================

This package provides modular, reusable components for building multi-agent systems:

- **core**: Shared infrastructure (config, middleware, checkpointer, utils)
- **tools**: Domain-specific tools organized by pattern
- **agents**: Agent prompts and configurations
- **state**: TypedDict and Pydantic state models

Example Usage:
    from agentic_patterns.core import get_model, get_memory_checkpointer
    from agentic_patterns.tools import FINANCE_TOOLS, SUPPORT_TOOLS
    from agentic_patterns.agents import BUDGET_AGENT_PROMPT
    from agentic_patterns.state import SupportState, RouterState
"""

from agentic_patterns.core import (
    get_model,
    get_memory_checkpointer,
    create_subagent_middleware,
    create_supervisor_middleware,
    create_support_middleware,
    create_skills_middleware,
)

__version__ = "0.1.0"

__all__ = [
    # Core
    "get_model",
    "get_memory_checkpointer",
    "create_subagent_middleware",
    "create_supervisor_middleware",
    "create_support_middleware",
    "create_skills_middleware",
]
