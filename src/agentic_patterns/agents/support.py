"""
Agent prompts and step configuration for the handoffs customer support pattern.

Provides:
- Step-specific system prompts
- STEP_CONFIG dictionary mapping steps to prompts/tools
- get_step_config function for dynamic configuration
"""

from agentic_patterns.state.support import SupportState
from agentic_patterns.tools.support import (
    lookup_customer,
    classify_issue,
    check_billing_history,
    process_refund,
    apply_discount,
    run_diagnostics,
    check_service_status,
    create_engineering_ticket,
    escalate_to_specialist,
    resolve_ticket,
)
from agentic_patterns.tools.support.workflow import CUSTOMERS


GREETING_PROMPT = """You are a friendly customer support greeter. Your role is to:
- Welcome the customer warmly
- Ask for their customer ID or email to look up their account
- Once identified, hand off to issue collection

Keep responses brief and professional. Don't try to solve issues yet - just identify the customer."""

ISSUE_COLLECTOR_PROMPT = """You are collecting information about the customer's issue.

Customer: {customer_name} (ID: {customer_id})
Plan: {customer_plan}

Your role is to:
- Ask what issue they're experiencing
- Classify it as billing, technical, or general
- Assess priority based on impact
- Hand off to the appropriate specialist

Ask clarifying questions if needed before classifying."""

BILLING_PROMPT = """You are a billing specialist helping {customer_name}.

Customer ID: {customer_id}
Plan: {customer_plan}
Current Balance: ${customer_balance}
Last Payment: {last_payment}

Issue: {issue_description}
Priority: {priority}

You can:
- Check billing history
- Process refunds (up to $100)
- Apply discounts (up to 20%)
- Explain charges

For complex billing issues, escalate to resolution."""

TECH_SUPPORT_PROMPT = """You are a technical support specialist helping {customer_name}.

Customer ID: {customer_id}
Plan: {customer_plan}

Issue: {issue_description}
Priority: {priority}

You can:
- Run diagnostic checks
- Guide through troubleshooting steps
- Check service status
- Create support tickets for engineering

For issues requiring escalation, hand off to resolution."""

RESOLUTION_PROMPT = """You are the resolution specialist finalizing support for {customer_name}.

Customer ID: {customer_id}
Ticket: {ticket_id}
Issue Type: {issue_type}
Issue: {issue_description}

Your role is to:
- Summarize what was done
- Confirm the issue is resolved or explain next steps
- Offer any additional assistance
- Close the interaction professionally

If the customer has new issues, hand back to issue collector."""

BASE_SUPPORT_PROMPT = """You are a customer support agent that adapts based on the conversation stage.

Current workflow steps:
1. greeting: Welcome customer and identify them
2. issue_collector: Understand and classify their issue
3. billing_specialist: Handle billing-related issues
4. tech_support: Handle technical issues
5. resolution: Finalize and close the interaction

Use the appropriate tools based on the current stage of the conversation.
Tools will automatically transition you to the next appropriate step.

Always be professional, empathetic, and focused on resolving the customer's issue."""


STEP_CONFIG = {
    "greeting": {
        "prompt": GREETING_PROMPT,
        "tools": [lookup_customer],
        "requires": [],
    },
    "issue_collector": {
        "prompt": ISSUE_COLLECTOR_PROMPT,
        "tools": [classify_issue],
        "requires": ["customer_id", "customer_name"],
    },
    "billing_specialist": {
        "prompt": BILLING_PROMPT,
        "tools": [check_billing_history, process_refund, apply_discount,
                  escalate_to_specialist, resolve_ticket],
        "requires": ["customer_id", "issue_description"],
    },
    "tech_support": {
        "prompt": TECH_SUPPORT_PROMPT,
        "tools": [run_diagnostics, check_service_status, create_engineering_ticket,
                  escalate_to_specialist, resolve_ticket],
        "requires": ["customer_id", "issue_description"],
    },
    "resolution": {
        "prompt": RESOLUTION_PROMPT,
        "tools": [resolve_ticket, escalate_to_specialist],
        "requires": ["customer_id"],
    },
}


def get_step_config(state: SupportState) -> tuple[str, list]:
    """Get the prompt and tools for the current step.

    Args:
        state: Current support state

    Returns:
        Tuple of (formatted_prompt, tools_list)

    Raises:
        ValueError: If required state fields are missing
    """
    current_step = state.get("current_step", "greeting")
    config = STEP_CONFIG[current_step]

    # Validate required state exists
    for key in config["requires"]:
        if state.get(key) is None:
            raise ValueError(f"{key} must be set before {current_step}")

    # Get customer data for prompt formatting
    customer_id = state.get("customer_id", "")
    customer = CUSTOMERS.get(customer_id, {})

    # Format prompt with state values
    format_values = {
        "customer_name": state.get("customer_name", "Customer"),
        "customer_id": customer_id,
        "customer_plan": customer.get("plan", "Unknown"),
        "customer_balance": customer.get("balance", 0),
        "last_payment": customer.get("last_payment", "N/A"),
        "issue_type": state.get("issue_type", "unknown"),
        "issue_description": state.get("issue_description", "Not yet collected"),
        "priority": state.get("priority", "unknown"),
        "ticket_id": state.get("ticket_id", "Not assigned"),
    }

    formatted_prompt = config["prompt"].format(**format_values)
    return formatted_prompt, config["tools"]
