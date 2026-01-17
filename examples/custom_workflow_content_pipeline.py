"""
Custom Workflows Pattern: AI-Powered Content Pipeline
=====================================================
A custom workflow for content creation with research, writing, and review stages.
Uses StateGraph with nodes, conditional edges, and loops for iterative improvement.

This pattern is best when:
- You need full control over the workflow logic
- The workflow has complex branching and looping
- You want to implement custom state management
- Standard patterns don't fit your use case
"""

from typing import Literal
from langgraph.graph import StateGraph, START, END

# Import from the agentic_patterns package
from agentic_patterns.core import get_model
from agentic_patterns.state.content import ContentState, CONTENT_CONFIGS


# Initialize model
model = get_model()


# ============================================
# Pipeline Node Functions
# ============================================

def research_topic(state: ContentState) -> ContentState:
    """Research the topic and gather information."""
    config = CONTENT_CONFIGS.get(state['content_type'], CONTENT_CONFIGS['blog'])

    prompt = f"""You are a content researcher. Research the following topic thoroughly.

Topic: {state['topic']}
Content Type: {state['content_type']}
Target Audience: {state['target_audience']}
Tone: {state['tone']}
Keywords to include: {', '.join(state.get('keywords', []))}

Provide research notes including:
1. Key points and facts about the topic (5-7 points)
2. Statistics or data that could be referenced
3. Common questions the audience might have
4. Potential angles or hooks for the content
5. Competitor content insights (what works, what's missing)
{"6. SEO considerations and related keywords" if config['seo_required'] else ""}

Format your research in a structured way that will help the content writer."""

    result = model.invoke(prompt)

    return {
        "research_notes": result.content,
        "status": "outlining"
    }


def create_outline(state: ContentState) -> ContentState:
    """Create a content outline based on research."""
    config = CONTENT_CONFIGS.get(state['content_type'], CONTENT_CONFIGS['blog'])

    prompt = f"""You are a content strategist. Create a detailed outline for the content.

Topic: {state['topic']}
Content Type: {state['content_type']}
Target Audience: {state['target_audience']}
Tone: {state['tone']}
Structure guideline: {config['structure']}
Word count target: {config['min_words']}-{config['max_words']} words

Research Notes:
{state['research_notes']}

Create an outline that includes:
1. A compelling title/headline
2. Section headers with brief descriptions
3. Key points for each section
4. Where to incorporate keywords: {', '.join(state.get('keywords', []))}
5. Call-to-action placement

Make the outline detailed enough for a writer to follow."""

    result = model.invoke(prompt)

    return {
        "outline": result.content,
        "status": "drafting"
    }


def write_draft(state: ContentState) -> ContentState:
    """Write the content draft based on research and outline."""
    config = CONTENT_CONFIGS.get(state['content_type'], CONTENT_CONFIGS['blog'])

    # Build revision context if this is a revision
    revision_context = ""
    if state.get('review_feedback') and state.get('revision_count', 0) > 0:
        revision_context = f"""

IMPORTANT - This is revision #{state['revision_count']}. Address this feedback:
{state['review_feedback']}

Focus on improving the specific areas mentioned while maintaining what works."""

    prompt = f"""You are an expert content writer. Write the full content based on the outline and research.

Topic: {state['topic']}
Content Type: {state['content_type']}
Target Audience: {state['target_audience']}
Tone: {state['tone']}
Word count: {config['min_words']}-{config['max_words']} words
Structure: {config['structure']}

Research Notes:
{state['research_notes']}

Outline:
{state['outline']}

Keywords to naturally incorporate: {', '.join(state.get('keywords', []))}
{revision_context}

Write engaging, well-structured content that:
1. Follows the outline structure
2. Uses the research effectively
3. Maintains the specified tone throughout
4. Naturally incorporates keywords
5. Includes a clear call-to-action
6. Is optimized for the target audience

Write the complete {state['content_type']} content now:"""

    result = model.invoke(prompt)
    content = result.content

    # Calculate word count
    word_count = len(content.split())

    return {
        "draft": content,
        "word_count": word_count,
        "status": "reviewing"
    }


def review_content(state: ContentState) -> ContentState:
    """Review the content for quality and provide scores and feedback."""
    config = CONTENT_CONFIGS.get(state['content_type'], CONTENT_CONFIGS['blog'])

    prompt = f"""You are a senior content editor. Review this {state['content_type']} thoroughly.

Content to Review:
{state['draft']}

Evaluation Criteria:
1. Clarity (1-10): Is the content clear and easy to understand?
2. Engagement (1-10): Is it compelling and engaging for {state['target_audience']}?
3. Accuracy (1-10): Are the facts and claims accurate?
4. Tone (1-10): Does it match the {state['tone']} tone requirement?
5. Structure (1-10): Does it follow proper {state['content_type']} structure?
6. Keywords (1-10): Are keywords ({', '.join(state.get('keywords', []))}) naturally incorporated?
7. CTA (1-10): Is the call-to-action clear and compelling?
{"8. SEO (1-10): Is it optimized for search engines?" if config['seo_required'] else ""}

Word count: {state['word_count']} (target: {config['min_words']}-{config['max_words']})

Provide your review in this exact format:
SCORES:
- Clarity: X/10
- Engagement: X/10
- Accuracy: X/10
- Tone: X/10
- Structure: X/10
- Keywords: X/10
- CTA: X/10
{"- SEO: X/10" if config['seo_required'] else ""}
- Overall: X/10

VERDICT: APPROVED or NEEDS_REVISION

FEEDBACK:
[Specific, actionable feedback for improvement. If APPROVED, still note minor suggestions.]"""

    result = model.invoke(prompt)
    review = result.content

    # Parse scores from review
    scores = {}
    try:
        for line in review.split('\n'):
            if '/10' in line and ':' in line:
                key = line.split(':')[0].strip('- ').lower()
                score = int(line.split(':')[1].strip().split('/')[0])
                scores[key] = score
    except:
        scores = {"overall": 5}  # Default if parsing fails

    # Determine verdict
    verdict = "approved" if "VERDICT: APPROVED" in review.upper() else "needs_revision"

    # Calculate SEO score (if applicable)
    seo_score = scores.get('seo', 0) / 10.0 if config['seo_required'] else 1.0

    return {
        "review_feedback": review,
        "quality_scores": scores,
        "seo_score": seo_score,
        "revision_count": state.get("revision_count", 0) + 1,
        "status": verdict
    }


def finalize_content(state: ContentState) -> ContentState:
    """Finalize the approved content with any minor polish."""
    config = CONTENT_CONFIGS.get(state['content_type'], CONTENT_CONFIGS['blog'])

    # Quick final polish
    prompt = f"""Make any final minor improvements to this content. Fix any typos, improve flow slightly,
but don't change the substance. Keep it within {config['min_words']}-{config['max_words']} words.

Content:
{state['draft']}

Return the polished final version:"""

    result = model.invoke(prompt)

    return {
        "final_content": result.content,
        "status": "completed"
    }


def handle_rejection(state: ContentState) -> ContentState:
    """Handle content that couldn't meet quality standards after max revisions."""
    return {
        "status": "rejected",
        "final_content": f"""Content could not meet quality standards after {state['revision_count']} revisions.

Last draft:
{state['draft']}

Final feedback:
{state['review_feedback']}

Recommendation: Consider manual editing or restarting with different parameters."""
    }


# ============================================
# Routing Functions
# ============================================

def route_after_review(state: ContentState) -> Literal["finalize", "revise", "reject"]:
    """Determine next step based on review outcome."""
    # Check if approved
    if state["status"] == "approved":
        return "finalize"

    # Check revision limit
    max_revisions = 3
    if state.get("revision_count", 0) >= max_revisions:
        return "reject"

    # Check if overall score is very low (no point in more revisions)
    overall_score = state.get("quality_scores", {}).get("overall", 5)
    if overall_score <= 3 and state.get("revision_count", 0) >= 2:
        return "reject"

    return "revise"


# ============================================
# Build Workflow Graph
# ============================================

workflow = StateGraph(ContentState)

# Add nodes
workflow.add_node("research", research_topic)
workflow.add_node("outline", create_outline)
workflow.add_node("write", write_draft)
workflow.add_node("review", review_content)
workflow.add_node("finalize", finalize_content)
workflow.add_node("reject", handle_rejection)

# Add edges - linear flow with conditional loop
workflow.add_edge(START, "research")
workflow.add_edge("research", "outline")
workflow.add_edge("outline", "write")
workflow.add_edge("write", "review")

# Conditional routing after review
workflow.add_conditional_edges(
    "review",
    route_after_review,
    {
        "finalize": "finalize",
        "revise": "write",  # Loop back to writing with feedback
        "reject": "reject"
    }
)

workflow.add_edge("finalize", END)
workflow.add_edge("reject", END)

# Compile
app = workflow.compile()


# ============================================
# Helper Functions
# ============================================

def create_content(
    topic: str,
    content_type: str = "blog",
    target_audience: str = "general audience",
    tone: str = "professional",
    keywords: list[str] = None
) -> dict:
    """Create content using the pipeline.

    Args:
        topic: The topic to write about
        content_type: Type of content (blog, social_twitter, social_linkedin, email, press_release)
        target_audience: Who the content is for
        tone: Writing tone (professional, casual, technical, friendly)
        keywords: SEO keywords to incorporate

    Returns:
        Dictionary with final content and metadata
    """
    if keywords is None:
        keywords = []

    result = app.invoke({
        "topic": topic,
        "content_type": content_type,
        "target_audience": target_audience,
        "tone": tone,
        "keywords": keywords,
        "revision_count": 0
    })

    return {
        "status": result["status"],
        "content": result.get("final_content", result.get("draft", "")),
        "word_count": result.get("word_count", 0),
        "quality_scores": result.get("quality_scores", {}),
        "revisions": result.get("revision_count", 0),
        "seo_score": result.get("seo_score", 0)
    }


def visualize_workflow():
    """Print a text visualization of the workflow."""
    print("""
Content Pipeline Workflow:

    [START]
       │
       ▼
  ┌─────────┐
  │ Research │
  └────┬────┘
       │
       ▼
  ┌─────────┐
  │ Outline │
  └────┬────┘
       │
       ▼
  ┌─────────┐◄─────────────┐
  │  Write  │              │
  └────┬────┘              │
       │                   │
       ▼                   │
  ┌─────────┐     ┌────────┴───────┐
  │ Review  │────▶│ Needs Revision │
  └────┬────┘     └────────────────┘
       │
       ├──────────────┐
       │              │
       ▼              ▼
  ┌─────────┐    ┌─────────┐
  │ Approve │    │ Reject  │
  └────┬────┘    └────┬────┘
       │              │
       ▼              │
  ┌─────────┐         │
  │Finalize │         │
  └────┬────┘         │
       │              │
       ▼              ▼
     [END]          [END]
""")


# ============================================
# Example Usage
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("CUSTOM WORKFLOWS PATTERN: AI Content Pipeline")
    print("=" * 60)

    visualize_workflow()

    # Example 1: Blog post
    print("\n" + "=" * 60)
    print("Example 1: Creating a Blog Post")
    print("=" * 60)

    result = create_content(
        topic="The Future of AI in Healthcare: Opportunities and Challenges",
        content_type="blog",
        target_audience="Healthcare executives and decision-makers",
        tone="professional",
        keywords=["AI healthcare", "medical AI", "healthcare technology", "digital health"]
    )

    print(f"\nStatus: {result['status']}")
    print(f"Word Count: {result['word_count']}")
    print(f"Revisions: {result['revisions']}")
    print(f"Quality Scores: {result['quality_scores']}")
    print(f"SEO Score: {result['seo_score']:.1%}")
    print(f"\nContent Preview (first 500 chars):\n{result['content'][:500]}...")

    # Example 2: LinkedIn post
    print("\n" + "=" * 60)
    print("Example 2: Creating a LinkedIn Post")
    print("=" * 60)

    result = create_content(
        topic="5 Lessons I Learned From Failing My First Startup",
        content_type="social_linkedin",
        target_audience="Entrepreneurs and startup founders",
        tone="friendly",
        keywords=["startup lessons", "entrepreneurship", "failure to success"]
    )

    print(f"\nStatus: {result['status']}")
    print(f"Word Count: {result['word_count']}")
    print(f"Revisions: {result['revisions']}")
    print(f"\nFull Content:\n{result['content']}")

    # Example 3: Marketing email
    print("\n" + "=" * 60)
    print("Example 3: Creating a Marketing Email")
    print("=" * 60)

    result = create_content(
        topic="Launch Announcement: New AI-Powered Analytics Dashboard",
        content_type="email",
        target_audience="Existing SaaS customers",
        tone="friendly",
        keywords=["new feature", "analytics", "AI-powered"]
    )

    print(f"\nStatus: {result['status']}")
    print(f"Word Count: {result['word_count']}")
    print(f"Revisions: {result['revisions']}")
    print(f"\nFull Content:\n{result['content']}")
