import pytest

from agent.runner.orchestrator import ResearchOrchestrator
from agent.tools.base import AgentTool
from agent.tools.registry import ToolRegistry


class FakeWebSearchTool(AgentTool):
    name = "web_search"
    description = "Fake web search"

    async def execute(self, query: str, **kwargs):
        return {
            "status": "success",
            "query": query,
            "results": [
                {
                    "title": "Example Product",
                    "url": "https://example.com/product",
                    "snippet": "Example product page",
                }
            ],
            "result_count": 1,
        }


class FakeBrowserTool(AgentTool):
    name = "browser"
    description = "Fake browser"

    async def execute(self, action: str, **kwargs):
        if action == "navigate":
            return {
                "status": "success",
                "action": "navigate",
                "url": kwargs["url"],
                "title": "Example Product",
                "status_code": 200,
            }

        if action == "get_text":
            return {
                "status": "success",
                "action": "get_text",
                "text": "Example Product ₹99 In Stock",
            }

        raise ValueError(f"Unsupported action: {action}")


class FakeExtractionTool(AgentTool):
    name = "extract_structured_data"
    description = "Fake extraction"

    async def execute(
        self,
        content: str,
        schema: dict,
        instructions=None,
        **kwargs,
    ):
        return {
            "status": "success",
            "data": {
                "products": [
                    {
                        "name": "Example Product",
                        "price": 99,
                        "in_stock": True,
                    }
                ]
            },
            "schema": schema,
            "content_length": len(content),
        }


@pytest.mark.asyncio
async def test_research_page():
    registry = ToolRegistry()

    registry.register(FakeWebSearchTool())
    registry.register(FakeBrowserTool())
    registry.register(FakeExtractionTool())

    orchestrator = ResearchOrchestrator(registry)

    result = await orchestrator.research_page(
        url="https://example.com/product",
        schema={
            "type": "object",
            "properties": {
                "products": {
                    "type": "array",
                }
            },
        },
    )

    assert result["navigation"]["status"] == "success"
    assert result["extraction"]["status"] == "success"
    assert (
        result["extraction"]["data"]["products"][0]["name"]
        == "Example Product"
    )