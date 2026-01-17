"""
Context Quarantine Pattern: Data Analysis Pipeline
==================================================
Subagents isolate large tool outputs from the main agent's context,
preventing context bloat while preserving analysis quality.

Key Concepts:
- Main agent delegates data-heavy tasks to quarantine subagents
- Subagents process large datasets in isolated contexts
- Only summaries/insights are returned to main agent
- Raw data never enters the main conversation context

Architecture:
                    ┌──────────────────────┐
                    │     MAIN AGENT       │
                    │  (Clean context)     │
                    │                      │
                    │  Context: ~2K tokens │
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
         │                    │                    │
         └────────────────────┼────────────────────┘
                              │
                    (Summaries only: ~1.5K tokens)
                              │
                              ▼
                    ┌──────────────────────┐
                    │     MAIN AGENT       │
                    │  Context: ~3.5K      │
                    │  (NOT 100K+ tokens!) │
                    └──────────────────────┘

This pattern is best when:
- Tool outputs are large (data queries, file contents, API responses)
- Context bloat degrades agent performance
- You need sustained reasoning over multiple steps
- Raw data isn't needed in final response

Reference:
- https://docs.langchain.com/oss/python/langchain/multi-agent/context-quarantine
"""

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
from typing import TypedDict, Annotated, Literal
import operator
import json

# Load environment variables
load_dotenv()


# ============================================
# Simulated Large Data Sources
# ============================================

# Simulate a large dataset (in production, this would be real database queries)
MOCK_SALES_DATA = """
SALES TRANSACTION LOG (Last 30 Days)
=====================================
Transaction ID | Date       | Product          | Qty | Unit Price | Total    | Region      | Customer Segment
---------------------------------------------------------------------------------------------------------
TXN-001       | 2025-01-01 | Enterprise Plan  | 1   | $999.00    | $999.00  | North America | Enterprise
TXN-002       | 2025-01-01 | Pro Plan         | 3   | $49.99     | $149.97  | Europe        | SMB
TXN-003       | 2025-01-01 | Starter Plan     | 10  | $9.99      | $99.90   | Asia Pacific  | Startup
TXN-004       | 2025-01-02 | Enterprise Plan  | 2   | $999.00    | $1998.00 | North America | Enterprise
TXN-005       | 2025-01-02 | Pro Plan         | 5   | $49.99     | $249.95  | North America | SMB
""" + "\n".join([
    f"TXN-{i:03d}       | 2025-01-{(i%28)+1:02d} | {'Enterprise Plan' if i%5==0 else 'Pro Plan' if i%3==0 else 'Starter Plan'}  | {(i%10)+1}   | ${'999.00' if i%5==0 else '49.99' if i%3==0 else '9.99'}    | ${(i%10+1)*999 if i%5==0 else (i%10+1)*49.99 if i%3==0 else (i%10+1)*9.99:.2f}  | {'North America' if i%4==0 else 'Europe' if i%4==1 else 'Asia Pacific' if i%4==2 else 'Latin America'} | {'Enterprise' if i%5==0 else 'SMB' if i%3==0 else 'Startup'}"
    for i in range(6, 500)  # Simulate 500 transactions
])

MOCK_USER_ACTIVITY = """
USER ACTIVITY LOG (Last 7 Days)
================================
User ID  | Timestamp           | Action              | Duration | Feature        | Success
--------------------------------------------------------------------------------------------
USR-001  | 2025-01-15 09:00:00 | login               | -        | auth           | true
USR-001  | 2025-01-15 09:01:00 | view_dashboard      | 45s      | dashboard      | true
USR-001  | 2025-01-15 09:02:30 | create_task         | 120s     | tasks          | true
USR-002  | 2025-01-15 09:05:00 | login               | -        | auth           | true
USR-002  | 2025-01-15 09:05:30 | export_report       | 30s      | reports        | false
""" + "\n".join([
    f"USR-{(i%100)+1:03d}  | 2025-01-{15+(i%7):02d} {(i%24):02d}:{(i*7)%60:02d}:00 | {'login' if i%10==0 else 'view_dashboard' if i%10==1 else 'create_task' if i%10==2 else 'edit_task' if i%10==3 else 'delete_task' if i%10==4 else 'export_report' if i%10==5 else 'invite_user' if i%10==6 else 'change_settings' if i%10==7 else 'view_analytics' if i%10==8 else 'api_call'}              | {'-' if i%10==0 else f'{(i%180)+10}s'}      | {'auth' if i%10==0 else 'dashboard' if i%10==1 else 'tasks' if i%10 in [2,3,4] else 'reports' if i%10==5 else 'team' if i%10==6 else 'settings' if i%10==7 else 'analytics' if i%10==8 else 'api'}           | {'true' if i%7!=0 else 'false'}"
    for i in range(6, 1000)  # Simulate 1000 activity records
])

MOCK_ERROR_LOGS = """
ERROR LOG (Last 24 Hours)
==========================
Timestamp           | Level    | Service      | Error Code | Message                                          | Stack Trace
--------------------------------------------------------------------------------------------------------------------------
2025-01-20 00:15:32 | ERROR    | api-gateway  | E5001      | Rate limit exceeded for IP 192.168.1.100        | at RateLimiter.check (rate-limiter.js:45)...
2025-01-20 00:30:45 | WARNING  | auth-service | W3002      | JWT token expires in < 5 minutes                | at TokenValidator.validate (auth.js:120)...
2025-01-20 01:00:00 | ERROR    | db-service   | E2001      | Connection pool exhausted                        | at Pool.acquire (pg-pool.js:89)...
""" + "\n".join([
    f"2025-01-20 {(i%24):02d}:{(i*3)%60:02d}:{(i*7)%60:02d} | {'ERROR' if i%5==0 else 'WARNING' if i%3==0 else 'INFO'}    | {'api-gateway' if i%6==0 else 'auth-service' if i%6==1 else 'db-service' if i%6==2 else 'worker' if i%6==3 else 'cache' if i%6==4 else 'notification'}   | {'E' if i%5==0 else 'W' if i%3==0 else 'I'}{1000+(i%9)*1000+i%1000}      | {'Rate limit exceeded' if i%10==0 else 'Connection timeout' if i%10==1 else 'Invalid request format' if i%10==2 else 'Resource not found' if i%10==3 else 'Permission denied' if i%10==4 else 'Service unavailable' if i%10==5 else 'Retry limit reached' if i%10==6 else 'Cache miss' if i%10==7 else 'Queue full' if i%10==8 else 'Memory warning'}                        | at Handler.process (handler.js:{100+i%500})..."
    for i in range(4, 300)  # Simulate 300 error entries
])


# ============================================
# State Definition
# ============================================

class AnalysisState(TypedDict):
    """State for the analysis workflow."""
    messages: Annotated[list, operator.add]
    query: str
    data_summary: str
    analysis_summary: str
    recommendations: str
    final_report: str


# ============================================
# Utility Functions
# ============================================

def get_model():
    """Initialize the chat model."""
    return init_chat_model("gpt-4o-mini", model_provider="openai")


def count_tokens_approx(text: str) -> int:
    """Approximate token count (roughly 4 chars per token)."""
    return len(text) // 4


# ============================================
# Quarantine Subagent Tools (Large Outputs)
# ============================================

@tool
def query_sales_database(date_range: str, filters: str) -> str:
    """Query the sales database for transaction data.

    Args:
        date_range: Date range to query (e.g., "last_30_days", "last_quarter")
        filters: Additional filters (e.g., "region=North America", "product=Enterprise")
    """
    # In production, this would be a real database query
    # Returns LARGE dataset (simulated ~50K tokens)
    return MOCK_SALES_DATA


@tool
def query_user_activity(user_segment: str, time_period: str) -> str:
    """Query user activity logs.

    Args:
        user_segment: User segment to analyze (e.g., "all", "enterprise", "trial")
        time_period: Time period (e.g., "last_7_days", "last_month")
    """
    # Returns LARGE dataset (simulated ~40K tokens)
    return MOCK_USER_ACTIVITY


@tool
def query_error_logs(severity: str, service: str) -> str:
    """Query error and warning logs.

    Args:
        severity: Minimum severity level (e.g., "ERROR", "WARNING", "INFO")
        service: Service to filter by (e.g., "all", "api-gateway", "auth-service")
    """
    # Returns LARGE dataset (simulated ~30K tokens)
    return MOCK_ERROR_LOGS


@tool
def run_statistical_analysis(data_type: str, metrics: str) -> str:
    """Run statistical analysis on collected data.

    Args:
        data_type: Type of data to analyze (sales, activity, errors)
        metrics: Metrics to calculate (e.g., "mean,median,std,trends")
    """
    # Simulates processing and returns analysis
    return f"""
STATISTICAL ANALYSIS RESULTS
============================
Data Type: {data_type}
Metrics: {metrics}

SUMMARY STATISTICS:
------------------
Total Records Analyzed: 1,847
Time Period: 2025-01-01 to 2025-01-20

SALES METRICS:
- Total Revenue: $487,293.45
- Average Transaction: $263.78
- Median Transaction: $149.97
- Std Deviation: $412.33
- Revenue Growth (MoM): +12.3%

DISTRIBUTION:
- Enterprise Plans: 23% of transactions, 67% of revenue
- Pro Plans: 45% of transactions, 28% of revenue
- Starter Plans: 32% of transactions, 5% of revenue

REGIONAL BREAKDOWN:
- North America: 42% ($204,663.25)
- Europe: 28% ($136,442.17)
- Asia Pacific: 20% ($97,458.69)
- Latin America: 10% ($48,729.34)

TRENDS:
- Week-over-week growth: +8.2%
- Enterprise adoption increasing
- APAC showing fastest growth (+23% MoM)

ANOMALIES DETECTED:
- Spike in transactions on Jan 15 (likely promotion)
- Unusual drop in LATAM on Jan 12 (investigate)
"""


@tool
def generate_visualizations(chart_types: str, data_points: str) -> str:
    """Generate data visualizations (returns descriptions for text-based output).

    Args:
        chart_types: Types of charts to generate (e.g., "bar,line,pie")
        data_points: Key data points to visualize
    """
    return f"""
VISUALIZATION SPECIFICATIONS
============================
Charts Generated: {chart_types}
Data Points: {data_points}

CHART 1: Revenue by Region (Pie Chart)
- North America: 42% (largest slice)
- Europe: 28%
- Asia Pacific: 20%
- Latin America: 10%
[Recommended: Highlight APAC growth potential]

CHART 2: Daily Revenue Trend (Line Chart)
- X-axis: Date (Jan 1-20)
- Y-axis: Revenue ($)
- Trend line showing +12.3% growth
- Notable spike on Jan 15
[Recommended: Add annotation for Jan 15 promotion]

CHART 3: Product Mix (Stacked Bar)
- Shows transaction volume by product tier
- Enterprise: Low volume, high value
- Pro: Medium volume, medium value
- Starter: High volume, low value
[Recommended: Include revenue overlay]

CHART 4: Error Rate by Service (Bar Chart)
- api-gateway: 45 errors (highest)
- db-service: 32 errors
- auth-service: 28 errors
- Others: < 20 errors each
[Recommended: Color-code by severity]

Export formats available: PNG, SVG, PDF
Dashboard URL: https://analytics.example.com/dashboard/jan2025
"""


# ============================================
# Quarantine Subagents
# ============================================

def create_data_collector_agent():
    """Create the data collection subagent that handles large queries."""
    model = get_model()

    system_prompt = """You are a Data Collection Specialist. Your job is to:

1. Query the appropriate data sources based on the analysis request
2. Process and validate the raw data
3. Extract key statistics and patterns
4. Return a CONCISE SUMMARY (max 500 words)

CRITICAL: You work with large datasets that would overwhelm the main agent's context.
Your role is to quarantine this data and return only essential insights.

Output format:
- Data sources queried
- Record counts
- Key statistics (5-10 bullet points)
- Data quality notes
- Recommended focus areas

DO NOT return raw data. Return summaries only."""

    return create_react_agent(
        model,
        tools=[query_sales_database, query_user_activity, query_error_logs],
        prompt=system_prompt,
    )


def create_analysis_processor_agent():
    """Create the analysis processing subagent."""
    model = get_model()

    system_prompt = """You are a Data Analysis Specialist. Your job is to:

1. Run statistical analysis on collected data
2. Identify trends, patterns, and anomalies
3. Generate visualization specifications
4. Return a CONCISE SUMMARY (max 400 words)

CRITICAL: You process large analytical outputs that would overwhelm the main context.
Quarantine detailed calculations and return only key insights.

Output format:
- Analysis type performed
- Key findings (5-7 bullet points)
- Statistical highlights
- Trend summary
- Anomalies or concerns

DO NOT return raw calculations. Return insights only."""

    return create_react_agent(
        model,
        tools=[run_statistical_analysis, generate_visualizations],
        prompt=system_prompt,
    )


# ============================================
# Main Coordinator (Clean Context)
# ============================================

COORDINATOR_PROMPT = """You are a Business Intelligence Coordinator.

Your role is to:
1. Understand the user's analysis request
2. Delegate data collection to the Data Collector (quarantine subagent)
3. Delegate analysis to the Analysis Processor (quarantine subagent)
4. Synthesize their SUMMARIES into a coherent report

CRITICAL CONTEXT MANAGEMENT:
- Subagents handle large datasets in isolated contexts
- You receive ONLY their summaries (500-600 tokens each)
- Raw data NEVER enters your context
- This keeps your reasoning sharp and focused

When delegating:
- Be specific about what data/analysis is needed
- Trust subagent summaries - they've done the heavy lifting
- Focus on synthesis and recommendations

Your final output should be an executive-level report that answers the user's question."""


def create_quarantine_workflow():
    """Create the context quarantine workflow."""
    model = get_model()
    checkpointer = InMemorySaver()

    # Create quarantine subagents
    data_collector = create_data_collector_agent()
    analysis_processor = create_analysis_processor_agent()

    def collect_data(state: AnalysisState) -> dict:
        """Quarantine subagent: Collect and summarize data."""
        print("\n  [DATA COLLECTOR] Processing large datasets in quarantine...")

        # This subagent processes ~100K tokens of raw data
        result = data_collector.invoke({
            "messages": [HumanMessage(
                content=f"Collect and summarize data for this analysis: {state['query']}\n"
                        "Query sales, user activity, and error logs. Return only a summary."
            )]
        })

        summary = result["messages"][-1].content

        # Log context savings
        raw_data_tokens = count_tokens_approx(MOCK_SALES_DATA + MOCK_USER_ACTIVITY + MOCK_ERROR_LOGS)
        summary_tokens = count_tokens_approx(summary)
        print(f"  [DATA COLLECTOR] Raw data: ~{raw_data_tokens:,} tokens")
        print(f"  [DATA COLLECTOR] Summary returned: ~{summary_tokens:,} tokens")
        print(f"  [DATA COLLECTOR] Context saved: ~{raw_data_tokens - summary_tokens:,} tokens ({(1-summary_tokens/raw_data_tokens)*100:.1f}% reduction)")

        return {"data_summary": summary}

    def analyze_data(state: AnalysisState) -> dict:
        """Quarantine subagent: Analyze data and return insights."""
        print("\n  [ANALYSIS PROCESSOR] Running analysis in quarantine...")

        result = analysis_processor.invoke({
            "messages": [HumanMessage(
                content=f"Based on this data summary, perform statistical analysis and generate visualizations:\n\n"
                        f"{state['data_summary']}\n\n"
                        f"Original query: {state['query']}\n"
                        "Return only key insights and recommendations."
            )]
        })

        summary = result["messages"][-1].content
        summary_tokens = count_tokens_approx(summary)
        print(f"  [ANALYSIS PROCESSOR] Analysis summary: ~{summary_tokens:,} tokens")

        return {"analysis_summary": summary}

    def synthesize_report(state: AnalysisState) -> dict:
        """Main agent: Synthesize summaries into final report."""
        print("\n  [COORDINATOR] Synthesizing final report (clean context)...")

        # The coordinator only sees summaries, not raw data
        coordinator_context = f"""
Data Summary:
{state['data_summary']}

Analysis Summary:
{state['analysis_summary']}
"""
        context_tokens = count_tokens_approx(coordinator_context)
        print(f"  [COORDINATOR] Total context: ~{context_tokens:,} tokens (vs ~120K if raw data included)")

        # Generate final report
        final_report = f"""
================================================================================
BUSINESS INTELLIGENCE REPORT
================================================================================
Query: {state['query']}
Generated: 2025-01-20

EXECUTIVE SUMMARY
-----------------
This report analyzes sales performance, user engagement, and system health
based on data from the past 30 days. Key findings indicate strong growth
with some areas requiring attention.

DATA COLLECTION FINDINGS
------------------------
{state['data_summary']}

ANALYSIS INSIGHTS
-----------------
{state['analysis_summary']}

RECOMMENDATIONS
---------------
Based on the analysis, we recommend:

1. **Expand APAC Investment**: Fastest growing region (+23% MoM), consider
   localized marketing campaigns and regional pricing.

2. **Enterprise Upsell Focus**: Enterprise plans drive 67% of revenue with only
   23% of transactions. Prioritize enterprise conversion programs.

3. **Address API Gateway Errors**: Highest error rate among services. Schedule
   infrastructure review and implement better rate limiting.

4. **Capitalize on Promotion Success**: Jan 15 spike suggests promotions work.
   Plan Q1 promotion calendar.

5. **Investigate LATAM Drop**: Unusual activity decrease on Jan 12 requires
   investigation - possible payment processor issue.

NEXT STEPS
----------
- Schedule weekly metrics review
- Set up automated anomaly alerts
- Plan APAC expansion roadmap
- API gateway optimization sprint

================================================================================
Report generated with Context Quarantine Pattern
Raw data processed: ~120,000 tokens (quarantined)
Final context used: ~{context_tokens:,} tokens
================================================================================
"""
        return {"final_report": final_report}

    # Build workflow
    workflow = StateGraph(AnalysisState)

    workflow.add_node("collect", collect_data)
    workflow.add_node("analyze", analyze_data)
    workflow.add_node("synthesize", synthesize_report)

    workflow.add_edge(START, "collect")
    workflow.add_edge("collect", "analyze")
    workflow.add_edge("analyze", "synthesize")
    workflow.add_edge("synthesize", END)

    return workflow.compile()


# ============================================
# Example Usage
# ============================================

if __name__ == "__main__":
    print("=" * 80)
    print("CONTEXT QUARANTINE PATTERN: Data Analysis Pipeline")
    print("=" * 80)
    print("\nArchitecture:")
    print("  Main Coordinator (Clean Context: ~3K tokens)")
    print("    │")
    print("    ├── Data Collector (Quarantine)")
    print("    │     ├── query_sales_database → ~50K tokens")
    print("    │     ├── query_user_activity → ~40K tokens")
    print("    │     ├── query_error_logs → ~30K tokens")
    print("    │     └── Returns: 500 token SUMMARY")
    print("    │")
    print("    └── Analysis Processor (Quarantine)")
    print("          ├── run_statistical_analysis → Large calculations")
    print("          ├── generate_visualizations → Chart specs")
    print("          └── Returns: 400 token SUMMARY")
    print("\nKey Feature: CONTEXT ISOLATION")
    print("  - Raw data (~120K tokens) NEVER enters main context")
    print("  - Only summaries (~1.5K tokens) reach coordinator")
    print("  - Main agent reasoning stays sharp and focused")
    print("  - Prevents context bloat degradation")
    print("=" * 80)

    # Create the workflow
    pipeline = create_quarantine_workflow()

    # Example query
    query = """
    Analyze our business performance for the past month. I need to understand:
    1. How are sales trending across regions and products?
    2. What does user engagement look like?
    3. Are there any system health concerns?
    4. What should we focus on for Q1?
    """

    print(f"\nQuery: {query.strip()}")
    print("\n" + "-" * 80)
    print("Processing with context quarantine...")
    print("-" * 80)

    result = pipeline.invoke({
        "messages": [],
        "query": query,
        "data_summary": "",
        "analysis_summary": "",
        "recommendations": "",
        "final_report": ""
    })

    print(result["final_report"])

    print("\n" + "=" * 80)
    print("Benefits of Context Quarantine Pattern:")
    print("  1. PERFORMANCE - Main agent never sees 120K+ tokens of raw data")
    print("  2. RELIABILITY - Clean context = better reasoning quality")
    print("  3. COST - Fewer tokens in main context = lower API costs")
    print("  4. SCALABILITY - Can process arbitrarily large datasets")
    print("  5. MAINTAINABILITY - Clear separation of data processing vs. synthesis")
    print("=" * 80)
    print("\nComparison with WITHOUT quarantine:")
    print("  - Without: Main agent context = 120K+ tokens (degraded performance)")
    print("  - With:    Main agent context = ~3K tokens (optimal performance)")
    print("  - Token reduction: ~97%")
    print("=" * 80)
