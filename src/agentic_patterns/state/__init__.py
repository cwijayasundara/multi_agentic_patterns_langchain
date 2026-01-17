"""
State module - TypedDict and Pydantic state models.

Provides state definitions for each pattern:
- SupportState: Customer support state machine state
- RouterState: Router pattern workflow state
- ContentState: Content pipeline workflow state
"""

from agentic_patterns.state.support import (
    SupportState,
    SupportStep,
)

from agentic_patterns.state.router import (
    RouterState,
    AgentInput,
    AgentOutput,
    Classification,
    ClassificationResult,
)

from agentic_patterns.state.content import (
    ContentState,
    CONTENT_CONFIGS,
)

__all__ = [
    # Support state
    "SupportState",
    "SupportStep",
    # Router state
    "RouterState",
    "AgentInput",
    "AgentOutput",
    "Classification",
    "ClassificationResult",
    # Content state
    "ContentState",
    "CONTENT_CONFIGS",
]
