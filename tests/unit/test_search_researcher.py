import pytest

from agent.runner.search_researcher import SearchResearcher
from agent.tools.base import AgentTool
from agent.tools.registry import ToolRegistry


class FakeSearchTool(AgentTool):
    name = "web_search"
    description = "Fake search"

    async def execute(self, query: str, **kwargs):
        return {
            "status": "success",
            "query": query,
            "results": [
                {
                    "title": "Product One",
                    "url": "https://example.com/one",
                    "snippet": "Product one",
                },
                {
                    "title": "Product Two",
                    "url": "https://example.com/two",
                    "snippet": "Product two",
                },
                {
                    "title": "Product One Duplicate",
                    "url": "https://example.com/one",
                    "snippet": "Duplicate",
                },
            ],
            "result_count": 3,
        }


@pytest.mark.asyncio
async def test_search_researcher():
    registry = ToolRegistry()
    registry.register(FakeSearchTool())

    researcher = SearchResearcher(registry)

    result = await researcher.discover(
        query="protein bars",
        max_urls=2,
    )

    assert result["query"] == "protein bars"

    assert result["selected_urls"] == [
        "https://example.com/one",
        "https://example.com/two",
    ]