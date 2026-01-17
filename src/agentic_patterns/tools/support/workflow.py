"""
Workflow tools for customer support state machine.

These tools handle customer lookup and issue classification,
driving the state machine transitions.
"""

from typing import Literal, Annotated
from langchain_core.tools import tool, InjectedToolCallId
from langchain_core.messages import ToolMessage
from langgraph.types import Command


# Mock customer database
CUSTOMERS = {
    "C001": {
        "name": "Alice Johnson",
        "email": "alice@example.com",
        "plan": "Premium",
        "account_status": "active",
        "balance": 0.00,
        "last_payment": "2026-01-01",
    },
    "C002": {
        "name": "Bob Smith",
        "email": "bob@example.com",
        "plan": "Basic",
        "account_status": "active",
        "balance": 29.99,
        "last_payment": "2025-12-15",
    },
}

# Module-level ticket counter
_ticket_counter = 1000


def _get_next_ticket_id() -> str:
    """Get the next ticket ID and increment counter."""
    global _ticket_counter
    _ticket_counter += 1
    return f"TKT-{_ticket_counter}"


@tool
def lookup_customer(
    customer_id: str,
    tool_call_id: Annotated[str, InjectedToolCallId]
) -> Command:
    """Look up customer by ID and transition to issue collection.

    Args:
        customer_id: Customer ID (e.g., "C001")
    """
    customer = CUSTOMERS.get(customer_id)

    if not customer:
        return Command(update={
            "messages": [ToolMessage(
                content=f"Customer {customer_id} not found. Please verify the ID.",
                tool_call_id=tool_call_id
            )]
        })

    return Command(update={
        "messages": [ToolMessage(
            content=f"Found customer: {customer['name']} ({customer['plan']} plan)",
            tool_call_id=tool_call_id
        )],
        "customer_id": customer_id,
        "customer_name": customer["name"],
        "current_step": "issue_collector"  # State transition
    })


@tool
def classify_issue(
    issue_type: Literal["billing", "technical", "general"],
    description: str,
    priority: Literal["low", "medium", "high", "urgent"],
    tool_call_id: Annotated[str, InjectedToolCallId]
) -> Command:
    """Classify the customer's issue and route to appropriate specialist.

    Args:
        issue_type: Type of issue - billing, technical, or general
        description: Brief description of the issue
        priority: Issue priority based on impact
    """
    ticket_id = _get_next_ticket_id()

    # Determine next step based on issue type
    next_step = {
        "billing": "billing_specialist",
        "technical": "tech_support",
        "general": "resolution"
    }.get(issue_type, "resolution")

    return Command(update={
        "messages": [ToolMessage(
            content=f"Issue classified as {issue_type} ({priority} priority). "
                   f"Created ticket {ticket_id}. Routing to specialist.",
            tool_call_id=tool_call_id
        )],
        "issue_type": issue_type,
        "issue_description": description,
        "priority": priority,
        "ticket_id": ticket_id,
        "current_step": next_step
    })
