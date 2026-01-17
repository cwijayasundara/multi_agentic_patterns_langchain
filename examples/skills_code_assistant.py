"""
Skills Pattern: Multi-Language Code Assistant
=============================================
A single agent that progressively loads specialized coding skills on demand.
Skills are .md files with YAML frontmatter, following the Agent Skills pattern.

Skill Structure:
  skills/
  ├── python-expert/
  │   └── SKILL.md
  ├── javascript-expert/
  │   └── SKILL.md
  └── ...

This pattern is best when:
- You have a single agent with many possible specializations
- No need to enforce specific constraints between skills
- Different teams can develop capabilities independently
- You want lightweight composition without full sub-agents

Key Concepts:
- Progressive disclosure: Load skill descriptions initially, full content on demand
- Skill descriptions in system prompt help agent recognize when to load skills
- load_skill tool fetches full content when needed
- Context efficiency: Only 2-3 skills loaded per task, not all available

Middleware (Context Engineering):
- SummarizationMiddleware: Compress long coding sessions
- ContextEditingMiddleware: Clear old skill content when context fills
- LLMToolSelectorMiddleware: Intelligently filter tools based on query
- ToolCallLimitMiddleware: Prevent excessive skill loading

Reference:
- https://docs.langchain.com/oss/python/langchain/multi-agent/skills-sql-assistant
- https://docs.langchain.com/oss/python/langchain/middleware/built-in
"""

from pathlib import Path
from langchain.agents import create_agent

# Import from the agentic_patterns package
from agentic_patterns.core import (
    get_model,
    get_memory_checkpointer,
    create_skills_middleware,
)
from agentic_patterns.tools.code import (
    CODE_TOOLS,
    set_skills_directory,
    reset_loaded_skills,
)


# Initialize model and checkpointer
model = get_model()
checkpointer = get_memory_checkpointer()

# Set the skills directory (relative to examples/ folder)
SKILLS_DIR = Path(__file__).parent.parent / "skills"
set_skills_directory(SKILLS_DIR)

# Get middleware stack
SKILLS_MIDDLEWARE = create_skills_middleware()


# ============================================
# System Prompt
# ============================================

SKILLS_AGENT_PROMPT = """You are a versatile code assistant with access to specialized skills.

Skills are external .md files containing domain expertise, coding standards, and best practices.
Skills use progressive disclosure - only loaded when needed to conserve context.

Your Workflow:
1. When asked about a specific programming language or domain, FIRST load the appropriate skill
2. Apply the expertise from loaded skills to answer questions
3. Follow all guidelines from loaded skills strictly
4. You can load multiple skills for cross-cutting concerns (e.g., python-expert + devops-expert)

Available Actions:
- load_skill: Load a skill to gain expertise (e.g., 'python-expert', 'go-expert')
- list_available_skills: See all skills you can load
- list_loaded_skills: See your current active skills
- unload_skill: Remove a skill if no longer needed
- get_skill_details: Preview a skill before loading
- generate_boilerplate: Create starter code for projects

Important:
- Always load relevant skills before answering technical questions
- Follow the coding standards and best practices from loaded skills
- Provide complete, production-ready code examples
- Explain your reasoning based on skill guidelines"""


# ============================================
# Create Skills-Based Agent
# ============================================

agent = create_agent(
    model=model,
    tools=CODE_TOOLS,
    system_prompt=SKILLS_AGENT_PROMPT,
    middleware=SKILLS_MIDDLEWARE,
    checkpointer=checkpointer,
)

app = agent


# ============================================
# Example Usage
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("SKILLS PATTERN: Multi-Language Code Assistant")
    print("=" * 60)

    # Import to show discovered skills
    from agentic_patterns.tools.code.skills import _skills

    print(f"\nDiscovered {len(_skills)} skills from {SKILLS_DIR}:")
    for skill_id, skill in _skills.items():
        desc = skill['description'][:50] + "..." if len(skill['description']) > 50 else skill['description']
        print(f"  - {skill_id}: {desc}")

    # Example queries demonstrating skill loading and usage
    queries = [
        "What skills are available?",
        "Help me write a Python async function to fetch multiple URLs concurrently and handle errors gracefully.",
        "Now help me write the same thing in Go with proper context handling.",
    ]

    # Config with thread_id for checkpointer
    config = {"configurable": {"thread_id": "skills_demo_session"}}

    for i, query in enumerate(queries, 1):
        print(f"\n{'='*60}")
        print(f"Query {i}: {query}")
        print("-" * 60)

        result = app.invoke(
            {"messages": [{"role": "user", "content": query}]},
            config=config
        )

        print(f"\nResponse:\n{result['messages'][-1].content}")

        # Reset loaded skills between demo queries
        if i == 1:
            reset_loaded_skills()
