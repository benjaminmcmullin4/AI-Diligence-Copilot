import instructor
from anthropic import Anthropic
from pydantic import BaseModel
from core.config import get_settings


def get_llm_client():
    settings = get_settings()
    client = Anthropic(api_key=settings.anthropic_api_key)
    return instructor.from_anthropic(client)


def call_llm(
    response_model: type[BaseModel],
    system: str,
    user: str,
    max_tokens: int | None = None,
) -> BaseModel:
    settings = get_settings()
    client = get_llm_client()
    return client.chat.completions.create(
        model=settings.claude_model,
        max_tokens=max_tokens or settings.max_tokens,
        max_retries=settings.max_retries,
        messages=[{"role": "user", "content": user}],
        system=system,
        response_model=response_model,
    )
