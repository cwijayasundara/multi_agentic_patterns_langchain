"""
Tools for the Pattern Selector Agent.

Exports:
- Pattern tools: list_all_patterns, load_pattern, search_patterns, etc.
- Decision tools: evaluate_requirements, analyze_use_case, etc.
- Combined tool list: SELECTOR_TOOLS
"""

from pattern_selector_agent.tools.patterns import (
    PATTERN_TOOLS,
    list_all_patterns,
    load_pattern,
    search_patterns,
    get_pattern_comparison,
    get_pattern_decision_tree,
    get_loaded_patterns,
    reset_loaded_patterns,
)

from pattern_selector_agent.tools.decision import (
    DECISION_TOOLS,
    evaluate_requirements,
    analyze_use_case,
    get_clarifying_questions,
)

# Combined tool list for the agent
SELECTOR_TOOLS = PATTERN_TOOLS + DECISION_TOOLS

__all__ = [
    # Pattern tools
    "PATTERN_TOOLS",
    "list_all_patterns",
    "load_pattern",
    "search_patterns",
    "get_pattern_comparison",
    "get_pattern_decision_tree",
    "get_loaded_patterns",
    "reset_loaded_patterns",
    # Decision tools
    "DECISION_TOOLS",
    "evaluate_requirements",
    "analyze_use_case",
    "get_clarifying_questions",
    # Combined
    "SELECTOR_TOOLS",
]
