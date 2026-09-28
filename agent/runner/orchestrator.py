from typing import Any

from agent.tools.registry import ToolRegistry


class ResearchOrchestrator:

    def __init__(
        self,
        tools: ToolRegistry,
    ) -> None:

        self.tools = tools

    async def search_web(
        self,
        query: str,
    ) -> dict[str, Any]:

        tool = self.tools.get(
            "web_search"
        )

        return await tool.execute(
            query=query,
        )

    async def browse(
        self,
        url: str,
    ) -> dict[str, Any]:

        tool = self.tools.get(
            "browser"
        )

        return await tool.execute(
            action="navigate",
            url=url,
        )

    async def get_page_text(
        self,
    ) -> dict[str, Any]:

        tool = self.tools.get(
            "browser"
        )

        return await tool.execute(
            action="get_text"
        )

    async def extract(
        self,
        content: str,
        schema: dict[str, Any],
        instructions: str | None = None,
    ) -> dict[str, Any]:

        tool = self.tools.get(
            "extract_structured_data"
        )

        return await tool.execute(
            content=content,
            schema=schema,
            instructions=instructions,
        )

    async def research_page(
        self,
        url: str,
        schema: dict[str, Any],
        instructions: str | None = None,
    ) -> dict[str, Any]:

        navigation = await self.browse(
            url
        )

        if navigation["status"] != "success":
            raise RuntimeError(
                f"Failed to navigate to {url}"
            )

        browser = self.tools.get("browser")
        try:
            page_content = await browser.execute(action="get_content")
        except (KeyError, ValueError):
            page_content = {"status": "failed"}
        page_text = page_content
        if page_content.get("status") != "success":
            page_text = await self.get_page_text()

        if page_text["status"] != "success":
            raise RuntimeError(
                f"Failed to obtain content from {url}"
            )

        content = page_text.get("content") or page_text.get("text", "")

        if not content.strip():
            raise RuntimeError(
                f"Page contains no extractable content: {url}"
            )

        extraction = await self.extract(
            content=content,
            schema=schema,
            instructions=instructions,
        )

        if extraction["status"] != "success":

            raise RuntimeError(
                "Structured extraction failed: "
                f"{extraction.get('error', 'unknown error')}"
            )

        return {
            "url": url,
            "navigation": navigation,
            "page_content_type": page_text.get(
                "content_type"
            ),
            "extraction": extraction,
        }