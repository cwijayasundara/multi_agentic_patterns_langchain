---
name: deep-agents
title: Deep Agents
description: Context-isolated subagents that handle tool-heavy work and return only summaries
category: multi-agent
complexity: medium
---

## When to Use

- Tasks require many tool calls with large outputs
- Context management is critical (prevent bloat)
- Main agent needs to maintain coherent reasoning over long conversations
- Subagents should handle data-intensive work independently
- You want automatic planning with task/todo tools
- Intermediate results don't need to be in main context

## When NOT to Use

- Tasks are simple with few tool calls
- You need all intermediate data in the main conversation
- Real-time streaming of subagent work to users is required
- Subagents need access to the full conversation history

## Key Characteristics

| Capability | Rating |
|------------|--------|
| Context Isolation | Very High |
| Tool-Heavy Work | High |
| Automatic Planning | High |
| Streaming Support | Low |
| Context Efficiency | Very High |

## Decision Triggers

Ask yourself these questions:

1. "Will tool calls generate large amounts of data?" -> HIGH fit if yes
2. "Does the main agent need to maintain long conversations?" -> HIGH fit if yes
3. "Can subagents work independently and return summaries?" -> HIGH fit if yes
4. "Do you need built-in task planning?" -> HIGH fit if yes

## Example Use Cases

- **Research Assistant**: Deep agent searches 50+ sources, returns 500-word summary
- **Data Analysis**: Process 10,000 rows, return key insights
- **Code Analysis**: Analyze entire codebase, summarize architecture
- **Document Processing**: Extract data from 100 documents, compile report

## Trade-offs

**Pros:**
- Prevents context bloat from intermediate tool outputs
- Subagents get clean, focused contexts
- Built-in task/todo tools for planning
- Main agent stays coherent over long sessions

**Cons:**
- Cannot stream subagent work in real-time
- Subagents don't see full conversation history
- Additional setup with `deepagents` library
- Summaries may lose some detail

## Architecture Pattern

```
User <-> Main Agent
              |
         [task() tool]
              |
         Deep Agent (isolated context)
              |
         [many tool calls]
              |
         Summary returned to Main Agent
```

## Code Reference

See: `examples/deep_agents_research_assistant.py`

## Key APIs

- `create_deep_agent()` from `deepagents`
- `task()` tool for delegation
- Automatic context isolation
- Built-in planning tools
