import pytest

from agent.tools.browser import BrowserTool


@pytest.mark.asyncio
async def test_browser_tool_navigation():

    tool = BrowserTool()

    try:
        result = await tool.execute(
            action="navigate",
            url="https://example.com",
        )

        assert result["status"] == "success"
        assert result["status_code"] == 200
        assert result["title"] == "Example Domain"

    finally:
        await tool.close()


@pytest.mark.asyncio
async def test_browser_tool_text_extraction():

    tool = BrowserTool()

    try:
        await tool.execute(
            action="navigate",
            url="https://example.com",
        )

        result = await tool.execute(
            action="get_text",
        )

        assert result["status"] == "success"
        assert "Example Domain" in result["text"]

    finally:
        await tool.close()