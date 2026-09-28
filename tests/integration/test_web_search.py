import pytest

from agent.tools.web_search import WebSearchTool


@pytest.mark.asyncio
async def test_web_search():

    tool = WebSearchTool()

    result = await tool.execute(
        query="Instamart",
    )

    assert result["status"] == "success"
    assert result["query"] == "Instamart"
    assert result["result_count"] > 0

    first_result = result["results"][0]

    assert first_result["title"]
    assert first_result["url"]