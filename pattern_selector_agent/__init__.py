"""
Pattern Selector Agent - Help users choose the right agentic architecture.

This package uses the **Skills pattern** to progressively load pattern
documentation on demand, combined with Handoffs-style conversation phases.

Key Features:
- Progressive disclosure: Pattern details loaded only when needed
- Context management: Middleware clears old pattern content to prevent bloat
- Phase-based flow: gather -> clarify -> recommend

Usage:
    # Interactive CLI
    python -m pattern_selector_agent

    # Programmatic usage
    from pattern_selector_agent import create_selector_agent, chat

    agent = create_selector_agent()
    response = chat("I want to build a customer support system", agent=agent)

Available Patterns:
    1. Subagents - Supervisor coordinates specialized subagents
    2. Deep Agents - Context-isolated subagents for tool-heavy work
    3. Supervisor Forward - Forward responses verbatim (compliance)
    4. Hierarchical Teams - Multi-level team hierarchy
    5. Context Quarantine - Isolate large outputs via summarization
    6. Skills - Single agent with dynamic prompt specializations
    7. Handoffs - State machine with stage-based progression
    8. Router - Classify and dispatch queries in parallel
    9. Custom Workflows - StateGraph with conditional edges
"""

from pattern_selector_agent.agent import (
    create_selector_agent,
    chat,
    run_interactive,
    get_app,
)

from pattern_selector_agent.middleware import create_selector_middleware

from pattern_selector_agent.state import (
    SelectorState,
    SelectorPhase,
    Requirement,
    Clarification,
    Recommendation,
)

from pattern_selector_agent.tools import (
    SELECTOR_TOOLS,
    PATTERN_TOOLS,
    DECISION_TOOLS,
    list_all_patterns,
    load_pattern,
    search_patterns,
    get_pattern_comparison,
    get_pattern_decision_tree,
    evaluate_requirements,
    analyze_use_case,
    get_clarifying_questions,
    reset_loaded_patterns,
)

from pattern_selector_agent.prompts import SELECTOR_SYSTEM_PROMPT


__version__ = "0.1.0"

__all__ = [
    # Agent
    "create_selector_agent",
    "chat",
    "run_interactive",
    "get_app",
    # Middleware
    "create_selector_middleware",
    # State
    "SelectorState",
    "SelectorPhase",
    "Requirement",
    "Clarification",
    "Recommendation",
    # Tools
    "SELECTOR_TOOLS",
    "PATTERN_TOOLS",
    "DECISION_TOOLS",
    "list_all_patterns",
    "load_pattern",
    "search_patterns",
    "get_pattern_comparison",
    "get_pattern_decision_tree",
    "evaluate_requirements",
    "analyze_use_case",
    "get_clarifying_questions",
    "reset_loaded_patterns",
    # Prompts
    "SELECTOR_SYSTEM_PROMPT",
]
