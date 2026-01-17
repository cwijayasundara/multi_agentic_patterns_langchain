"""
Router Pattern: Multi-Source Knowledge Base
===========================================
A routing step classifies input and directs it to specialized agents in parallel,
with results synthesized into a combined response.

Key Concepts:
- Structured output (Pydantic) for classification decisions
- Send() for parallel agent dispatch
- operator.add reducer for collecting results
- Synthesis phase combines results into coherent response

Middleware (Context Engineering):
- ModelRetryMiddleware: Resilient classification and synthesis calls
- ModelFallbackMiddleware: Automatic failover for high availability
- PIIDetectionMiddleware: Protect sensitive data in knowledge base queries

Note: Since router uses StateGraph (not create_agent), middleware is applied
differently - we wrap model calls directly in node functions.

Reference:
- https://docs.langchain.com/oss/python/langchain/multi-agent/router-knowledge-base
- https://docs.langchain.com/oss/python/langchain/middleware/built-in
"""

from langgraph.graph import StateGraph, START, END
from langgraph.types import Send

# Import from the agentic_patterns package
from agentic_patterns.core import (
    get_model,
    sanitize_query,
    with_retry_and_fallback,
)
from agentic_patterns.core.config import get_fallback_model
from agentic_patterns.tools.knowledge import (
    search_docs,
    search_faq,
    search_tutorials,
)
from agentic_patterns.state.router import (
    RouterState,
    AgentInput,
    ClassificationResult,
)
from agentic_patterns.agents.knowledge import (
    CLASSIFICATION_PROMPT,
    SYNTHESIS_PROMPT,
)


# Initialize models
model = get_model()
fallback_model = get_fallback_model()


# ============================================
# Classification Phase
# ============================================

def classify_query(state: RouterState) -> dict:
    """Classify the user's query and determine which agents to invoke.

    Uses structured output to ensure valid classification decisions.
    Includes PII redaction and retry/fallback for resilience.
    """
    # Context Engineering: Sanitize query before processing
    sanitized_query = sanitize_query(state["query"])

    def primary_classify():
        structured_llm = model.with_structured_output(ClassificationResult)
        return structured_llm.invoke(
            CLASSIFICATION_PROMPT.format(query=sanitized_query)
        )

    def fallback_classify():
        structured_llm = fallback_model.with_structured_output(ClassificationResult)
        return structured_llm.invoke(
            CLASSIFICATION_PROMPT.format(query=sanitized_query)
        )

    # Apply retry with fallback
    classify_fn = with_retry_and_fallback(
        primary_classify,
        fallback_classify,
        max_retries=2,
    )

    result = classify_fn()

    return {
        "classifications": [
            {"source": c.source, "query": c.query, "relevance": c.relevance}
            for c in result.classifications
        ]
    }


# ============================================
# Parallel Dispatch with Send()
# ============================================

def route_to_agents(state: RouterState) -> list[Send]:
    """Map classifications to Send objects for parallel execution.

    Each agent receives only its targeted query, maintaining clean interfaces.
    """
    if not state["classifications"]:
        # No relevant sources - go directly to synthesis
        return [Send("synthesize", state)]

    sends = []
    for classification in state["classifications"]:
        source = classification["source"]
        sends.append(Send(
            f"{source}_agent",
            {"query": classification["query"]}
        ))

    return sends


# ============================================
# Specialized Agent Nodes
# ============================================

def docs_agent(state: AgentInput) -> dict:
    """Technical documentation agent."""
    query = state["query"]

    # Use the search tool
    search_result = search_docs.invoke({"query": query})

    # Generate a focused response
    response = model.invoke(
        f"""You are a technical documentation expert. Based on the following documentation,
answer this question concisely: {query}

Documentation:
{search_result}

Provide a clear, technical answer. Include code examples if relevant."""
    )

    return {"results": [{"source": "docs", "result": response.content}]}


def faq_agent(state: AgentInput) -> dict:
    """FAQ agent."""
    query = state["query"]

    search_result = search_faq.invoke({"query": query})

    response = model.invoke(
        f"""You are a customer support FAQ specialist. Based on these FAQs,
answer this question helpfully: {query}

FAQs:
{search_result}

Be friendly and direct. If the FAQ doesn't cover the question exactly, provide the closest relevant information."""
    )

    return {"results": [{"source": "faq", "result": response.content}]}


def tutorial_agent(state: AgentInput) -> dict:
    """Tutorial agent."""
    query = state["query"]

    search_result = search_tutorials.invoke({"query": query})

    response = model.invoke(
        f"""You are a developer advocate helping users learn. Based on these tutorials,
answer this question with practical guidance: {query}

Tutorials:
{search_result}

Focus on actionable steps. Include code snippets where helpful."""
    )

    return {"results": [{"source": "tutorial", "result": response.content}]}


# ============================================
# Synthesis Phase
# ============================================

def synthesize_results(state: RouterState) -> dict:
    """Combine results from all sources into a coherent response.

    Handles cases where no results were found or only partial information is available.
    Includes retry/fallback for resilience.
    """
    if not state.get("results"):
        return {
            "final_answer": "I couldn't find relevant information in our knowledge base "
                           "for your question. Please try rephrasing or contact support "
                           "for more specific assistance."
        }

    # Format results by source
    formatted_results = "\n\n".join([
        f"**From {r['source'].upper()}:**\n{r['result']}"
        for r in state["results"]
    ])

    # Sanitize the original query in the synthesis prompt
    sanitized_query = sanitize_query(state["query"])

    def primary_synthesize():
        return model.invoke(
            SYNTHESIS_PROMPT.format(
                query=sanitized_query,
                formatted_results=formatted_results
            )
        )

    def fallback_synthesize():
        return fallback_model.invoke(
            SYNTHESIS_PROMPT.format(
                query=sanitized_query,
                formatted_results=formatted_results
            )
        )

    # Apply retry with fallback
    synthesize_fn = with_retry_and_fallback(
        primary_synthesize,
        fallback_synthesize,
        max_retries=2,
    )

    response = synthesize_fn()

    return {"final_answer": response.content}


# ============================================
# Build Workflow Graph
# ============================================

workflow = StateGraph(RouterState)

# Add nodes
workflow.add_node("classify", classify_query)
workflow.add_node("docs_agent", docs_agent)
workflow.add_node("faq_agent", faq_agent)
workflow.add_node("tutorial_agent", tutorial_agent)
workflow.add_node("synthesize", synthesize_results)

# Add edges
workflow.add_edge(START, "classify")

# Conditional routing based on classification
workflow.add_conditional_edges(
    "classify",
    route_to_agents,
    ["docs_agent", "faq_agent", "tutorial_agent", "synthesize"]
)

# All agents flow to synthesis
workflow.add_edge("docs_agent", "synthesize")
workflow.add_edge("faq_agent", "synthesize")
workflow.add_edge("tutorial_agent", "synthesize")
workflow.add_edge("synthesize", END)

# Compile
app = workflow.compile()


# ============================================
# Helper Functions
# ============================================

def query_knowledge_base(question: str) -> str:
    """Query the knowledge base with a question.

    Args:
        question: User's question

    Returns:
        Synthesized answer from relevant sources
    """
    result = app.invoke({"query": question})
    return result["final_answer"]


def query_with_trace(question: str) -> dict:
    """Query with full trace of which sources were consulted.

    Args:
        question: User's question

    Returns:
        Dict with final_answer, sources_consulted, and classifications
    """
    result = app.invoke({"query": question})
    return {
        "question": question,
        "classifications": result.get("classifications", []),
        "sources_consulted": [r["source"] for r in result.get("results", [])],
        "final_answer": result["final_answer"]
    }


# ============================================
# Example Usage
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("ROUTER PATTERN: Multi-Source Knowledge Base")
    print("=" * 60)
    print("\nArchitecture:")
    print("  [Query] → [Classify] → [Parallel Agents] → [Synthesize]")
    print("\nSources: docs, faq, tutorial")
    print("=" * 60)

    # Example queries demonstrating different routing scenarios
    queries = [
        # Single source query
        "What payment methods do you accept?",

        # Multi-source query
        "How do I get started with the API and what does it cost?",

        # Technical query
        "How do I authenticate API requests and what are the rate limits?",

        # Tutorial query
        "How do I set up webhooks to receive real-time events?",
    ]

    for i, query in enumerate(queries, 1):
        print(f"\n{'='*60}")
        print(f"Query {i}: {query}")
        print("-" * 60)

        result = query_with_trace(query)

        print(f"\nClassifications: {len(result['classifications'])}")
        for c in result['classifications']:
            print(f"  - {c['source']}: {c['query'][:50]}...")

        print(f"\nSources consulted: {result['sources_consulted']}")
        print(f"\nAnswer:\n{result['final_answer'][:500]}...")
