"""
Skill loading tools for the skills pattern.

Skills are .md files with YAML frontmatter that provide domain-specific
expertise, coding standards, and best practices.

Module-level state:
- _loaded_skills: List of currently loaded skill IDs
- _skills: Dictionary of discovered skills (populated by discover_skills)
- _skills_dir: Path to the skills directory
"""

import re
from pathlib import Path
from langchain_core.tools import tool


# Module-level state
_loaded_skills: list[str] = []
_skills: dict = {}
_skills_dir: Path = Path(__file__).parent.parent.parent.parent.parent.parent / "skills"


def set_skills_directory(path: Path) -> None:
    """Set the skills directory and rediscover skills.

    Args:
        path: Path to the skills directory
    """
    global _skills_dir, _skills
    _skills_dir = Path(path)
    _skills = discover_skills()


def get_loaded_skills() -> list[str]:
    """Get the list of currently loaded skill IDs."""
    return _loaded_skills.copy()


def reset_loaded_skills() -> None:
    """Reset the loaded skills list (useful for testing)."""
    global _loaded_skills
    _loaded_skills = []


def parse_skill_frontmatter(content: str) -> dict:
    """Parse YAML frontmatter from SKILL.md content.

    Args:
        content: Full content of SKILL.md file

    Returns:
        Dictionary with 'name', 'description', and 'body' keys
    """
    frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
    match = re.match(frontmatter_pattern, content, re.DOTALL)

    if not match:
        return {"name": "unknown", "description": "No description", "body": content}

    frontmatter_text = match.group(1)
    body = match.group(2)

    # Simple YAML parsing for name and description
    metadata = {}
    for line in frontmatter_text.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            metadata[key.strip()] = value.strip()

    return {
        "name": metadata.get("name", "unknown"),
        "description": metadata.get("description", "No description"),
        "body": body.strip()
    }


def discover_skills() -> dict:
    """Discover all available skills from the skills directory.

    Uses progressive disclosure - only loads name and description at startup.

    Returns:
        Dictionary mapping skill_id to {name, description, path}
    """
    skills = {}

    if not _skills_dir.exists():
        return skills

    for skill_dir in _skills_dir.iterdir():
        if skill_dir.is_dir():
            skill_file = skill_dir / "SKILL.md"
            if skill_file.exists():
                content = skill_file.read_text()
                parsed = parse_skill_frontmatter(content)

                skill_id = skill_dir.name  # e.g., "python-expert"
                skills[skill_id] = {
                    "name": parsed["name"],
                    "description": parsed["description"],
                    "path": skill_file
                }

    return skills


def load_skill_content(skill_path: Path) -> str:
    """Load full skill content when activated.

    Args:
        skill_path: Path to SKILL.md file

    Returns:
        Full skill body content (without frontmatter)
    """
    content = skill_path.read_text()
    parsed = parse_skill_frontmatter(content)
    return parsed["body"]


# Discover skills at module load (progressive disclosure - metadata only)
_skills = discover_skills()


@tool
def load_skill(skill_name: str) -> str:
    """Load a specialized coding skill to enhance your expertise.

    Skills are loaded from external .md files and provide domain-specific
    guidelines, patterns, and best practices.

    Args:
        skill_name: Name of the skill to load (e.g., 'python-expert', 'go-expert')
    """
    global _loaded_skills

    # Normalize skill name (support both underscore and hyphen)
    skill_id = skill_name.lower().replace("_", "-").replace(" ", "-")

    if skill_id not in _skills:
        available = ", ".join(_skills.keys())
        return f"Skill '{skill_name}' not found.\n\nAvailable skills:\n{available}"

    skill = _skills[skill_id]

    if skill_id in _loaded_skills:
        return f"Skill '{skill['name']}' is already loaded."

    # Load full skill content (progressive disclosure)
    skill_content = load_skill_content(skill["path"])

    _loaded_skills.append(skill_id)

    return f"""Successfully loaded: {skill['name']}

Description: {skill['description']}

{skill_content}

---
Skill '{skill['name']}' is now active. Apply these guidelines to all related questions."""


@tool
def list_available_skills() -> str:
    """List all available skills that can be loaded.

    Skills are discovered from the skills/ directory. Each skill is a folder
    containing a SKILL.md file with instructions and guidelines.
    """
    if not _skills:
        return "No skills found. Create skills in the 'skills/' directory."

    output = ["Available Skills:", "=" * 50]

    for skill_id, skill in sorted(_skills.items()):
        status = " (LOADED)" if skill_id in _loaded_skills else ""
        output.append(f"\n{skill['name']}{status}")
        output.append(f"  ID: {skill_id}")
        output.append(f"  Description: {skill['description']}")

    output.append(f"\n{'=' * 50}")
    output.append(f"Total: {len(_skills)} skills available")
    output.append(f"Loaded: {len(_loaded_skills)} skills active")

    return "\n".join(output)


@tool
def list_loaded_skills() -> str:
    """List all currently loaded skills in this session."""
    if not _loaded_skills:
        return "No skills currently loaded. Use load_skill to load one."

    output = ["Currently Loaded Skills:", "=" * 40]
    for skill_id in _loaded_skills:
        skill = _skills[skill_id]
        output.append(f"- {skill['name']} ({skill_id})")

    return "\n".join(output)


@tool
def unload_skill(skill_name: str) -> str:
    """Unload a previously loaded skill to free up context.

    Args:
        skill_name: Name of the skill to unload
    """
    global _loaded_skills
    skill_id = skill_name.lower().replace("_", "-").replace(" ", "-")

    if skill_id not in _loaded_skills:
        return f"Skill '{skill_name}' is not currently loaded."

    _loaded_skills.remove(skill_id)
    return f"Skill '{_skills[skill_id]['name']}' has been unloaded."


@tool
def get_skill_details(skill_name: str) -> str:
    """Get detailed information about a specific skill without loading it.

    This previews the skill content so you can decide if it's relevant.

    Args:
        skill_name: Name of the skill to inspect
    """
    skill_id = skill_name.lower().replace("_", "-").replace(" ", "-")

    if skill_id not in _skills:
        available = ", ".join(_skills.keys())
        return f"Skill '{skill_name}' not found.\n\nAvailable: {available}"

    skill = _skills[skill_id]
    is_loaded = " (Currently Loaded)" if skill_id in _loaded_skills else ""

    # Load full content for preview
    skill_content = load_skill_content(skill["path"])

    return f"""{skill['name']}{is_loaded}
{"=" * 50}

ID: {skill_id}
Description: {skill['description']}
Path: {skill['path']}

Full Skill Content:
{skill_content}"""
