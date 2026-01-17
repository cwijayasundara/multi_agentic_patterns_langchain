# LangChain 1.2.x Multi-Agent Patterns

This repository contains sample applications demonstrating each of the 9 core agentic patterns in LangChain/LangGraph 1.2.x, organized as a reusable Python package.

## Overview

| Pattern | Sample App | Description |
|---------|------------|-------------|
| **Subagents** | Personal Finance Assistant | Supervisor coordinates budget, investment, and tax specialist agents |
| **Deep Agents** | Research Assistant | Main agent delegates to specialized subagents with context isolation |
| **Supervisor Forward** | Legal Document Assistant | Forwards subagent responses verbatim without paraphrasing |
| **Hierarchical Teams** | Product Launch Coordinator | Nested team subgraphs with multi-level coordination |
| **Context Quarantine** | Data Analysis Pipeline | Isolates large tool outputs, returns only summaries |
| **Skills** | Multi-Language Code Assistant | Single agent loads specialized coding skills on demand |
| **Handoffs** | Customer Support Bot | Agents dynamically hand off conversations based on context |
| **Router** | Multi-Source Knowledge Base | Routes queries to specialized agents in parallel, synthesizes results |
| **Custom Workflows** | Content Pipeline | StateGraph with research → write → review loop and conditional edges |

## Pattern Selection Flowchart

Use this decision tree to select the right pattern for your use case:

```
                                    ┌─────────────────────────────┐
                                    │   START: What type of       │
                                    │   agentic system do you     │
                                    │   need to build?            │
                                    └──────────────┬──────────────┘
                                                   │
                         ┌─────────────────────────┼─────────────────────────┐
                         │                         │                         │
                         ▼                         ▼                         ▼
              ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
              │  Single Agent    │    │  Multi-Agent     │    │  Custom Logic    │
              │  (one agent,     │    │  (coordinate     │    │  (complex flows, │
              │   many skills)   │    │   specialists)   │    │   loops, gates)  │
              └────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘
                       │                       │                       │
                       ▼                       │                       ▼
              ┌──────────────────┐             │              ┌──────────────────┐
              │     SKILLS       │             │              │ CUSTOM WORKFLOWS │
              │                  │             │              │                  │
              │ • One agent      │             │              │ • StateGraph     │
              │ • Dynamic skills │             │              │ • Branching      │
              │ • Direct user    │             │              │ • Looping        │
              │   interaction    │             │              │ • Quality gates  │
              └──────────────────┘             │              └──────────────────┘
                                               │
                    ┌──────────────────────────┼──────────────────────────┐
                    │                          │                          │
                    ▼                          ▼                          ▼
         ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
         │ Do agents need  │       │ Do you need     │       │ Is the workflow │
         │ to talk to user │       │ parallel        │       │ sequential with │
         │ directly?       │       │ execution?      │       │ state/stages?   │
         └────────┬────────┘       └────────┬────────┘       └────────┬────────┘
                  │                         │                         │
         ┌────────┴────────┐       ┌────────┴────────┐       ┌────────┴────────┐
         │                 │       │                 │       │                 │
        YES               NO      YES               NO      YES               NO
         │                 │       │                 │       │                 │
         ▼                 │       ▼                 │       ▼                 │
┌──────────────┐           │ ┌──────────────┐       │ ┌──────────────┐        │
│   HANDOFFS   │           │ │    ROUTER    │       │ │   HANDOFFS   │        │
│              │           │ │              │       │ │              │        │
│ • Stages     │           │ │ • Parallel   │       │ │ • Stage-     │        │
│ • Direct     │           │ │   dispatch   │       │ │   based      │        │
│   user chat  │           │ │ • Synthesize │       │ │ • User       │        │
│ • Transfers  │           │ │   results    │       │ │   facing     │        │
└──────────────┘           │ └──────────────┘       │ └──────────────┘        │
                           │                        │                         │
                           └───────────┬────────────┘                         │
                                       │                                      │
                                       ▼                                      │
                          ┌─────────────────────────┐                         │
                          │ What's your primary     │◄────────────────────────┘
                          │ concern?                │
                          └───────────┬─────────────┘
                                      │
        ┌─────────────────┬───────────┼───────────┬─────────────────┐
        │                 │           │           │                 │
        ▼                 ▼           ▼           ▼                 ▼
┌──────────────┐ ┌──────────────┐ ┌────────┐ ┌──────────────┐ ┌──────────────┐
│ Context bloat│ │ Exact wording│ │ Scale  │ │ Centralized  │ │ Large data   │
│ from tools   │ │ preservation │ │ to many│ │ control      │ │ processing   │
│              │ │              │ │ agents │ │              │ │              │
└──────┬───────┘ └──────┬───────┘ └───┬────┘ └──────┬───────┘ └──────┬───────┘
       │                │             │             │                │
       ▼                ▼             ▼             ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌────────────┐ ┌──────────┐ ┌──────────────┐
│ DEEP AGENTS  │ │  SUPERVISOR  │ │HIERARCHICAL│ │SUBAGENTS │ │  CONTEXT     │
│              │ │ FORWARD TOOL │ │   TEAMS    │ │          │ │ QUARANTINE   │
│ • Isolated   │ │              │ │            │ │ • Central│ │              │
│   subagents  │ │ • Verbatim   │ │ • Nested   │ │   super- │ │ • Isolate    │
│ • Summaries  │ │   forwarding │ │   teams    │ │   visor  │ │   huge       │
│   only       │ │ • Audit      │ │ • Team     │ │ • Domain │ │   outputs    │
│ • Planning   │ │   trails     │ │   leads    │ │   experts│ │ • Return     │
│   tools      │ │ • Legal/med  │ │ • 10+      │ │ • Synthe-│ │   summaries  │
└──────────────┘ └──────────────┘ │   agents   │ │   size   │ └──────────────┘
                                  └────────────┘ └──────────┘
```

### Quick Selection Guide

| Question | Answer | Pattern |
|----------|--------|---------|
| Do you need a single agent with many capabilities? | Yes | **Skills** |
| Do agents need to talk directly to users in stages? | Yes | **Handoffs** |
| Do you need to query multiple sources in parallel? | Yes | **Router** |
| Are tool outputs huge and causing context bloat? | Yes | **Deep Agents** or **Context Quarantine** |
| Must expert responses be forwarded without changes? | Yes | **Supervisor Forward Tool** |
| Do you have 10+ specialists across multiple teams? | Yes | **Hierarchical Teams** |
| Do you need a central coordinator for domain experts? | Yes | **Subagents** |
| Do you need complex branching, loops, or quality gates? | Yes | **Custom Workflows** |

### Pattern Selection by Use Case

| Use Case | Recommended Pattern | Why |
|----------|---------------------|-----|
| Customer support with stages | **Handoffs** | Natural conversation flow, state-driven |
| Code assistant (multi-language) | **Skills** | Dynamic expertise, single agent |
| Legal/medical document review | **Supervisor Forward** | Exact wording, audit trails |
| Research with many searches | **Deep Agents** | Context isolation, planning |
| Enterprise knowledge base | **Router** | Parallel queries, synthesis |
| Product launch coordination | **Hierarchical Teams** | Multiple teams, nested structure |
| Personal finance advisor | **Subagents** | Domain experts, centralized |
| Data analytics pipeline | **Context Quarantine** | Large outputs, summaries |
| Content with review cycles | **Custom Workflows** | Loops, quality gates |

## Quick Start

### 1. Setup Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package in editable mode
pip install -e .

# Set up API key
cp .env.example .env
# Edit .env and add your OpenAI API key
```

### 2. Run Sample Applications

```bash
# Subagents Pattern - Personal Finance Assistant
python examples/subagents_finance_assistant.py

# Deep Agents Pattern - Research Assistant (context isolation)
python examples/deep_agents_research_assistant.py

# Supervisor Forward Tool Pattern - Legal Assistant (verbatim forwarding)
python examples/supervisor_forward_tool.py

# Hierarchical Teams Pattern - Product Launch (nested subgraphs)
python examples/hierarchical_teams.py

# Context Quarantine Pattern - Data Analysis (isolate large outputs)
python examples/context_quarantine.py

# Skills Pattern - Code Assistant
python examples/skills_code_assistant.py

# Handoffs Pattern - Customer Support
python examples/handoffs_customer_support.py

# Router Pattern - Knowledge Base
python examples/router_knowledge_base.py

# Custom Workflows Pattern - Content Pipeline
python examples/custom_workflow_content_pipeline.py
```

## Package Structure

The repository is organized as a Python package for easy reuse:

```
langchain_agentic_patterns/
├── src/agentic_patterns/          # Main package
│   ├── core/                      # Shared infrastructure
│   │   ├── config.py              # Model initialization
│   │   ├── middleware.py          # Middleware preset factories
│   │   ├── checkpointer.py        # Checkpointer setup
│   │   └── utils.py               # PII redaction, retry helpers
│   │
│   ├── tools/                     # Domain-specific tools
│   │   ├── finance/               # Budget, investment, tax tools
│   │   ├── support/               # Customer support tools
│   │   ├── code/                  # Skill loading, code generation
│   │   └── knowledge/             # Knowledge base search
│   │
│   ├── agents/                    # Agent prompts & configs
│   │   ├── finance.py             # Finance agent prompts
│   │   ├── support.py             # Support prompts, step config
│   │   └── knowledge.py           # Router agent prompts
│   │
│   └── state/                     # TypedDict & Pydantic models
│       ├── support.py             # SupportState, SupportStep
│       ├── router.py              # RouterState, QueryClassification
│       └── content.py             # ContentState
│
├── skills/                        # External skill files (.md)
├── examples/                      # Simplified demo applications
└── pyproject.toml                 # Package configuration
```

## Using the Package

```python
# Import core utilities
from agentic_patterns.core import get_model, get_memory_checkpointer
from agentic_patterns.core import create_subagent_middleware, create_support_middleware

# Import tools
from agentic_patterns.tools import FINANCE_TOOLS, SUPPORT_TOOLS, CODE_TOOLS
from agentic_patterns.tools.finance import get_spending_by_category, execute_rebalance

# Import agent prompts
from agentic_patterns.agents import BUDGET_AGENT_PROMPT, FINANCE_SUPERVISOR_PROMPT

# Import state definitions
from agentic_patterns.state import SupportState, RouterState, ContentState
```

## Pattern Details

### 1. Subagents Pattern (`examples/subagents_finance_assistant.py`)

**When to use:**
- You have distinct domains requiring specialized agents
- Each domain has multiple tools or complex logic
- You want centralized workflow control
- Sub-agents don't need to converse directly with users

**Architecture:**
```
┌─────────────────────────────────────┐
│           Supervisor Agent           │
│  (routes queries, synthesizes)       │
└─────────┬─────────┬─────────┬───────┘
          │         │         │
    ┌─────▼───┐ ┌───▼───┐ ┌───▼───┐
    │ Budget  │ │Invest │ │  Tax  │
    │ Analyst │ │Advisor│ │Consult│
    └─────────┘ └───────┘ └───────┘
```

### 2. Deep Agents Pattern (`examples/deep_agents_research_assistant.py`)

**When to use:**
- Tasks require many tool calls with large intermediate outputs
- Context bloat is degrading agent reliability
- You need sustained reasoning across multi-step workflows
- Different phases require specialized expertise with isolation

**Key Feature: Context Isolation**
- Subagents handle tool-heavy work in isolated contexts
- Main agent receives only final summaries, not raw data
- Prevents context window from filling with intermediate results
- Built-in planning, filesystem, and summarization middleware

**Architecture:**
```
┌─────────────────────────────────────┐
│         Main Agent (Coordinator)     │
│   • Delegates via task() tool        │
│   • Receives only final summaries    │
└─────────┬─────────┬─────────┬───────┘
          │         │         │
    ┌─────▼───┐ ┌───▼───┐ ┌───▼────┐
    │Researcher│ │Analyst│ │ Writer │
    │(isolated)│ │(isolated)│(isolated)│
    │  context │ │ context│ │ context │
    └─────────┘ └───────┘ └────────┘
```

### 3. Supervisor with Forward Tool (`examples/supervisor_forward_tool.py`)

**When to use:**
- Exact wording matters (legal, medical, financial advice)
- You need audit trails of who said what
- Paraphrasing could introduce errors or liability
- Subagent expertise should be presented without modification

**Architecture:**
```
┌─────────────────────────────────────┐
│         Supervisor Agent            │
│  (routes, forwards verbatim)        │
└─────────┬─────────┬─────────┬───────┘
          │         │         │
    ┌─────▼───┐ ┌───▼────┐ ┌──▼───┐
    │Contract │ │Compliance│ │  IP  │
    │Specialist│ │Specialist│ │Expert│
    └─────────┘ └─────────┘ └──────┘
          │         │         │
          └─────────┼─────────┘
                    ▼
         [Forwarded Verbatim to User]
```

### 4. Hierarchical Teams (`examples/hierarchical_teams.py`)

**When to use:**
- Complex workflows require multiple levels of coordination
- Teams operate semi-independently but need synchronization
- Different teams have different internal workflows
- You need to scale to many specialists without overwhelming a single supervisor

**Architecture:**
```
┌──────────────────────────────────────────┐
│         Launch Supervisor                 │
└────────────────┬─────────────────────────┘
                 │
    ┌────────────┼────────────┐
    ▼            ▼            ▼
┌────────┐  ┌────────┐  ┌────────┐
│Marketing│  │Engineer│  │  QA    │
│  Team   │  │  Team  │  │ Team   │
│(subgraph)│ │(subgraph)│ │(subgraph)│
└────┬────┘  └────┬────┘  └────┬────┘
     │            │            │
   ┌─┼─┐       ┌─┼─┐       ┌─┼─┐
   ▼ ▼ ▼       ▼ ▼ ▼       ▼ ▼ ▼
 [3 specs]   [3 specs]   [3 specs]
```

### 5. Context Quarantine (`examples/context_quarantine.py`)

**When to use:**
- Tool outputs are large (data queries, file contents, API responses)
- Context bloat degrades agent performance
- You need sustained reasoning over multiple steps
- Raw data isn't needed in final response

**Key Feature: Context Isolation**
- Quarantine subagents process 100K+ tokens of raw data
- Only summaries (~500 tokens) returned to main agent
- Main agent context stays clean and focused
- Prevents performance degradation from context bloat

**Architecture:**
```
┌─────────────────────────────────────┐
│      Main Agent (Clean: ~3K)        │
└─────────┬─────────┬─────────────────┘
          │         │
    ┌─────▼───┐ ┌───▼────┐
    │  Data   │ │Analysis│
    │Collector│ │Processor│
    │(~100K)  │ │(~50K)  │
    │         │ │        │
    │Returns: │ │Returns:│
    │ 500 tok │ │ 400 tok│
    └─────────┘ └────────┘
```

### 6. Skills Pattern (`examples/skills_code_assistant.py`)

**When to use:**
- Single agent with many possible specializations
- No need to enforce constraints between skills
- Different teams developing capabilities independently
- Want lightweight composition without full sub-agents

**Architecture:**
```
┌────────────────────────────────┐
│        Code Assistant          │
│   ┌─────────────────────────┐  │
│   │    Loaded Skills:       │  │
│   │  • python_expert        │  │
│   │  • javascript_expert    │  │
│   │  • rust_expert          │  │
│   └─────────────────────────┘  │
└────────────────────────────────┘
```

### 7. Handoffs Pattern (`examples/handoffs_customer_support.py`)

**When to use:**
- Multi-stage conversational experiences
- Capabilities unlock sequentially after preconditions
- Agents need to converse directly with users
- Different conversation stages need specialized handling

**Architecture:**
```
┌──────────┐     ┌──────────┐     ┌──────────┐
│ Greeting │◄───►│ Billing  │◄───►│  Tech    │
│  Agent   │     │  Agent   │     │ Support  │
└──────────┘     └──────────┘     └──────────┘
     ▲                                  ▲
     └──────────────────────────────────┘
```

### 8. Router Pattern (`examples/router_knowledge_base.py`)

**When to use:**
- Distinct knowledge domains (verticals)
- Need to query multiple sources in parallel
- Want synthesized results from combined responses
- Routing logic is deterministic or simple classification

**Architecture:**
```
       ┌─────────────┐
       │   Router    │
       │ (classify)  │
       └──────┬──────┘
              │
    ┌─────────┼─────────┐
    ▼         ▼         ▼
┌───────┐ ┌───────┐ ┌───────┐
│ Docs  │ │  FAQ  │ │Tutor- │
│ Agent │ │ Agent │ │ials   │
└───┬───┘ └───┬───┘ └───┬───┘
    │         │         │
    └─────────┼─────────┘
              ▼
       ┌─────────────┐
       │ Synthesize  │
       └─────────────┘
```

### 9. Custom Workflows Pattern (`examples/custom_workflow_content_pipeline.py`)

**When to use:**
- Need full control over workflow logic
- Complex branching and looping required
- Custom state management needed
- Standard patterns don't fit your use case

**Architecture:**
```
[START]
    │
    ▼
┌─────────┐
│Research │
└────┬────┘
     ▼
┌─────────┐
│ Outline │
└────┬────┘
     ▼
┌─────────┐◄───────┐
│  Write  │        │
└────┬────┘        │
     ▼             │
┌─────────┐   (revise)
│ Review  │────────┘
└────┬────┘
     │
┌────┴────┐
▼         ▼
[Approve] [Reject]
    │         │
    ▼         ▼
[Finalize] [END]
    │
    ▼
  [END]
```

## Middleware & Context Engineering

Each pattern demonstrates production-ready middleware for context management, resilience, and safety.

### Middleware by Pattern

| Pattern | Middleware | Purpose |
|---------|------------|---------|
| **Subagents** | `SummarizationMiddleware` | Compress conversation at 4000 tokens |
| | `ToolRetryMiddleware` | Exponential backoff for failed tool calls |
| | `ModelFallbackMiddleware` | Automatic failover (gpt-4o-mini → claude-3-5-haiku) |
| **Handoffs** | `HumanInTheLoopMiddleware` | Require approval for refunds/discounts |
| | `ModelCallLimitMiddleware` | Prevent infinite loops (50/thread, 10/run) |
| | `ContextEditingMiddleware` | Clear old tool outputs at 50000 tokens |
| | `SummarizationMiddleware` | Compress at 6000 tokens |
| **Router** | Custom retry/fallback | StateGraph uses custom logic (not middleware) |
| | PII redaction | Sanitize queries before processing |
| | Structured output | Type-safe routing with Pydantic |
| **Skills** | `LLMToolSelectorMiddleware` | Select relevant tools before main call |
| | `ToolCallLimitMiddleware` | Max 10 skill loads per thread |
| | `ContextEditingMiddleware` | Clear old skill content at 60000 tokens |
| | `SummarizationMiddleware` | Compress at 8000 tokens |

### Key Context Engineering Techniques

1. **Token Management**: Automatic summarization prevents context overflow in long conversations
2. **Resilience**: Retry with exponential backoff + model fallback ensures high availability
3. **Safety**: Human-in-the-loop approval for sensitive operations (refunds, discounts)
4. **Privacy**: PII redaction before query processing protects user data
5. **Cost Control**: Tool call limits prevent runaway agent loops

## Dependencies

- `langchain>=1.2.4` - Core framework with `init_chat_model()` and middleware
- `langchain-openai>=1.1.7` - OpenAI integration
- `langgraph>=1.0.6` - Graph-based agent workflows with `StateGraph`, `Send()`
- `langgraph-supervisor>=0.0.31` - `create_supervisor()` for subagent coordination
- `langgraph-swarm>=0.0.15` - `create_swarm()`, `create_handoff_tool()` for agent handoffs
- `deepagents>=0.1.0` - `create_deep_agent()` for context-isolated subagents
- `python-dotenv>=1.0.0` - Environment variable management

## Resources

- [LangChain Multi-Agent Docs](https://docs.langchain.com/oss/python/langchain/multi-agent)
- [Choosing the Right Multi-Agent Architecture](https://www.blog.langchain.com/choosing-the-right-multi-agent-architecture/)
- [LangGraph Documentation](https://docs.langchain.com/oss/python/langgraph/)
- [LangGraph Supervisor GitHub](https://github.com/langchain-ai/langgraph-supervisor-py)
- [LangGraph Swarm GitHub](https://github.com/langchain-ai/langgraph-swarm-py)
- [Deep Agents Documentation](https://docs.langchain.com/oss/python/deepagents/overview)
- [Deep Agents GitHub](https://github.com/langchain-ai/deepagents)

## Performance Considerations

| Pattern | Model Calls (simple) | Best For |
|---------|---------------------|----------|
| Subagents | 4 | Centralized control, distinct domains |
| Deep Agents | 3-6 | Context isolation, complex research tasks |
| Supervisor Forward | 4 | Exact wording preservation, audit trails |
| Hierarchical Teams | 6-12 | Complex nested workflows, large teams |
| Context Quarantine | 3-5 | Large data processing, context management |
| Skills | 3 | Single agent, many specializations |
| Handoffs | 3 | Multi-stage conversations |
| Router | 3-5 | Parallel querying, result synthesis |
| Custom | Variable | Complex workflows, full control |

## License

MIT License
