# LangChain Multi-Agent Patterns: Design Document

A comprehensive guide to the 9 core multi-agent patterns in LangChain/LangGraph 1.2.x, including architecture diagrams, comparison tables, and decision frameworks.

> **References**:
> - [Choosing the Right Multi-Agent Architecture](https://www.blog.langchain.com/choosing-the-right-multi-agent-architecture/)
> - [Subagents: Personal Assistant](https://docs.langchain.com/oss/python/langchain/multi-agent/subagents-personal-assistant)
> - [Handoffs: Customer Support](https://docs.langchain.com/oss/python/langchain/multi-agent/handoffs-customer-support)
> - [Router: Knowledge Base](https://docs.langchain.com/oss/python/langchain/multi-agent/router-knowledge-base)
> - [Skills: SQL Assistant](https://docs.langchain.com/oss/python/langchain/multi-agent/skills-sql-assistant)

---

## Table of Contents

1. [Package Structure](#package-structure)
2. [When to Use Multi-Agent Systems](#when-to-use-multi-agent-systems)
3. [Pattern 1: Subagents (Supervisor)](#pattern-1-subagents-supervisor)
4. [Pattern 2: Deep Agents](#pattern-2-deep-agents)
5. [Pattern 3: Supervisor with Forward Tool](#pattern-3-supervisor-with-forward-tool)
6. [Pattern 4: Hierarchical Teams](#pattern-4-hierarchical-teams)
7. [Pattern 5: Context Quarantine](#pattern-5-context-quarantine)
8. [Pattern 6: Skills](#pattern-6-skills)
9. [Pattern 7: Handoffs](#pattern-7-handoffs)
10. [Pattern 8: Router](#pattern-8-router)
11. [Pattern 9: Custom Workflows](#pattern-9-custom-workflows)
12. [Comparison Table](#comparison-table)
13. [Decision Flowchart](#decision-flowchart)
14. [Performance Characteristics](#performance-characteristics)
15. [Middleware & Context Engineering](#middleware--context-engineering)

---

## Package Structure

This repository is organized as a reusable Python package (`agentic_patterns`) with example applications:

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
│   │   ├── finance/               # Budget, investment, tax tools (9)
│   │   ├── support/               # Customer support tools (10)
│   │   ├── code/                  # Skill loading, code generation (6)
│   │   └── knowledge/             # Knowledge base search (3)
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
│   ├── subagents_finance_assistant.py
│   ├── deep_agents_research_assistant.py
│   ├── supervisor_forward_tool.py
│   ├── hierarchical_teams.py
│   ├── context_quarantine.py
│   ├── skills_code_assistant.py
│   ├── handoffs_customer_support.py
│   ├── router_knowledge_base.py
│   └── custom_workflow_content_pipeline.py
└── pyproject.toml                 # Package configuration
```

### Using the Package

```python
# Install in editable mode
pip install -e .

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

---

## When to Use Multi-Agent Systems

**Start simple**: Many agentic tasks are best handled by a single agent with well-designed tools. Single agents are simpler to build, reason about, and debug.

**Graduate to multi-agent when you hit these limits**:

1. **Context Management**: Specialized knowledge for each capability doesn't fit comfortably in a single prompt
2. **Distributed Development**: Different teams need to develop capabilities independently
3. **Complex Routing**: Different conversation stages need specialized handling
4. **Parallel Execution**: Multiple domains need to be queried simultaneously

> **Rule of thumb**: Add tools before adding agents. Add agents only when complexity demands it.

---

## Pattern 1: Subagents (Supervisor)

### Overview

A supervisor agent coordinates specialized subagents by calling them as tools. The main agent maintains conversation context while subagents remain **stateless**, providing strong context isolation.

### Architecture Diagram

```
                    ┌─────────────────────────────────────┐
                    │         SUPERVISOR AGENT            │
                    │   • Maintains conversation context  │
                    │   • Routes queries to specialists   │
                    │   • Synthesizes final responses     │
                    └─────────────┬───────────────────────┘
                                  │
            ┌─────────────────────┼─────────────────────┐
            │                     │                     │
            ▼                     ▼                     ▼
    ┌───────────────┐     ┌───────────────┐     ┌───────────────┐
    │   SUBAGENT A  │     │   SUBAGENT B  │     │   SUBAGENT C  │
    │   (Stateless) │     │   (Stateless) │     │   (Stateless) │
    │               │     │               │     │               │
    │  ┌─────────┐  │     │  ┌─────────┐  │     │  ┌─────────┐  │
    │  │ Tool 1  │  │     │  │ Tool 3  │  │     │  │ Tool 5  │  │
    │  │ Tool 2  │  │     │  │ Tool 4  │  │     │  │ Tool 6  │  │
    │  └─────────┘  │     │  └─────────┘  │     │  └─────────┘  │
    └───────────────┘     └───────────────┘     └───────────────┘
```

### Data Flow

```
User Query
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│                      SUPERVISOR                              │
│  1. Analyze query                                           │
│  2. Decide which subagent(s) to invoke                      │
│  3. Can invoke MULTIPLE subagents in PARALLEL               │
└─────────────────────────────────────────────────────────────┘
    │                    │                    │
    ▼                    ▼                    ▼
┌─────────┐        ┌─────────┐        ┌─────────┐
│Subagent │        │Subagent │        │Subagent │
│    A    │        │    B    │        │    C    │
└────┬────┘        └────┬────┘        └────┬────┘
     │                  │                  │
     └──────────────────┼──────────────────┘
                        ▼
              ┌─────────────────┐
              │   SUPERVISOR    │
              │   Synthesizes   │
              │    Response     │
              └────────┬────────┘
                       ▼
                 Final Response
```

### When to Use

| Use Case | Example |
|----------|---------|
| Multiple distinct domains | Personal finance: budget + investments + taxes |
| Centralized workflow control | Research system coordinating domain experts |
| Parallel execution needed | Querying calendar, email, and CRM simultaneously |
| Subagents don't need user interaction | Backend processing agents |

### Pros & Cons

| Pros | Cons |
|------|------|
| Strong context isolation | Extra latency (4 calls vs 3) |
| Parallel execution | Higher token overhead |
| Multi-hop support | No direct user interaction for subagents |
| Excellent distributed development | Results must flow through supervisor |

### Implementation

```python
from langchain.agents import create_agent
from langgraph_supervisor import create_supervisor

# Import from agentic_patterns package
from agentic_patterns.core import get_model, create_subagent_middleware, create_supervisor_middleware
from agentic_patterns.tools.finance import BUDGET_TOOLS, INVESTMENT_TOOLS, TAX_TOOLS
from agentic_patterns.agents.finance import (
    BUDGET_AGENT_PROMPT, INVESTMENT_AGENT_PROMPT, TAX_AGENT_PROMPT, FINANCE_SUPERVISOR_PROMPT
)

model = get_model()

# Create specialized subagents with middleware
budget_agent = create_agent(
    model=model,
    tools=BUDGET_TOOLS,
    name="budget_analyst",
    system_prompt=BUDGET_AGENT_PROMPT,
    middleware=create_subagent_middleware()
)

investment_agent = create_agent(
    model=model,
    tools=INVESTMENT_TOOLS,
    name="investment_advisor",
    system_prompt=INVESTMENT_AGENT_PROMPT,
    middleware=create_subagent_middleware()
)

# Create supervisor to coordinate them
workflow = create_supervisor(
    agents=[budget_agent, investment_agent],
    model=model,
    system_prompt=FINANCE_SUPERVISOR_PROMPT,
    middleware=create_supervisor_middleware()
)
```

**Example**: `examples/subagents_finance_assistant.py`

---

## Pattern 2: Deep Agents

### Overview

Deep Agents solve the **context bloat problem** by delegating complex research tasks to specialized subagents that execute in **isolated contexts**. The main agent receives only final summaries, not raw intermediate data, preventing context windows from filling with tool outputs.

### Architecture Diagram

```
                    ┌─────────────────────────────────────┐
                    │       MAIN AGENT (Coordinator)       │
                    │   • Delegates via task() tool        │
                    │   • Receives only final summaries    │
                    │   • Built-in planning (todo tools)   │
                    └─────────────┬───────────────────────┘
                                  │
            ┌─────────────────────┼─────────────────────┐
            │                     │                     │
            ▼                     ▼                     ▼
    ┌───────────────┐     ┌───────────────┐     ┌───────────────┐
    │   RESEARCHER  │     │    ANALYST    │     │    WRITER     │
    │   (Isolated)  │     │   (Isolated)  │     │   (Isolated)  │
    │               │     │               │     │               │
    │  ┌─────────┐  │     │  ┌─────────┐  │     │  ┌─────────┐  │
    │  │web_search│ │     │  │analyze_ │  │     │  │write_   │  │
    │  │         │  │     │  │data     │  │     │  │report   │  │
    │  └─────────┘  │     │  └─────────┘  │     │  └─────────┘  │
    └───────────────┘     └───────────────┘     └───────────────┘
           │                     │                     │
           └─────────────────────┼─────────────────────┘
                                 │
                          (Summaries only)
```

### Data Flow (Context Isolation)

```
User: "Research AI agent architectures and write a report"
                │
                ▼
┌─────────────────────────────────────────────────────────────┐
│                    MAIN AGENT                                │
│  1. Plans task breakdown                                     │
│  2. Delegates research via task(name="researcher", ...)      │
└─────────────────────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────┐
│              RESEARCHER SUBAGENT (Isolated Context)          │
│                                                              │
│  • Executes multiple web_search() calls                      │
│  • Processes 10,000+ tokens of raw search results            │
│  • Returns only: 500-token summary + key facts               │
│                                                              │
│  [Raw results STAY HERE - never reach main agent]            │
└─────────────────────────────────────────────────────────────┘
                │
                ▼ (Summary only: ~500 tokens)
┌─────────────────────────────────────────────────────────────┐
│                    MAIN AGENT                                │
│  • Receives concise summary, not raw data                    │
│  • Context remains manageable                                │
│  • Delegates next task to analyst                            │
└─────────────────────────────────────────────────────────────┘
```

### When to Use

| Use Case | Example |
|----------|---------|
| Tasks with many tool calls | Research requiring 10+ web searches |
| Large intermediate outputs | Code generation, data analysis |
| Sustained reasoning needed | Multi-step research workflows |
| Context management critical | Agents that degrade with context bloat |

### Pros & Cons

| Pros | Cons |
|------|------|
| Strong context isolation | Requires `deepagents` package |
| Prevents context bloat | Subagent results are summarized (lossy) |
| Built-in planning tools | More complex debugging |
| Specialized expertise per subagent | Subagents don't share state |

### Implementation

```python
from deepagents import create_deep_agent

# Define subagents with focused capabilities
research_subagent = {
    "name": "researcher",
    "description": "Conducts web research to gather information on topics.",
    "system_prompt": \"\"\"You are an expert researcher. Your job is to:
1. Break down research questions into search queries
2. Use web_search to find relevant information
3. Synthesize findings into a concise summary

IMPORTANT: Keep your response under 500 words.\"\"\",
    "tools": [web_search],
}

analysis_subagent = {
    "name": "analyst",
    "description": "Analyzes data and extracts insights.",
    "system_prompt": \"\"\"You are a data analyst. Extract key insights and trends.
Keep response under 400 words.\"\"\",
    "tools": [analyze_data],
}

writer_subagent = {
    "name": "writer",
    "description": "Writes polished reports from research and analysis.",
    "system_prompt": \"\"\"You are a technical writer. Create clear, structured reports.
Keep response under 800 words.\"\"\",
    "tools": [write_report],
}

MAIN_AGENT_PROMPT = \"\"\"You are a research coordinator managing a team of specialists.

Your team:
- **researcher**: Gathers information from web searches
- **analyst**: Analyzes data and extracts insights
- **writer**: Produces polished final reports

IMPORTANT:
- Always delegate specialized work to subagents
- Do NOT try to do research, analysis, or writing yourself
- Your role is coordination and synthesis\"\"\"

# Create the deep agent
agent = create_deep_agent(
    model="openai:gpt-4o-mini",
    system_prompt=MAIN_AGENT_PROMPT,
    subagents=[research_subagent, analysis_subagent, writer_subagent],
    name="research-coordinator",
)

# Run the agent
result = agent.invoke({
    "messages": [{"role": "user", "content": "Research multi-agent patterns and write a report"}]
})
```

**Example**: `examples/deep_agents_research_assistant.py`

---

## Pattern 3: Supervisor with Forward Tool

### Overview

A supervisor that forwards subagent responses **directly to users without re-generating or paraphrasing**. This preserves exact wording for domains where accuracy is critical, such as legal, medical, or financial advice.

### Architecture Diagram

```
                    ┌─────────────────────────────────────┐
                    │         SUPERVISOR AGENT            │
                    │   • Routes queries to specialists   │
                    │   • Forwards responses VERBATIM     │
                    │   • No paraphrasing/modification    │
                    └─────────────┬───────────────────────┘
                                  │
            ┌─────────────────────┼─────────────────────┐
            │                     │                     │
            ▼                     ▼                     ▼
    ┌───────────────┐     ┌───────────────┐     ┌───────────────┐
    │   CONTRACT    │     │  COMPLIANCE   │     │      IP       │
    │  SPECIALIST   │     │  SPECIALIST   │     │   SPECIALIST  │
    │               │     │               │     │               │
    │ analyze_clause│     │ check_regs    │     │ research_ip   │
    └───────────────┘     └───────────────┘     └───────────────┘
            │                     │                     │
            └─────────────────────┼─────────────────────┘
                                  │
                    [FORWARDED VERBATIM TO USER]
                    "[FROM CONTRACT SPECIALIST]"
```

### When to Use

| Use Case | Example |
|----------|---------|
| Exact wording matters | Legal contracts, medical advice |
| Audit trails needed | Compliance documentation |
| Liability concerns | Financial recommendations |
| Attribution required | Expert opinions with clear source |

### Pros & Cons

| Pros | Cons |
|------|------|
| Preserves exact expert wording | No synthesis across specialists |
| Clear accountability/attribution | Responses may be longer |
| Reduces paraphrasing errors | Less conversational feel |
| Audit-friendly | Users see "from specialist" tags |

### Implementation

```python
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool

def create_forward_tool(agent_name: str):
    """Create a forward tool that passes responses directly."""
    @tool
    def forward_to_user(response: str) -> str:
        f\"\"\"Forward the {agent_name}'s response directly to the user.

        Args:
            response: The complete response to forward verbatim
        \"\"\"
        return f"[FORWARDED FROM {agent_name.upper()}]\\n\\n{response}"

    return forward_to_user

# Supervisor with routing + forward tools
supervisor = create_react_agent(
    model,
    tools=[
        route_to_specialist,  # Routes to contract/compliance/IP
        forward_contract_response,  # Forwards verbatim
        forward_compliance_response,
        forward_ip_response,
    ],
    prompt=SUPERVISOR_PROMPT,
)
```

**Example**: `examples/supervisor_forward_tool.py`

---

## Pattern 4: Hierarchical Teams

### Overview

A multi-level hierarchy where **subagents are themselves LangGraph subgraphs**, enabling complex nested workflows with team-level coordination. Each team operates independently and rolls up results to the top supervisor.

### Architecture Diagram

```
                    ┌──────────────────────┐
                    │   LAUNCH SUPERVISOR  │
                    │   (Top-level coord)  │
                    └──────────┬───────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
    ┌───────────┐        ┌───────────┐        ┌───────────┐
    │ MARKETING │        │ENGINEERING│        │    QA     │
    │   TEAM    │        │   TEAM    │        │   TEAM    │
    │ (Subgraph)│        │ (Subgraph)│        │ (Subgraph)│
    └─────┬─────┘        └─────┬─────┘        └─────┬─────┘
          │                    │                    │
    ┌─────┼─────┐        ┌─────┼─────┐        ┌─────┼─────┐
    │     │     │        │     │     │        │     │     │
    ▼     ▼     ▼        ▼     ▼     ▼        ▼     ▼     ▼
  Content SEO  Social  Backend Frontend DevOps Manual Auto  Perf
  Writer Spec  Media    Dev    Dev     Eng   Test   Test  Test
```

### When to Use

| Use Case | Example |
|----------|---------|
| Complex nested workflows | Product launches, large projects |
| Multiple teams with internal structure | Enterprise organizations |
| Team-level encapsulation | Independent team development |
| Scale to many specialists | 10+ specialists without overwhelming supervisor |

### Pros & Cons

| Pros | Cons |
|------|------|
| Scales to large teams | More complex setup |
| Teams can be developed independently | Longer execution paths |
| Clear organizational structure | Debugging across levels |
| Parallel execution at team level | More code to maintain |

### Implementation

```python
from langgraph.graph import StateGraph, START, END

# Each team is a compiled subgraph
def create_marketing_team():
    workflow = StateGraph(TeamState)
    workflow.add_node("content", content_specialist)
    workflow.add_node("seo", seo_specialist)
    workflow.add_node("social", social_specialist)
    workflow.add_node("lead", marketing_lead)

    # Specialists work in parallel
    workflow.add_edge(START, "content")
    workflow.add_edge(START, "seo")
    workflow.add_edge(START, "social")
    # Lead synthesizes
    workflow.add_edge("content", "lead")
    workflow.add_edge("seo", "lead")
    workflow.add_edge("social", "lead")
    workflow.add_edge("lead", END)

    return workflow.compile()

# Top supervisor coordinates teams
def create_launch_supervisor():
    marketing_team = create_marketing_team()
    engineering_team = create_engineering_team()
    qa_team = create_qa_team()

    workflow = StateGraph(LaunchState)
    workflow.add_node("marketing", lambda s: marketing_team.invoke(...))
    workflow.add_node("engineering", lambda s: engineering_team.invoke(...))
    workflow.add_node("qa", lambda s: qa_team.invoke(...))
    workflow.add_node("synthesize", synthesize_final_plan)

    # Teams work in parallel
    workflow.add_edge(START, "marketing")
    workflow.add_edge(START, "engineering")
    workflow.add_edge(START, "qa")
    # Final synthesis
    workflow.add_edge("marketing", "synthesize")
    workflow.add_edge("engineering", "synthesize")
    workflow.add_edge("qa", "synthesize")
    workflow.add_edge("synthesize", END)

    return workflow.compile()
```

**Example**: `examples/hierarchical_teams.py`

---

## Pattern 5: Context Quarantine

### Overview

Subagents **isolate large tool outputs** from the main agent's context, preventing context bloat while preserving analysis quality. Raw data is processed in "quarantine" and only summaries return to the main agent.

### Architecture Diagram

```
                    ┌──────────────────────┐
                    │     MAIN AGENT       │
                    │  (Clean context)     │
                    │                      │
                    │  Context: ~3K tokens │
                    └──────────┬───────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
    ┌───────────┐        ┌───────────┐        ┌───────────┐
    │ DATA      │        │ ANALYSIS  │        │ REPORT    │
    │ COLLECTOR │        │ PROCESSOR │        │ GENERATOR │
    │           │        │           │        │           │
    │ Processes │        │ Processes │        │ Processes │
    │ 50K tokens│        │ 30K tokens│        │ 20K tokens│
    │           │        │           │        │           │
    │ Returns:  │        │ Returns:  │        │ Returns:  │
    │ 500 token │        │ 400 token │        │ 600 token │
    │ summary   │        │ summary   │        │ summary   │
    └───────────┘        └───────────┘        └───────────┘
```

### Context Savings

```
WITHOUT Quarantine:
  Main context = 50K + 30K + 20K = 100K+ tokens
  Result: Degraded reasoning, high costs, potential overflow

WITH Quarantine:
  Main context = 500 + 400 + 600 = ~1.5K tokens
  Result: Sharp reasoning, low costs, reliable performance
  Savings: ~97% token reduction
```

### When to Use

| Use Case | Example |
|----------|---------|
| Large tool outputs | Database queries, file contents |
| Data processing pipelines | Analytics, reporting |
| Sustained reasoning needed | Multi-step analysis |
| Cost optimization | Reducing API token usage |

### Pros & Cons

| Pros | Cons |
|------|------|
| Prevents context bloat | Summaries lose some detail |
| Better reasoning quality | Extra processing overhead |
| Significant cost savings | More complex architecture |
| Handles arbitrarily large data | Requires good summarization |

### Implementation

```python
def create_quarantine_workflow():
    # Quarantine subagent - processes large data
    data_collector = create_react_agent(
        model,
        tools=[query_database, fetch_api],  # Large outputs
        prompt="Process data and return ONLY a 500-word summary..."
    )

    def collect_data(state):
        # This processes ~100K tokens internally
        result = data_collector.invoke({"messages": [...]})
        # Returns only ~500 token summary
        return {"data_summary": result["messages"][-1].content}

    def synthesize_report(state):
        # Main agent only sees summaries (~1.5K tokens total)
        # NOT the 100K+ tokens of raw data
        return {"final_report": generate_report(state["data_summary"])}

    workflow = StateGraph(AnalysisState)
    workflow.add_node("collect", collect_data)  # Quarantine
    workflow.add_node("synthesize", synthesize_report)  # Clean context

    workflow.add_edge(START, "collect")
    workflow.add_edge("collect", "synthesize")
    workflow.add_edge("synthesize", END)

    return workflow.compile()
```

**Example**: `examples/context_quarantine.py`

---

## Pattern 6: Skills

### Overview

A single agent dynamically loads specialized prompts and knowledge **on-demand**. Think of it as "progressive disclosure" for agent capabilities—the agent stays in control while adopting specialized personas.

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      SINGLE AGENT                           │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │              LOADED SKILLS (Dynamic)                │   │
│   │                                                     │   │
│   │   ┌──────────┐  ┌──────────┐  ┌──────────┐         │   │
│   │   │ Python   │  │JavaScript│  │   SQL    │  ...    │   │
│   │   │ Expert   │  │  Expert  │  │  Expert  │         │   │
│   │   └──────────┘  └──────────┘  └──────────┘         │   │
│   │                                                     │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │                 SKILL TOOLS                         │   │
│   │  • load_skill(name)     • list_available_skills()   │   │
│   │  • unload_skill(name)   • get_skill_details(name)   │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Skill Loading Flow

```
User: "Help me write Python async code"
                │
                ▼
┌───────────────────────────────────┐
│         AGENT DECIDES:            │
│   "I need Python expertise"       │
└───────────────┬───────────────────┘
                │
                ▼
┌───────────────────────────────────┐
│      load_skill("python")         │
│                                   │
│  ┌─────────────────────────────┐  │
│  │  SKILL LOADED:              │  │
│  │  • Coding standards         │  │
│  │  • Best practices           │  │
│  │  • Common patterns          │  │
│  │  • Type hints guidance      │  │
│  └─────────────────────────────┘  │
└───────────────┬───────────────────┘
                │
                ▼
┌───────────────────────────────────┐
│   Agent responds WITH skill       │
│   knowledge now in context        │
└───────────────────────────────────┘
```

### When to Use

| Use Case | Example |
|----------|---------|
| Single agent, many specializations | Code assistant supporting multiple languages |
| Lightweight composition | No need for full subagent infrastructure |
| Direct user interaction needed | User wants to talk to one consistent agent |
| Different teams developing skills | Python team, JS team, DevOps team each own their skill |

### Pros & Cons

| Pros | Cons |
|------|------|
| Direct user interaction | Context accumulates (token bloat) |
| Simple implementation | Less efficient for multi-domain queries |
| Excellent for repeat requests (40% savings) | Limited parallelization |
| Distributed skill development | Skills cannot enforce constraints on each other |

### Implementation

```python
from langchain.agents import create_agent

# Import from agentic_patterns package
from agentic_patterns.core import get_model, get_memory_checkpointer, create_skills_middleware
from agentic_patterns.tools.code import CODE_TOOLS, set_skills_directory

model = get_model()
checkpointer = get_memory_checkpointer()

# Set skills directory for loading .md skill files
set_skills_directory("./skills")

SKILLS_AGENT_PROMPT = """You are a versatile code assistant with access to specialized skills.
Available Actions:
- load_skill: Load a skill to gain expertise (e.g., 'python-expert', 'go-expert')
- list_available_skills: See all skills you can load
- list_loaded_skills: See your current active skills
- unload_skill: Remove a skill if no longer needed
Always load relevant skills before answering technical questions."""

agent = create_agent(
    model=model,
    tools=CODE_TOOLS,
    system_prompt=SKILLS_AGENT_PROMPT,
    middleware=create_skills_middleware(),
    checkpointer=checkpointer,
)
```

**Example**: `examples/skills_code_assistant.py`

---

## Pattern 7: Handoffs

### Overview

Agents **hand off conversations dynamically** based on context. The active agent changes through tool calling, with state persisting across conversation turns. Each agent can transfer control to others.

### Architecture Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                    CONVERSATION STATE                        │
│            (Persists across turns, tracks active agent)      │
└──────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│   GREETING    │◄───►│   BILLING     │◄───►│    TECH       │
│    AGENT      │     │    AGENT      │     │   SUPPORT     │
│               │     │               │     │               │
│ • Identify    │     │ • Payments    │     │ • Diagnostics │
│ • Route       │     │ • Refunds     │     │ • Tickets     │
│ • FAQ         │     │ • Discounts   │     │ • Escalation  │
└───────────────┘     └───────────────┘     └───────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │   HANDOFF TOOLS   │
                    │                   │
                    │ transfer_to_billing()    │
                    │ transfer_to_tech()       │
                    │ transfer_to_greeting()   │
                    └───────────────────┘
```

### Handoff Flow

```
Turn 1: User asks general question
                │
                ▼
        ┌───────────────┐
        │   GREETING    │ ◄── Active
        │    AGENT      │
        └───────┬───────┘
                │
                ▼
        "How can I help you?"

Turn 2: User asks about billing
                │
                ▼
        ┌───────────────┐
        │   GREETING    │
        │    AGENT      │
        └───────┬───────┘
                │
                ▼
        transfer_to_billing()
                │
                ▼
        ┌───────────────┐
        │   BILLING     │ ◄── Now Active
        │    AGENT      │
        └───────┬───────┘
                │
                ▼
        "I can help with your bill..."

Turn 3: User asks technical question
                │
                ▼
        ┌───────────────┐
        │   BILLING     │
        │    AGENT      │
        └───────┬───────┘
                │
                ▼
        transfer_to_tech()
                │
                ▼
        ┌───────────────┐
        │    TECH       │ ◄── Now Active
        │   SUPPORT     │
        └───────────────┘
```

### When to Use

| Use Case | Example |
|----------|---------|
| Multi-stage conversations | Customer support with stages |
| Sequential constraints | Capabilities unlock after preconditions |
| Direct user interaction | Each agent talks to user directly |
| State-driven transitions | Onboarding flows, wizards |

### Pros & Cons

| Pros | Cons |
|------|------|
| Natural conversation flow | Cannot parallelize |
| Direct user interaction | Requires state management |
| Sequential constraints enforced | Not for multi-hop workflows |
| Efficient for repeat requests | More complex debugging |

### Implementation

```python
from langgraph.prebuilt import create_react_agent

# Import from agentic_patterns package
from agentic_patterns.core import get_model, get_memory_checkpointer, create_support_middleware
from agentic_patterns.tools.support import SUPPORT_TOOLS
from agentic_patterns.state.support import SupportState
from agentic_patterns.agents.support import BASE_SUPPORT_PROMPT, STEP_CONFIG

model = get_model()
checkpointer = get_memory_checkpointer()

# Create agent with state-driven behavior
agent = create_react_agent(
    model,
    tools=SUPPORT_TOOLS,  # Tools return Command objects that update state
    checkpointer=checkpointer,
    state_schema=SupportState,
    middleware=create_support_middleware(),
)

# The agent's behavior changes based on current_step in state
# Tools like lookup_customer and classify_issue transition the workflow
```

**Example**: `examples/handoffs_customer_support.py`

---

## Pattern 8: Router

### Overview

A router classifies queries and dispatches them to specialized agents **in parallel**. Results are then synthesized into a coherent response. Typically **stateless**—each request handled independently.

### Architecture Diagram

```
                         User Query
                              │
                              ▼
                    ┌─────────────────┐
                    │     ROUTER      │
                    │   (Classify)    │
                    │                 │
                    │ • Rule-based    │
                    │ • LLM-based     │
                    │ • Hybrid        │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   DOCS AGENT    │ │   FAQ AGENT     │ │ TUTORIAL AGENT  │
│                 │ │                 │ │                 │
│ • API docs      │ │ • Pricing       │ │ • Getting started│
│ • Architecture  │ │ • Billing       │ │ • SDK guides    │
│ • Database      │ │ • Security      │ │ • Deployment    │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │
         │      PARALLEL     │      EXECUTION    │
         │                   │                   │
         └───────────────────┼───────────────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   SYNTHESIZER   │
                    │                 │
                    │ • Combine       │
                    │ • Deduplicate   │
                    │ • Format        │
                    └────────┬────────┘
                             │
                             ▼
                      Final Response
```

### Parallel Dispatch with Send()

```
┌──────────────────────────────────────────────────────────────┐
│                    STATE GRAPH                               │
└──────────────────────────────────────────────────────────────┘

[START] ──► [CLASSIFY] ──► dispatch_to_agents()
                                   │
                 ┌─────────────────┼─────────────────┐
                 │                 │                 │
                 ▼                 ▼                 ▼
          Send("docs")      Send("faq")      Send("tutorial")
                 │                 │                 │
                 │    PARALLEL     │    EXECUTION    │
                 │                 │                 │
                 └─────────────────┼─────────────────┘
                                   │
                                   ▼
                            [SYNTHESIZE]
                                   │
                                   ▼
                                [END]
```

### When to Use

| Use Case | Example |
|----------|---------|
| Distinct knowledge verticals | Docs + FAQ + Tutorials |
| Parallel querying needed | Enterprise knowledge base |
| Result synthesis required | Combining insights from multiple sources |
| Deterministic routing | Clear domain boundaries |

### Pros & Cons

| Pros | Cons |
|------|------|
| Excellent parallelization | Stateless (repeated routing overhead) |
| Efficient multi-domain queries | Limited multi-hop capability |
| Consistent per-request performance | Less distributed development support |
| Clear separation of concerns | Repeated context passing |

### Implementation

```python
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send

# Import from agentic_patterns package
from agentic_patterns.core import get_model, sanitize_query, with_retry_and_fallback
from agentic_patterns.tools.knowledge import search_docs, search_faq, search_tutorials
from agentic_patterns.state.router import RouterState, ClassificationResult
from agentic_patterns.agents.knowledge import CLASSIFICATION_PROMPT, SYNTHESIS_PROMPT

model = get_model()

def classify_query(state: RouterState) -> dict:
    """Classify query with PII redaction and retry/fallback."""
    sanitized = sanitize_query(state["query"])
    structured_llm = model.with_structured_output(ClassificationResult)
    result = structured_llm.invoke(CLASSIFICATION_PROMPT.format(query=sanitized))
    return {"classifications": [c.dict() for c in result.classifications]}

def route_to_agents(state: RouterState) -> list[Send]:
    """Dispatch to classified agents in parallel using Send()."""
    return [
        Send(f"{c['source']}_agent", {"query": c["query"]})
        for c in state["classifications"]
    ]

workflow = StateGraph(RouterState)
workflow.add_node("classify", classify_query)
workflow.add_node("docs_agent", docs_agent)
workflow.add_node("faq_agent", faq_agent)
workflow.add_node("tutorial_agent", tutorial_agent)
workflow.add_node("synthesize", synthesize_results)

workflow.add_edge(START, "classify")
workflow.add_conditional_edges("classify", route_to_agents, ["docs_agent", "faq_agent", "tutorial_agent", "synthesize"])
workflow.add_edge("docs_agent", "synthesize")
workflow.add_edge("faq_agent", "synthesize")
workflow.add_edge("tutorial_agent", "synthesize")
workflow.add_edge("synthesize", END)
```

**Example**: `examples/router_knowledge_base.py`

---

## Pattern 9: Custom Workflows

### Overview

Build **bespoke execution flows** using LangGraph's StateGraph. Mix deterministic logic with agentic behavior. Full control over branching, looping, and state management.

### Architecture Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                    STATE GRAPH                               │
│                                                              │
│   ┌────────────────────────────────────────────────────┐     │
│   │              ContentState (TypedDict)              │     │
│   │                                                    │     │
│   │  • topic, content_type, target_audience           │     │
│   │  • research_notes, outline, draft                 │     │
│   │  • review_feedback, revision_count                │     │
│   │  • quality_scores, final_content, status          │     │
│   └────────────────────────────────────────────────────┘     │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Content Pipeline Flow

```
                        [START]
                           │
                           ▼
                    ┌─────────────┐
                    │  RESEARCH   │
                    │             │
                    │ • Key points│
                    │ • Statistics│
                    │ • Angles    │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   OUTLINE   │
                    │             │
                    │ • Structure │
                    │ • Sections  │
                    │ • Keywords  │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐◄─────────────────┐
                    │    WRITE    │                  │
                    │             │                  │
                    │ • Draft     │                  │
                    │ • Apply     │                  │
                    │   feedback  │                  │
                    └──────┬──────┘                  │
                           │                        │
                           ▼                        │
                    ┌─────────────┐                 │
                    │   REVIEW    │                 │
                    │             │                 │
                    │ • Scores    │                 │
                    │ • Feedback  │                 │
                    └──────┬──────┘                 │
                           │                        │
              ┌────────────┼────────────┐           │
              │            │            │           │
              ▼            ▼            ▼           │
        [APPROVED]   [NEEDS REVISION]  [REJECT]     │
              │            │            │           │
              │            └────────────┼───────────┘
              │                         │
              ▼                         ▼
        ┌─────────────┐           ┌─────────────┐
        │  FINALIZE   │           │   REJECT    │
        │             │           │             │
        │ • Polish    │           │ • Document  │
        │ • Format    │           │ • Feedback  │
        └──────┬──────┘           └──────┬──────┘
               │                         │
               ▼                         ▼
             [END]                     [END]
```

### Conditional Routing

```python
from typing import Literal
from langgraph.graph import StateGraph, START, END

# Import from agentic_patterns package
from agentic_patterns.core import get_model
from agentic_patterns.state.content import ContentState, CONTENT_CONFIGS

model = get_model()

def route_after_review(state: ContentState) -> Literal["finalize", "revise", "reject"]:
    """Determine next step based on review outcome."""
    if state["status"] == "approved":
        return "finalize"

    if state.get("revision_count", 0) >= 3:  # MAX_REVISIONS
        return "reject"

    if state.get("quality_scores", {}).get("overall", 5) <= 3:
        return "reject"

    return "revise"  # Loop back to write node

# Build workflow with nodes and conditional edges
workflow = StateGraph(ContentState)
workflow.add_node("research", research_topic)
workflow.add_node("outline", create_outline)
workflow.add_node("write", write_draft)
workflow.add_node("review", review_content)
workflow.add_node("finalize", finalize_content)
workflow.add_node("reject", handle_rejection)

workflow.add_edge(START, "research")
workflow.add_edge("research", "outline")
workflow.add_edge("outline", "write")
workflow.add_edge("write", "review")

# Conditional routing after review
workflow.add_conditional_edges(
    "review",
    route_after_review,
    {"finalize": "finalize", "revise": "write", "reject": "reject"}
)
workflow.add_edge("finalize", END)
workflow.add_edge("reject", END)
```

**Example**: `examples/custom_workflow_content_pipeline.py`

### When to Use

| Use Case | Example |
|----------|---------|
| Complex branching logic | Content approval workflows |
| Iterative loops | Write-review-revise cycles |
| Custom state management | Pipeline with quality gates |
| Standard patterns don't fit | Unique business logic |

### Pros & Cons

| Pros | Cons |
|------|------|
| Full control over flow | More code to write |
| Custom state management | Steeper learning curve |
| Mix deterministic + agentic | Manual orchestration |
| Arbitrary complexity | Harder to debug |

---

## Comparison Table

### Capability Matrix

| Capability | Subagents | Deep Agents | Forward | Hierarchical | Quarantine | Skills | Handoffs | Router | Custom |
|------------|:---------:|:-----------:|:-------:|:------------:|:----------:|:------:|:--------:|:------:|:------:|
| **Distributed Development** | ★★★★★ | ★★★★★ | ★★★★☆ | ★★★★★ | ★★★★☆ | ★★★★★ | ★★☆☆☆ | ★★★☆☆ | ★★★★☆ |
| **Parallelization** | ★★★★★ | ★★★☆☆ | ★★★★☆ | ★★★★★ | ★★★☆☆ | ★★★☆☆ | ☆☆☆☆☆ | ★★★★★ | ★★★★★ |
| **Multi-hop Support** | ★★★★★ | ★★★★★ | ★★★★☆ | ★★★★★ | ★★★★☆ | ★★★★★ | ★★★★★ | ☆☆☆☆☆ | ★★★★★ |
| **Direct User Interaction** | ★☆☆☆☆ | ★★☆☆☆ | ★★★★☆ | ★★☆☆☆ | ★★☆☆☆ | ★★★★★ | ★★★★★ | ★★★☆☆ | ★★★★☆ |
| **Context Isolation** | ★★★★☆ | ★★★★★ | ★★★☆☆ | ★★★★☆ | ★★★★★ | ★★☆☆☆ | ★★☆☆☆ | ★★★★☆ | ★★★☆☆ |
| **Wording Accuracy** | ★★☆☆☆ | ★★★☆☆ | ★★★★★ | ★★☆☆☆ | ★★★☆☆ | ★★★☆☆ | ★★★☆☆ | ★★★☆☆ | ★★★☆☆ |
| **Scalability** | ★★★☆☆ | ★★★★☆ | ★★★☆☆ | ★★★★★ | ★★★★★ | ★★★☆☆ | ★★☆☆☆ | ★★★★☆ | ★★★★☆ |
| **Simplicity** | ★★★☆☆ | ★★★☆☆ | ★★★★☆ | ★★☆☆☆ | ★★★☆☆ | ★★★★☆ | ★★★☆☆ | ★★★★☆ | ★★☆☆☆ |

### Use Case Matrix

| Requirement | Best Pattern | Why |
|-------------|--------------|-----|
| Multiple distinct domains + parallel | **Subagents** | Centralized control, parallel execution |
| Tool-heavy tasks with context bloat | **Deep Agents** | Context isolation prevents overflow |
| Exact wording preservation needed | **Forward Tool** | No paraphrasing, audit trails |
| Large org with multiple teams | **Hierarchical** | Nested team coordination |
| Large data, need summaries only | **Quarantine** | Isolates huge outputs, returns summaries |
| Single agent, many specializations | **Skills** | Lightweight, direct interaction |
| Sequential workflow + state | **Handoffs** | State persistence, natural transitions |
| Parallel queries + synthesis | **Router** | Optimal for parallel dispatch |
| Complex branching/looping | **Custom** | Full control over logic |
| Legal/medical/financial advice | **Forward Tool** | Liability requires exact expert wording |
| Product launches, large projects | **Hierarchical** | Team-level encapsulation |
| Data analytics pipelines | **Quarantine** | Process 100K+ tokens, return insights |
| Customer support flows | **Handoffs** | Multi-stage conversations |
| Code assistant (multi-language) | **Skills** | Dynamic expertise loading |
| Knowledge base (multi-vertical) | **Router** | Parallel domain querying |
| Research system (many tool calls) | **Deep Agents** | Subagents handle tool-heavy work |
| Content pipeline | **Custom** | Review loops, quality gates |

---

## Decision Flowchart

```
                              START
                                │
                                ▼
                    ┌───────────────────────┐
                    │ Do you need multiple  │
                    │ specialized agents?   │
                    └───────────┬───────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
                   YES                      NO
                    │                       │
                    ▼                       ▼
        ┌───────────────────┐    ┌───────────────────┐
        │ Do agents need to │    │   Single Agent    │
        │ talk directly to  │    │   with Tools      │
        │ users?            │    │                   │
        └─────────┬─────────┘    └───────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
       YES                  NO
        │                   │
        ▼                   ▼
┌───────────────┐  ┌───────────────────────┐
│ Is workflow   │  │ Need parallel         │
│ sequential    │  │ execution?            │
│ (stages)?     │  └───────────┬───────────┘
└───────┬───────┘              │
        │              ┌───────┴───────┐
┌───────┴───────┐      │               │
│               │     YES              NO
YES             NO     │               │
│               │      ▼               ▼
▼               ▼  ┌────────┐    ┌──────────┐
┌────────┐  ┌──────────┐│SUBAGENTS│    │SUBAGENTS │
│HANDOFFS│  │  SKILLS  ││        │    │(simpler) │
│        │  │          │└────────┘    └──────────┘
└────────┘  └──────────┘


                    ┌───────────────────────┐
                    │ Need result synthesis │
                    │ from multiple sources?│
                    └───────────┬───────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
                   YES                      NO
                    │                       │
                    ▼                       ▼
              ┌──────────┐         ┌───────────────┐
              │  ROUTER  │         │ Need complex  │
              │          │         │ branching or  │
              └──────────┘         │ loops?        │
                                   └───────┬───────┘
                                           │
                                   ┌───────┴───────┐
                                   │               │
                                  YES              NO
                                   │               │
                                   ▼               ▼
                            ┌──────────┐    ┌──────────┐
                            │  CUSTOM  │    │ Simplest │
                            │ WORKFLOW │    │ Pattern  │
                            └──────────┘    │ That Fits│
                                            └──────────┘
```

### Quick Decision Guide

```
┌─────────────────────────────────────────────────────────────────┐
│                    QUICK PATTERN SELECTOR                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  "I need to coordinate domain experts"          → SUBAGENTS     │
│                                                                 │
│  "Tasks have many tool calls, context bloats"   → DEEP AGENTS   │
│                                                                 │
│  "Exact wording matters, can't paraphrase"      → FORWARD TOOL  │
│                                                                 │
│  "Multiple teams with internal structure"       → HIERARCHICAL  │
│                                                                 │
│  "Large data, only need summaries"              → QUARANTINE    │
│                                                                 │
│  "I want one agent that can do many things"     → SKILLS        │
│                                                                 │
│  "Users go through stages/steps"                → HANDOFFS      │
│                                                                 │
│  "Query multiple sources, combine results"      → ROUTER        │
│                                                                 │
│  "I need loops, branches, custom logic"         → CUSTOM        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Performance Characteristics

### Model Calls by Scenario

| Scenario | Subagents | Deep | Forward | Hierarchical | Quarantine | Skills | Handoffs | Router |
|----------|:---------:|:----:|:-------:|:------------:|:----------:|:------:|:--------:|:------:|
| **Single Request** | 4 | 3-6 | 4 | 6-12 | 3-5 | 3 | 3 | 3 |
| **Repeat Request** | 4 | 3-6 | 4 | 6-12 | 3-5 | 2 | 2 | 2-3 |
| **Multi-Domain** | 5 | 6-10 | 5 | 12-20 | 5-8 | 3 | N/A | 5 |

### Token Usage (Multi-Domain Query)

```
Quarantine:  ~3,000 tokens  ██░░░░░░░░░░░░░ (Best isolation, summaries only)
Deep Agents: ~6,000 tokens  █████░░░░░░░░░░ (Strong isolation)
Subagents:   ~9,000 tokens  ████████░░░░░░░ (Parallel, isolated)
Router:      ~9,000 tokens  ████████░░░░░░░ (Parallel, isolated)
Forward:    ~10,000 tokens  █████████░░░░░░ (Verbatim responses, longer)
Hierarchical:~12,000 tokens ██████████░░░░░ (Multiple levels)
Handoffs:   ~14,000 tokens  ████████████░░░ (Sequential, shared context)
Skills:     ~15,000 tokens  █████████████░░ (Context accumulation)
```

### Efficiency Summary

| Pattern | Best For | Worst For |
|---------|----------|-----------|
| **Subagents** | Parallel multi-domain | Single simple requests |
| **Deep Agents** | Tool-heavy research tasks | Simple queries (overkill) |
| **Forward Tool** | Legal/medical exactness | Conversational synthesis |
| **Hierarchical** | Large teams, complex orgs | Small projects |
| **Quarantine** | Large data processing | Small tool outputs |
| **Skills** | Repeat requests | Multi-domain (token bloat) |
| **Handoffs** | Sequential flows | Parallel execution |
| **Router** | Parallel synthesis | Stateful conversations |
| **Custom** | Complex logic | Simple use cases |

---

## Middleware & Context Engineering

Production multi-agent systems require more than just pattern selection—they need robust context management, resilience, and safety mechanisms. LangChain 1.2.x provides middleware for these concerns.

> **Reference**: [LangChain Middleware Documentation](https://docs.langchain.com/oss/python/langchain/middleware/built-in)

### Middleware Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      AGENT EXECUTION                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   User Message                                                   │
│        │                                                         │
│        ▼                                                         │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │              MIDDLEWARE STACK                           │   │
│   │                                                         │   │
│   │   ┌─────────────────────────────────────────────────┐   │   │
│   │   │ 1. SummarizationMiddleware                      │   │   │
│   │   │    Compress history when approaching limits     │   │   │
│   │   └─────────────────────────────────────────────────┘   │   │
│   │                         │                               │   │
│   │                         ▼                               │   │
│   │   ┌─────────────────────────────────────────────────┐   │   │
│   │   │ 2. ContextEditingMiddleware                     │   │   │
│   │   │    Remove old tool outputs, trim messages       │   │   │
│   │   └─────────────────────────────────────────────────┘   │   │
│   │                         │                               │   │
│   │                         ▼                               │   │
│   │   ┌─────────────────────────────────────────────────┐   │   │
│   │   │ 3. HumanInTheLoopMiddleware                     │   │   │
│   │   │    Require approval for sensitive operations    │   │   │
│   │   └─────────────────────────────────────────────────┘   │   │
│   │                         │                               │   │
│   │                         ▼                               │   │
│   │   ┌─────────────────────────────────────────────────┐   │   │
│   │   │ 4. ToolRetryMiddleware                          │   │   │
│   │   │    Retry failed tool calls with backoff         │   │   │
│   │   └─────────────────────────────────────────────────┘   │   │
│   │                         │                               │   │
│   │                         ▼                               │   │
│   │   ┌─────────────────────────────────────────────────┐   │   │
│   │   │ 5. ModelFallbackMiddleware                      │   │   │
│   │   │    Switch to backup model on failures           │   │   │
│   │   └─────────────────────────────────────────────────┘   │   │
│   │                                                         │   │
│   └─────────────────────────────────────────────────────────┘   │
│        │                                                         │
│        ▼                                                         │
│   Agent Response                                                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Middleware by Pattern

| Pattern | Middleware Stack | Configuration |
|---------|-----------------|---------------|
| **Subagents** | Summarization + ToolRetry + ModelFallback | Full resilience for supervisor |
| **Handoffs** | HITL + ModelCallLimit + ContextEditing + Summarization | Safety + cost control |
| **Router** | Custom (retry/fallback/PII redaction) | StateGraph-specific |
| **Skills** | LLMToolSelector + ToolCallLimit + ContextEditing + Summarization | Smart tool selection |

### Context Engineering Techniques

#### 1. Summarization Middleware

Compresses conversation history when approaching token limits.

```python
from langchain.agents.middleware import SummarizationMiddleware

summarization = SummarizationMiddleware(
    model="gpt-4o-mini",           # Smaller model for cost efficiency
    trigger=("tokens", 4000),       # Start summarizing at 4000 tokens
    keep=("messages", 10),          # Keep 10 most recent messages
)
```

**When to use**: Long conversations, multi-turn financial planning, extended support sessions.

#### 2. Tool Retry Middleware

Automatically retries failed tool calls with exponential backoff.

```python
from langchain.agents.middleware import ToolRetryMiddleware

tool_retry = ToolRetryMiddleware(
    max_retries=2,           # Maximum retry attempts
    backoff_factor=2.0,      # Exponential backoff multiplier
    initial_delay=1.0,       # Initial delay in seconds
    jitter=True,             # Add randomness to prevent thundering herd
)
```

**When to use**: External API calls, database operations, any potentially flaky integrations.

#### 3. Model Fallback Middleware

Switches to backup model when primary fails.

```python
from langchain.agents.middleware import ModelFallbackMiddleware

model_fallback = ModelFallbackMiddleware(
    "gpt-4o-mini",                    # Primary model
    "claude-3-5-haiku-20241022",      # Fallback model
)
```

**When to use**: Production systems requiring high availability.

#### 4. Human-in-the-Loop Middleware

Requires human approval for sensitive operations.

```python
from langchain.agents.middleware import HumanInTheLoopMiddleware

hitl = HumanInTheLoopMiddleware(
    tools_requiring_approval=["issue_refund", "apply_discount"],
)
```

**When to use**: Financial operations, customer support escalations, any action with real-world consequences.

#### 5. Context Editing Middleware

Removes old tool outputs when context exceeds threshold.

```python
from langchain.agents.middleware import ContextEditingMiddleware

context_editing = ContextEditingMiddleware(
    remove_tool_outputs_after=("tokens", 50000),  # Clear old outputs
)
```

**When to use**: Tool-heavy agents that accumulate large outputs (code execution, search results).

#### 6. Model Call Limit Middleware

Prevents infinite loops by limiting model calls.

```python
from langchain.agents.middleware import ModelCallLimitMiddleware

call_limit = ModelCallLimitMiddleware(
    per_thread=50,    # Max calls per conversation thread
    per_run=10,       # Max calls per single run
)
```

**When to use**: Any production agent to prevent runaway costs.

#### 7. LLM Tool Selector Middleware

Uses LLM to select relevant tools before main call.

```python
from langchain.agents.middleware import LLMToolSelectorMiddleware

tool_selector = LLMToolSelectorMiddleware(
    model="gpt-4o-mini",    # Fast model for selection
    max_tools=5,            # Select up to 5 relevant tools
)
```

**When to use**: Agents with many tools (15+) where providing all tools hurts performance.

### Pattern-Specific Middleware Examples

The `agentic_patterns.core.middleware` module provides factory functions for pre-configured middleware stacks:

#### Subagents Pattern (Finance Assistant)

```python
from agentic_patterns.core import (
    get_model, create_subagent_middleware, create_supervisor_middleware
)
from agentic_patterns.tools.finance import BUDGET_TOOLS, INVESTMENT_TOOLS, TAX_TOOLS
from agentic_patterns.agents.finance import FINANCE_SUPERVISOR_PROMPT

model = get_model()

# Sub-agents: lightweight retry only
budget_agent = create_agent(
    model,
    tools=BUDGET_TOOLS,
    middleware=create_subagent_middleware(),  # ToolRetryMiddleware only
)

# Supervisor: full context management
supervisor = create_agent(
    model,
    tools=[analyze_budget, analyze_investments, analyze_taxes],
    system_prompt=FINANCE_SUPERVISOR_PROMPT,
    middleware=create_supervisor_middleware(),  # Summarization + retry + fallback
)
```

#### Handoffs Pattern (Customer Support)

```python
from agentic_patterns.core import get_model, get_memory_checkpointer, create_support_middleware
from agentic_patterns.tools.support import SUPPORT_TOOLS
from agentic_patterns.state.support import SupportState

model = get_model()
checkpointer = get_memory_checkpointer()

# Pre-configured middleware: HITL + limits + context management
support_agent = create_react_agent(
    model,
    tools=SUPPORT_TOOLS,
    state_schema=SupportState,
    middleware=create_support_middleware(),  # HumanInTheLoop + ModelCallLimit + ContextEditing + Summarization
    checkpointer=checkpointer,
)
```

#### Router Pattern (StateGraph - Custom Logic)

```python
from agentic_patterns.core import sanitize_query, with_retry_and_fallback
from agentic_patterns.state.router import RouterState

# StateGraph uses custom utility functions instead of middleware
def classify_query(state: RouterState) -> dict:
    # PII redaction using core utility
    sanitized = sanitize_query(state["query"])

    def primary():
        return model.with_structured_output(ClassificationResult).invoke(prompt)

    def fallback():
        return fallback_model.with_structured_output(ClassificationResult).invoke(prompt)

    # Retry with fallback using core utility
    result = with_retry_and_fallback(primary, fallback, max_retries=2)()
    return {"classifications": [...]}
```

#### Skills Pattern (Code Assistant)

```python
from agentic_patterns.core import get_model, get_memory_checkpointer, create_skills_middleware
from agentic_patterns.tools.code import CODE_TOOLS

model = get_model()
checkpointer = get_memory_checkpointer()

# Pre-configured middleware: tool selector + limits + context management
code_assistant = create_agent(
    model,
    tools=CODE_TOOLS,
    middleware=create_skills_middleware(),  # LLMToolSelector + ToolCallLimit + ContextEditing + Summarization
    checkpointer=checkpointer,
)
```

### Middleware Selection Guide

```
┌─────────────────────────────────────────────────────────────────┐
│                MIDDLEWARE SELECTION FLOWCHART                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Long conversations?                                             │
│      │                                                           │
│      YES ──► SummarizationMiddleware                             │
│                                                                  │
│  External API calls?                                             │
│      │                                                           │
│      YES ──► ToolRetryMiddleware                                 │
│                                                                  │
│  Production system?                                              │
│      │                                                           │
│      YES ──► ModelFallbackMiddleware + ModelCallLimitMiddleware  │
│                                                                  │
│  Sensitive operations (refunds, deletions)?                      │
│      │                                                           │
│      YES ──► HumanInTheLoopMiddleware                            │
│                                                                  │
│  Heavy tool outputs (code, search)?                              │
│      │                                                           │
│      YES ──► ContextEditingMiddleware                            │
│                                                                  │
│  Many tools (15+)?                                               │
│      │                                                           │
│      YES ──► LLMToolSelectorMiddleware                           │
│                                                                  │
│  Processing user data?                                           │
│      │                                                           │
│      YES ──► PII Redaction (custom or middleware)                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Summary

| Pattern | Key Characteristic | Primary Trade-off |
|---------|-------------------|-------------------|
| **Subagents** | Centralized coordination | Control vs. latency |
| **Deep Agents** | Context isolation | Token efficiency vs. info loss |
| **Forward Tool** | Verbatim forwarding | Accuracy vs. conversational flow |
| **Hierarchical** | Nested team structure | Scalability vs. complexity |
| **Quarantine** | Large data isolation | Context savings vs. detail loss |
| **Skills** | Progressive disclosure | Simplicity vs. token usage |
| **Handoffs** | State-driven transitions | Natural flow vs. no parallelism |
| **Router** | Parallel dispatch | Efficiency vs. statelessness |
| **Custom** | Full control | Flexibility vs. complexity |

> **Remember**: Start simple. Add complexity only when you hit clear limits. The best architecture is the simplest one that meets your requirements.
