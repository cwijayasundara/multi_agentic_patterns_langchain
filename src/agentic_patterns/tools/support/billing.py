"""
Billing tools for customer support.

These tools handle billing history, refunds, and discounts.
Tools that modify state return Command objects.
"""

from typing import Annotated
from langchain_core.tools import tool, InjectedToolCallId
from langchain_core.messages import ToolMessage
from langgraph.types import Command

# Re-use customer database from workflow module
from agentic_patterns.tools.support.workflow import CUSTOMERS


@tool
def check_billing_history(customer_id: str) -> str:
    """Check customer's billing history.

    Args:
        customer_id: Customer ID to look up
    """
    customer = CUSTOMERS.get(customer_id, {})
    return f"""Billing History for {customer_id}:
- Current Balance: ${customer.get('balance', 0):.2f}
- Last Payment: {customer.get('last_payment', 'N/A')}
- Plan: {customer.get('plan', 'Unknown')}
- Payment Status: {'Current' if customer.get('balance', 0) == 0 else 'Outstanding'}"""


@tool
def process_refund(
    customer_id: str,
    amount: float,
    reason: str,
    tool_call_id: Annotated[str, InjectedToolCallId]
) -> Command:
    """Process a refund for the customer (max $100).

    Args:
        customer_id: Customer ID
        amount: Refund amount (max $100)
        reason: Reason for refund
    """
    if amount > 100:
        return Command(update={
            "messages": [ToolMessage(
                content="Refund amount exceeds $100 limit. Please escalate to manager.",
                tool_call_id=tool_call_id
            )]
        })

    return Command(update={
        "messages": [ToolMessage(
            content=f"Refund of ${amount:.2f} processed for {customer_id}. "
                   f"Reason: {reason}. Will reflect in 3-5 business days.",
            tool_call_id=tool_call_id
        )],
        "resolution_status": f"Refund of ${amount:.2f} processed"
    })


@tool
def apply_discount(
    customer_id: str,
    discount_percent: int,
    duration_months: int,
    tool_call_id: Annotated[str, InjectedToolCallId]
) -> Command:
    """Apply a discount to customer's account (max 20%).

    Args:
        customer_id: Customer ID
        discount_percent: Discount percentage (max 20)
        duration_months: How many months the discount applies
    """
    if discount_percent > 20:
        return Command(update={
            "messages": [ToolMessage(
                content="Discount exceeds 20% limit. Please escalate for approval.",
                tool_call_id=tool_call_id
            )]
        })

    return Command(update={
        "messages": [ToolMessage(
            content=f"Applied {discount_percent}% discount for {duration_months} months "
                   f"to account {customer_id}.",
            tool_call_id=tool_call_id
        )],
        "resolution_status": f"{discount_percent}% discount applied"
    })
