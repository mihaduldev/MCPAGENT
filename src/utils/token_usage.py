"""
Token usage and cost calculation utilities
"""

from typing import Optional, Dict, Any
from src.config import settings
from src.config.logging import get_logger

logger = get_logger(__name__)


# OpenAI pricing per 1M tokens (as of 2024)
OPENAI_PRICING = {
    "gpt-4o": {"prompt": 2.50, "completion": 10.00},  # per 1M tokens
    "gpt-4o-mini": {"prompt": 0.15, "completion": 0.60},
    "gpt-4-turbo": {"prompt": 10.00, "completion": 30.00},
    "gpt-4-turbo-preview": {"prompt": 10.00, "completion": 30.00},  # alias
    "gpt-4": {"prompt": 30.00, "completion": 60.00},
    "gpt-3.5-turbo": {"prompt": 0.50, "completion": 1.50},
    "gpt-3.5-turbo-16k": {"prompt": 3.00, "completion": 4.00},
    "default": {"prompt": 1.00, "completion": 2.00},  # fallback
}

# Anthropic pricing per 1M tokens
ANTHROPIC_PRICING = {
    "claude-3-5-sonnet-20241022": {"prompt": 3.00, "completion": 15.00},
    "claude-3-5-sonnet": {"prompt": 3.00, "completion": 15.00},
    "claude-3-opus-20240229": {"prompt": 15.00, "completion": 75.00},
    "claude-3-sonnet-20240229": {"prompt": 3.00, "completion": 15.00},
    "claude-3-haiku-20240307": {"prompt": 0.25, "completion": 1.25},
    "default": {"prompt": 3.00, "completion": 15.00},
}

# Groq pricing (very cheap, often free tier)
GROQ_PRICING = {
    "default": {"prompt": 0.00, "completion": 0.00},  # Free tier
}


def extract_token_usage(response: Any) -> Optional[Dict[str, int]]:
    """
    Extract token usage from LLM response
    
    Args:
        response: LLM response object (from LangChain)
        
    Returns:
        Dict with prompt_tokens, completion_tokens, total_tokens, or None
    """
    try:
        # Check for response_metadata (LangChain standard)
        if hasattr(response, 'response_metadata'):
            metadata = response.response_metadata
            if metadata and 'token_usage' in metadata:
                usage = metadata['token_usage']
                return {
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", usage.get("prompt_tokens", 0) + usage.get("completion_tokens", 0))
                }
        
        # Check for usage_metadata (alternative format)
        if hasattr(response, 'usage_metadata'):
            usage = response.usage_metadata
            return {
                "prompt_tokens": getattr(usage, 'prompt_tokens', 0),
                "completion_tokens": getattr(usage, 'completion_tokens', 0),
                "total_tokens": getattr(usage, 'total_token_count', 0)
            }
        
        # Check if response has token_usage directly
        if hasattr(response, 'token_usage'):
            usage = response.token_usage
            if isinstance(usage, dict):
                return {
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0)
                }
        
        # Check for usage in response object directly
        if hasattr(response, 'usage'):
            usage = response.usage
            if hasattr(usage, 'prompt_tokens'):
                return {
                    "prompt_tokens": usage.prompt_tokens,
                    "completion_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens
                }
    
    except Exception as e:
        logger.debug(f"Could not extract token usage: {e}")
    
    return None


def calculate_cost(
    prompt_tokens: int,
    completion_tokens: int,
    model: Optional[str] = None,
    provider: Optional[str] = None
) -> Optional[float]:
    """
    Calculate cost in USD based on token usage and model pricing
    
    Args:
        prompt_tokens: Number of prompt tokens
        completion_tokens: Number of completion tokens
        model: Model name
        provider: LLM provider (openai, anthropic, groq, etc.)
        
    Returns:
        Cost in USD or None if cannot calculate
    """
    if prompt_tokens == 0 and completion_tokens == 0:
        return None
    
    provider = provider or settings.llm_provider
    model = model or getattr(settings, f"{provider}_model", None)
    
    try:
        # Get pricing based on provider
        if provider == "openai":
            pricing = OPENAI_PRICING.get(model, OPENAI_PRICING["default"])
        elif provider == "anthropic":
            pricing = ANTHROPIC_PRICING.get(model, ANTHROPIC_PRICING["default"])
        elif provider == "groq":
            pricing = GROQ_PRICING.get(model, GROQ_PRICING["default"])
        else:
            # Unknown provider - use default pricing
            pricing = {"prompt": 1.00, "completion": 2.00}
        
        # Calculate cost (pricing is per 1M tokens)
        prompt_cost = (prompt_tokens / 1_000_000) * pricing["prompt"]
        completion_cost = (completion_tokens / 1_000_000) * pricing["completion"]
        total_cost = prompt_cost + completion_cost
        
        return round(total_cost, 6)  # Round to 6 decimal places
    
    except Exception as e:
        logger.warning(f"Could not calculate cost: {e}")
        return None


def get_token_usage_and_cost(
    response: Any,
    model: Optional[str] = None,
    provider: Optional[str] = None
) -> tuple[Optional[int], Optional[float]]:
    """
    Extract token usage and calculate cost from LLM response
    
    Args:
        response: LLM response object
        model: Model name
        provider: LLM provider
        
    Returns:
        Tuple of (total_tokens, cost_usd)
    """
    usage = extract_token_usage(response)
    
    if usage:
        total_tokens = usage.get("total_tokens", 0)
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        
        cost = calculate_cost(prompt_tokens, completion_tokens, model, provider)
        
        return total_tokens, cost
    
    return None, None

