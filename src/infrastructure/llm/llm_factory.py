"""
LLM factory for creating language model instances
"""

from typing import Optional
import os

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama

from src.config import settings
from src.config.logging import get_logger

logger = get_logger(__name__)


def create_llm(
    provider: Optional[str] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    streaming: bool = False
):
    """
    Create LLM instance based on configuration
    
    Args:
        provider: LLM provider (openai, anthropic, gemini, ollama, groq)
        model: Model name
        temperature: Temperature setting
        streaming: Enable streaming
        
    Returns:
        LLM instance
    """
    provider = provider or settings.llm_provider
    temperature = temperature if temperature is not None else settings.openai_temperature
    
    logger.info(f"Creating LLM: provider={provider}, streaming={streaming}")
    
    try:
        if provider == "openai":
            return _create_openai(model, temperature, streaming)
        elif provider == "anthropic":
            return _create_anthropic(model, temperature, streaming)
        elif provider == "gemini":
            return _create_gemini(model, temperature, streaming)
        elif provider == "ollama":
            return _create_ollama(model, temperature, streaming)
        elif provider == "groq":
            return _create_groq(model, temperature, streaming)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
    except Exception as e:
        logger.error(f"Failed to create LLM: {e}")
        raise


def _create_openai(
    model: Optional[str],
    temperature: float,
    streaming: bool
) -> ChatOpenAI:
    """Create OpenAI LLM"""
    model = model or settings.openai_model
    api_key = settings.openai_api_key
    
    if not api_key:
        raise ValueError("OpenAI API key not configured")
    
    return ChatOpenAI(
        model=model,
        api_key=api_key.get_secret_value(),
        temperature=temperature,
        streaming=streaming,
        max_tokens=settings.openai_max_tokens
    )


def _create_anthropic(
    model: Optional[str],
    temperature: float,
    streaming: bool
) -> ChatAnthropic:
    """Create Anthropic Claude LLM"""
    model = model or settings.anthropic_model
    api_key = settings.anthropic_api_key
    
    if not api_key:
        raise ValueError("Anthropic API key not configured")
    
    return ChatAnthropic(
        model=model,
        api_key=api_key.get_secret_value(),
        temperature=temperature,
        streaming=streaming
    )


def _create_gemini(
    model: Optional[str],
    temperature: float,
    streaming: bool
) -> ChatGoogleGenerativeAI:
    """Create Google Gemini LLM"""
    model = model or settings.gemini_model
    api_key = settings.google_api_key
    
    if not api_key:
        raise ValueError("Google API key not configured")
    
    return ChatGoogleGenerativeAI(
        model=model,
        google_api_key=api_key.get_secret_value(),
        temperature=temperature,
        streaming=streaming
    )


def _create_ollama(
    model: Optional[str],
    temperature: float,
    streaming: bool
) -> ChatOllama:
    """Create Ollama LLM (local)"""
    model = model or settings.ollama_model
    
    return ChatOllama(
        model=model,
        base_url=settings.ollama_base_url,
        temperature=temperature,
        streaming=streaming
    )


def _create_groq(
    model: Optional[str],
    temperature: float,
    streaming: bool
) -> ChatOpenAI:
    """Create Groq LLM (OpenAI-compatible API)"""
    model = model or settings.groq_model
    api_key = settings.groq_api_key
    
    if not api_key:
        raise ValueError("Groq API key not configured")
    
    return ChatOpenAI(
        model=model,
        api_key=api_key.get_secret_value(),
        base_url="https://api.groq.com/openai/v1",
        temperature=temperature,
        streaming=streaming
    )

