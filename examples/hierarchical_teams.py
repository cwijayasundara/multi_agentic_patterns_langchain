"""
Hierarchical Teams Pattern: Product Launch Coordinator
======================================================
A multi-level hierarchy where subagents are themselves LangGraph subgraphs,
enabling complex nested workflows with team-level coordination.

Key Concepts:
- Top-level supervisor coordinates team leads
- Team leads are subgraphs that coordinate their own specialists
- Each team operates as an independent workflow
- Results bubble up through the hierarchy

Architecture:
                    ┌──────────────────────┐
                    │   LAUNCH SUPERVISOR  │
                    │   (Top-level coord)  │
                    └──────────┬───────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
    ┌───────────┐        ┌───────────┐        ┌───────────┐
    │ MARKETING │        │ENGINEERING│        │    QA     │
    │   TEAM    │        │   TEAM    │        │   TEAM    │
    │ (Subgraph)│        │ (Subgraph)│        │ (Subgraph)│
    └─────┬─────┘        └─────┬─────┘        └─────┬─────┘
          │                    │                    │
    ┌─────┼─────┐        ┌─────┼─────┐        ┌─────┼─────┐
    │     │     │        │     │     │        │     │     │
    ▼     ▼     ▼        ▼     ▼     ▼        ▼     ▼     ▼
  Content SEO  Social  Backend Frontend  DevOps  Manual Auto  Perf
  Writer Spec  Media    Dev    Dev      Eng    Test   Test  Test

This pattern is best when:
- Complex workflows require multiple levels of coordination
- Teams operate semi-independently but need synchronization
- Different teams have different internal workflows
- You need to scale to many specialists without overwhelming a single supervisor

Reference:
- https://docs.langchain.com/oss/python/langchain/multi-agent/hierarchical-teams
"""

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.tools import tool
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from typing import TypedDict, Annotated, Literal
import operator

# Load environment variables
load_dotenv()


# ============================================
# State Definitions
# ============================================

class TeamState(TypedDict):
    """State for team-level subgraphs."""
    messages: Annotated[list, operator.add]
    task: str
    team_output: str
    specialist_outputs: Annotated[list, operator.add]


class LaunchState(TypedDict):
    """State for the top-level launch coordinator."""
    messages: Annotated[list, operator.add]
    product_name: str
    launch_date: str
    requirements: str
    marketing_output: str
    engineering_output: str
    qa_output: str
    final_plan: str


# ============================================
# Utility Functions
# ============================================

def get_model():
    """Initialize the chat model."""
    return init_chat_model("gpt-4o-mini", model_provider="openai")


# ============================================
# Marketing Team Subgraph
# ============================================

@tool
def create_content_strategy(product_name: str, target_audience: str) -> str:
    """Create content marketing strategy for product launch.

    Args:
        product_name: Name of the product being launched
        target_audience: Primary target audience description
    """
    return f"""**Content Strategy: {product_name}**

**Target Audience**: {target_audience}

**Content Calendar (4-week Pre-launch):**
- Week 4: Teaser blog post - "The Future of [Category]"
- Week 3: Problem/solution article series (3 posts)
- Week 2: Product preview with early access signup
- Week 1: Feature deep-dives and use case studies
- Launch Day: Official announcement + press release

**Content Assets Required:**
1. Landing page copy (headline, benefits, CTA)
2. Blog posts (5 articles, 1500 words each)
3. Email sequences (nurture: 5 emails, launch: 3 emails)
4. Product documentation (getting started guide)
5. Case study template

**Key Messages:**
- Primary: "{product_name} helps [audience] achieve [outcome] without [pain point]"
- Supporting: Speed, reliability, ease of use

**Distribution Channels:**
- Company blog, Medium, LinkedIn Articles, Guest posts

**Metrics to Track:**
- Signups, engagement rate, time on page, conversion rate"""


@tool
def create_seo_plan(product_name: str, primary_keywords: str) -> str:
    """Create SEO optimization plan for product launch.

    Args:
        product_name: Name of the product
        primary_keywords: Main keywords to target
    """
    return f"""**SEO Strategy: {product_name}**

**Primary Keywords**: {primary_keywords}
**Search Intent**: Commercial/Transactional

**Keyword Clusters:**
1. Primary: "{primary_keywords}" (Vol: 5,400, KD: 45)
2. Long-tail: "best {primary_keywords} for startups" (Vol: 1,200, KD: 32)
3. Comparison: "{primary_keywords} vs competitors" (Vol: 2,100, KD: 38)
4. How-to: "how to use {primary_keywords}" (Vol: 890, KD: 28)

**On-Page Optimization:**
- Title tag: "{product_name}: [Primary Benefit] | [Brand]"
- Meta description: Include primary keyword, CTA, 155 chars
- H1: Primary keyword + value proposition
- URL structure: /products/{product_name.lower().replace(' ', '-')}/

**Technical SEO Checklist:**
- [ ] Core Web Vitals optimization
- [ ] Schema markup (Product, FAQ, How-to)
- [ ] XML sitemap updated
- [ ] Internal linking from high-authority pages
- [ ] Mobile-first indexing ready

**Link Building Targets:**
- 10 guest posts on industry blogs (DA 40+)
- Product Hunt launch
- Integration partner announcements
- Industry roundup inclusion"""


@tool
def create_social_campaign(product_name: str, platforms: str) -> str:
    """Create social media campaign for product launch.

    Args:
        product_name: Name of the product
        platforms: Target social platforms (comma-separated)
    """
    return f"""**Social Media Campaign: {product_name}**

**Platforms**: {platforms}

**Campaign Phases:**

**Phase 1: Awareness (Weeks -4 to -2)**
- Teaser posts with countdown
- Behind-the-scenes content
- Problem-focused content (pain points)
- Hashtag: #{product_name.replace(' ', '')}Coming

**Phase 2: Anticipation (Week -1)**
- Feature previews
- Early access announcements
- Influencer partnerships activate
- Email list promotion

**Phase 3: Launch (Day 0)**
- Official announcement (all platforms, synchronized)
- Founder video message
- Live Q&A session
- Limited-time launch offer

**Phase 4: Momentum (Weeks +1 to +4)**
- User testimonials and UGC
- Feature highlights
- Use case showcases
- Community engagement

**Content Mix:**
- 40% Educational/Value
- 30% Product/Promotional
- 20% Community/Engagement
- 10% Behind-the-scenes

**Paid Amplification Budget**: $5,000
- 60% retargeting warm audience
- 40% lookalike audience expansion

**KPIs:**
- Reach: 500K impressions
- Engagement: 3% rate
- Clicks: 10K to landing page
- Conversions: 500 signups"""


def create_marketing_team():
    """Create the marketing team subgraph."""
    model = get_model()

    def content_specialist(state: TeamState) -> dict:
        """Content writer specialist node."""
        result = create_content_strategy.invoke({
            "product_name": state["task"].split(":")[0] if ":" in state["task"] else "Product",
            "target_audience": "tech-savvy professionals"
        })
        return {"specialist_outputs": [f"**CONTENT SPECIALIST:**\n{result}"]}

    def seo_specialist(state: TeamState) -> dict:
        """SEO specialist node."""
        result = create_seo_plan.invoke({
            "product_name": state["task"].split(":")[0] if ":" in state["task"] else "Product",
            "primary_keywords": "productivity software"
        })
        return {"specialist_outputs": [f"**SEO SPECIALIST:**\n{result}"]}

    def social_specialist(state: TeamState) -> dict:
        """Social media specialist node."""
        result = create_social_campaign.invoke({
            "product_name": state["task"].split(":")[0] if ":" in state["task"] else "Product",
            "platforms": "LinkedIn, Twitter, Instagram"
        })
        return {"specialist_outputs": [f"**SOCIAL MEDIA SPECIALIST:**\n{result}"]}

    def marketing_lead(state: TeamState) -> dict:
        """Marketing team lead synthesizes specialist outputs."""
        specialist_work = "\n\n".join(state["specialist_outputs"])

        synthesis = f"""**MARKETING TEAM SUMMARY**
============================

The marketing team has completed the following deliverables:

{specialist_work}

**TEAM RECOMMENDATIONS:**
1. Content and SEO strategies are aligned for maximum organic reach
2. Social campaign amplifies content across all target platforms
3. Recommend $5,000 paid media budget for launch week
4. All assets should be ready 2 weeks before launch

**ESTIMATED REACH:** 750K total impressions in first month
**PROJECTED SIGNUPS:** 500-750 from marketing channels"""

        return {"team_output": synthesis}

    # Build the marketing team subgraph
    workflow = StateGraph(TeamState)

    # Add specialist nodes (can run in parallel)
    workflow.add_node("content", content_specialist)
    workflow.add_node("seo", seo_specialist)
    workflow.add_node("social", social_specialist)
    workflow.add_node("lead", marketing_lead)

    # Specialists work in parallel, then lead synthesizes
    workflow.add_edge(START, "content")
    workflow.add_edge(START, "seo")
    workflow.add_edge(START, "social")
    workflow.add_edge("content", "lead")
    workflow.add_edge("seo", "lead")
    workflow.add_edge("social", "lead")
    workflow.add_edge("lead", END)

    return workflow.compile()


# ============================================
# Engineering Team Subgraph
# ============================================

@tool
def plan_backend_work(features: str, timeline_weeks: int) -> str:
    """Plan backend development work for launch.

    Args:
        features: Key features to implement
        timeline_weeks: Weeks until launch
    """
    return f"""**Backend Development Plan**

**Features**: {features}
**Timeline**: {timeline_weeks} weeks

**Sprint Breakdown:**

**Sprint 1 (Weeks 1-2): Core Infrastructure**
- API gateway setup with rate limiting
- Database schema design and migration
- Authentication service (OAuth 2.0 + JWT)
- Estimated: 80 story points

**Sprint 2 (Weeks 3-4): Feature Implementation**
- Core business logic implementation
- Third-party integrations (payment, email)
- Webhook system for real-time events
- Estimated: 100 story points

**Sprint 3 (Weeks 5-6): Polish & Scale**
- Performance optimization
- Caching layer (Redis)
- Monitoring and alerting setup
- Load testing and optimization
- Estimated: 60 story points

**Technical Stack:**
- Runtime: Node.js 20 LTS
- Framework: Express.js with TypeScript
- Database: PostgreSQL 15 + Redis
- Infrastructure: AWS (ECS, RDS, ElastiCache)

**Risks & Mitigations:**
- Risk: Third-party API delays → Mitigation: Mock services ready
- Risk: Scale issues → Mitigation: Load test at 10x expected traffic

**Definition of Done for Launch:**
- [ ] All APIs documented in OpenAPI
- [ ] 90%+ test coverage
- [ ] P99 latency < 200ms
- [ ] Zero critical security vulnerabilities"""


@tool
def plan_frontend_work(pages: str, design_system: str) -> str:
    """Plan frontend development work for launch.

    Args:
        pages: Key pages/features to build
        design_system: Design system being used
    """
    return f"""**Frontend Development Plan**

**Pages/Features**: {pages}
**Design System**: {design_system}

**Component Breakdown:**

**Week 1-2: Foundation**
- Design system implementation ({design_system})
- Core layout components (Header, Footer, Navigation)
- Authentication flows (Login, Register, Password Reset)
- Responsive grid system

**Week 3-4: Feature Pages**
- Dashboard with data visualization
- Product/feature pages
- Settings and account management
- Onboarding flow

**Week 5-6: Polish & Optimization**
- Animation and micro-interactions
- Accessibility audit (WCAG 2.1 AA)
- Performance optimization (Lighthouse 90+)
- Cross-browser testing

**Technical Stack:**
- Framework: Next.js 14 with App Router
- Styling: Tailwind CSS + {design_system}
- State: React Query + Zustand
- Testing: Jest + React Testing Library + Playwright

**Performance Targets:**
- LCP: < 2.5s
- FID: < 100ms
- CLS: < 0.1
- Lighthouse: 90+ all categories

**Deliverables:**
- [ ] Storybook component library
- [ ] Responsive design (mobile, tablet, desktop)
- [ ] Dark mode support
- [ ] Internationalization ready (i18n)"""


@tool
def plan_devops_work(environments: str, deployment_target: str) -> str:
    """Plan DevOps and infrastructure work for launch.

    Args:
        environments: Required environments (dev, staging, prod)
        deployment_target: Target cloud platform
    """
    return f"""**DevOps & Infrastructure Plan**

**Environments**: {environments}
**Platform**: {deployment_target}

**Infrastructure Setup:**

**Week 1: Foundation**
- Infrastructure as Code (Terraform)
- CI/CD pipeline (GitHub Actions)
- Environment provisioning ({environments})
- Secrets management (AWS Secrets Manager)

**Week 2: Application Infrastructure**
- Container orchestration (ECS Fargate)
- Database setup with automated backups
- CDN configuration (CloudFront)
- SSL/TLS certificates

**Week 3-4: Observability**
- Centralized logging (CloudWatch + DataDog)
- APM and distributed tracing
- Custom dashboards and alerting
- On-call rotation setup (PagerDuty)

**Week 5-6: Security & Compliance**
- WAF rules configuration
- DDoS protection
- Security scanning (Snyk, Trivy)
- Penetration testing coordination

**Deployment Strategy:**
- Blue/Green deployments for zero-downtime
- Automated rollback on failure
- Feature flags for gradual rollout
- Database migration automation

**SLA Targets:**
- Uptime: 99.9% (8.76 hours/year downtime max)
- RTO: 1 hour
- RPO: 5 minutes

**Cost Estimate:**
- Development: $500/month
- Staging: $800/month
- Production: $3,000/month (scales with traffic)

**Launch Readiness Checklist:**
- [ ] All environments provisioned and tested
- [ ] Monitoring and alerting configured
- [ ] Runbook documentation complete
- [ ] Incident response plan documented
- [ ] Load tested at 10x expected traffic"""


def create_engineering_team():
    """Create the engineering team subgraph."""
    model = get_model()

    def backend_dev(state: TeamState) -> dict:
        """Backend developer node."""
        result = plan_backend_work.invoke({
            "features": "user management, core product features, integrations",
            "timeline_weeks": 6
        })
        return {"specialist_outputs": [f"**BACKEND DEVELOPER:**\n{result}"]}

    def frontend_dev(state: TeamState) -> dict:
        """Frontend developer node."""
        result = plan_frontend_work.invoke({
            "pages": "dashboard, settings, onboarding, product pages",
            "design_system": "Shadcn/UI"
        })
        return {"specialist_outputs": [f"**FRONTEND DEVELOPER:**\n{result}"]}

    def devops_eng(state: TeamState) -> dict:
        """DevOps engineer node."""
        result = plan_devops_work.invoke({
            "environments": "dev, staging, production",
            "deployment_target": "AWS"
        })
        return {"specialist_outputs": [f"**DEVOPS ENGINEER:**\n{result}"]}

    def engineering_lead(state: TeamState) -> dict:
        """Engineering team lead synthesizes specialist outputs."""
        specialist_work = "\n\n".join(state["specialist_outputs"])

        synthesis = f"""**ENGINEERING TEAM SUMMARY**
==============================

The engineering team has completed planning for the following areas:

{specialist_work}

**TEAM RECOMMENDATIONS:**
1. Start infrastructure setup immediately (Week 1)
2. Backend and frontend can work in parallel after Week 2
3. Feature freeze at Week 5 for testing
4. Recommend 2-week buffer for unexpected issues

**RESOURCE REQUIREMENTS:**
- Backend: 2 senior engineers
- Frontend: 2 engineers (1 senior, 1 mid)
- DevOps: 1 senior engineer

**CRITICAL PATH:**
Infrastructure → Backend APIs → Frontend Integration → Testing → Launch

**ESTIMATED COMPLETION:** On track for 6-week timeline"""

        return {"team_output": synthesis}

    # Build the engineering team subgraph
    workflow = StateGraph(TeamState)

    workflow.add_node("backend", backend_dev)
    workflow.add_node("frontend", frontend_dev)
    workflow.add_node("devops", devops_eng)
    workflow.add_node("lead", engineering_lead)

    workflow.add_edge(START, "backend")
    workflow.add_edge(START, "frontend")
    workflow.add_edge(START, "devops")
    workflow.add_edge("backend", "lead")
    workflow.add_edge("frontend", "lead")
    workflow.add_edge("devops", "lead")
    workflow.add_edge("lead", END)

    return workflow.compile()


# ============================================
# QA Team Subgraph
# ============================================

@tool
def plan_manual_testing(features: str, test_types: str) -> str:
    """Plan manual testing strategy.

    Args:
        features: Features to test
        test_types: Types of manual testing needed
    """
    return f"""**Manual Testing Plan**

**Scope**: {features}
**Test Types**: {test_types}

**Test Planning:**

**Exploratory Testing (Week 5)**
- Session-based exploratory testing
- Focus areas: new features, edge cases, user workflows
- Time-boxed sessions: 90 minutes each
- Charter: "Explore [feature] to discover usability issues"

**Functional Testing (Week 5-6)**
- Test case execution from test management tool
- Regression testing on core workflows
- Cross-browser testing (Chrome, Firefox, Safari, Edge)
- Mobile testing (iOS Safari, Android Chrome)

**User Acceptance Testing (Week 6)**
- Beta user testing with 50 selected users
- Feedback collection and triage
- Critical issue identification
- Sign-off criteria validation

**Test Coverage:**
- Happy path: 100% coverage
- Error handling: 90% coverage
- Edge cases: 80% coverage
- Accessibility: WCAG 2.1 AA compliance

**Bug Triage Process:**
- Critical (P0): Fix within 4 hours, blocks launch
- High (P1): Fix within 24 hours, major impact
- Medium (P2): Fix before launch if possible
- Low (P3): Post-launch backlog

**Exit Criteria:**
- [ ] Zero P0/P1 bugs open
- [ ] < 5 P2 bugs open
- [ ] All critical user journeys pass
- [ ] Stakeholder sign-off obtained"""


@tool
def plan_automated_testing(test_framework: str, coverage_target: int) -> str:
    """Plan automated testing strategy.

    Args:
        test_framework: Testing framework being used
        coverage_target: Target code coverage percentage
    """
    return f"""**Automated Testing Plan**

**Framework**: {test_framework}
**Coverage Target**: {coverage_target}%

**Test Pyramid:**

**Unit Tests (70% of tests)**
- Framework: Jest + React Testing Library
- Coverage: {coverage_target}% line coverage
- Focus: Business logic, utility functions, components
- Run time: < 5 minutes

**Integration Tests (20% of tests)**
- Framework: Supertest for API, MSW for mocking
- Coverage: All API endpoints
- Focus: Service interactions, database operations
- Run time: < 10 minutes

**E2E Tests (10% of tests)**
- Framework: {test_framework}
- Coverage: Critical user journeys (10 scenarios)
- Focus: Full user workflows, cross-browser
- Run time: < 30 minutes

**CI/CD Integration:**
- Unit tests: Run on every PR
- Integration tests: Run on every PR
- E2E tests: Run on merge to main
- Full suite: Nightly runs

**Test Data Management:**
- Fixtures for consistent test data
- Database seeding scripts
- Test environment isolation
- Data cleanup after tests

**Monitoring & Reporting:**
- Test results in GitHub PR comments
- Coverage reports (Codecov)
- Flaky test detection and quarantine
- Test execution trends dashboard

**Current Status:**
- Unit tests: 450 tests, 87% coverage
- Integration tests: 120 tests
- E2E tests: 25 scenarios
- Estimated: 95% ready for launch"""


@tool
def plan_performance_testing(load_profile: str, sla_targets: str) -> str:
    """Plan performance and load testing.

    Args:
        load_profile: Expected load profile
        sla_targets: Performance SLA targets
    """
    return f"""**Performance Testing Plan**

**Load Profile**: {load_profile}
**SLA Targets**: {sla_targets}

**Test Scenarios:**

**1. Baseline Test**
- Users: 100 concurrent
- Duration: 10 minutes
- Purpose: Establish performance baseline
- Metrics: Response time, throughput, error rate

**2. Load Test**
- Users: 1,000 concurrent (expected peak)
- Duration: 30 minutes
- Purpose: Validate system handles expected load
- Ramp-up: 100 users/minute

**3. Stress Test**
- Users: 5,000 concurrent (5x expected)
- Duration: 15 minutes
- Purpose: Find breaking points
- Identify bottlenecks

**4. Soak Test**
- Users: 500 concurrent
- Duration: 4 hours
- Purpose: Memory leaks, resource exhaustion
- Monitor: Memory, connections, disk

**5. Spike Test**
- Users: 0 → 2,000 → 0 in 5 minutes
- Purpose: Test auto-scaling
- Validate graceful degradation

**Performance Targets:**
- API Response Time: P50 < 100ms, P99 < 500ms
- Page Load Time: < 3 seconds
- Time to Interactive: < 5 seconds
- Error Rate: < 0.1%
- Throughput: 1,000 requests/second

**Tools:**
- Load testing: k6
- APM: DataDog
- Profiling: Node.js built-in profiler

**Bottleneck Analysis:**
- Database queries (N+1, missing indexes)
- Memory allocation
- External API calls
- Network latency

**Results Summary:**
- Current P99: 180ms (Target: 500ms) ✓
- Current throughput: 1,200 rps ✓
- Current error rate: 0.02% ✓
- STATUS: Performance targets MET"""


def create_qa_team():
    """Create the QA team subgraph."""
    model = get_model()

    def manual_tester(state: TeamState) -> dict:
        """Manual QA tester node."""
        result = plan_manual_testing.invoke({
            "features": "core product features, user workflows",
            "test_types": "exploratory, functional, UAT"
        })
        return {"specialist_outputs": [f"**MANUAL QA TESTER:**\n{result}"]}

    def automation_engineer(state: TeamState) -> dict:
        """Test automation engineer node."""
        result = plan_automated_testing.invoke({
            "test_framework": "Playwright",
            "coverage_target": 85
        })
        return {"specialist_outputs": [f"**AUTOMATION ENGINEER:**\n{result}"]}

    def performance_engineer(state: TeamState) -> dict:
        """Performance test engineer node."""
        result = plan_performance_testing.invoke({
            "load_profile": "1,000 concurrent users, 10,000 daily active",
            "sla_targets": "P99 < 500ms, 99.9% uptime"
        })
        return {"specialist_outputs": [f"**PERFORMANCE ENGINEER:**\n{result}"]}

    def qa_lead(state: TeamState) -> dict:
        """QA team lead synthesizes specialist outputs."""
        specialist_work = "\n\n".join(state["specialist_outputs"])

        synthesis = f"""**QA TEAM SUMMARY**
=====================

The QA team has completed planning for the following areas:

{specialist_work}

**TEAM RECOMMENDATIONS:**
1. Begin automation framework setup in Week 1
2. Manual test case design in parallel with development
3. Performance baseline testing in Week 4
4. Full regression and UAT in Weeks 5-6

**QUALITY GATES:**
- Code coverage: ≥ 85%
- Zero P0/P1 bugs
- Performance SLAs met
- Accessibility compliant

**LAUNCH READINESS ASSESSMENT:**
Based on current progress and plans:
- Automated testing: 95% ready
- Manual testing: Plans complete, execution pending
- Performance testing: Baseline established

**RECOMMENDATION:** PROCEED with launch preparation
**CONFIDENCE LEVEL:** HIGH"""

        return {"team_output": synthesis}

    # Build the QA team subgraph
    workflow = StateGraph(TeamState)

    workflow.add_node("manual", manual_tester)
    workflow.add_node("automation", automation_engineer)
    workflow.add_node("performance", performance_engineer)
    workflow.add_node("lead", qa_lead)

    workflow.add_edge(START, "manual")
    workflow.add_edge(START, "automation")
    workflow.add_edge(START, "performance")
    workflow.add_edge("manual", "lead")
    workflow.add_edge("automation", "lead")
    workflow.add_edge("performance", "lead")
    workflow.add_edge("lead", END)

    return workflow.compile()


# ============================================
# Top-Level Launch Supervisor
# ============================================

def create_launch_supervisor():
    """Create the top-level launch coordinator."""
    model = get_model()

    # Compile team subgraphs
    marketing_team = create_marketing_team()
    engineering_team = create_engineering_team()
    qa_team = create_qa_team()

    def gather_requirements(state: LaunchState) -> dict:
        """Gather and validate launch requirements."""
        return {
            "messages": [AIMessage(content=f"Initiating product launch planning for {state['product_name']}...")]
        }

    def coordinate_marketing(state: LaunchState) -> dict:
        """Coordinate with marketing team."""
        result = marketing_team.invoke({
            "messages": [],
            "task": f"{state['product_name']}: {state['requirements']}",
            "team_output": "",
            "specialist_outputs": []
        })
        return {"marketing_output": result["team_output"]}

    def coordinate_engineering(state: LaunchState) -> dict:
        """Coordinate with engineering team."""
        result = engineering_team.invoke({
            "messages": [],
            "task": f"{state['product_name']}: {state['requirements']}",
            "team_output": "",
            "specialist_outputs": []
        })
        return {"engineering_output": result["team_output"]}

    def coordinate_qa(state: LaunchState) -> dict:
        """Coordinate with QA team."""
        result = qa_team.invoke({
            "messages": [],
            "task": f"{state['product_name']}: {state['requirements']}",
            "team_output": "",
            "specialist_outputs": []
        })
        return {"qa_output": result["team_output"]}

    def synthesize_launch_plan(state: LaunchState) -> dict:
        """Synthesize final launch plan from all teams."""
        final_plan = f"""
{'='*80}
PRODUCT LAUNCH PLAN: {state['product_name']}
Launch Date: {state['launch_date']}
{'='*80}

{state['marketing_output']}

{'='*80}

{state['engineering_output']}

{'='*80}

{state['qa_output']}

{'='*80}
EXECUTIVE SUMMARY
{'='*80}

**Launch Readiness Score: 92/100**

**Key Milestones:**
- Week 1-2: Infrastructure + Content creation
- Week 3-4: Feature development + Marketing campaigns
- Week 5-6: Testing + Final polish
- Launch Day: Coordinated release

**Cross-Team Dependencies:**
1. Marketing needs product screenshots from Engineering (Week 3)
2. QA needs stable build from Engineering (Week 4)
3. All teams sync daily during Week 6

**Risk Summary:**
- Engineering: Medium (third-party integrations)
- Marketing: Low (content pipeline established)
- QA: Low (frameworks ready)

**Budget Summary:**
- Marketing: $5,000 (paid media)
- Engineering: $3,800/month (infrastructure)
- QA: $0 (existing tools)

**RECOMMENDATION:** Proceed with launch as planned
**NEXT STEPS:** Schedule kick-off meeting with all team leads

{'='*80}
"""
        return {
            "final_plan": final_plan,
            "messages": [AIMessage(content="Launch plan synthesis complete.")]
        }

    # Build the top-level workflow
    workflow = StateGraph(LaunchState)

    workflow.add_node("gather", gather_requirements)
    workflow.add_node("marketing", coordinate_marketing)
    workflow.add_node("engineering", coordinate_engineering)
    workflow.add_node("qa", coordinate_qa)
    workflow.add_node("synthesize", synthesize_launch_plan)

    # Flow: gather → teams in parallel → synthesize
    workflow.add_edge(START, "gather")
    workflow.add_edge("gather", "marketing")
    workflow.add_edge("gather", "engineering")
    workflow.add_edge("gather", "qa")
    workflow.add_edge("marketing", "synthesize")
    workflow.add_edge("engineering", "synthesize")
    workflow.add_edge("qa", "synthesize")
    workflow.add_edge("synthesize", END)

    return workflow.compile()


# ============================================
# Example Usage
# ============================================

if __name__ == "__main__":
    print("=" * 80)
    print("HIERARCHICAL TEAMS PATTERN: Product Launch Coordinator")
    print("=" * 80)
    print("\nArchitecture:")
    print("  Launch Supervisor (Top-Level)")
    print("    │")
    print("    ├── Marketing Team (Subgraph)")
    print("    │     ├── Content Specialist")
    print("    │     ├── SEO Specialist")
    print("    │     ├── Social Media Specialist")
    print("    │     └── Marketing Lead (synthesizes)")
    print("    │")
    print("    ├── Engineering Team (Subgraph)")
    print("    │     ├── Backend Developer")
    print("    │     ├── Frontend Developer")
    print("    │     ├── DevOps Engineer")
    print("    │     └── Engineering Lead (synthesizes)")
    print("    │")
    print("    └── QA Team (Subgraph)")
    print("          ├── Manual QA Tester")
    print("          ├── Automation Engineer")
    print("          ├── Performance Engineer")
    print("          └── QA Lead (synthesizes)")
    print("\nKey Feature: NESTED SUBGRAPHS")
    print("  - Each team operates as independent workflow")
    print("  - Team leads synthesize specialist work")
    print("  - Top supervisor coordinates across teams")
    print("  - Results bubble up through hierarchy")
    print("=" * 80)

    # Create the launch coordinator
    coordinator = create_launch_supervisor()

    # Example launch request
    initial_state = {
        "messages": [],
        "product_name": "TaskFlow Pro",
        "launch_date": "March 15, 2025",
        "requirements": "B2B productivity tool for remote teams, target SMB market, "
                       "key features: task management, time tracking, team collaboration",
        "marketing_output": "",
        "engineering_output": "",
        "qa_output": "",
        "final_plan": ""
    }

    print("\n" + "=" * 80)
    print(f"LAUNCHING PRODUCT: {initial_state['product_name']}")
    print(f"TARGET DATE: {initial_state['launch_date']}")
    print("-" * 80)
    print(f"Requirements: {initial_state['requirements']}")
    print("=" * 80)

    print("\nCoordinating with all teams...")
    print("(This involves 3 team subgraphs, each with 3 specialists + 1 lead)")
    print("-" * 80)

    result = coordinator.invoke(initial_state)

    print(result["final_plan"])

    print("\n" + "=" * 80)
    print("Benefits of Hierarchical Teams Pattern:")
    print("  1. SCALABILITY - Handle 9+ specialists without overwhelming supervisor")
    print("  2. MODULARITY - Teams can be developed/tested independently")
    print("  3. ENCAPSULATION - Team-specific logic stays within team subgraph")
    print("  4. PARALLELIZATION - Teams work concurrently at multiple levels")
    print("  5. REUSABILITY - Team subgraphs can be reused across projects")
    print("=" * 80)
