# Pattern Selector Agent

An interactive agent that helps users choose the right agentic architecture from 9 LangChain/LangGraph patterns.

## Architecture

This agent uses the **Skills Pattern** combined with **Handoffs-style conversation phases**:

```
┌─────────────────────────────────────────────────────────────┐
│                    Pattern Selector Agent                    │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              System Prompt (Lightweight)             │   │
│  │  - Brief summaries of all 9 patterns                │   │
│  │  - Phase-based guidance (gather → clarify → recommend)│   │
│  │  - Decision heuristics                              │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                 │
│                           ▼                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                 Middleware Stack                     │   │
│  │  1. LLMToolSelectorMiddleware (smart tool routing)  │   │
│  │  2. ToolCallLimitMiddleware (max 9 pattern loads)   │   │
│  │  3. ContextEditingMiddleware (clear old patterns)   │   │
│  │  4. SummarizationMiddleware (compress long chats)   │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                 │
│                           ▼                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    Tools (8 total)                   │   │
│  │                                                     │   │
│  │  Pattern Tools:           Decision Tools:           │   │
│  │  - list_all_patterns()    - evaluate_requirements() │   │
│  │  - load_pattern()         - analyze_use_case()      │   │
│  │  - search_patterns()      - get_clarifying_questions()│  │
│  │  - get_pattern_comparison()                         │   │
│  │  - get_pattern_decision_tree()                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                 │
│                           ▼                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Knowledge Base (9 .md files)            │   │
│  │                                                     │   │
│  │  knowledge/                                         │   │
│  │  ├── subagents.md        ├── skills.md             │   │
│  │  ├── deep-agents.md      ├── handoffs.md           │   │
│  │  ├── supervisor-forward.md├── router.md            │   │
│  │  ├── hierarchical-teams.md├── custom-workflows.md  │   │
│  │  └── context-quarantine.md                         │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## Why Skills Pattern?

The agent uses **progressive disclosure** to manage context efficiently:

| Approach | Context Size | Problem |
|----------|-------------|---------|
| Load all 9 patterns upfront | ~15,000 tokens | Context bloat, unfocused responses |
| **Load on demand (Skills)** | ~2,000 base + loaded | Focused, efficient, scalable |

**How it works:**
1. System prompt contains only brief summaries (~500 tokens)
2. `load_pattern()` tool fetches full details when needed (~1,500 tokens each)
3. Middleware clears old pattern content when context grows too large
4. Only 2-3 patterns typically loaded per conversation

## Package Structure

```
pattern_selector_agent/
├── __init__.py           # Package exports
├── __main__.py           # CLI entry point (python -m pattern_selector_agent)
├── agent.py              # Agent creation with Skills-pattern middleware
├── prompts.py            # System prompt with phase-based guidance
├── state.py              # SelectorState TypedDict (for future state tracking)
├── middleware.py         # Skills-pattern middleware factory
├── README.md             # This file
├── tools/
│   ├── __init__.py       # Tool exports
│   ├── patterns.py       # Pattern loading/searching tools
│   └── decision.py       # Requirement evaluation tools
└── knowledge/            # Pattern documentation (loaded on demand)
    ├── subagents.md
    ├── deep-agents.md
    ├── supervisor-forward.md
    ├── hierarchical-teams.md
    ├── context-quarantine.md
    ├── skills.md
    ├── handoffs.md
    ├── router.md
    └── custom-workflows.md
```

## Middleware Stack

The agent uses four middleware components (same as Skills code assistant):

```python
from pattern_selector_agent import create_selector_middleware

middleware = create_selector_middleware()
# Returns: [
#   LLMToolSelectorMiddleware,   # Selects relevant tools per query
#   ToolCallLimitMiddleware,     # Max 9 pattern loads per thread
#   ContextEditingMiddleware,    # Clears old pattern content at 50K tokens
#   SummarizationMiddleware,     # Compresses at 8K tokens
# ]
```

| Middleware | Purpose | Configuration |
|------------|---------|---------------|
| `LLMToolSelectorMiddleware` | Routes to relevant tools | Max 5 tools, always includes `load_pattern` |
| `ToolCallLimitMiddleware` | Prevents loading all patterns | Max 9 loads per thread |
| `ContextEditingMiddleware` | Clears stale pattern content | Triggers at 50K tokens, keeps 3 recent |
| `SummarizationMiddleware` | Compresses long conversations | Triggers at 8K tokens, keeps 15 messages |

## Conversation Flow

The agent follows a three-phase conversation pattern:

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   GATHERING  │ ──▶ │  CLARIFYING  │ ──▶ │ RECOMMENDING │
└──────────────┘     └──────────────┘     └──────────────┘
       │                    │                    │
       ▼                    ▼                    ▼
  Listen to user      Ask 2-4 targeted     Load pattern(s)
  analyze_use_case()  questions            Explain trade-offs
  Identify candidates get_clarifying_      Point to code
                      questions()
```

**Example:**
```
User: "I want to build a customer support system"
                    ↓
Agent: [GATHERING] Identifies candidates: handoffs, subagents
       Asks: "Do specialists talk directly to customers?"
                    ↓
User: "Yes, with greeting → billing → resolution stages"
                    ↓
Agent: [CLARIFYING → RECOMMENDING]
       Loads handoffs pattern
       Recommends Handoffs with trade-offs
       Points to examples/handoffs_customer_support.py
```

## Tools Reference

### Pattern Tools (`tools/patterns.py`)

| Tool | Purpose |
|------|---------|
| `list_all_patterns()` | Brief descriptions of all 9 patterns |
| `load_pattern(name)` | Load full pattern details into context |
| `search_patterns(query)` | Search pattern docs by keyword |
| `get_pattern_comparison(names)` | Side-by-side comparison table |
| `get_pattern_decision_tree()` | Quick decision flowchart |

### Decision Tools (`tools/decision.py`)

| Tool | Purpose |
|------|---------|
| `evaluate_requirements(reqs)` | Score patterns against requirements |
| `analyze_use_case(desc)` | Identify candidate patterns from description |
| `get_clarifying_questions(desc)` | Generate targeted clarifying questions |

## Knowledge Files Format

Each pattern knowledge file uses YAML frontmatter:

```markdown
---
name: handoffs
title: Handoffs (State Machine)
description: Agents hand off conversations via Command objects
category: multi-agent
complexity: medium
---

## When to Use
- Workflow has clear stages/phases
- Specialists need direct user interaction
...

## When NOT to Use
- Need parallel execution (use Subagents)
...

## Key Characteristics
| Capability | Rating |
|------------|--------|
| Direct User Interaction | Very High |
...

## Code Reference
See: examples/handoffs_customer_support.py
```

## Usage

### Interactive CLI

```bash
python -m pattern_selector_agent
```

### Programmatic

```python
from pattern_selector_agent import create_selector_agent, chat

# Create agent with Skills-pattern middleware
agent = create_selector_agent()

# Multi-turn conversation
response1 = chat("I want to build a research system", agent=agent, thread_id="session1")
response2 = chat("It should search multiple sources in parallel", agent=agent, thread_id="session1")

# Check which patterns are loaded
from pattern_selector_agent.tools import get_loaded_patterns
print(get_loaded_patterns())  # e.g., ['router']
```

### Custom Configuration

```python
from pattern_selector_agent import create_selector_agent, create_selector_middleware
from agentic_patterns.core import get_model

# Custom middleware settings
middleware = create_selector_middleware(
    max_tools=6,
    pattern_thread_limit=5,  # Limit to 5 patterns per session
    context_trigger=40000,   # Clear earlier
)

# Custom model
agent = create_selector_agent(
    model=get_model("gpt-4o"),
    middleware=middleware,
)
```

## Dependencies

Uses the existing `agentic_patterns` package:
- `agentic_patterns.core.get_model()` - Model initialization
- `agentic_patterns.core.get_memory_checkpointer()` - State persistence
- LangChain middleware components

## Design Decisions

1. **Skills over Subagents**: Pattern documentation is knowledge-based, not tool-based. Skills pattern is lighter weight and more appropriate.

2. **Progressive Loading**: Avoids context bloat by loading pattern details only when discussing specific patterns.

3. **Phase-Based Prompting**: Guides the agent through gather → clarify → recommend flow without complex state machines.

4. **Middleware Reuse**: Uses same middleware patterns as the Skills code assistant example for consistency.

5. **Knowledge as .md Files**: Easy to update pattern documentation without code changes.
