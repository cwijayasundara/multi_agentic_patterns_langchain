---
name: skills
title: Skills (Prompt-Based Specializations)
description: Single agent dynamically loads prompt-based specializations from external .md files
category: single-agent
complexity: low
---

## When to Use

- Single agent with many possible specializations
- Skills are prompt-based (guidelines, patterns, best practices)
- Different teams can develop capabilities independently
- No need for separate agent instances per skill
- Lightweight composition without full sub-agents
- Skills can be added without code changes

## When NOT to Use

- Skills need their own isolated tool sets (use **Subagents**)
- Need strict enforcement between specializations
- Skills conflict with each other
- Heavy coordination between specializations needed

## Key Characteristics

| Capability | Rating |
|------------|--------|
| Development Flexibility | Very High |
| Lightweight Composition | Very High |
| Skill Independence | High |
| Tool Isolation | Low |
| Runtime Adaptability | High |

## Decision Triggers

Ask yourself these questions:

1. "Are specializations primarily prompt/knowledge-based?" -> HIGH fit if yes
2. "Can one agent effectively use multiple skills?" -> HIGH fit if yes
3. "Do you want to add capabilities without code changes?" -> HIGH fit if yes
4. "Are skills independent and non-conflicting?" -> HIGH fit if yes

## Example Use Cases

- **Code Assistant**: Load Python-expert, JavaScript-expert, SQL-expert skills
- **Writing Assistant**: Load technical-writing, creative-writing, documentation skills
- **Support Agent**: Load product-knowledge, troubleshooting, policy skills
- **Analysis Assistant**: Load financial-analysis, statistical-analysis skills

## Trade-offs

**Pros:**
- Very lightweight - just .md files with prompts
- Skills can be developed by non-engineers
- Hot-swappable without restarts
- Single agent reduces complexity
- Progressive loading conserves context

**Cons:**
- All skills share the same tools
- No hard boundaries between skills
- Skills may conflict in edge cases
- Less isolation than separate agents

## Architecture Pattern

```
User <-> Single Agent
              |
         [load_skill tool]
              |
    +----+----+----+----+
    |    |    |    |    |
   S1   S2   S3   S4  ...
(skill .md files loaded on demand)
```

## Skill File Format

```markdown
---
name: python-expert
description: Use for Python development, best practices, async programming
---

# Python Expert Skill

Guidelines, patterns, and expertise content here...
```

## Code Reference

See: `examples/skills_code_assistant.py`

## Key APIs

- `create_agent()` with skill-loading tools
- `load_skill(name)` - Load a skill into context
- `list_available_skills()` - See available skills
- `unload_skill(name)` - Remove a skill from context
- Skills stored in `skills/` directory
