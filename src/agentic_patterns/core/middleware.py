"""
Middleware preset factories for each agent pattern.

Each pattern has specific context engineering requirements:
- Subagents: Tool retry + summarization + model fallback
- Support: Human approval + call limits + context editing + summarization
- Skills: Tool selector + skill limits + context editing + summarization
"""

from langchain.agents.middleware import (
    SummarizationMiddleware,
    ToolRetryMiddleware,
    ModelFallbackMiddleware,
    HumanInTheLoopMiddleware,
    ModelCallLimitMiddleware,
    ContextEditingMiddleware,
    ClearToolUsesEdit,
    LLMToolSelectorMiddleware,
    ToolCallLimitMiddleware,
)


def create_subagent_middleware():
    """Create middleware stack for subagents (lighter weight).

    Returns:
        List of middleware for subagent use:
        - ToolRetryMiddleware: Retry failed tool calls with exponential backoff
    """
    tool_retry = ToolRetryMiddleware(
        max_retries=2,
        backoff_factor=2.0,
        initial_delay=1.0,
        jitter=True,
    )
    return [tool_retry]


def create_supervisor_middleware(
    summarization_trigger: int = 4000,
    summarization_keep: int = 10,
):
    """Create middleware stack for supervisor agents (full context management).

    Args:
        summarization_trigger: Token threshold to start summarizing
        summarization_keep: Number of recent messages to preserve

    Returns:
        List of middleware for supervisor use:
        - SummarizationMiddleware: Compress conversation history
        - ToolRetryMiddleware: Retry failed tool calls
        - ModelFallbackMiddleware: Switch to backup model on failures
    """
    summarization = SummarizationMiddleware(
        model="gpt-4o-mini",
        trigger=("tokens", summarization_trigger),
        keep=("messages", summarization_keep),
    )
    tool_retry = ToolRetryMiddleware(
        max_retries=2,
        backoff_factor=2.0,
        initial_delay=1.0,
        jitter=True,
    )
    model_fallback = ModelFallbackMiddleware(
        "gpt-4o-mini",
        "gpt-4o",  # Fallback to more capable OpenAI model
    )
    return [summarization, tool_retry, model_fallback]


def create_support_middleware(
    approval_tools: dict = None,
    thread_limit: int = 50,
    run_limit: int = 10,
    context_trigger: int = 50000,
    context_keep: int = 5,
    summarization_trigger: int = 6000,
    summarization_keep: int = 15,
):
    """Create middleware stack for customer support agents.

    Args:
        approval_tools: Dict mapping tool names to approval requirement (True/False)
        thread_limit: Max model calls per conversation thread
        run_limit: Max model calls per single turn
        context_trigger: Token threshold to clear old tool outputs
        context_keep: Number of recent tool results to preserve
        summarization_trigger: Token threshold to start summarizing
        summarization_keep: Number of recent messages to preserve

    Returns:
        List of middleware for support use:
        - HumanInTheLoopMiddleware: Require approval for sensitive actions
        - ModelCallLimitMiddleware: Prevent infinite loops
        - ContextEditingMiddleware: Clear old tool outputs
        - SummarizationMiddleware: Compress long conversations
    """
    if approval_tools is None:
        approval_tools = {
            "process_refund": True,
            "apply_discount": True,
            "create_engineering_ticket": False,
            "resolve_ticket": False,
        }

    human_approval = HumanInTheLoopMiddleware(
        interrupt_on=approval_tools,
        description_prefix="Support action pending approval",
    )
    call_limit = ModelCallLimitMiddleware(
        thread_limit=thread_limit,
        run_limit=run_limit,
        exit_behavior="end",
    )
    context_edit = ContextEditingMiddleware(
        edits=[
            ClearToolUsesEdit(
                trigger=context_trigger,
                keep=context_keep,
                placeholder="[Previous tool output cleared for context management]",
            ),
        ],
    )
    summarization = SummarizationMiddleware(
        model="gpt-4o-mini",
        trigger=("tokens", summarization_trigger),
        keep=("messages", summarization_keep),
    )
    return [human_approval, call_limit, context_edit, summarization]


def create_skills_middleware(
    max_tools: int = 4,
    always_include_tools: list = None,
    skill_thread_limit: int = 10,
    context_trigger: int = 60000,
    context_keep: int = 3,
    exclude_tools_from_clearing: list = None,
    summarization_trigger: int = 8000,
    summarization_keep: int = 20,
):
    """Create middleware stack for skills-based agents.

    Args:
        max_tools: Maximum tools to select per query
        always_include_tools: Tools to always include in selection
        skill_thread_limit: Max skill loads per thread
        context_trigger: Token threshold to clear old tool outputs
        context_keep: Number of recent tool results to preserve
        exclude_tools_from_clearing: Tools to exclude from context clearing
        summarization_trigger: Token threshold to start summarizing
        summarization_keep: Number of recent messages to preserve

    Returns:
        List of middleware for skills-based agents:
        - LLMToolSelectorMiddleware: Select relevant tools
        - ToolCallLimitMiddleware: Limit skill loads
        - ContextEditingMiddleware: Clear old skill content
        - SummarizationMiddleware: Compress long sessions
    """
    if always_include_tools is None:
        always_include_tools = ["load_skill", "list_available_skills"]
    if exclude_tools_from_clearing is None:
        exclude_tools_from_clearing = ["generate_boilerplate"]

    tool_selector = LLMToolSelectorMiddleware(
        model="gpt-4o-mini",
        max_tools=max_tools,
        always_include=always_include_tools,
    )
    skill_limit = ToolCallLimitMiddleware(
        tool_name="load_skill",
        thread_limit=skill_thread_limit,
        exit_behavior="continue",
    )
    context_edit = ContextEditingMiddleware(
        edits=[
            ClearToolUsesEdit(
                trigger=context_trigger,
                keep=context_keep,
                exclude_tools=exclude_tools_from_clearing,
                placeholder="[Skill content cleared - reload if needed]",
            ),
        ],
    )
    summarization = SummarizationMiddleware(
        model="gpt-4o-mini",
        trigger=("tokens", summarization_trigger),
        keep=("messages", summarization_keep),
    )
    return [tool_selector, skill_limit, context_edit, summarization]
