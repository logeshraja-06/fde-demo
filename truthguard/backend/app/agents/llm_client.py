import logging
from typing import Dict, Any, Optional
from app.config import settings

logger = logging.getLogger("truthguard.llm")


def call_gemini_chat(
    system_prompt: str,
    user_prompt: str,
    temperature: float = 0.1
) -> Optional[str]:
    """
    Calls Google Gemini API using the official google-genai SDK
    configured with GEMINI_API_KEY from server/.env.
    """
    if not settings.GEMINI_API_KEY or len(settings.GEMINI_API_KEY.strip()) < 10:
        return None

    try:
        from google import genai  # type: ignore
        from google.genai import types  # type: ignore

        client = genai.Client(api_key=settings.GEMINI_API_KEY)
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=temperature,
                max_output_tokens=1200,
            ),
        )
        if response and response.text:
            return response.text.strip()
        return None
    except Exception as exc:
        logger.warning(f"Google Gemini API call encountered error ({exc}). Attempting fallback routing.")
        return None


def call_openai_chat(
    system_prompt: str,
    user_prompt: str,
    response_format: Optional[Dict[str, Any]] = None,
    temperature: float = 0.0
) -> Optional[str]:
    """Calls OpenAI chat completion API if configured."""
    if not settings.OPENAI_API_KEY or len(settings.OPENAI_API_KEY.strip()) < 10:
        return None

    try:
        from openai import OpenAI  # type: ignore
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        kwargs = {
            "model": settings.OPENAI_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature
        }
        if response_format:
            kwargs["response_format"] = response_format

        resp = client.chat.completions.create(**kwargs)
        return resp.choices[0].message.content
    except Exception as exc:
        logger.warning(f"OpenAI API call failed ({exc}). Falling back to deterministic agent engine.")
        return None


def call_llm_chat(
    system_prompt: str,
    user_prompt: str,
    response_format: Optional[Dict[str, Any]] = None,
    temperature: float = 0.1
) -> Optional[str]:
    """
    Primary LLM entry point for TruthGuard.
    Prioritizes Google Gemini (configured via server/.env), then OpenAI, then local fallback.
    """
    # 1. Try Google Gemini first
    gemini_resp = call_gemini_chat(system_prompt=system_prompt, user_prompt=user_prompt, temperature=temperature)
    if gemini_resp:
        return gemini_resp

    # 2. Try OpenAI
    openai_resp = call_openai_chat(system_prompt=system_prompt, user_prompt=user_prompt, response_format=response_format, temperature=temperature)
    if openai_resp:
        return openai_resp

    return None
