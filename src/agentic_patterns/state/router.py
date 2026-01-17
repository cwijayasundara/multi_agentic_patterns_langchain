"""
State definitions for the router knowledge base pattern.

Defines:
- AgentInput/AgentOutput: Simple I/O types for subagents
- Classification: Pydantic model for a single routing decision
- ClassificationResult: Pydantic model for complete classification
- RouterState: TypedDict for the router workflow state
"""

import operator
from typing import Annotated, Literal
from typing_extensions import TypedDict
from pydantic import BaseModel, Field


class AgentInput(TypedDict):
    """Simple query passed to each subagent."""
    query: str


class AgentOutput(TypedDict):
    """Result returned by each subagent."""
    source: str
    result: str


class RouterState(TypedDict):
    """Main workflow state tracking query, classifications, results, and final answer.

    The results field uses a reducer (operator.add) to collect parallel outputs
    into a single list.
    """
    query: str
    classifications: list[dict]  # Which agents to invoke with targeted queries
    results: Annotated[list[AgentOutput], operator.add]  # Accumulated from parallel agents
    final_answer: str


class Classification(BaseModel):
    """A single classification decision."""
    source: Literal["docs", "faq", "tutorial"] = Field(
        description="Which knowledge source to query"
    )
    query: str = Field(
        description="Targeted sub-question optimized for this source"
    )
    relevance: str = Field(
        description="Why this source is relevant to the user's question"
    )


class ClassificationResult(BaseModel):
    """Result of classifying a user query."""
    classifications: list[Classification] = Field(
        description="List of agents to invoke with targeted sub-questions. "
                   "Only include sources that are relevant - may be empty, one, or multiple."
    )
    reasoning: str = Field(
        description="Brief explanation of the routing decision"
    )
