"""
Resolution tools for customer support.

These tools handle escalation and ticket resolution.
"""

from typing import Literal, Annotated
from langchain_core.tools import tool, InjectedToolCallId
from langchain_core.messages import ToolMessage
from langgraph.types import Command


@tool
def escalate_to_specialist(
    specialist: Literal["billing_specialist", "tech_support", "resolution"],
    tool_call_id: Annotated[str, InjectedToolCallId]
) -> Command:
    """Hand off to a different specialist.

    Args:
        specialist: Which specialist to hand off to
    """
    return Command(update={
        "messages": [ToolMessage(
            content=f"Handing off to {specialist.replace('_', ' ')}.",
            tool_call_id=tool_call_id
        )],
        "current_step": specialist
    })


@tool
def resolve_ticket(
    resolution_summary: str,
    tool_call_id: Annotated[str, InjectedToolCallId],
    follow_up_needed: bool = False
) -> Command:
    """Mark the ticket as resolved.

    Args:
        resolution_summary: Summary of how the issue was resolved
        follow_up_needed: Whether follow-up is needed
    """
    return Command(update={
        "messages": [ToolMessage(
            content=f"Ticket resolved: {resolution_summary}"
                   f"{' (Follow-up scheduled)' if follow_up_needed else ''}",
            tool_call_id=tool_call_id
        )],
        "current_step": "resolution",
        "resolution_status": resolution_summary
    })
