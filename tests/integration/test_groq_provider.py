import pytest

from agent.providers.groq_provider import GroqProvider


@pytest.mark.asyncio
async def test_groq_connection():
    provider = GroqProvider()

    result = await provider.generate(
        prompt="Reply with exactly: GROQ_CONNECTION_OK",
    )

    assert "GROQ_CONNECTION_OK" in result