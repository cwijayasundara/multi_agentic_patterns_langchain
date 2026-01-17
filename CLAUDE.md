# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository demonstrates the 9 core multi-agent patterns in LangChain/LangGraph 1.2.x through working sample applications. The codebase is organized as a Python package (`agentic_patterns`) with reusable components and example applications.

## Running the Examples

**Important:** Use a fresh virtual environment. LangChain 1.2.x has breaking changes and is incompatible with older LangChain packages (e.g., langchain-milvus, nvidia-nat-langchain).

```bash
# Setup (use a fresh venv to avoid dependency conflicts)
python -m venv venv
source venv/bin/activate
pip install -e .  # Install package in editable mode

# Configure OpenAI API key
cp .env.example .env
# Edit .env with your OPENAI_API_KEY

# Run any pattern
python examples/subagents_finance_assistant.py
python examples/deep_agents_research_assistant.py
python examples/skills_code_assistant.py
python examples/handoffs_customer_support.py
python examples/router_knowledge_base.py
python examples/custom_workflow_content_pipeline.py
```

## Package Structure

```
langchain_agentic_patterns/
├── src/agentic_patterns/             # Main package
│   ├── __init__.py
│   │
│   ├── core/                         # Shared infrastructure
│   │   ├── config.py                 # get_model(), DEFAULT_MODEL constants
│   │   ├── middleware.py             # Middleware preset factories
│   │   ├── checkpointer.py           # get_memory_checkpointer()
│   │   └── utils.py                  # PII redaction, retry/fallback wrapper
│   │
│   ├── tools/                        # Domain-specific tools
│   │   ├── finance/                  # Budget, investment, tax (9 tools)
│   │   ├── support/                  # Workflow, billing, tech, resolution (10 tools)
│   │   ├── code/                     # Skills, generation (6 tools)
│   │   └── knowledge/                # Search tools (3 tools)
│   │
│   ├── agents/                       # Agent prompts & configs
│   │   ├── finance.py                # BUDGET/INVESTMENT/TAX/SUPERVISOR prompts
│   │   ├── support.py                # STEP_CONFIG, get_step_config()
│   │   └── knowledge.py              # CLASSIFICATION/SYNTHESIS prompts
│   │
│   └── state/                        # TypedDict & Pydantic models
│       ├── support.py                # SupportState, SupportStep
│       ├── router.py                 # RouterState, ClassificationResult
│       └── content.py                # ContentState, CONTENT_CONFIGS
│
├── skills/                           # External skill .md files
├── examples/                         # Simplified demo applications
│   ├── subagents_finance_assistant.py
│   ├── deep_agents_research_assistant.py
│   ├── supervisor_forward_tool.py
│   ├── hierarchical_teams.py
│   ├── context_quarantine.py
│   ├── skills_code_assistant.py
│   ├── handoffs_customer_support.py
│   ├── router_knowledge_base.py
│   └── custom_workflow_content_pipeline.py
└── pyproject.toml                    # Package configuration
```

## Architecture

### Pattern 1: Subagents (`examples/subagents_finance_assistant.py`)
- **Structure**: Supervisor agent coordinates specialized subagents (budget_analyst, investment_advisor, tax_consultant)
- **Key APIs**: `create_agent()` from langchain.agents, subagent wrapper tools
- **Imports from package**:
  - `agentic_patterns.core`: get_model, get_memory_checkpointer, create_subagent_middleware
  - `agentic_patterns.tools.finance`: BUDGET_TOOLS, INVESTMENT_TOOLS, TAX_TOOLS
  - `agentic_patterns.agents.finance`: BUDGET_AGENT_PROMPT, FINANCE_SUPERVISOR_PROMPT

### Pattern 2: Deep Agents (`examples/deep_agents_research_assistant.py`)
- **Structure**: Main agent delegates to specialized subagents with context isolation
- **Key APIs**: `create_deep_agent()` from deepagents, `task()` tool for delegation
- **Key Features**:
  - Subagents handle tool-heavy work in isolated contexts
  - Main agent receives only final summaries, not raw data
  - Prevents context bloat from intermediate results
  - Built-in planning with task/todo tools
- **Use when**: Tasks require many tool calls with large outputs, context management is critical

### Pattern 3: Supervisor with Forward Tool (`examples/supervisor_forward_tool.py`)
- **Structure**: Supervisor forwards subagent responses verbatim without re-generating
- **Key APIs**: `create_react_agent()`, forward tools that pass responses unchanged
- **Key Features**:
  - Subagent responses forwarded directly to users
  - Prevents paraphrasing errors in legal/medical/financial domains
  - Maintains audit trails and accountability
- **Use when**: Exact wording matters, liability concerns, need attribution

### Pattern 4: Hierarchical Teams (`examples/hierarchical_teams.py`)
- **Structure**: Multi-level hierarchy where team leads are LangGraph subgraphs
- **Key APIs**: `StateGraph` for teams, nested subgraph compilation
- **Key Features**:
  - Teams operate as independent workflows
  - Team leads synthesize specialist outputs
  - Top supervisor coordinates across teams
- **Use when**: Complex nested workflows, large organizations, team-level encapsulation

### Pattern 5: Context Quarantine (`examples/context_quarantine.py`)
- **Structure**: Subagents isolate large tool outputs from main agent context
- **Key APIs**: `StateGraph`, quarantine subagents with summarization
- **Key Features**:
  - Raw data (~100K tokens) never enters main context
  - Only summaries (~500 tokens) returned
  - Prevents context bloat degradation
- **Use when**: Large data processing, sustained reasoning needed, tool outputs are huge

### Pattern 6: Skills (`examples/skills_code_assistant.py`)
- **Structure**: Single agent dynamically loads prompt-based specializations
- **Key APIs**: `create_agent()` with skill-loading tools
- **Imports from package**:
  - `agentic_patterns.core`: get_model, create_skills_middleware
  - `agentic_patterns.tools.code`: CODE_TOOLS, set_skills_directory, reset_loaded_skills
- **State**: Module-level `_loaded_skills` list in `tools/code/skills.py`

### Pattern 7: Handoffs (`examples/handoffs_customer_support.py`)
- **Structure**: Agents hand off conversations dynamically via Command objects
- **Key APIs**: `create_react_agent()`, `Command` from langgraph.types
- **Imports from package**:
  - `agentic_patterns.core`: get_model, create_support_middleware
  - `agentic_patterns.tools.support`: SUPPORT_TOOLS
  - `agentic_patterns.state.support`: SupportState
  - `agentic_patterns.agents.support`: BASE_SUPPORT_PROMPT, STEP_CONFIG

### Pattern 8: Router (`examples/router_knowledge_base.py`)
- **Structure**: StateGraph classifies queries and dispatches to specialized agents in parallel using `Send()`
- **Key APIs**: `StateGraph`, `Send`, structured output with Pydantic
- **Imports from package**:
  - `agentic_patterns.core`: get_model, sanitize_query, with_retry_and_fallback
  - `agentic_patterns.tools.knowledge`: search_docs, search_faq, search_tutorials
  - `agentic_patterns.state.router`: RouterState, AgentInput, ClassificationResult
  - `agentic_patterns.agents.knowledge`: CLASSIFICATION_PROMPT, SYNTHESIS_PROMPT

### Pattern 9: Custom Workflows (`examples/custom_workflow_content_pipeline.py`)
- **Structure**: StateGraph with research -> outline -> write -> review loop
- **Key APIs**: `StateGraph`, `add_conditional_edges()`
- **Imports from package**:
  - `agentic_patterns.core`: get_model
  - `agentic_patterns.state.content`: ContentState, CONTENT_CONFIGS

## Middleware & Context Engineering

Each pattern uses middleware factories from `agentic_patterns.core.middleware`:

| Pattern | Factory Function | Purpose |
|---------|-----------------|---------|
| Subagents | `create_subagent_middleware()` | ToolRetryMiddleware |
| Subagents | `create_supervisor_middleware()` | Summarization + retry + fallback |
| Handoffs | `create_support_middleware()` | Human approval + limits + context |
| Skills | `create_skills_middleware()` | Tool selector + limits + context |

> **Reference**: [LangChain Middleware Documentation](https://docs.langchain.com/oss/python/langchain/middleware/built-in)

### Middleware by Pattern

#### Subagents Pattern
- `SummarizationMiddleware`: Compress conversation at 4000 tokens
- `ToolRetryMiddleware`: Exponential backoff for failed tool calls
- `ModelFallbackMiddleware`: Automatic failover (gpt-4o-mini → claude-3-5-haiku)

#### Handoffs Pattern
- `HumanInTheLoopMiddleware`: Require approval for refunds/discounts
- `ModelCallLimitMiddleware`: Prevent infinite loops (50/thread, 10/run)
- `ContextEditingMiddleware`: Clear old tool outputs at 50000 tokens
- `SummarizationMiddleware`: Compress at 6000 tokens

#### Router Pattern
- Custom retry/fallback logic (StateGraph doesn't use middleware directly)
- PII redaction before processing queries
- Structured output for type-safe routing

#### Skills Pattern
- `LLMToolSelectorMiddleware`: Select relevant tools before main call
- `ToolCallLimitMiddleware`: Max 10 skill loads per thread
- `ContextEditingMiddleware`: Clear old skill content at 60000 tokens
- `SummarizationMiddleware`: Compress at 8000 tokens

## Key Dependencies

- `langchain` - Core framework with `init_chat_model()` for provider-agnostic model initialization
- `langchain-openai` - OpenAI integration (auto-selected by `init_chat_model` when using OpenAI models)
- `langgraph` - Graph-based workflows, `StateGraph`
- `langgraph-supervisor` - `create_supervisor()` for subagent coordination
- `langgraph-swarm` - `create_swarm()`, `create_handoff_tool()` for agent handoffs
- `deepagents` - `create_deep_agent()` for context-isolated subagents
- `python-dotenv` - Environment variable management

## Common Import Patterns

```python
# Core utilities
from agentic_patterns.core import get_model, get_memory_checkpointer
from agentic_patterns.core import create_subagent_middleware, create_support_middleware

# Tool collections
from agentic_patterns.tools import FINANCE_TOOLS, SUPPORT_TOOLS, CODE_TOOLS, KNOWLEDGE_TOOLS

# Individual tools
from agentic_patterns.tools.finance import get_spending_by_category, execute_rebalance
from agentic_patterns.tools.support import lookup_customer, process_refund

# Agent prompts
from agentic_patterns.agents import BUDGET_AGENT_PROMPT, FINANCE_SUPERVISOR_PROMPT
from agentic_patterns.agents.support import STEP_CONFIG, get_step_config

# State definitions
from agentic_patterns.state import SupportState, RouterState, ContentState
```

## Tool Counts by Module

| Module | Tools |
|--------|-------|
| `tools/finance/budget.py` | 3 (get_spending_by_category, create_budget_alert, get_monthly_summary) |
| `tools/finance/investment.py` | 3 (get_portfolio_performance, get_asset_allocation, execute_rebalance) |
| `tools/finance/tax.py` | 3 (estimate_tax_liability, find_tax_optimization_opportunities, get_tax_loss_harvesting_candidates) |
| `tools/support/workflow.py` | 2 (lookup_customer, classify_issue) |
| `tools/support/billing.py` | 3 (check_billing_history, process_refund, apply_discount) |
| `tools/support/tech.py` | 3 (run_diagnostics, check_service_status, create_engineering_ticket) |
| `tools/support/resolution.py` | 2 (escalate_to_specialist, resolve_ticket) |
| `tools/code/skills.py` | 5 (load_skill, list_available_skills, list_loaded_skills, unload_skill, get_skill_details) |
| `tools/code/generation.py` | 1 (generate_boilerplate) |
| `tools/knowledge/search.py` | 3 (search_docs, search_faq, search_tutorials) |
| **Total** | **28 tools** |

## Development Notes

- All examples use `get_model()` which defaults to `gpt-4o-mini` via `init_chat_model()`
- Tools are defined with `@tool` decorator from `langchain_core.tools`
- Support tools return `Command` objects for state transitions
- Skills pattern uses module-level state (`_loaded_skills`) for demo simplicity
- Mock data is used in place of real APIs/databases for demonstration
- Each example file has an `if __name__ == "__main__":` block with example queries
