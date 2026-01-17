"""
Model configuration and initialization.

Provides a centralized way to initialize LangChain chat models
with consistent defaults across all patterns.
"""

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

# Load environment variables on module import
load_dotenv()

# Default model configuration
DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_MODEL_PROVIDER = "openai"

# Fallback model for high availability
FALLBACK_MODEL = "gpt-4o"
FALLBACK_MODEL_PROVIDER = "openai"


def get_model(
    model: str = DEFAULT_MODEL,
    model_provider: str = DEFAULT_MODEL_PROVIDER,
    **kwargs
):
    """Initialize a chat model with consistent defaults.

    Args:
        model: Model identifier (default: "gpt-4o-mini")
        model_provider: Provider name (default: "openai")
        **kwargs: Additional arguments passed to init_chat_model

    Returns:
        Initialized chat model instance

    Example:
        >>> model = get_model()  # Uses defaults
        >>> model = get_model("gpt-4o", "openai")  # Custom model
    """
    return init_chat_model(model, model_provider=model_provider, **kwargs)


def get_fallback_model(**kwargs):
    """Get the fallback model for high availability scenarios.

    Returns:
        Initialized fallback chat model instance
    """
    return init_chat_model(
        FALLBACK_MODEL,
        model_provider=FALLBACK_MODEL_PROVIDER,
        **kwargs
    )
