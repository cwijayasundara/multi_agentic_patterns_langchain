"""
Tax planning tools for the subagents pattern.

These tools provide tax liability estimates, optimization opportunities,
and tax-loss harvesting candidates. In production, these would connect
to actual tax planning services.
"""

from langchain_core.tools import tool


@tool
def estimate_tax_liability(
    income: float,
    filing_status: str,
    deductions: dict
) -> dict:
    """Estimate tax liability based on income and deductions.

    Args:
        income: Total annual income
        filing_status: "single", "married_joint", "married_separate", "head_of_household"
        deductions: Dict with deduction types and amounts
    """
    # Simplified mock calculation
    standard_deduction = {"single": 14600, "married_joint": 29200,
                         "married_separate": 14600, "head_of_household": 21900}
    taxable_income = income - standard_deduction.get(filing_status, 14600)
    estimated_tax = taxable_income * 0.22  # Simplified

    return {
        "gross_income": income,
        "filing_status": filing_status,
        "standard_deduction": standard_deduction.get(filing_status),
        "taxable_income": taxable_income,
        "estimated_federal_tax": estimated_tax,
        "effective_rate": f"{(estimated_tax/income)*100:.1f}%",
        "deductions_applied": deductions
    }


@tool
def find_tax_optimization_opportunities(
    income: float,
    current_contributions: dict
) -> list[dict]:
    """Find tax optimization opportunities.

    Args:
        income: Annual income
        current_contributions: Current retirement/HSA contributions
    """
    opportunities = []

    # Check 401k
    current_401k = current_contributions.get("401k", 0)
    max_401k = 23000
    if current_401k < max_401k:
        opportunities.append({
            "type": "401k_contribution",
            "potential_savings": (max_401k - current_401k) * 0.22,
            "action": f"Increase 401k contribution by ${max_401k - current_401k}",
            "priority": "high"
        })

    # Check HSA
    current_hsa = current_contributions.get("hsa", 0)
    max_hsa = 4150
    if current_hsa < max_hsa:
        opportunities.append({
            "type": "hsa_contribution",
            "potential_savings": (max_hsa - current_hsa) * 0.22,
            "action": f"Contribute ${max_hsa - current_hsa} more to HSA",
            "priority": "medium"
        })

    return opportunities


@tool
def get_tax_loss_harvesting_candidates(portfolio_id: str = "default") -> list[dict]:
    """Find positions with unrealized losses for tax-loss harvesting.

    Args:
        portfolio_id: Portfolio to analyze
    """
    return [
        {"symbol": "XYZ", "purchase_price": 150.00, "current_price": 120.00,
         "unrealized_loss": -300.00, "shares": 10, "wash_sale_safe": True},
        {"symbol": "ABC", "purchase_price": 80.00, "current_price": 65.00,
         "unrealized_loss": -750.00, "shares": 50, "wash_sale_safe": True},
    ]
