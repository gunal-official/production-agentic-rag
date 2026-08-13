import asyncio

from openai import (
    APIConnectionError,
    APITimeoutError,
    AsyncOpenAI,
    RateLimitError,
)

from app.core.config import settings
from app.llm.base import LLMProvider


class GroqProvider(LLMProvider):
    def __init__(self) -> None:
        if not settings.groq_api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not configured"
            )

        self.client = AsyncOpenAI(
            api_key=settings.groq_api_key,
            base_url="https://api.groq.com/openai/v1",
            timeout=20.0,
        )

    async def generate(
        self,
        prompt: str,
    ) -> str:
        max_attempts = 3

        for attempt in range(
            1,
            max_attempts + 1,
        ):
            try:
                response = await self.client.chat.completions.create(
                    model=settings.groq_model,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    temperature=0.0,
                )

                content = response.choices[0].message.content

                if not content:
                    raise RuntimeError(
                        "Groq returned an empty response"
                    )

                return content.strip()

            except RateLimitError:
                if attempt == max_attempts:
                    raise

                await asyncio.sleep(
                    2 ** (attempt - 1)
                )

            except (
                APIConnectionError,
                APITimeoutError,
            ):
                if attempt == max_attempts:
                    raise

                await asyncio.sleep(
                    float(attempt)
                )

        raise RuntimeError(
            "Groq request failed after retries"
        )