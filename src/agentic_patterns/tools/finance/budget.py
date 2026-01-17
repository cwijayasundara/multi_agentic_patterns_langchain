"""
Budget analysis tools for the subagents pattern.

These tools provide spending analysis, budget alerts, and monthly summaries.
In production, these would connect to actual financial APIs.
"""

from langchain_core.tools import tool


@tool
def get_spending_by_category(
    categories: list[str],
    time_period: str = "last_month"
) -> dict:
    """Get spending breakdown by categories.

    Args:
        categories: List of categories like ["food", "transport", "utilities"]
        time_period: Time period - "last_week", "last_month", "last_quarter", "last_year"
    """
    # Mock data - in production, query actual financial APIs
    mock_spending = {
        "food": {"amount": 850.00, "trend": "+5%", "budget": 800.00},
        "transport": {"amount": 320.00, "trend": "-10%", "budget": 400.00},
        "utilities": {"amount": 180.00, "trend": "+2%", "budget": 200.00},
        "entertainment": {"amount": 250.00, "trend": "+15%", "budget": 200.00},
        "shopping": {"amount": 420.00, "trend": "+20%", "budget": 300.00},
        "healthcare": {"amount": 150.00, "trend": "0%", "budget": 200.00},
    }
    return {cat: mock_spending.get(cat, {"amount": 0, "trend": "N/A", "budget": 0})
            for cat in categories}


@tool
def create_budget_alert(
    category: str,
    threshold_percent: int,
    notification_method: str = "email"
) -> str:
    """Create an alert when spending in a category exceeds threshold.

    Args:
        category: Spending category to monitor
        threshold_percent: Alert when spending exceeds this % of budget (e.g., 80)
        notification_method: How to notify - "email", "sms", "push"
    """
    return f"Budget alert created: Notify via {notification_method} when {category} exceeds {threshold_percent}% of budget"


@tool
def get_monthly_summary(month: str, year: int) -> dict:
    """Get complete monthly financial summary.

    Args:
        month: Month name (e.g., "January", "February")
        year: Year (e.g., 2026)
    """
    return {
        "month": month,
        "year": year,
        "total_income": 8500.00,
        "total_expenses": 5200.00,
        "savings": 3300.00,
        "savings_rate": "38.8%",
        "top_expense_categories": ["Rent", "Food", "Transport"],
        "budget_status": "Under budget by $400"
    }
