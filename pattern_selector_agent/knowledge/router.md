---
name: router
title: Router (Parallel Dispatch)
description: StateGraph classifies queries and dispatches to specialized agents in parallel using Send()
category: workflow
complexity: medium
---

## When to Use

- Single queries may need multiple knowledge sources
- Parallel execution of searches/lookups is beneficial
- Query classification determines which agents to invoke
- Results need to be synthesized from multiple sources
- Structured output for type-safe routing
- Stateless query handling (no conversation context needed)

## When NOT to Use

- Sequential processing is required
- Only one agent per query
- Need conversation state across queries (use **Handoffs**)
- Complex multi-turn coordination (use **Subagents**)

## Key Characteristics

| Capability | Rating |
|------------|--------|
| Parallel Dispatch | Very High |
| Query Classification | High |
| Result Synthesis | High |
| Stateful Conversations | Low |
| Setup Complexity | Medium |

## Decision Triggers

Ask yourself these questions:

1. "Can queries be classified to determine routing?" -> HIGH fit if yes
2. "Should multiple sources be queried in parallel?" -> HIGH fit if yes
3. "Do results need synthesis from multiple agents?" -> HIGH fit if yes
4. "Are queries mostly stateless/independent?" -> HIGH fit if yes

## Example Use Cases

- **Knowledge Base**:
  - Classify: "How do I reset my password?"
  - Route to: FAQ agent + Tutorial agent (parallel)
  - Synthesize: Combined response

- **Search System**:
  - Classify: "Find Python async tutorials"
  - Route to: Docs, Tutorials, Examples agents (parallel)
  - Synthesize: Ranked results

- **Support Triage**:
  - Classify: Issue type
  - Route to: Relevant knowledge bases (parallel)
  - Synthesize: Comprehensive answer

- **Multi-Source Research**:
  - Classify: Research topic
  - Route to: Academic, News, Industry agents (parallel)
  - Synthesize: Research summary

## Trade-offs

**Pros:**
- Fast parallel execution
- Single query can hit multiple sources
- Type-safe routing with structured output
- Clear separation of knowledge domains
- Easy to add new routing targets

**Cons:**
- No conversation memory by default
- Classification must be accurate
- Synthesis may be complex
- Higher API costs (parallel calls)

## Architecture Pattern

```
User Query
    |
Classifier (LLM + structured output)
    |
    +-> Agent A (parallel)
    +-> Agent B (parallel)  } via Send()
    +-> Agent C (parallel)
    |
Synthesizer (combines results)
    |
User Response
```

## Code Reference

See: `examples/router_knowledge_base.py`

## Key APIs

- `StateGraph` for workflow definition
- `Send()` for parallel dispatch
- Pydantic models for structured output (ClassificationResult)
- `add_conditional_edges()` for routing logic
- Synthesis node to combine results
