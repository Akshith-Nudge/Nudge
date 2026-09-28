import pytest

from agent.providers.base import AIProvider
from agent.tools.extract import ExtractionTool


class FakeAIProvider(AIProvider):
    async def generate(
        self,
        prompt: str,
        instructions: str | None = None,
    ) -> str:
        return "test"

    async def extract_structured(
        self,
        content: str,
        schema: dict,
        instructions: str | None = None,
    ) -> dict:
        return {
            "products": [
                {
                    "name": "Test Protein Bar",
                    "brand": "Test Brand",
                    "price": 99,
                    "mrp": 120,
                    "in_stock": True,
                }
            ]
        }


@pytest.mark.asyncio
async def test_extraction_tool():
    provider = FakeAIProvider()
    tool = ExtractionTool(provider)

    result = await tool.execute(
        content="Test Protein Bar - ₹99",
        schema={
            "type": "object",
            "properties": {
                "products": {
                    "type": "array",
                }
            },
        },
    )

    assert result["status"] == "success"
    assert len(result["data"]["products"]) == 1
    assert result["data"]["products"][0]["name"] == "Test Protein Bar"