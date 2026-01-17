"""
Tools module - Domain-specific tools organized by pattern.

Provides tool collections for each pattern:
- FINANCE_TOOLS: Budget, investment, and tax tools
- SUPPORT_TOOLS: Customer support workflow tools
- CODE_TOOLS: Skill loading and code generation tools
- KNOWLEDGE_TOOLS: Knowledge base search tools
"""

from agentic_patterns.tools.finance import (
    BUDGET_TOOLS,
    INVESTMENT_TOOLS,
    TAX_TOOLS,
    FINANCE_TOOLS,
    get_spending_by_category,
    create_budget_alert,
    get_monthly_summary,
    get_portfolio_performance,
    get_asset_allocation,
    execute_rebalance,
    estimate_tax_liability,
    find_tax_optimization_opportunities,
    get_tax_loss_harvesting_candidates,
)

from agentic_patterns.tools.support import (
    WORKFLOW_TOOLS,
    BILLING_TOOLS,
    TECH_TOOLS,
    RESOLUTION_TOOLS,
    SUPPORT_TOOLS,
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

from agentic_patterns.tools.code import (
    SKILL_TOOLS,
    GENERATION_TOOLS,
    CODE_TOOLS,
    load_skill,
    list_available_skills,
    list_loaded_skills,
    unload_skill,
    get_skill_details,
    generate_boilerplate,
)

from agentic_patterns.tools.knowledge import (
    KNOWLEDGE_TOOLS,
    search_docs,
    search_faq,
    search_tutorials,
)

__all__ = [
    # Finance tools
    "BUDGET_TOOLS",
    "INVESTMENT_TOOLS",
    "TAX_TOOLS",
    "FINANCE_TOOLS",
    "get_spending_by_category",
    "create_budget_alert",
    "get_monthly_summary",
    "get_portfolio_performance",
    "get_asset_allocation",
    "execute_rebalance",
    "estimate_tax_liability",
    "find_tax_optimization_opportunities",
    "get_tax_loss_harvesting_candidates",
    # Support tools
    "WORKFLOW_TOOLS",
    "BILLING_TOOLS",
    "TECH_TOOLS",
    "RESOLUTION_TOOLS",
    "SUPPORT_TOOLS",
    "lookup_customer",
    "classify_issue",
    "check_billing_history",
    "process_refund",
    "apply_discount",
    "run_diagnostics",
    "check_service_status",
    "create_engineering_ticket",
    "escalate_to_specialist",
    "resolve_ticket",
    # Code tools
    "SKILL_TOOLS",
    "GENERATION_TOOLS",
    "CODE_TOOLS",
    "load_skill",
    "list_available_skills",
    "list_loaded_skills",
    "unload_skill",
    "get_skill_details",
    "generate_boilerplate",
    # Knowledge tools
    "KNOWLEDGE_TOOLS",
    "search_docs",
    "search_faq",
    "search_tutorials",
]
