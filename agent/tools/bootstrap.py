from agent.tools.browser import BrowserTool
from agent.tools.extract import ExtractionTool
from agent.tools.registry import ToolRegistry
from agent.tools.web_search import WebSearchTool
from config.settings import settings


def create_tool_registry() -> ToolRegistry:
    registry = ToolRegistry()

    registry.register(WebSearchTool())
    registry.register(BrowserTool())

    ai_provider = None
    if settings.groq_api_key:
        from agent.providers.groq_provider import GroqProvider

        ai_provider = GroqProvider()

    registry.register(
        ExtractionTool(
            provider=ai_provider,
        )
    )

    return registry