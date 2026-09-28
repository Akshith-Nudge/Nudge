import json
from typing import Any

from groq import AsyncGroq

from agent.providers.base import AIProvider
from config.settings import settings


class GroqProvider(AIProvider):
    def __init__(
        self,
        model: str | None = None,
    ) -> None:
        if not settings.groq_api_key:
            raise RuntimeError("GROQ_API_KEY is not configured.")

        self.model = model or settings.groq_model

        self.client = AsyncGroq(
            api_key=settings.groq_api_key,
        )

    async def generate(
        self,
        prompt: str,
        instructions: str | None = None,
    ) -> str:
        messages: list[dict[str, str]] = []

        if instructions:
            messages.append(
                {
                    "role": "system",
                    "content": instructions,
                }
            )

        messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
        )

        content = response.choices[0].message.content

        if content is None:
            raise RuntimeError("Groq returned an empty response.")

        return content

    async def extract_structured(
        self,
        content: str,
        schema: dict[str, Any],
        instructions: str | None = None,
    ) -> dict[str, Any]:
        schema_text = json.dumps(
            schema,
            indent=2,
        )

        system_prompt = instructions or (
            "You are a structured data extraction system. "
            "Extract only information supported by the supplied content. "
            "Do not invent values. "
            "Return valid JSON matching the requested schema exactly."
        )

        prompt = f"""
Extract structured data from the following content.

Required JSON schema:

{schema_text}

Content:

{content}
"""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0,
            response_format={
                "type": "json_object",
            },
        )

        output = response.choices[0].message.content

        if output is None:
            raise RuntimeError(
                "Groq returned an empty extraction response."
            )

        try:
            return json.loads(output)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"Groq returned invalid JSON: {output}"
            ) from exc