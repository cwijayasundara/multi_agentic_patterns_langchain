"""
Code assistant tools for the skills pattern.

Provides tools for:
- Skill discovery and loading
- Code boilerplate generation
"""

from agentic_patterns.tools.code.skills import (
    load_skill,
    list_available_skills,
    list_loaded_skills,
    unload_skill,
    get_skill_details,
    get_loaded_skills,
    reset_loaded_skills,
    set_skills_directory,
)

from agentic_patterns.tools.code.generation import generate_boilerplate

# Tool collections for easy import
SKILL_TOOLS = [
    load_skill,
    list_available_skills,
    list_loaded_skills,
    unload_skill,
    get_skill_details,
]

GENERATION_TOOLS = [generate_boilerplate]

CODE_TOOLS = SKILL_TOOLS + GENERATION_TOOLS

__all__ = [
    # Skill tools
    "load_skill",
    "list_available_skills",
    "list_loaded_skills",
    "unload_skill",
    "get_skill_details",
    # Skill state management
    "get_loaded_skills",
    "reset_loaded_skills",
    "set_skills_directory",
    # Generation tools
    "generate_boilerplate",
    # Collections
    "SKILL_TOOLS",
    "GENERATION_TOOLS",
    "CODE_TOOLS",
]
