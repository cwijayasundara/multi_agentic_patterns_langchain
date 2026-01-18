---
name: hierarchical-teams
title: Hierarchical Teams
description: Multi-level hierarchy where team leads are LangGraph subgraphs coordinating specialists
category: multi-agent
complexity: high
---

## When to Use

- Complex nested workflows with multiple levels of coordination
- Large organizations with team-based structures
- Team-level encapsulation is important (teams operate independently)
- Team leads need to synthesize specialist outputs
- Top supervisor coordinates across multiple teams
- Different teams may have different tooling and expertise

## When NOT to Use

- Flat coordination is sufficient (use **Subagents**)
- Simple workflows with few agents
- All agents can report directly to one supervisor
- You don't need team-level abstraction

## Key Characteristics

| Capability | Rating |
|------------|--------|
| Organizational Complexity | Very High |
| Team Encapsulation | Very High |
| Scalability | High |
| Setup Complexity | High |
| Coordination Overhead | Medium |

## Decision Triggers

Ask yourself these questions:

1. "Do you need multiple levels of coordination?" -> HIGH fit if yes
2. "Should teams operate as independent workflows?" -> HIGH fit if yes
3. "Do team leads need to synthesize their specialists' work?" -> HIGH fit if yes
4. "Is organizational structure important to model?" -> HIGH fit if yes

## Example Use Cases

- **Software Company**:
  - Top Supervisor
    - Engineering Team (Lead + Backend + Frontend + DevOps)
    - Product Team (Lead + Designer + Researcher + PM)
    - QA Team (Lead + Manual Tester + Automation)

- **Research Organization**:
  - Director
    - Research Team (Lead + Scientists + Analysts)
    - Publications Team (Lead + Writers + Reviewers)

- **Customer Service Org**:
  - Operations Manager
    - Billing Team (Lead + Specialists)
    - Technical Team (Lead + Support Engineers)
    - Escalation Team (Lead + Senior Specialists)

## Trade-offs

**Pros:**
- Mirrors real organizational structures
- Teams can be developed and tested independently
- Clear chain of command and accountability
- Team leads handle intra-team coordination
- Scales well for complex organizations

**Cons:**
- Higher setup and maintenance complexity
- More latency due to multiple coordination levels
- Potential for miscommunication between teams
- May be overkill for simpler use cases

## Architecture Pattern

```
User <-> Top Supervisor
              |
    +---------+---------+
    |         |         |
  Team A    Team B    Team C
  (Lead)    (Lead)    (Lead)
    |         |         |
  +---+     +---+     +---+
  |   |     |   |     |   |
 S1  S2    S3  S4    S5  S6
(specialists)
```

## Code Reference

See: `examples/hierarchical_teams.py`

## Key APIs

- `StateGraph` for defining teams as subgraphs
- Nested subgraph compilation
- Team leads as intermediate coordinators
- Top supervisor coordinates team leads
