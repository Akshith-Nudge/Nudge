import pytest

from agent.runner.orchestrator import ResearchOrchestrator
from agent.tools.bootstrap import create_tool_registry


@pytest.mark.asyncio
async def test_real_research_pipeline():
    registry = create_tool_registry()

    browser = registry.get("browser")

    try:
        orchestrator = ResearchOrchestrator(registry)

        result = await orchestrator.research_page(
            url="https://example.com",
            schema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                    },
                    "description": {
                        "type": "string",
                    },
                },
                "required": [
                    "title",
                    "description",
                ],
                "additionalProperties": False,
            },
            instructions=(
                "Extract the title and description of the page. "
                "Only use information present in the supplied content."
            ),
        )

        assert result["navigation"]["status"] == "success"
        assert result["extraction"]["status"] == "success"

        data = result["extraction"]["data"]

        assert isinstance(data["title"], str)
        assert isinstance(data["description"], str)

    finally:
        await browser.close()