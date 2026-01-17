"""
Subagents Pattern: Personal Finance Assistant
==============================================
A supervisor agent coordinates specialized sub-agents for budget, investment, and tax domains.

Architecture (Three-Layer System):
1. Bottom Layer: Low-level API tools (rigid, format-specific)
2. Middle Layer: Domain-specific sub-agents (natural language → structured calls)
3. Top Layer: Supervisor agent (high-level routing and coordination)

Key Concept: Sub-agents are wrapped as tools for the supervisor, enabling:
- Centralized workflow control
- Parallel sub-agent execution
- Clean separation of concerns

Middleware (Context Engineering):
- SummarizationMiddleware: Compress conversation history for long sessions
- ToolRetryMiddleware: Resilient tool calls with exponential backoff
- ModelFallbackMiddleware: Automatic failover to backup models

Reference:
- https://docs.langchain.com/oss/python/langchain/multi-agent/subagents-personal-assistant
- https://docs.langchain.com/oss/python/langchain/middleware/built-in
"""

from langchain_core.tools import tool
from langchain.agents import create_agent

# Import from the agentic_patterns package
from agentic_patterns.core import (
    get_model,
    get_memory_checkpointer,
    create_subagent_middleware,
    create_supervisor_middleware,
)
from agentic_patterns.tools.finance import (
    BUDGET_TOOLS,
    INVESTMENT_TOOLS,
    TAX_TOOLS,
)
from agentic_patterns.agents.finance import (
    BUDGET_AGENT_PROMPT,
    INVESTMENT_AGENT_PROMPT,
    TAX_AGENT_PROMPT,
    FINANCE_SUPERVISOR_PROMPT,
)


# Initialize model and checkpointer
model = get_model()
checkpointer = get_memory_checkpointer()

# Get middleware stacks
SUBAGENT_MIDDLEWARE = create_subagent_middleware()
SUPERVISOR_MIDDLEWARE = create_supervisor_middleware()


# ============================================
# Layer 2: Domain-Specific Sub-Agents (Middle Layer)
# ============================================

budget_agent = create_agent(
    model,
    tools=BUDGET_TOOLS,
    system_prompt=BUDGET_AGENT_PROMPT,
    name="budget_analyst",
    middleware=SUBAGENT_MIDDLEWARE,
)

investment_agent = create_agent(
    model,
    tools=INVESTMENT_TOOLS,
    system_prompt=INVESTMENT_AGENT_PROMPT,
    name="investment_advisor",
    middleware=SUBAGENT_MIDDLEWARE,
)

tax_agent = create_agent(
    model,
    tools=TAX_TOOLS,
    system_prompt=TAX_AGENT_PROMPT,
    name="tax_consultant",
    middleware=SUBAGENT_MIDDLEWARE,
)


# ============================================
# Layer 2.5: Wrap Sub-Agents as Tools
# ============================================

@tool
def analyze_budget(request: str) -> str:
    """Analyze spending patterns, budgets, and provide budget-related insights.

    Use for questions about:
    - Monthly/weekly spending analysis
    - Budget vs actual comparisons
    - Spending trends and patterns
    - Budget alerts and notifications

    Args:
        request: Natural language request about budgeting
    """
    result = budget_agent.invoke({
        "messages": [{"role": "user", "content": request}]
    })
    return result["messages"][-1].content


@tool
def analyze_investments(request: str) -> str:
    """Analyze investment portfolio performance and allocation.

    Use for questions about:
    - Portfolio performance and returns
    - Asset allocation and diversification
    - Rebalancing recommendations
    - Investment risk metrics

    Args:
        request: Natural language request about investments
    """
    result = investment_agent.invoke({
        "messages": [{"role": "user", "content": request}]
    })
    return result["messages"][-1].content


@tool
def analyze_taxes(request: str) -> str:
    """Provide tax planning analysis and optimization strategies.

    Use for questions about:
    - Tax liability estimates
    - Tax optimization opportunities
    - Tax-loss harvesting
    - Retirement contribution strategies

    Args:
        request: Natural language request about taxes
    """
    result = tax_agent.invoke({
        "messages": [{"role": "user", "content": request}]
    })
    return result["messages"][-1].content


# ============================================
# Layer 3: Supervisor Agent (Top Layer)
# ============================================

supervisor = create_agent(
    model,
    tools=[analyze_budget, analyze_investments, analyze_taxes],
    system_prompt=FINANCE_SUPERVISOR_PROMPT,
    name="finance_supervisor",
    middleware=SUPERVISOR_MIDDLEWARE,
    checkpointer=checkpointer,
)

# Export the compiled supervisor
app = supervisor


# ============================================
# Example Usage
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("SUBAGENTS PATTERN: Personal Finance Assistant")
    print("=" * 60)
    print("\nArchitecture:")
    print("  Layer 3: Supervisor Agent (routes and coordinates)")
    print("  Layer 2: Sub-Agents (budget, investment, tax specialists)")
    print("  Layer 1: Low-Level Tools (API calls, calculations)")
    print("=" * 60)

    # Example queries demonstrating multi-domain coordination
    queries = [
        # Single domain query
        "How did my spending compare to budget last month?",

        # Multi-domain query requiring coordination
        "I want to reduce my tax burden. Review my portfolio for tax-loss harvesting "
        "opportunities and suggest retirement contribution optimizations.",

        # Complex cross-domain analysis
        "Give me a complete financial health check - analyze my spending habits, "
        "portfolio performance, and tax situation. What should I prioritize?",
    ]

    # Config with thread_id for checkpointer
    config = {"configurable": {"thread_id": "finance_demo_session"}}

    for i, query in enumerate(queries, 1):
        print(f"\n{'='*60}")
        print(f"Query {i}: {query}")
        print("-" * 60)

        # Stream the response to see the agent's reasoning
        for step in app.stream({"messages": [{"role": "user", "content": query}]}, config=config):
            for key, value in step.items():
                if value and "messages" in value:
                    for msg in value["messages"]:
                        if hasattr(msg, 'content') and msg.content:
                            print(f"\n[{key}]: {msg.content[:500]}...")
