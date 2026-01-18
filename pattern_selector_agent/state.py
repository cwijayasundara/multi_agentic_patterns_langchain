"""
State definitions for the Pattern Selector Agent.

Defines:
- SelectorPhase: Literal type for conversation phases
- SelectorState: TypedDict for the complete selector state
"""

from typing import Literal, NotRequired
from typing_extensions import TypedDict


SelectorPhase = Literal["gathering", "clarifying", "recommending"]


class Requirement(TypedDict):
    """A single extracted requirement from the user's problem description."""
    aspect: str  # e.g., "parallelization", "user_interaction", "context_size"
    description: str  # The actual requirement
    importance: Literal["must_have", "nice_to_have", "optional"]


class Clarification(TypedDict):
    """A clarification question and its answer."""
    question: str
    answer: str


class Recommendation(TypedDict):
    """A pattern recommendation with reasoning."""
    pattern_name: str
    confidence: Literal["high", "medium", "low"]
    reasoning: str
    trade_offs: list[str]


class SelectorState(TypedDict):
    """State for the pattern selector workflow.

    The current_phase field drives the conversation flow:
    - gathering: Initial problem description collection
    - clarifying: Asking targeted questions to understand requirements
    - recommending: Making final pattern recommendations
    """
    # Workflow control
    current_phase: NotRequired[SelectorPhase]

    # User input
    problem_description: NotRequired[str]

    # Extracted requirements
    requirements: NotRequired[list[Requirement]]

    # Clarification Q&A
    clarifications: NotRequired[list[Clarification]]

    # Pattern context
    loaded_patterns: NotRequired[list[str]]

    # Final output
    recommendations: NotRequired[list[Recommendation]]
