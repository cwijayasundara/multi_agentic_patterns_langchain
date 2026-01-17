"""
Knowledge base tools for the router pattern.

Provides search tools for:
- Technical documentation
- FAQs
- Tutorials
"""

from agentic_patterns.tools.knowledge.search import (
    search_docs,
    search_faq,
    search_tutorials,
    DOCS_KNOWLEDGE,
    FAQ_KNOWLEDGE,
    TUTORIAL_KNOWLEDGE,
)

# Tool collection for easy import
KNOWLEDGE_TOOLS = [search_docs, search_faq, search_tutorials]

__all__ = [
    "search_docs",
    "search_faq",
    "search_tutorials",
    "DOCS_KNOWLEDGE",
    "FAQ_KNOWLEDGE",
    "TUTORIAL_KNOWLEDGE",
    "KNOWLEDGE_TOOLS",
]
