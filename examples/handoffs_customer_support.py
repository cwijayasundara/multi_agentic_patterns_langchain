"""
Handoffs Pattern: Customer Support State Machine
=================================================
A state machine where a single agent's behavior dynamically changes based on workflow state.
The agent's configuration (system prompt + tools) updates based on the current step.

Key Concepts:
- current_step field drives the workflow
- Tools return Command objects that update state AND transition steps
- Middleware applies step-specific configuration
- State persists across conversation turns via checkpointer

Middleware (Context Engineering):
- HumanInTheLoopMiddleware: Require approval for sensitive actions (refunds, discounts)
- ModelCallLimitMiddleware: Prevent infinite loops in complex conversations
- ContextEditingMiddleware: Clear old tool outputs to manage token usage
- SummarizationMiddleware: Compress long support conversations

Reference:
- https://docs.langchain.com/oss/python/langchain/multi-agent/handoffs-customer-support
- https://docs.langchain.com/oss/python/langchain/middleware/built-in
"""

from langchain.agents import create_agent

# Import from the agentic_patterns package
from agentic_patterns.core import (
    get_model,
    get_memory_checkpointer,
    create_support_middleware,
)
from agentic_patterns.tools.support import SUPPORT_TOOLS
from agentic_patterns.state.support import SupportState
from agentic_patterns.agents.support import (
    BASE_SUPPORT_PROMPT,
    STEP_CONFIG,
    get_step_config,
)


# Initialize model and checkpointer
model = get_model()
checkpointer = get_memory_checkpointer()

# Get middleware stack
SUPPORT_MIDDLEWARE = create_support_middleware()


# ============================================
# Create Agent with Checkpointer
# ============================================

agent = create_agent(
    model,
    tools=SUPPORT_TOOLS,
    system_prompt=BASE_SUPPORT_PROMPT,
    checkpointer=checkpointer,
    middleware=SUPPORT_MIDDLEWARE,
)

app = agent


# ============================================
# Helper Functions
# ============================================

def start_support_session() -> dict:
    """Create initial state for a new support session."""
    return {
        "current_step": "greeting"
    }


def chat(message: str, thread_id: str = "default") -> str:
    """Send a message and get a response.

    Args:
        message: User message
        thread_id: Conversation thread ID for state persistence

    Returns:
        Agent's response
    """
    config = {"configurable": {"thread_id": thread_id}}

    result = app.invoke(
        {"messages": [{"role": "user", "content": message}]},
        config=config
    )

    return result["messages"][-1].content


# ============================================
# Example Usage
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("HANDOFFS PATTERN: Customer Support State Machine")
    print("=" * 60)
    print("\nWorkflow Steps:")
    print("  greeting → issue_collector → specialist → resolution")
    print("\nTools drive transitions by updating current_step in state.")
    print("=" * 60)

    # Simulate a support conversation
    thread_id = "demo_session_1"
    config = {"configurable": {"thread_id": thread_id}}

    conversation = [
        "Hi, I need help with my account",
        "My customer ID is C001",
        "I was charged twice for last month's subscription",
        "Yes, please process a refund for the duplicate charge of $29.99",
    ]

    for i, message in enumerate(conversation, 1):
        print(f"\n{'='*60}")
        print(f"Turn {i}")
        print(f"Customer: {message}")
        print("-" * 60)

        result = app.invoke(
            {"messages": [{"role": "user", "content": message}]},
            config=config
        )

        response = result["messages"][-1].content
        print(f"Agent: {response}")

        # Show current state (for demo purposes)
        state = app.get_state(config)
        current_step = state.values.get("current_step", "greeting")
        print(f"\n[State: current_step={current_step}]")
