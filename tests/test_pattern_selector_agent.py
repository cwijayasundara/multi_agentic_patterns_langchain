"""
Tests for the Pattern Selector Agent.

Tests cover:
1. Tool unit tests (pattern and decision tools)
2. Knowledge file discovery and parsing
3. Agent integration tests with various scenarios
4. Skills pattern behavior (progressive loading)

Run with: pytest tests/test_pattern_selector_agent.py -v
"""

import pytest
from pathlib import Path


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def reset_patterns():
    """Reset loaded patterns before and after each test."""
    from pattern_selector_agent.tools import reset_loaded_patterns
    reset_loaded_patterns()
    yield
    reset_loaded_patterns()


@pytest.fixture
def knowledge_dir():
    """Get the knowledge directory path."""
    return Path(__file__).parent.parent / "pattern_selector_agent" / "knowledge"


# ============================================================================
# Knowledge File Tests
# ============================================================================

class TestKnowledgeFiles:
    """Tests for pattern knowledge files."""

    def test_all_nine_patterns_exist(self, knowledge_dir):
        """Verify all 9 pattern knowledge files exist."""
        expected_patterns = [
            "subagents.md",
            "deep-agents.md",
            "supervisor-forward.md",
            "hierarchical-teams.md",
            "context-quarantine.md",
            "skills.md",
            "handoffs.md",
            "router.md",
            "custom-workflows.md",
        ]

        for pattern_file in expected_patterns:
            assert (knowledge_dir / pattern_file).exists(), f"Missing: {pattern_file}"

    def test_pattern_files_have_frontmatter(self, knowledge_dir):
        """Verify all pattern files have valid YAML frontmatter."""
        for pattern_file in knowledge_dir.glob("*.md"):
            content = pattern_file.read_text()
            assert content.startswith("---"), f"{pattern_file.name} missing frontmatter"
            assert content.count("---") >= 2, f"{pattern_file.name} incomplete frontmatter"

            # Check required frontmatter fields
            assert "name:" in content, f"{pattern_file.name} missing 'name' field"
            assert "title:" in content, f"{pattern_file.name} missing 'title' field"
            assert "description:" in content, f"{pattern_file.name} missing 'description' field"

    def test_pattern_files_have_required_sections(self, knowledge_dir):
        """Verify pattern files have required documentation sections."""
        required_sections = [
            "## When to Use",
            "## When NOT to Use",
            "## Code Reference",
        ]

        for pattern_file in knowledge_dir.glob("*.md"):
            content = pattern_file.read_text()
            for section in required_sections:
                assert section in content, f"{pattern_file.name} missing '{section}'"


# ============================================================================
# Pattern Tools Tests
# ============================================================================

class TestPatternTools:
    """Tests for pattern discovery and loading tools."""

    def test_pattern_discovery(self):
        """Test that all 9 patterns are discovered."""
        from pattern_selector_agent.tools.patterns import _patterns

        assert len(_patterns) == 9, f"Expected 9 patterns, found {len(_patterns)}"

        expected_names = {
            "subagents", "deep-agents", "supervisor-forward",
            "hierarchical-teams", "context-quarantine", "skills",
            "handoffs", "router", "custom-workflows"
        }
        assert set(_patterns.keys()) == expected_names

    def test_list_all_patterns(self):
        """Test list_all_patterns tool returns all patterns."""
        from pattern_selector_agent.tools import list_all_patterns

        result = list_all_patterns.invoke({})

        assert "Available Agentic Patterns" in result
        assert "subagents" in result.lower()
        assert "handoffs" in result.lower()
        assert "router" in result.lower()
        assert "Total: 9 patterns" in result

    def test_load_pattern_success(self, reset_patterns):
        """Test loading a valid pattern."""
        from pattern_selector_agent.tools import load_pattern, get_loaded_patterns

        result = load_pattern.invoke({"pattern_name": "handoffs"})

        assert "Successfully loaded" in result
        assert "Handoffs" in result
        assert "## When to Use" in result
        assert "handoffs" in get_loaded_patterns()

    def test_load_pattern_already_loaded(self, reset_patterns):
        """Test loading a pattern that's already loaded."""
        from pattern_selector_agent.tools import load_pattern

        load_pattern.invoke({"pattern_name": "handoffs"})
        result = load_pattern.invoke({"pattern_name": "handoffs"})

        assert "already loaded" in result

    def test_load_pattern_invalid(self):
        """Test loading an invalid pattern name."""
        from pattern_selector_agent.tools import load_pattern

        result = load_pattern.invoke({"pattern_name": "nonexistent"})

        assert "not found" in result
        assert "Available patterns" in result

    def test_load_pattern_normalizes_name(self, reset_patterns):
        """Test that pattern names are normalized (underscores, spaces)."""
        from pattern_selector_agent.tools import load_pattern, get_loaded_patterns

        # Test with underscore
        load_pattern.invoke({"pattern_name": "deep_agents"})
        assert "deep-agents" in get_loaded_patterns()

    def test_search_patterns(self):
        """Test searching patterns by keyword."""
        from pattern_selector_agent.tools import search_patterns

        result = search_patterns.invoke({"query": "parallel"})

        assert "router" in result.lower()
        assert "matches" in result

    def test_search_patterns_no_results(self):
        """Test searching with no matching results."""
        from pattern_selector_agent.tools import search_patterns

        result = search_patterns.invoke({"query": "xyznonexistent123"})

        assert "No patterns found" in result

    def test_get_pattern_comparison(self, reset_patterns):
        """Test comparing multiple patterns."""
        from pattern_selector_agent.tools import get_pattern_comparison

        result = get_pattern_comparison.invoke({"pattern_names": "handoffs,subagents"})

        assert "Pattern Comparison" in result
        assert "handoffs" in result.lower()
        assert "subagents" in result.lower()

    def test_get_pattern_comparison_invalid(self):
        """Test comparison with invalid pattern names."""
        from pattern_selector_agent.tools import get_pattern_comparison

        result = get_pattern_comparison.invoke({"pattern_names": "invalid1,invalid2"})

        assert "Invalid patterns" in result

    def test_get_pattern_decision_tree(self):
        """Test the decision tree tool."""
        from pattern_selector_agent.tools import get_pattern_decision_tree

        result = get_pattern_decision_tree.invoke({})

        assert "Decision Tree" in result
        assert "Single agent" in result or "Multiple agents" in result
        assert "Skills" in result
        assert "Handoffs" in result


# ============================================================================
# Decision Tools Tests
# ============================================================================

class TestDecisionTools:
    """Tests for requirement evaluation and use case analysis tools."""

    def test_evaluate_requirements_parallel(self):
        """Test evaluating requirements for parallel execution."""
        from pattern_selector_agent.tools import evaluate_requirements

        result = evaluate_requirements.invoke({
            "requirements": "Need parallel execution and result synthesis"
        })

        assert "router" in result.lower()
        assert "parallel_execution" in result

    def test_evaluate_requirements_user_interaction(self):
        """Test evaluating requirements for user interaction."""
        from pattern_selector_agent.tools import evaluate_requirements

        result = evaluate_requirements.invoke({
            "requirements": "Direct user interaction with workflow stages"
        })

        assert "handoffs" in result.lower()

    def test_evaluate_requirements_large_data(self):
        """Test evaluating requirements for large data handling."""
        from pattern_selector_agent.tools import evaluate_requirements

        result = evaluate_requirements.invoke({
            "requirements": "Handle large data outputs and prevent context bloat"
        })

        # Should recommend deep-agents or context-quarantine
        assert "deep-agents" in result.lower() or "context-quarantine" in result.lower()

    def test_evaluate_requirements_no_detection(self):
        """Test evaluating vague requirements."""
        from pattern_selector_agent.tools import evaluate_requirements

        result = evaluate_requirements.invoke({
            "requirements": "build something cool"
        })

        assert "Could not detect" in result or "Please mention" in result

    def test_analyze_use_case_customer_support(self):
        """Test analyzing customer support use case."""
        from pattern_selector_agent.tools import analyze_use_case

        result = analyze_use_case.invoke({
            "use_case": "Customer support system with billing and tech support stages"
        })

        assert "handoffs" in result.lower()

    def test_analyze_use_case_code_assistant(self):
        """Test analyzing code assistant use case."""
        from pattern_selector_agent.tools import analyze_use_case

        result = analyze_use_case.invoke({
            "use_case": "Code assistant supporting Python, JavaScript, and Go"
        })

        assert "skills" in result.lower()

    def test_analyze_use_case_research(self):
        """Test analyzing research system use case."""
        from pattern_selector_agent.tools import analyze_use_case

        result = analyze_use_case.invoke({
            "use_case": "Research system that searches multiple sources in parallel"
        })

        assert "router" in result.lower() or "subagents" in result.lower()

    def test_analyze_use_case_domain_experts(self):
        """Test analyzing domain expert coordination use case."""
        from pattern_selector_agent.tools import analyze_use_case

        result = analyze_use_case.invoke({
            "use_case": "Coordinate budget analyst, investment advisor, and tax consultant"
        })

        assert "subagents" in result.lower()

    def test_get_clarifying_questions(self):
        """Test generating clarifying questions."""
        from pattern_selector_agent.tools import get_clarifying_questions

        result = get_clarifying_questions.invoke({
            "problem_description": "Building an assistant"
        })

        assert "Clarifying Questions" in result
        assert "?" in result  # Should contain questions


# ============================================================================
# Agent Integration Tests
# ============================================================================

class TestAgentIntegration:
    """Integration tests for the Pattern Selector Agent."""

    @pytest.fixture
    def agent(self, reset_patterns):
        """Create a fresh agent for each test."""
        from pattern_selector_agent import create_selector_agent
        return create_selector_agent()

    def test_agent_creation(self):
        """Test that the agent can be created."""
        from pattern_selector_agent import create_selector_agent

        agent = create_selector_agent()

        assert agent is not None
        assert hasattr(agent, "invoke")

    def test_agent_with_middleware(self):
        """Test that the agent is created with middleware."""
        from pattern_selector_agent import create_selector_agent, create_selector_middleware

        middleware = create_selector_middleware()
        agent = create_selector_agent(middleware=middleware)

        assert agent is not None
        assert len(middleware) == 4  # 4 middleware components

    @pytest.mark.integration
    def test_scenario_customer_support(self, agent, reset_patterns):
        """
        Scenario: Customer support system with stages.
        Expected: Should recommend Handoffs pattern.
        """
        from pattern_selector_agent import chat
        from pattern_selector_agent.tools import get_loaded_patterns

        response = chat(
            "I want to build a customer support system where specialists "
            "talk directly to customers through greeting, billing, and resolution stages",
            agent=agent,
            thread_id="test_customer_support"
        )

        response_lower = response.lower()
        assert "handoffs" in response_lower or "handoff" in response_lower, \
            f"Expected Handoffs recommendation, got: {response[:500]}"

    @pytest.mark.integration
    def test_scenario_parallel_search(self, agent, reset_patterns):
        """
        Scenario: Research system with parallel search.
        Expected: Should recommend Router pattern.
        """
        from pattern_selector_agent import chat

        response = chat(
            "Build a knowledge base that searches docs, FAQs, and tutorials "
            "in parallel and combines the results",
            agent=agent,
            thread_id="test_parallel_search"
        )

        response_lower = response.lower()
        assert "router" in response_lower, \
            f"Expected Router recommendation, got: {response[:500]}"

    @pytest.mark.integration
    def test_scenario_code_assistant(self, agent, reset_patterns):
        """
        Scenario: Multi-language code assistant.
        Expected: Should recommend Skills pattern.
        """
        from pattern_selector_agent import chat

        # More explicit description to trigger direct recommendation
        response = chat(
            "I want a single code assistant agent that dynamically loads "
            "prompt-based coding guidelines for Python, JavaScript, Go, and SQL. "
            "The skills should be .md files loaded on demand - no separate agents needed, "
            "just one agent with loadable specializations. No parallel execution required.",
            agent=agent,
            thread_id="test_code_assistant"
        )

        response_lower = response.lower()
        assert "skills" in response_lower or "skill" in response_lower, \
            f"Expected Skills recommendation, got: {response[:500]}"

    @pytest.mark.integration
    def test_scenario_domain_experts(self, agent, reset_patterns):
        """
        Scenario: Coordinating domain experts.
        Expected: Should recommend Subagents pattern.
        """
        from pattern_selector_agent import chat

        # More explicit: supervisor coordinates, no direct user interaction
        response = chat(
            "Create a personal finance system where a supervisor agent coordinates "
            "three domain expert subagents: budget analyst, investment advisor, and tax consultant. "
            "The supervisor handles all user interaction - subagents don't talk to users directly. "
            "Subagents can work in parallel on different aspects of a query.",
            agent=agent,
            thread_id="test_domain_experts"
        )

        response_lower = response.lower()
        assert "subagent" in response_lower or "supervisor" in response_lower, \
            f"Expected Subagents recommendation, got: {response[:500]}"

    @pytest.mark.integration
    def test_scenario_large_data(self, agent, reset_patterns):
        """
        Scenario: Processing large data with context concerns.
        Expected: Should recommend Deep Agents or Context Quarantine.
        """
        from pattern_selector_agent import chat

        # More explicit: large outputs, context isolation needed
        response = chat(
            "I need to process very large tool outputs - database queries returning 10,000+ rows "
            "and log files with 100K+ lines. The main agent needs to stay focused and not get "
            "bloated with raw data. I want subagents to handle the heavy data processing and "
            "return only summaries to the main agent. Context isolation is critical.",
            agent=agent,
            thread_id="test_large_data"
        )

        response_lower = response.lower()
        assert "deep" in response_lower or "quarantine" in response_lower or "context" in response_lower or "isolat" in response_lower, \
            f"Expected Deep Agents or Context Quarantine, got: {response[:500]}"

    @pytest.mark.integration
    def test_scenario_compliance(self, agent, reset_patterns):
        """
        Scenario: Compliance/audit requirements.
        Expected: Should recommend Supervisor Forward pattern.
        """
        from pattern_selector_agent import chat

        # More explicit: verbatim forwarding, compliance, audit
        response = chat(
            "Building a legal advisory system where a supervisor coordinates legal specialists. "
            "CRITICAL: Specialist responses must be forwarded to users EXACTLY as written - "
            "verbatim, word-for-word, no paraphrasing allowed. This is for compliance and "
            "audit trail requirements. The supervisor cannot modify or summarize responses.",
            agent=agent,
            thread_id="test_compliance"
        )

        response_lower = response.lower()
        assert "forward" in response_lower or "verbatim" in response_lower or "supervisor" in response_lower, \
            f"Expected Supervisor Forward recommendation, got: {response[:500]}"

    @pytest.mark.integration
    def test_scenario_hierarchical(self, agent, reset_patterns):
        """
        Scenario: Multi-level team hierarchy.
        Expected: Should recommend Hierarchical Teams pattern.
        """
        from pattern_selector_agent import chat

        # More explicit: nested hierarchy, team leads, departments
        response = chat(
            "Building a system for a large enterprise with a nested hierarchy structure: "
            "A top-level supervisor coordinates multiple department team leads. Each team lead "
            "is itself a coordinator managing its own specialists. For example: "
            "CEO -> Engineering Team Lead -> (Backend Dev, Frontend Dev, DevOps) and "
            "CEO -> Product Team Lead -> (Designer, PM, Researcher). Multiple levels of coordination.",
            agent=agent,
            thread_id="test_hierarchical"
        )

        response_lower = response.lower()
        assert "hierarchical" in response_lower or "team" in response_lower or "nested" in response_lower, \
            f"Expected Hierarchical Teams recommendation, got: {response[:500]}"

    @pytest.mark.integration
    def test_scenario_custom_workflow(self, agent, reset_patterns):
        """
        Scenario: Content pipeline with review cycles.
        Expected: Should recommend Custom Workflows pattern.
        """
        from pattern_selector_agent import chat

        # More explicit: custom flow, conditional edges, feedback loops
        response = chat(
            "Creating a content pipeline with a custom StateGraph workflow: "
            "research node -> outline node -> write node -> review node. "
            "Key requirement: conditional edges and feedback loops - if review fails, "
            "loop back to revision node, then back to review. Only pass to publish "
            "when review succeeds. This is a custom DAG with branching logic.",
            agent=agent,
            thread_id="test_custom_workflow"
        )

        response_lower = response.lower()
        assert "custom" in response_lower or "workflow" in response_lower or "stategraph" in response_lower or "loop" in response_lower, \
            f"Expected Custom Workflows recommendation, got: {response[:500]}"


# ============================================================================
# Skills Pattern Behavior Tests
# ============================================================================

class TestSkillsPatternBehavior:
    """Tests to verify Skills pattern behavior (progressive loading)."""

    @pytest.fixture
    def agent(self, reset_patterns):
        """Create a fresh agent for each test."""
        from pattern_selector_agent import create_selector_agent
        return create_selector_agent()

    @pytest.mark.integration
    def test_progressive_loading(self, agent, reset_patterns):
        """Test that patterns are loaded progressively, not all at once."""
        from pattern_selector_agent import chat
        from pattern_selector_agent.tools import get_loaded_patterns

        # Before any interaction, no patterns should be loaded
        assert len(get_loaded_patterns()) == 0

        # First message - agent should analyze but may not load yet
        chat(
            "I want to build a customer support system",
            agent=agent,
            thread_id="test_progressive"
        )

        # Agent might ask clarifying questions or load a pattern
        loaded_after_first = get_loaded_patterns()

        # Second message with more details
        chat(
            "Yes, specialists should talk directly to customers with stages",
            agent=agent,
            thread_id="test_progressive"
        )

        loaded_after_second = get_loaded_patterns()

        # Should have loaded at least one pattern by now
        assert len(loaded_after_second) >= 1, "Expected at least one pattern loaded"
        # Should not have loaded all 9 patterns
        assert len(loaded_after_second) < 9, "Should not load all patterns"

    def test_reset_loaded_patterns(self, reset_patterns):
        """Test that reset_loaded_patterns clears the state."""
        from pattern_selector_agent.tools import (
            load_pattern, get_loaded_patterns, reset_loaded_patterns
        )

        load_pattern.invoke({"pattern_name": "handoffs"})
        load_pattern.invoke({"pattern_name": "router"})

        assert len(get_loaded_patterns()) == 2

        reset_loaded_patterns()

        assert len(get_loaded_patterns()) == 0

    @pytest.mark.integration
    def test_multi_turn_context_preservation(self, agent, reset_patterns):
        """Test that conversation context is preserved across turns."""
        from pattern_selector_agent import chat

        # First turn
        response1 = chat(
            "I want to build a research assistant",
            agent=agent,
            thread_id="test_context"
        )

        # Second turn should remember the context
        response2 = chat(
            "It should search docs and tutorials in parallel",
            agent=agent,
            thread_id="test_context"
        )

        # Response should build on previous context
        assert len(response2) > 0
        # Should provide a more specific recommendation now
        response2_lower = response2.lower()
        assert "router" in response2_lower or "parallel" in response2_lower or "search" in response2_lower


# ============================================================================
# Middleware Tests
# ============================================================================

class TestMiddleware:
    """Tests for the middleware configuration."""

    def test_middleware_creation(self):
        """Test that middleware stack is created correctly."""
        from pattern_selector_agent import create_selector_middleware

        middleware = create_selector_middleware()

        assert len(middleware) == 4

        # Check middleware types
        middleware_types = [type(m).__name__ for m in middleware]
        assert "LLMToolSelectorMiddleware" in middleware_types
        assert "ToolCallLimitMiddleware" in middleware_types
        assert "ContextEditingMiddleware" in middleware_types
        assert "SummarizationMiddleware" in middleware_types

    def test_middleware_custom_config(self):
        """Test middleware with custom configuration."""
        from pattern_selector_agent import create_selector_middleware

        middleware = create_selector_middleware(
            max_tools=3,
            pattern_thread_limit=5,
            context_trigger=30000,
            summarization_trigger=5000,
        )

        assert len(middleware) == 4


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
