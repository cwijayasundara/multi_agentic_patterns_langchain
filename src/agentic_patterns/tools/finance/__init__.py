"""
Finance tools for the subagents pattern.

Provides tools for:
- Budget analysis and alerts
- Investment portfolio management
- Tax planning and optimization
"""

from agentic_patterns.tools.finance.budget import (
    get_spending_by_category,
    create_budget_alert,
    get_monthly_summary,
)

from agentic_patterns.tools.finance.investment import (
    get_portfolio_performance,
    get_asset_allocation,
    execute_rebalance,
)

from agentic_patterns.tools.finance.tax import (
    estimate_tax_liability,
    find_tax_optimization_opportunities,
    get_tax_loss_harvesting_candidates,
)

# Tool collections for easy import
BUDGET_TOOLS = [get_spending_by_category, create_budget_alert, get_monthly_summary]
INVESTMENT_TOOLS = [get_portfolio_performance, get_asset_allocation, execute_rebalance]
TAX_TOOLS = [estimate_tax_liability, find_tax_optimization_opportunities, get_tax_loss_harvesting_candidates]

FINANCE_TOOLS = BUDGET_TOOLS + INVESTMENT_TOOLS + TAX_TOOLS

__all__ = [
    # Budget tools
    "get_spending_by_category",
    "create_budget_alert",
    "get_monthly_summary",
    # Investment tools
    "get_portfolio_performance",
    "get_asset_allocation",
    "execute_rebalance",
    # Tax tools
    "estimate_tax_liability",
    "find_tax_optimization_opportunities",
    "get_tax_loss_harvesting_candidates",
    # Collections
    "BUDGET_TOOLS",
    "INVESTMENT_TOOLS",
    "TAX_TOOLS",
    "FINANCE_TOOLS",
]
