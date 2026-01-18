---
name: subagents
title: Subagents (Supervisor)
description: Supervisor coordinates specialized subagents for distinct domains
category: multi-agent
complexity: medium
---

## When to Use

- Multiple distinct domains requiring specialized agents (e.g., budget + investment + tax)
- Centralized workflow control needed
- Parallel execution of domain experts is beneficial
- Subagents don't need direct user interaction
- Each domain has its own tool set and expertise
- You want clear separation of concerns between specialists

## When NOT to Use

- Agents need to talk directly to users (use **Handoffs** instead)
- Simple single-domain tasks (use a single agent with tools)
- Context bloat from large tool outputs is a concern (use **Deep Agents** or **Context Quarantine**)
- You need complex nested team structures (use **Hierarchical Teams**)
- Tasks are sequential with state-based progression (use **Handoffs**)

## Key Characteristics

| Capability | Rating |
|------------|--------|
| Distributed Development | High |
| Parallelization | High |
| Context Isolation | Medium |
| Direct User Interaction | Low |
| Coordination Complexity | Medium |

## Decision Triggers

Ask yourself these questions:

1. "Do you need a central coordinator for domain experts?" -> HIGH fit if yes
2. "Do subagents need to talk directly to users?" -> LOW fit if yes
3. "Are domains clearly separable with distinct tool sets?" -> HIGH fit if yes
4. "Can tasks be executed in parallel?" -> HIGH fit if yes

## Example Use Cases

- **Personal Finance**: Budget analyst + Investment advisor + Tax consultant
- **Research System**: Literature researcher + Data analyst + Report writer
- **E-commerce**: Inventory manager + Pricing optimizer + Order fulfillment
- **Multi-service Backend**: Auth service + Payment service + Notification service

## Trade-offs

**Pros:**
- Strong separation of concerns between domains
- Each subagent can be developed and tested independently
- Supervisor can execute subagents in parallel
- Clear accountability for each domain

**Cons:**
- Extra latency (supervisor + subagent calls)
- Subagents cannot interact directly with users
- Supervisor becomes a single point of coordination
- Context must flow through supervisor

## Architecture Pattern

```
User <-> Supervisor Agent
              |
    +---------+---------+
    |         |         |
Subagent  Subagent  Subagent
    A         B         C
```

## Code Reference

See: `examples/subagents_finance_assistant.py`

## Key APIs

- `create_agent()` from `langchain.agents`
- Subagents wrapped as tools for the supervisor
- `get_memory_checkpointer()` for state persistence
