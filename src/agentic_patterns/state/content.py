"""
State definitions for the custom workflow content pipeline pattern.

Defines:
- ContentState: TypedDict for the content creation pipeline
- CONTENT_CONFIGS: Configuration for different content types
"""

from typing_extensions import TypedDict


class ContentState(TypedDict):
    """State for the content creation pipeline."""
    # Input parameters
    topic: str
    content_type: str  # "blog", "social_twitter", "social_linkedin", "email", "press_release"
    target_audience: str
    tone: str  # "professional", "casual", "technical", "friendly"
    keywords: list[str]

    # Pipeline state
    research_notes: str
    outline: str
    draft: str
    review_feedback: str
    revision_count: int
    quality_scores: dict  # Scores from review
    final_content: str
    status: str  # "researching", "outlining", "drafting", "reviewing", "approved", "rejected"

    # Metadata
    word_count: int
    seo_score: float


CONTENT_CONFIGS = {
    "blog": {
        "min_words": 800,
        "max_words": 1500,
        "structure": "Introduction, 3-5 sections with headers, conclusion with CTA",
        "seo_required": True
    },
    "social_twitter": {
        "min_words": 20,
        "max_words": 50,
        "structure": "Hook, value, CTA - under 280 characters",
        "seo_required": False
    },
    "social_linkedin": {
        "min_words": 100,
        "max_words": 400,
        "structure": "Hook, story/insight, takeaway, CTA with line breaks for readability",
        "seo_required": False
    },
    "email": {
        "min_words": 150,
        "max_words": 500,
        "structure": "Subject line, greeting, value proposition, CTA, signature",
        "seo_required": False
    },
    "press_release": {
        "min_words": 300,
        "max_words": 600,
        "structure": "Headline, dateline, lead paragraph, body, boilerplate, contact info",
        "seo_required": True
    }
}
