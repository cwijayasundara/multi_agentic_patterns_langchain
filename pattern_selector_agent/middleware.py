"""
Middleware configuration for the Pattern Selector Agent.

Uses Skills pattern middleware for progressive pattern loading:
- LLMToolSelectorMiddleware: Select relevant tools before main call
- ToolCallLimitMiddleware: Limit pattern loads per thread
- ContextEditingMiddleware: Clear old pattern content when context fills
- SummarizationMiddleware: Compress long sessions
"""

from langchain.agents.middleware import (
    SummarizationMiddleware,
    ContextEditingMiddleware,
    ClearToolUsesEdit,
    LLMToolSelectorMiddleware,
    ToolCallLimitMiddleware,
)


def create_selector_middleware(
    max_tools: int = 5,
    always_include_tools: list = None,
    pattern_thread_limit: int = 9,  # All 9 patterns at most
    context_trigger: int = 50000,
    context_keep: int = 3,
    exclude_tools_from_clearing: list = None,
    summarization_trigger: int = 8000,
    summarization_keep: int = 15,
):
    """Create middleware stack for the Pattern Selector Agent.

    Follows the Skills pattern approach:
    - Progressive disclosure: Only load pattern details when needed
    - Context management: Clear old pattern content to prevent bloat
    - Smart tool selection: Route to relevant tools based on query

    Args:
        max_tools: Maximum tools to select per query
        always_include_tools: Tools to always include in selection
        pattern_thread_limit: Max pattern loads per thread
        context_trigger: Token threshold to clear old tool outputs
        context_keep: Number of recent tool results to preserve
        exclude_tools_from_clearing: Tools to exclude from context clearing
        summarization_trigger: Token threshold to start summarizing
        summarization_keep: Number of recent messages to preserve

    Returns:
        List of middleware for the pattern selector agent
    """
    if always_include_tools is None:
        always_include_tools = [
            "load_pattern",
            "list_all_patterns",
            "get_pattern_decision_tree",
        ]

    if exclude_tools_from_clearing is None:
        exclude_tools_from_clearing = [
            "get_pattern_comparison",
            "evaluate_requirements",
        ]

    # Select relevant tools based on query
    tool_selector = LLMToolSelectorMiddleware(
        model="gpt-4o-mini",
        max_tools=max_tools,
        always_include=always_include_tools,
    )

    # Limit how many patterns can be loaded per session
    pattern_limit = ToolCallLimitMiddleware(
        tool_name="load_pattern",
        thread_limit=pattern_thread_limit,
        exit_behavior="continue",  # Allow conversation to continue after limit
    )

    # Clear old pattern content when context grows too large
    context_edit = ContextEditingMiddleware(
        edits=[
            ClearToolUsesEdit(
                trigger=context_trigger,
                keep=context_keep,
                exclude_tools=exclude_tools_from_clearing,
                placeholder="[Pattern content cleared - use load_pattern to reload if needed]",
            ),
        ],
    )

    # Summarize long conversations
    summarization = SummarizationMiddleware(
        model="gpt-4o-mini",
        trigger=("tokens", summarization_trigger),
        keep=("messages", summarization_keep),
    )

    return [tool_selector, pattern_limit, context_edit, summarization]
