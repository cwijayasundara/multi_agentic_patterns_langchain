"""
Pattern knowledge tools for the Pattern Selector Agent.

Tools for searching, loading, and comparing pattern documentation.
Uses progressive disclosure - loads summaries first, full content on demand.
"""

import re
from pathlib import Path
from langchain_core.tools import tool


# Module-level state
_loaded_patterns: list[str] = []
_patterns: dict = {}
_knowledge_dir: Path = Path(__file__).parent.parent / "knowledge"


def parse_pattern_frontmatter(content: str) -> dict:
    """Parse YAML frontmatter from pattern .md content.

    Args:
        content: Full content of pattern .md file

    Returns:
        Dictionary with metadata and body
    """
    frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
    match = re.match(frontmatter_pattern, content, re.DOTALL)

    if not match:
        return {
            "name": "unknown",
            "title": "Unknown Pattern",
            "description": "No description",
            "category": "unknown",
            "complexity": "unknown",
            "body": content
        }

    frontmatter_text = match.group(1)
    body = match.group(2)

    # Simple YAML parsing
    metadata = {}
    for line in frontmatter_text.split('\n'):
        if ':' in line:
            key, value = line.split(':', 1)
            metadata[key.strip()] = value.strip()

    return {
        "name": metadata.get("name", "unknown"),
        "title": metadata.get("title", "Unknown Pattern"),
        "description": metadata.get("description", "No description"),
        "category": metadata.get("category", "unknown"),
        "complexity": metadata.get("complexity", "unknown"),
        "body": body.strip()
    }


def discover_patterns() -> dict:
    """Discover all available patterns from the knowledge directory.

    Returns:
        Dictionary mapping pattern_name to metadata
    """
    patterns = {}

    if not _knowledge_dir.exists():
        return patterns

    for pattern_file in _knowledge_dir.glob("*.md"):
        content = pattern_file.read_text()
        parsed = parse_pattern_frontmatter(content)

        pattern_name = parsed["name"]
        patterns[pattern_name] = {
            "name": parsed["name"],
            "title": parsed["title"],
            "description": parsed["description"],
            "category": parsed["category"],
            "complexity": parsed["complexity"],
            "path": pattern_file
        }

    return patterns


def get_loaded_patterns() -> list[str]:
    """Get list of currently loaded pattern names."""
    return _loaded_patterns.copy()


def reset_loaded_patterns() -> None:
    """Reset loaded patterns (useful for testing)."""
    global _loaded_patterns
    _loaded_patterns = []


# Discover patterns at module load
_patterns = discover_patterns()


@tool
def list_all_patterns() -> str:
    """List all 9 available agentic patterns with brief descriptions.

    Use this at the start of a conversation to understand what patterns exist.
    Each pattern is designed for specific use cases and trade-offs.
    """
    if not _patterns:
        return "No patterns found in knowledge directory."

    output = [
        "Available Agentic Patterns",
        "=" * 60,
        ""
    ]

    # Group by category
    categories = {}
    for name, pattern in _patterns.items():
        cat = pattern["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(pattern)

    for category, patterns in sorted(categories.items()):
        output.append(f"\n## {category.upper()}")
        output.append("-" * 40)
        for p in sorted(patterns, key=lambda x: x["name"]):
            status = " (LOADED)" if p["name"] in _loaded_patterns else ""
            output.append(f"\n**{p['title']}**{status}")
            output.append(f"  Name: {p['name']}")
            output.append(f"  Complexity: {p['complexity']}")
            output.append(f"  {p['description']}")

    output.append(f"\n{'=' * 60}")
    output.append(f"Total: {len(_patterns)} patterns")
    output.append(f"Loaded: {len(_loaded_patterns)} patterns in context")

    return "\n".join(output)


@tool
def load_pattern(pattern_name: str) -> str:
    """Load full details of a specific pattern into context.

    Use this when you need in-depth information about a pattern's
    use cases, trade-offs, and decision triggers.

    Args:
        pattern_name: Name of the pattern (e.g., 'subagents', 'handoffs')
    """
    global _loaded_patterns

    # Normalize name
    name = pattern_name.lower().replace("_", "-").replace(" ", "-")

    if name not in _patterns:
        available = ", ".join(_patterns.keys())
        return f"Pattern '{pattern_name}' not found.\n\nAvailable patterns: {available}"

    pattern = _patterns[name]

    if name in _loaded_patterns:
        return f"Pattern '{pattern['title']}' is already loaded in context."

    # Load full content
    content = pattern["path"].read_text()
    parsed = parse_pattern_frontmatter(content)

    _loaded_patterns.append(name)

    return f"""Successfully loaded: {pattern['title']}

Category: {pattern['category']}
Complexity: {pattern['complexity']}

{parsed['body']}

---
Pattern '{pattern['title']}' is now in context. Use this information to evaluate fit for the user's requirements."""


@tool
def search_patterns(query: str) -> str:
    """Search pattern documentation for specific keywords or concepts.

    Use this to find patterns that mention specific capabilities or terms.

    Args:
        query: Search term (e.g., 'parallel', 'context isolation', 'user interaction')
    """
    query_lower = query.lower()
    results = []

    for name, pattern in _patterns.items():
        # Load and search full content
        content = pattern["path"].read_text().lower()

        if query_lower in content:
            # Count occurrences for relevance
            count = content.count(query_lower)

            # Extract a snippet
            idx = content.find(query_lower)
            start = max(0, idx - 50)
            end = min(len(content), idx + len(query) + 100)
            snippet = "..." + content[start:end].replace("\n", " ") + "..."

            results.append({
                "name": name,
                "title": pattern["title"],
                "matches": count,
                "snippet": snippet
            })

    if not results:
        return f"No patterns found matching '{query}'.\n\nTry different keywords like: parallel, context, user interaction, coordination, workflow, state."

    # Sort by match count
    results.sort(key=lambda x: x["matches"], reverse=True)

    output = [f"Patterns matching '{query}':", "=" * 50, ""]

    for r in results:
        output.append(f"**{r['title']}** ({r['name']}) - {r['matches']} matches")
        output.append(f"  {r['snippet']}")
        output.append("")

    output.append(f"\nUse load_pattern(name) to get full details.")

    return "\n".join(output)


@tool
def get_pattern_comparison(pattern_names: str) -> str:
    """Get a side-by-side comparison of multiple patterns.

    Use this when narrowing down between 2-4 candidate patterns.

    Args:
        pattern_names: Comma-separated list of pattern names (e.g., 'subagents,handoffs')
    """
    names = [n.strip().lower().replace("_", "-") for n in pattern_names.split(",")]

    # Validate patterns
    invalid = [n for n in names if n not in _patterns]
    if invalid:
        available = ", ".join(_patterns.keys())
        return f"Invalid patterns: {invalid}\n\nAvailable: {available}"

    if len(names) < 2:
        return "Please provide at least 2 patterns to compare."

    if len(names) > 4:
        return "Please limit comparison to 4 patterns or fewer."

    # Build comparison table
    output = ["Pattern Comparison", "=" * 70, ""]

    # Basic info
    output.append("| Aspect | " + " | ".join(names) + " |")
    output.append("|" + "-" * 20 + "|" + (("-" * 15 + "|") * len(names)))

    # Title
    titles = [_patterns[n]["title"] for n in names]
    output.append("| Title | " + " | ".join(titles) + " |")

    # Category
    categories = [_patterns[n]["category"] for n in names]
    output.append("| Category | " + " | ".join(categories) + " |")

    # Complexity
    complexities = [_patterns[n]["complexity"] for n in names]
    output.append("| Complexity | " + " | ".join(complexities) + " |")

    output.append("")

    # Extract key characteristics from each pattern
    output.append("\n## Key Differences\n")

    for name in names:
        content = _patterns[name]["path"].read_text()
        parsed = parse_pattern_frontmatter(content)

        # Extract "When to Use" section
        when_to_use = ""
        if "## When to Use" in parsed["body"]:
            start = parsed["body"].find("## When to Use")
            end = parsed["body"].find("##", start + 10)
            when_to_use = parsed["body"][start:end if end > start else start + 500].strip()

        output.append(f"### {_patterns[name]['title']}")
        output.append(when_to_use[:400] + "..." if len(when_to_use) > 400 else when_to_use)
        output.append("")

    output.append("\nUse load_pattern(name) for complete details on any pattern.")

    return "\n".join(output)


@tool
def get_pattern_decision_tree() -> str:
    """Get a quick decision flowchart to help narrow down pattern choices.

    Use this as a starting point before diving into specific patterns.
    """
    return """Pattern Selection Decision Tree
================================

Start here and follow the questions:

1. **How many agents do you need?**
   |
   +-- Single agent -> Q2
   +-- Multiple agents -> Q3

2. **Single agent: What type of specialization?**
   |
   +-- Prompt-based skills (guidelines, patterns) -> **Skills**
   +-- Tool-based with workflow states -> **Handoffs** (single agent, multiple states)
   +-- Query routing to sources -> **Router**
   +-- Custom node sequence -> **Custom Workflows**

3. **Multiple agents: Do they need to talk directly to users?**
   |
   +-- Yes -> Q4
   +-- No (coordinator handles user) -> Q5

4. **Direct user interaction: Workflow type?**
   |
   +-- Sequential stages (state machine) -> **Handoffs**
   +-- Forward exact responses (compliance) -> **Supervisor Forward**

5. **No direct user interaction: Coordination style?**
   |
   +-- Flat (one supervisor) -> Q6
   +-- Hierarchical (teams with leads) -> **Hierarchical Teams**

6. **Flat coordination: Context concerns?**
   |
   +-- Large tool outputs (10K+ tokens) -> Q7
   +-- Normal outputs -> **Subagents**

7. **Large outputs: Processing style?**
   |
   +-- Isolated subagent work, return summaries -> **Deep Agents**
   +-- Quarantine raw data, summarize -> **Context Quarantine**

================================
Quick Summary:

| Need | Pattern |
|------|---------|
| Prompt-based specialization | Skills |
| Sequential user-facing stages | Handoffs |
| Parallel query dispatch | Router |
| Domain expert coordination | Subagents |
| Verbatim response forwarding | Supervisor Forward |
| Nested team structure | Hierarchical Teams |
| Tool-heavy isolated work | Deep Agents |
| Large data summarization | Context Quarantine |
| Complex custom logic | Custom Workflows |
"""


# Export all tools
PATTERN_TOOLS = [
    list_all_patterns,
    load_pattern,
    search_patterns,
    get_pattern_comparison,
    get_pattern_decision_tree,
]
