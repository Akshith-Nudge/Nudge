import pytest

from agent.runner.runner import ResearchAgent
from agent.state.models import ResearchRequest
from agent.tools.registry import ToolRegistry


@pytest.mark.asyncio
async def test_agent_creates_research_plan():

    registry = ToolRegistry()

    agent = ResearchAgent(
        tools=registry,
    )

    request = ResearchRequest(
        company="Example Foods",
        keyword="protein bars",
    )

    state = await agent.run(request)

    assert state.status == "completed"

    assert "identify_products" in state.completed_tasks
    assert "search_marketplaces" in state.completed_tasks
    assert "collect_product_observations" in state.completed_tasks
    assert "verify_regions" in state.completed_tasks