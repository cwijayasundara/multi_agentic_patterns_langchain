"""
Pattern Selector Agent - Main agent creation and entry point.

Uses the Skills Pattern approach:
- Pattern knowledge loaded on demand (progressive disclosure)
- Middleware for context management and tool selection
- Phase-based conversation flow (gather -> clarify -> recommend)

This agent helps users choose the right agentic architecture pattern
from the 9 patterns available in the LangChain/LangGraph ecosystem.

Usage:
    from pattern_selector_agent import create_selector_agent, chat

    # Create the agent
    agent = create_selector_agent()

    # Chat with the agent
    response = chat("I want to build a customer support system", agent=agent)
"""

from langchain.agents import create_agent

# Import from the agentic_patterns package
from agentic_patterns.core import get_model, get_memory_checkpointer

# Import local modules
from pattern_selector_agent.tools import SELECTOR_TOOLS, reset_loaded_patterns
from pattern_selector_agent.prompts import SELECTOR_SYSTEM_PROMPT
from pattern_selector_agent.middleware import create_selector_middleware


def create_selector_agent(
    model=None,
    checkpointer=None,
    system_prompt: str = None,
    middleware=None,
):
    """Create the Pattern Selector Agent using Skills pattern approach.

    The agent uses progressive disclosure:
    - Starts with brief pattern summaries in the system prompt
    - Loads full pattern details on demand via load_pattern() tool
    - Middleware manages context to prevent bloat from loaded patterns

    Args:
        model: Optional LLM model (defaults to get_model())
        checkpointer: Optional checkpointer (defaults to get_memory_checkpointer())
        system_prompt: Optional custom system prompt
        middleware: Optional middleware stack (defaults to create_selector_middleware())

    Returns:
        Configured agent instance with Skills-pattern behavior
    """
    if model is None:
        model = get_model()

    if checkpointer is None:
        checkpointer = get_memory_checkpointer()

    if system_prompt is None:
        system_prompt = SELECTOR_SYSTEM_PROMPT

    if middleware is None:
        middleware = create_selector_middleware()

    agent = create_agent(
        model=model,
        tools=SELECTOR_TOOLS,
        system_prompt=system_prompt,
        checkpointer=checkpointer,
        middleware=middleware,
    )

    return agent


def chat(
    message: str,
    agent=None,
    thread_id: str = "default",
    config: dict = None,
) -> str:
    """Send a message to the Pattern Selector Agent.

    Args:
        message: User message
        agent: Agent instance (creates one if not provided)
        thread_id: Conversation thread ID for state persistence
        config: Optional config dict (overrides thread_id if provided)

    Returns:
        Agent's response text
    """
    if agent is None:
        agent = create_selector_agent()

    if config is None:
        config = {"configurable": {"thread_id": thread_id}}

    result = agent.invoke(
        {"messages": [{"role": "user", "content": message}]},
        config=config,
    )

    return result["messages"][-1].content


def run_interactive():
    """Run the Pattern Selector Agent in interactive mode.

    This is the main entry point for CLI usage.
    Uses the Skills pattern with progressive pattern loading.
    """
    print("=" * 60)
    print("PATTERN SELECTOR: Choose Your Agentic Architecture")
    print("=" * 60)
    print()
    print("I help you choose the right pattern from 9 agentic architectures.")
    print()
    print("Patterns are loaded on demand (Skills pattern approach):")
    print("  - I start with brief summaries of all patterns")
    print("  - I load full details only when discussing specific patterns")
    print("  - This keeps our conversation focused and context-efficient")
    print()
    print("Available patterns:")
    print("  subagents, deep-agents, supervisor-forward, hierarchical-teams,")
    print("  context-quarantine, skills, handoffs, router, custom-workflows")
    print()
    print("Describe your problem and I'll recommend the best pattern(s).")
    print("Type 'quit' or 'exit' to end. Type 'reset' for a new conversation.")
    print("=" * 60)
    print()

    # Create agent and config
    agent = create_selector_agent()
    thread_id = "interactive_session"
    config = {"configurable": {"thread_id": thread_id}}

    while True:
        try:
            # Get user input
            user_input = input("You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["quit", "exit", "q"]:
                print("\nGoodbye! Happy building!")
                break

            if user_input.lower() == "reset":
                # Reset session - clear loaded patterns and create fresh thread
                reset_loaded_patterns()
                thread_id = f"interactive_session_{hash(user_input)}"
                config = {"configurable": {"thread_id": thread_id}}
                print("\n[Session reset. Loaded patterns cleared.]\n")
                continue

            if user_input.lower() == "loaded":
                # Show which patterns are currently loaded in context
                from pattern_selector_agent.tools import get_loaded_patterns
                loaded = get_loaded_patterns()
                if loaded:
                    print(f"\n[Patterns in context: {', '.join(loaded)}]\n")
                else:
                    print("\n[No patterns loaded yet]\n")
                continue

            # Get agent response
            print()
            result = agent.invoke(
                {"messages": [{"role": "user", "content": user_input}]},
                config=config,
            )

            response = result["messages"][-1].content
            print(f"Agent: {response}")
            print()

        except KeyboardInterrupt:
            print("\n\nGoodbye! Happy building!")
            break
        except Exception as e:
            print(f"\nError: {e}")
            print("Please try again or type 'quit' to exit.\n")


# Create a default agent instance for module-level access
_default_agent = None


def get_default_agent():
    """Get or create the default agent instance."""
    global _default_agent
    if _default_agent is None:
        _default_agent = create_selector_agent()
    return _default_agent


# Module-level app for consistency with other examples
app = None


def get_app():
    """Get or create the module-level app instance."""
    global app
    if app is None:
        app = create_selector_agent()
    return app
