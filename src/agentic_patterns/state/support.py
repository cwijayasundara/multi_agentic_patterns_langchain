"""
State definitions for the customer support handoffs pattern.

Defines:
- SupportStep: Literal type for workflow steps
- SupportState: TypedDict for the complete support state
"""

from typing import Literal, NotRequired
from typing_extensions import TypedDict


SupportStep = Literal[
    "greeting",
    "issue_collector",
    "billing_specialist",
    "tech_support",
    "resolution"
]


class SupportState(TypedDict):
    """State for the customer support workflow.

    The current_step field drives the entire workflow - it determines
    which configuration (prompt + tools) loads next.
    """
    # Workflow control
    current_step: NotRequired[SupportStep]

    # Collected information
    customer_id: NotRequired[str]
    customer_name: NotRequired[str]
    issue_type: NotRequired[Literal["billing", "technical", "general"]]
    issue_description: NotRequired[str]
    priority: NotRequired[Literal["low", "medium", "high", "urgent"]]

    # Resolution tracking
    ticket_id: NotRequired[str]
    resolution_status: NotRequired[str]
