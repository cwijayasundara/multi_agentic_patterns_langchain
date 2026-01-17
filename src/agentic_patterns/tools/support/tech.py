"""
Technical support tools for customer support.

These tools handle diagnostics, service status, and engineering tickets.
"""

from typing import Literal, Annotated
from langchain_core.tools import tool, InjectedToolCallId
from langchain_core.messages import ToolMessage
from langgraph.types import Command

# Module-level ticket counter for engineering tickets
_eng_ticket_counter = 1000


def _get_next_eng_ticket_id() -> str:
    """Get the next engineering ticket ID and increment counter."""
    global _eng_ticket_counter
    _eng_ticket_counter += 1
    return f"ENG-{_eng_ticket_counter}"


@tool
def run_diagnostics(service: str) -> str:
    """Run diagnostic checks on a service.

    Args:
        service: Service to diagnose (e.g., "api", "web", "mobile")
    """
    # Mock diagnostics
    return f"""Diagnostic Results for {service}:
- Service Status: Operational
- Response Time: 145ms (normal)
- Error Rate: 0.02% (normal)
- Last Incident: None in past 7 days
- Recommendation: Service is healthy. Issue may be client-side."""


@tool
def check_service_status() -> str:
    """Check overall service status."""
    return """Current Service Status:
- API: ✅ Operational
- Web App: ✅ Operational
- Mobile App: ✅ Operational
- Database: ✅ Operational
- CDN: ✅ Operational

No ongoing incidents. All systems normal."""


@tool
def create_engineering_ticket(
    title: str,
    description: str,
    severity: Literal["low", "medium", "high", "critical"],
    tool_call_id: Annotated[str, InjectedToolCallId]
) -> Command:
    """Create a ticket for engineering team.

    Args:
        title: Brief title of the issue
        description: Detailed description
        severity: Ticket severity
    """
    eng_ticket = _get_next_eng_ticket_id()

    return Command(update={
        "messages": [ToolMessage(
            content=f"Engineering ticket {eng_ticket} created. "
                   f"Severity: {severity}. Team will investigate within "
                   f"{'4 hours' if severity == 'critical' else '24 hours'}.",
            tool_call_id=tool_call_id
        )],
        "resolution_status": f"Escalated to engineering ({eng_ticket})"
    })
