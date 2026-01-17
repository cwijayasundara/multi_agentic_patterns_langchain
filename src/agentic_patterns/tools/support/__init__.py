"""
Customer support tools for the handoffs pattern.

Provides tools for:
- Workflow management (lookup, classify)
- Billing operations (history, refunds, discounts)
- Technical support (diagnostics, tickets)
- Resolution handling
"""

from agentic_patterns.tools.support.workflow import (
    lookup_customer,
    classify_issue,
)

from agentic_patterns.tools.support.billing import (
    check_billing_history,
    process_refund,
    apply_discount,
)

from agentic_patterns.tools.support.tech import (
    run_diagnostics,
    check_service_status,
    create_engineering_ticket,
)

from agentic_patterns.tools.support.resolution import (
    escalate_to_specialist,
    resolve_ticket,
)

# Tool collections for easy import
WORKFLOW_TOOLS = [lookup_customer, classify_issue]
BILLING_TOOLS = [check_billing_history, process_refund, apply_discount]
TECH_TOOLS = [run_diagnostics, check_service_status, create_engineering_ticket]
RESOLUTION_TOOLS = [escalate_to_specialist, resolve_ticket]

SUPPORT_TOOLS = WORKFLOW_TOOLS + BILLING_TOOLS + TECH_TOOLS + RESOLUTION_TOOLS

__all__ = [
    # Workflow tools
    "lookup_customer",
    "classify_issue",
    # Billing tools
    "check_billing_history",
    "process_refund",
    "apply_discount",
    # Tech tools
    "run_diagnostics",
    "check_service_status",
    "create_engineering_ticket",
    # Resolution tools
    "escalate_to_specialist",
    "resolve_ticket",
    # Collections
    "WORKFLOW_TOOLS",
    "BILLING_TOOLS",
    "TECH_TOOLS",
    "RESOLUTION_TOOLS",
    "SUPPORT_TOOLS",
]
