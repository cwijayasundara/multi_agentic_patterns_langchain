"""
Decision and evaluation tools for the Pattern Selector Agent.

Tools for analyzing requirements and scoring pattern fit.
"""

from langchain_core.tools import tool


# Pattern characteristics for scoring
PATTERN_CAPABILITIES = {
    "subagents": {
        "parallel_execution": 5,
        "context_isolation": 4,
        "distributed_development": 5,
        "direct_user_interaction": 1,
        "coordination_complexity": 3,
        "large_data_handling": 2,
        "workflow_stages": 2,
    },
    "deep-agents": {
        "parallel_execution": 3,
        "context_isolation": 5,
        "distributed_development": 4,
        "direct_user_interaction": 2,
        "coordination_complexity": 3,
        "large_data_handling": 5,
        "workflow_stages": 2,
    },
    "supervisor-forward": {
        "parallel_execution": 3,
        "context_isolation": 3,
        "distributed_development": 4,
        "direct_user_interaction": 3,
        "coordination_complexity": 3,
        "large_data_handling": 2,
        "workflow_stages": 2,
        "audit_compliance": 5,
        "response_accuracy": 5,
    },
    "hierarchical-teams": {
        "parallel_execution": 4,
        "context_isolation": 4,
        "distributed_development": 5,
        "direct_user_interaction": 2,
        "coordination_complexity": 5,
        "large_data_handling": 3,
        "workflow_stages": 3,
        "organizational_modeling": 5,
    },
    "context-quarantine": {
        "parallel_execution": 3,
        "context_isolation": 5,
        "distributed_development": 3,
        "direct_user_interaction": 2,
        "coordination_complexity": 3,
        "large_data_handling": 5,
        "workflow_stages": 2,
    },
    "skills": {
        "parallel_execution": 1,
        "context_isolation": 1,
        "distributed_development": 5,
        "direct_user_interaction": 4,
        "coordination_complexity": 1,
        "large_data_handling": 2,
        "workflow_stages": 1,
        "lightweight_composition": 5,
        "runtime_adaptability": 5,
    },
    "handoffs": {
        "parallel_execution": 1,
        "context_isolation": 2,
        "distributed_development": 4,
        "direct_user_interaction": 5,
        "coordination_complexity": 2,
        "large_data_handling": 2,
        "workflow_stages": 5,
        "state_persistence": 5,
    },
    "router": {
        "parallel_execution": 5,
        "context_isolation": 3,
        "distributed_development": 4,
        "direct_user_interaction": 2,
        "coordination_complexity": 2,
        "large_data_handling": 3,
        "workflow_stages": 1,
        "query_classification": 5,
        "result_synthesis": 5,
    },
    "custom-workflows": {
        "parallel_execution": 4,
        "context_isolation": 3,
        "distributed_development": 3,
        "direct_user_interaction": 3,
        "coordination_complexity": 4,
        "large_data_handling": 3,
        "workflow_stages": 5,
        "flexibility": 5,
        "feedback_loops": 5,
    },
}

# Mapping from requirement keywords to capabilities
REQUIREMENT_MAPPINGS = {
    # Parallelization keywords
    "parallel": "parallel_execution",
    "concurrent": "parallel_execution",
    "simultaneously": "parallel_execution",
    "at the same time": "parallel_execution",

    # Context keywords
    "context isolation": "context_isolation",
    "isolated context": "context_isolation",
    "separate context": "context_isolation",
    "context bloat": "large_data_handling",
    "large data": "large_data_handling",
    "big data": "large_data_handling",
    "large outputs": "large_data_handling",
    "huge results": "large_data_handling",

    # User interaction keywords
    "talk to user": "direct_user_interaction",
    "user interaction": "direct_user_interaction",
    "talk directly": "direct_user_interaction",
    "customer facing": "direct_user_interaction",
    "user-facing": "direct_user_interaction",

    # Workflow keywords
    "stages": "workflow_stages",
    "steps": "workflow_stages",
    "phases": "workflow_stages",
    "sequential": "workflow_stages",
    "state machine": "workflow_stages",
    "workflow": "workflow_stages",

    # Team/organization keywords
    "teams": "organizational_modeling",
    "departments": "organizational_modeling",
    "hierarchy": "organizational_modeling",
    "organization": "organizational_modeling",

    # Development keywords
    "independent development": "distributed_development",
    "separate teams": "distributed_development",
    "modular": "distributed_development",

    # Compliance keywords
    "compliance": "audit_compliance",
    "audit": "audit_compliance",
    "exact wording": "response_accuracy",
    "verbatim": "response_accuracy",
    "liability": "audit_compliance",

    # Flexibility keywords
    "custom": "flexibility",
    "flexible": "flexibility",
    "feedback loop": "feedback_loops",
    "revision": "feedback_loops",
    "review cycle": "feedback_loops",

    # Lightweight keywords
    "lightweight": "lightweight_composition",
    "simple": "lightweight_composition",
    "single agent": "lightweight_composition",

    # Routing keywords
    "classify": "query_classification",
    "route": "query_classification",
    "dispatch": "query_classification",
    "multiple sources": "result_synthesis",
    "combine results": "result_synthesis",
    "synthesize": "result_synthesis",
}


@tool
def evaluate_requirements(requirements: str) -> str:
    """Evaluate requirements against all patterns and return fit scores.

    Analyzes the provided requirements and scores each pattern's fit
    based on its capabilities.

    Args:
        requirements: Natural language description of requirements
            (e.g., "Need parallel execution, direct user interaction, workflow stages")
    """
    requirements_lower = requirements.lower()

    # Detect relevant capabilities from requirements
    detected_capabilities = set()
    for keyword, capability in REQUIREMENT_MAPPINGS.items():
        if keyword in requirements_lower:
            detected_capabilities.add(capability)

    if not detected_capabilities:
        return """Could not detect specific requirements from your description.

Please mention aspects like:
- Parallel execution / concurrent processing
- Direct user interaction
- Workflow stages / sequential steps
- Context isolation / large data handling
- Compliance / audit requirements
- Team structure / hierarchy
- Feedback loops / review cycles

Example: "Need parallel execution with direct user interaction and workflow stages"
"""

    # Score each pattern
    scores = {}
    for pattern_name, capabilities in PATTERN_CAPABILITIES.items():
        score = 0
        matched = []
        for cap in detected_capabilities:
            if cap in capabilities:
                score += capabilities[cap]
                matched.append(f"{cap}: {capabilities[cap]}/5")
        scores[pattern_name] = {
            "score": score,
            "max_possible": len(detected_capabilities) * 5,
            "matched": matched
        }

    # Sort by score
    sorted_patterns = sorted(scores.items(), key=lambda x: x[1]["score"], reverse=True)

    output = [
        "Requirement Analysis",
        "=" * 60,
        "",
        f"Detected capabilities needed: {', '.join(detected_capabilities)}",
        "",
        "Pattern Fit Scores:",
        "-" * 40,
        ""
    ]

    for pattern_name, data in sorted_patterns[:5]:  # Top 5
        percentage = (data["score"] / data["max_possible"] * 100) if data["max_possible"] > 0 else 0
        output.append(f"**{pattern_name}**: {data['score']}/{data['max_possible']} ({percentage:.0f}%)")
        if data["matched"]:
            for m in data["matched"]:
                output.append(f"  - {m}")
        output.append("")

    # Recommendations
    top = sorted_patterns[0]
    output.append("-" * 40)
    output.append(f"\n**Top Recommendation: {top[0]}**")
    if len(sorted_patterns) > 1 and sorted_patterns[1][1]["score"] > 0:
        output.append(f"**Alternative: {sorted_patterns[1][0]}**")

    output.append("\nUse load_pattern(name) to get full details and trade-offs.")

    return "\n".join(output)


@tool
def analyze_use_case(use_case: str) -> str:
    """Analyze a use case description and suggest candidate patterns.

    Takes a high-level use case description and identifies key
    characteristics that map to patterns.

    Args:
        use_case: Description of what you're trying to build
            (e.g., "A customer support system with billing and tech support specialists")
    """
    use_case_lower = use_case.lower()

    # Pattern indicators
    indicators = {
        "subagents": [
            "coordinate", "coordinator", "supervisor", "domain expert",
            "specialist", "different domains", "finance", "budget",
            "investment", "tax", "multi-service"
        ],
        "deep-agents": [
            "research", "search many", "large outputs", "summarize",
            "context management", "data intensive", "many tool calls",
            "long conversation"
        ],
        "supervisor-forward": [
            "legal", "medical", "compliance", "exact response",
            "verbatim", "liability", "audit", "attribution",
            "regulated", "financial advice"
        ],
        "hierarchical-teams": [
            "team", "department", "hierarchy", "organization",
            "team lead", "nested", "large scale", "enterprise"
        ],
        "context-quarantine": [
            "large data", "database", "big results", "summarize raw",
            "token limit", "context limit", "huge output",
            "10000", "100k"
        ],
        "skills": [
            "coding", "programming language", "python", "javascript",
            "code assistant", "writing assistant", "multiple skills",
            "prompt-based", "guidelines", "best practices"
        ],
        "handoffs": [
            "customer support", "stages", "steps", "greeting",
            "collect", "resolve", "state machine", "workflow",
            "sequential", "talk to user", "conversation flow"
        ],
        "router": [
            "search", "query", "classify", "dispatch", "parallel",
            "multiple sources", "knowledge base", "faq", "docs",
            "tutorials", "combine results"
        ],
        "custom-workflows": [
            "content pipeline", "review", "revision", "feedback loop",
            "approval", "quality gate", "custom flow", "conditional",
            "branch", "loop back"
        ],
    }

    matches = {}
    for pattern, keywords in indicators.items():
        count = sum(1 for kw in keywords if kw in use_case_lower)
        if count > 0:
            matches[pattern] = count

    if not matches:
        return """Could not identify a clear pattern match from your use case.

Please provide more details about:
- What problem are you solving?
- How should agents interact with users?
- Do you need parallel or sequential processing?
- Are there workflow stages?
- What kind of data are you processing?

Example: "Building a customer support system where specialists talk directly to customers through greeting, collection, and resolution stages"
"""

    # Sort by match count
    sorted_matches = sorted(matches.items(), key=lambda x: x[1], reverse=True)

    output = [
        "Use Case Analysis",
        "=" * 60,
        "",
        f"Input: \"{use_case[:100]}{'...' if len(use_case) > 100 else ''}\"",
        "",
        "Pattern Matches:",
        "-" * 40,
        ""
    ]

    for pattern, count in sorted_matches:
        matched_keywords = [kw for kw in indicators[pattern] if kw in use_case_lower]
        output.append(f"**{pattern}** ({count} keyword matches)")
        output.append(f"  Matched: {', '.join(matched_keywords[:5])}")
        output.append("")

    top_pattern = sorted_matches[0][0]
    output.append("-" * 40)
    output.append(f"\n**Suggested starting point: {top_pattern}**")
    output.append("\nNext steps:")
    output.append(f"1. load_pattern('{top_pattern}') - Review full details")
    output.append("2. Verify the 'When to Use' criteria match your needs")
    output.append("3. Check 'When NOT to Use' for potential mismatches")

    if len(sorted_matches) > 1:
        alt = sorted_matches[1][0]
        output.append(f"\nAlso consider: {alt}")

    return "\n".join(output)


@tool
def get_clarifying_questions(problem_description: str) -> str:
    """Generate clarifying questions based on a problem description.

    Identifies ambiguities and generates targeted questions to
    narrow down the right pattern.

    Args:
        problem_description: Initial description of what the user wants to build
    """
    problem_lower = problem_description.lower()

    questions = []

    # Check for missing information
    if "parallel" not in problem_lower and "sequential" not in problem_lower:
        questions.append({
            "aspect": "Execution Model",
            "question": "Do you need tasks to run in parallel (simultaneously), or sequentially (one after another)?",
            "why": "Parallel -> Router, Subagents | Sequential -> Handoffs, Custom Workflows"
        })

    if "user" not in problem_lower and "customer" not in problem_lower:
        questions.append({
            "aspect": "User Interaction",
            "question": "Do specialists need to talk directly to users, or should a coordinator handle all user interaction?",
            "why": "Direct interaction -> Handoffs | Coordinator handles -> Subagents"
        })

    if not any(kw in problem_lower for kw in ["large", "big", "huge", "context", "token"]):
        questions.append({
            "aspect": "Data Volume",
            "question": "Will your tools produce large outputs (thousands of lines, big JSON responses)?",
            "why": "Large outputs -> Deep Agents or Context Quarantine"
        })

    if not any(kw in problem_lower for kw in ["stage", "step", "phase", "workflow", "state"]):
        questions.append({
            "aspect": "Workflow Structure",
            "question": "Does your process have clear stages/phases (e.g., intake -> process -> resolve)?",
            "why": "Clear stages -> Handoffs | Ad-hoc coordination -> Subagents"
        })

    if not any(kw in problem_lower for kw in ["single", "one", "multiple", "many", "several"]):
        questions.append({
            "aspect": "Agent Count",
            "question": "Do you envision a single agent with multiple capabilities, or multiple specialized agents?",
            "why": "Single agent -> Skills | Multiple agents -> Subagents, Handoffs, etc."
        })

    if not any(kw in problem_lower for kw in ["compliance", "audit", "legal", "exact", "verbatim"]):
        questions.append({
            "aspect": "Response Handling",
            "question": "Do responses need to be forwarded exactly as specialists produce them (for compliance/audit)?",
            "why": "Exact forwarding needed -> Supervisor Forward"
        })

    if not questions:
        return """Your problem description is quite detailed. Here are some final clarifying questions:

1. **Scale**: How many agents/specialists do you anticipate?
2. **Complexity**: Do you need nested teams (team leads coordinating specialists)?
3. **Flexibility**: Will you need to add new capabilities without code changes?

Based on your description, consider using:
- load_pattern('pattern_name') to review detailed documentation
- evaluate_requirements('your key requirements') to score pattern fit
"""

    output = [
        "Clarifying Questions",
        "=" * 60,
        "",
        "To recommend the best pattern, please answer these questions:",
        ""
    ]

    for i, q in enumerate(questions[:4], 1):  # Max 4 questions
        output.append(f"**{i}. {q['aspect']}**")
        output.append(f"   {q['question']}")
        output.append(f"   _Why this matters: {q['why']}_")
        output.append("")

    return "\n".join(output)


# Export all tools
DECISION_TOOLS = [
    evaluate_requirements,
    analyze_use_case,
    get_clarifying_questions,
]
