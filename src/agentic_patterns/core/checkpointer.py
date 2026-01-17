"""
Checkpointer setup for state persistence.

Provides factory functions for creating checkpointers
used across different agent patterns.
"""

from langgraph.checkpoint.memory import InMemorySaver


def get_memory_checkpointer():
    """Create an in-memory checkpointer for state persistence.

    The InMemorySaver stores conversation state in memory, enabling:
    - Pause/resume of agent sessions
    - Multi-turn conversations with context
    - State tracking for middleware (e.g., SummarizationMiddleware)

    Returns:
        InMemorySaver instance

    Note:
        For production use, consider using a persistent checkpointer
        like PostgresSaver or RedisSaver from langgraph.checkpoint.
    """
    return InMemorySaver()
