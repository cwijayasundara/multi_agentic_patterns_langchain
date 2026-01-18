---
name: handoffs
title: Handoffs (State Machine)
description: Agents hand off conversations dynamically via Command objects with state-based progression
category: multi-agent
complexity: medium
---

## When to Use

- Workflow has clear stages/phases (greeting -> collect -> resolve)
- Specialists need to talk directly to users
- State-based progression through a workflow
- Only one agent active at a time (no parallelization needed)
- Conversation context must persist across handoffs
- Different prompts/tools for different workflow stages

## When NOT to Use

- Need parallel execution of agents (use **Subagents**)
- No clear workflow stages (use **Router**)
- Central coordinator should synthesize responses (use **Subagents**)
- Stages don't need different tool sets or prompts

## Key Characteristics

| Capability | Rating |
|------------|--------|
| Direct User Interaction | Very High |
| State-Based Flow | Very High |
| Stage Customization | High |
| Parallel Execution | None |
| Conversation Persistence | High |

## Decision Triggers

Ask yourself these questions:

1. "Does the workflow have clear sequential stages?" -> HIGH fit if yes
2. "Do specialists need to talk directly to users?" -> HIGH fit if yes
3. "Is only one agent active at a time?" -> HIGH fit if yes
4. "Do different stages need different prompts or tools?" -> HIGH fit if yes

## Example Use Cases

- **Customer Support**:
  - greeting -> issue_collector -> billing_specialist -> resolution
  - Each stage has specific prompts and tools

- **Onboarding Flow**:
  - welcome -> account_setup -> preferences -> verification -> complete

- **Sales Process**:
  - qualification -> discovery -> proposal -> negotiation -> close

- **Medical Intake**:
  - reception -> symptoms -> triage -> specialist -> discharge

## Trade-offs

**Pros:**
- Clear workflow progression
- Each stage fully customizable
- Specialists interact directly with users
- State persists across entire workflow
- Easy to understand and debug

**Cons:**
- Cannot run stages in parallel
- One active agent at a time
- Handoff logic must be carefully designed
- Sequential processing may be slower

## Architecture Pattern

```
User <-> Stage 1 (greeting)
              |
         [Command: goto Stage 2]
              |
User <-> Stage 2 (issue_collector)
              |
         [Command: goto Stage 3]
              |
User <-> Stage 3 (specialist)
              |
         [Command: goto Stage 4]
              |
User <-> Stage 4 (resolution)
```

## Code Reference

See: `examples/handoffs_customer_support.py`

## Key APIs

- `create_react_agent()` for stage agents
- `Command` from `langgraph.types` for state transitions
- Tools return Command objects to trigger handoffs
- `current_step` field drives workflow configuration
- State persists via checkpointer
