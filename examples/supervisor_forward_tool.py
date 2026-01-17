"""
Supervisor with Forward Tool Pattern: Legal Document Assistant
==============================================================
A supervisor that forwards subagent responses DIRECTLY to users without
re-generating or paraphrasing, preserving exact wording for accuracy.

Key Concepts:
- Supervisor coordinates specialized subagents (contract, compliance, IP)
- Subagent responses are forwarded verbatim using forward_tool
- Prevents paraphrasing errors in domains where exact wording matters
- Maintains accountability by preserving original expert responses

This pattern is best when:
- Exact wording matters (legal, medical, financial advice)
- You need audit trails of who said what
- Paraphrasing could introduce errors or liability
- Subagent expertise should be presented without modification

Reference:
- https://docs.langchain.com/oss/python/langchain/multi-agent/supervisor-forward-tool
"""

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain_core.tools import tool, StructuredTool
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from typing import TypedDict, Annotated, Literal
import operator

# Load environment variables
load_dotenv()


# ============================================
# State Definition
# ============================================

class SupervisorState(TypedDict):
    """State for the supervisor workflow."""
    messages: Annotated[list, operator.add]
    next_agent: str | None
    forwarded_response: str | None


# ============================================
# Subagent Tools (Domain-Specific)
# ============================================

@tool
def analyze_contract_clause(clause_text: str, clause_type: str) -> str:
    """Analyze a specific contract clause for legal implications.

    Args:
        clause_text: The text of the clause to analyze
        clause_type: Type of clause (indemnification, limitation_of_liability,
                     termination, confidentiality, force_majeure)
    """
    # Mock analysis - in production, this would use legal databases/AI
    analyses = {
        "indemnification": f"""**Legal Analysis: Indemnification Clause**

Clause under review: "{clause_text[:100]}..."

**Key Findings:**
1. **Scope**: This indemnification clause is MUTUAL, requiring both parties to
   indemnify each other for breaches.
2. **Trigger Events**: Indemnification is triggered by: (a) breach of representations,
   (b) negligence, (c) willful misconduct.
3. **Limitations**: The clause does NOT cap indemnification amounts, which represents
   significant exposure.

**Risk Assessment**: MODERATE-HIGH
- Uncapped liability exposure
- Broad trigger events
- Recommend negotiating a cap tied to contract value

**Recommended Language**: "Indemnification obligations shall not exceed the total
fees paid under this Agreement in the twelve (12) months preceding the claim."

*This analysis is provided for informational purposes and does not constitute legal advice.*""",

        "limitation_of_liability": f"""**Legal Analysis: Limitation of Liability Clause**

Clause under review: "{clause_text[:100]}..."

**Key Findings:**
1. **Direct Damages**: Limited to fees paid in the prior 12 months - STANDARD
2. **Consequential Damages**: EXCLUDED for both parties - FAVORABLE
3. **Carve-outs**: Indemnification and confidentiality breaches are carved out -
   WATCH ITEM

**Risk Assessment**: LOW-MODERATE
- Standard market terms for SaaS agreements
- Carve-outs create potential unlimited exposure for specific scenarios

**Recommendation**: ACCEPTABLE with minor modifications
- Consider adding a super-cap for carve-out scenarios

*This analysis is provided for informational purposes and does not constitute legal advice.*""",
    }
    return analyses.get(clause_type, f"Analysis for {clause_type}: Standard clause review completed. No significant concerns identified.")


@tool
def check_regulatory_compliance(jurisdiction: str, industry: str, activity: str) -> str:
    """Check regulatory compliance requirements for a specific activity.

    Args:
        jurisdiction: Legal jurisdiction (us_federal, us_california, eu_gdpr, uk)
        industry: Industry sector (fintech, healthcare, saas, ecommerce)
        activity: Specific activity to check (data_processing, cross_border_transfer,
                  marketing_communications, employee_monitoring)
    """
    # Mock compliance check
    return f"""**Regulatory Compliance Assessment**

**Jurisdiction**: {jurisdiction.upper().replace('_', ' ')}
**Industry**: {industry.title()}
**Activity**: {activity.replace('_', ' ').title()}

**Applicable Regulations:**
1. {'CCPA (California Consumer Privacy Act)' if 'california' in jurisdiction else 'GDPR Article 6' if 'eu' in jurisdiction else 'FTC Act Section 5'}
2. {'CPRA Amendments' if 'california' in jurisdiction else 'GDPR Article 13-14' if 'eu' in jurisdiction else 'State Privacy Laws'}

**Compliance Requirements:**
- [ ] Privacy notice must be provided BEFORE data collection
- [ ] Explicit consent required for sensitive data categories
- [ ] Data processing agreement required with all processors
- [ ] Records of processing activities must be maintained
- [ ] Data subject access request process must be implemented

**Penalties for Non-Compliance:**
- Civil penalties up to {'$7,500 per intentional violation' if 'california' in jurisdiction else '4% of annual global turnover or €20M' if 'eu' in jurisdiction else '$50,000 per violation'}

**Compliance Status**: REQUIRES REVIEW
**Recommended Action**: Engage privacy counsel for detailed assessment

*This assessment is for informational purposes only and does not constitute legal advice.*"""


@tool
def research_ip_rights(ip_type: str, description: str) -> str:
    """Research intellectual property rights and protections.

    Args:
        ip_type: Type of IP (patent, trademark, copyright, trade_secret)
        description: Description of the IP asset or question
    """
    return f"""**Intellectual Property Analysis**

**IP Type**: {ip_type.title().replace('_', ' ')}
**Subject**: {description[:100]}...

**Protection Analysis:**

{'**Patent Protection:**' if ip_type == 'patent' else '**' + ip_type.title() + ' Protection:**'}

1. **Eligibility Assessment**:
   - {'Novel: Requires demonstration that invention is new' if ip_type == 'patent' else 'Distinctiveness: Mark must be distinctive and not merely descriptive' if ip_type == 'trademark' else 'Originality: Work must be original expression, not ideas'}
   - {'Non-obvious: Cannot be obvious to person skilled in the art' if ip_type == 'patent' else 'Non-confusing: Must not cause likelihood of confusion with existing marks' if ip_type == 'trademark' else 'Fixation: Must be fixed in tangible medium'}

2. **Recommended Steps**:
   - {'File provisional patent application within 12 months of first disclosure' if ip_type == 'patent' else 'Conduct comprehensive trademark search before filing' if ip_type == 'trademark' else 'Register copyright with US Copyright Office for enhanced protection'}
   - {'Consider PCT filing for international protection' if ip_type == 'patent' else 'File in all relevant classes of goods/services' if ip_type == 'trademark' else 'Include copyright notice on all copies'}

3. **Timeline & Costs**:
   - {'Patent prosecution: 2-4 years, $15,000-$50,000+' if ip_type == 'patent' else 'Trademark registration: 8-12 months, $2,000-$5,000' if ip_type == 'trademark' else 'Copyright registration: 3-6 months, $45-$125'}

**Risk Assessment**: {'Patentability appears PROMISING based on description' if ip_type == 'patent' else 'Registration appears FEASIBLE pending full search'}

*This analysis is for informational purposes only. Consult with IP counsel for specific advice.*"""


# ============================================
# Forward Tool - Key Pattern Implementation
# ============================================

def create_forward_tool(agent_name: str):
    """Create a forward tool that passes responses directly without paraphrasing."""

    def forward_to_user(response: str) -> str:
        """Forward the specialist's response directly to the user."""
        return f"[FORWARDED FROM {agent_name.upper()}]\n\n{response}"

    return StructuredTool.from_function(
        func=forward_to_user,
        name=f"forward_{agent_name}_response",
        description=f"Forward the {agent_name}'s response directly to the user without modification. "
                    f"Use this tool to pass the expert's response verbatim. "
                    f"This ensures accuracy and maintains accountability for specialized advice.",
    )


# ============================================
# Subagent Definitions
# ============================================

def get_model():
    """Initialize the chat model."""
    return init_chat_model("gpt-4o-mini", model_provider="openai")


def create_contract_agent():
    """Create the contract analysis subagent."""
    model = get_model()

    system_prompt = """You are an expert contract attorney specializing in commercial agreements.

Your expertise includes:
- SaaS and technology agreements
- Licensing and IP provisions
- Risk allocation clauses
- Standard market terms analysis

When analyzing contracts:
1. Identify key provisions and their implications
2. Assess risk levels (LOW, MODERATE, HIGH)
3. Provide specific recommendations with suggested language
4. Always include a disclaimer that this is informational, not legal advice

Be precise and thorough. Your exact wording will be forwarded to the client."""

    return create_agent(
        model,
        tools=[analyze_contract_clause],
        system_prompt=system_prompt,
    )


def create_compliance_agent():
    """Create the regulatory compliance subagent."""
    model = get_model()

    system_prompt = """You are a regulatory compliance specialist with expertise in:

- Data privacy (GDPR, CCPA, CPRA, state privacy laws)
- Financial regulations (SOX, PCI-DSS, AML/KYC)
- Industry-specific compliance (HIPAA, FERPA, GLBA)

When assessing compliance:
1. Identify all applicable regulations
2. List specific requirements with citations
3. Assess current compliance status
4. Provide actionable remediation steps
5. Note penalties for non-compliance

Be comprehensive and precise. Your analysis will be forwarded verbatim to the client."""

    return create_agent(
        model,
        tools=[check_regulatory_compliance],
        system_prompt=system_prompt,
    )


def create_ip_agent():
    """Create the intellectual property subagent."""
    model = get_model()

    system_prompt = """You are an intellectual property attorney specializing in:

- Patent prosecution and strategy
- Trademark registration and enforcement
- Copyright protection
- Trade secret programs

When analyzing IP matters:
1. Assess protectability and strength
2. Recommend appropriate protection strategies
3. Identify risks and enforcement options
4. Provide timeline and cost estimates
5. Suggest next steps with specific actions

Your exact analysis will be forwarded to the client. Be precise and thorough."""

    return create_agent(
        model,
        tools=[research_ip_rights],
        system_prompt=system_prompt,
    )


# ============================================
# Supervisor with Forward Tool
# ============================================

SUPERVISOR_PROMPT = """You are a Legal Services Coordinator managing a team of legal specialists.

YOUR TEAM:
1. **Contract Specialist** - Analyzes contract clauses, negotiation points, risk allocation
2. **Compliance Specialist** - Regulatory requirements, privacy laws, industry compliance
3. **IP Specialist** - Patents, trademarks, copyrights, trade secrets

YOUR ROLE:
- Route client queries to the appropriate specialist
- Forward specialist responses DIRECTLY to the client using the forward tools
- DO NOT paraphrase or modify specialist responses - legal accuracy requires exact wording
- Coordinate when multiple specialists are needed

CRITICAL INSTRUCTION:
When you receive a specialist's response, use the appropriate forward_*_response tool
to pass it directly to the user. Do not summarize, paraphrase, or add your own analysis
to the specialist's response. This ensures:
- Legal accuracy is maintained
- Accountability is clear (specialist's exact words)
- No paraphrasing errors are introduced

For simple routing questions, you may respond directly. For substantive legal questions,
always delegate to the appropriate specialist and forward their response."""


def create_supervisor_workflow():
    """Create the supervisor workflow with forward tools."""
    model = get_model()
    checkpointer = InMemorySaver()

    # Create subagents
    contract_agent = create_contract_agent()
    compliance_agent = create_compliance_agent()
    ip_agent = create_ip_agent()

    # Create forward tools for each specialist
    forward_contract = create_forward_tool("contract_specialist")
    forward_compliance = create_forward_tool("compliance_specialist")
    forward_ip = create_forward_tool("ip_specialist")

    # Routing tool for supervisor
    @tool
    def route_to_specialist(
        specialist: Literal["contract", "compliance", "ip"],
        query: str
    ) -> str:
        """Route a query to the appropriate legal specialist.

        Args:
            specialist: Which specialist to consult (contract, compliance, ip)
            query: The specific question or request for the specialist
        """
        agents = {
            "contract": contract_agent,
            "compliance": compliance_agent,
            "ip": ip_agent,
        }

        agent = agents[specialist]
        result = agent.invoke({
            "messages": [HumanMessage(content=query)]
        })

        # Extract the final response
        final_message = result["messages"][-1]
        return final_message.content

    # Create supervisor agent with routing and forward tools
    supervisor = create_agent(
        model,
        tools=[route_to_specialist, forward_contract, forward_compliance, forward_ip],
        system_prompt=SUPERVISOR_PROMPT,
        checkpointer=checkpointer,
    )

    return supervisor


# ============================================
# Example Usage
# ============================================

if __name__ == "__main__":
    print("=" * 70)
    print("SUPERVISOR WITH FORWARD TOOL PATTERN: Legal Document Assistant")
    print("=" * 70)
    print("\nArchitecture:")
    print("  Supervisor (Coordinator)")
    print("    ├── route_to_specialist() - Routes queries to experts")
    print("    ├── forward_contract_response() - Forwards contract analysis verbatim")
    print("    ├── forward_compliance_response() - Forwards compliance assessment verbatim")
    print("    └── forward_ip_response() - Forwards IP analysis verbatim")
    print("\n  Subagents:")
    print("    ├── Contract Specialist (analyze_contract_clause)")
    print("    ├── Compliance Specialist (check_regulatory_compliance)")
    print("    └── IP Specialist (research_ip_rights)")
    print("\nKey Feature: FORWARD TOOL")
    print("  - Specialist responses are forwarded VERBATIM")
    print("  - No paraphrasing = no errors introduced")
    print("  - Maintains accountability and audit trail")
    print("  - Critical for legal/medical/financial domains")
    print("=" * 70)

    # Create the workflow
    supervisor = create_supervisor_workflow()

    # Example queries
    queries = [
        # Contract analysis - exact wording matters
        "Please analyze this indemnification clause: 'Each party shall indemnify, "
        "defend, and hold harmless the other party from any claims arising from "
        "the indemnifying party's breach of this Agreement or negligence.'",

        # Compliance check - regulatory precision required
        "We're a fintech startup in California planning to collect user financial "
        "data for our budgeting app. What compliance requirements do we need to meet?",

        # IP question - expert analysis should be preserved
        "We've developed a novel algorithm for detecting fraudulent transactions. "
        "What intellectual property protections should we consider?",
    ]

    config = {"configurable": {"thread_id": "legal_session_001"}}

    for i, query in enumerate(queries, 1):
        print(f"\n{'='*70}")
        print(f"Query {i}: {query[:80]}...")
        print("-" * 70)

        result = supervisor.invoke(
            {"messages": [HumanMessage(content=query)]},
            config=config
        )

        # Extract final response
        final_message = result["messages"][-1]
        print(f"\nResponse:\n{final_message.content}")

    print("\n" + "=" * 70)
    print("Benefits of Forward Tool Pattern:")
    print("  1. ACCURACY - Expert responses preserved verbatim")
    print("  2. ACCOUNTABILITY - Clear attribution to specialist")
    print("  3. COMPLIANCE - Audit trail for regulated industries")
    print("  4. TRUST - Users know they're getting expert analysis unchanged")
    print("=" * 70)
