"""
Agents module - Agent prompts and configurations.

Provides:
- Finance agent prompts (budget, investment, tax, supervisor)
- Support agent prompts and step configuration
- Knowledge agent prompts (docs, faq, tutorial)
"""

from agentic_patterns.agents.finance import (
    BUDGET_AGENT_PROMPT,
    INVESTMENT_AGENT_PROMPT,
    TAX_AGENT_PROMPT,
    FINANCE_SUPERVISOR_PROMPT,
)

from agentic_patterns.agents.support import (
    GREETING_PROMPT,
    ISSUE_COLLECTOR_PROMPT,
    BILLING_PROMPT,
    TECH_SUPPORT_PROMPT,
    RESOLUTION_PROMPT,
    BASE_SUPPORT_PROMPT,
    STEP_CONFIG,
    get_step_config,
)

from agentic_patterns.agents.knowledge import (
    CLASSIFICATION_PROMPT,
    DOCS_AGENT_PROMPT,
    FAQ_AGENT_PROMPT,
    TUTORIAL_AGENT_PROMPT,
    SYNTHESIS_PROMPT,
)

__all__ = [
    # Finance prompts
    "BUDGET_AGENT_PROMPT",
    "INVESTMENT_AGENT_PROMPT",
    "TAX_AGENT_PROMPT",
    "FINANCE_SUPERVISOR_PROMPT",
    # Support prompts and config
    "GREETING_PROMPT",
    "ISSUE_COLLECTOR_PROMPT",
    "BILLING_PROMPT",
    "TECH_SUPPORT_PROMPT",
    "RESOLUTION_PROMPT",
    "BASE_SUPPORT_PROMPT",
    "STEP_CONFIG",
    "get_step_config",
    # Knowledge prompts
    "CLASSIFICATION_PROMPT",
    "DOCS_AGENT_PROMPT",
    "FAQ_AGENT_PROMPT",
    "TUTORIAL_AGENT_PROMPT",
    "SYNTHESIS_PROMPT",
]
