from typing import Any

from agent.tools.base import AgentTool
from scraping.browser.session import BrowserSession


class BrowserTool(AgentTool):
    name = "browser"

    description = (
        "Generic browser tool for navigating websites, "
        "reading rendered page content, extracting visible "
        "text, retrieving HTML and capturing screenshots."
    )

    def __init__(self) -> None:
        self.session: BrowserSession | None = None

    async def start(self) -> None:

        if self.session is None:

            self.session = BrowserSession()

            await self.session.start()

    async def close(self) -> None:

        if self.session is not None:

            await self.session.close()

            self.session = None

    async def execute(
        self,
        action: str,
        **kwargs: Any,
    ) -> dict[str, Any]:

        if self.session is None:
            await self.start()

        if action == "navigate":
            return await self._navigate(
                kwargs["url"]
            )

        if action == "get_content":
            return await self._get_content()

        if action == "get_text":
            return await self._get_text()

        if action == "screenshot":
            return await self._screenshot(
                kwargs["path"]
            )

        raise ValueError(
            f"Unsupported browser action: {action}"
        )

    async def _navigate(
        self,
        url: str,
    ) -> dict[str, Any]:

        assert self.session is not None

        result = await self.session.navigate(
            url
        )

        return {
            "status": "success",
            "action": "navigate",
            **result,
        }

    async def _get_content(
        self,
    ) -> dict[str, Any]:

        assert self.session is not None

        content = (
            await self.session.get_page_content()
        )

        return {
            "status": "success",
            "action": "get_content",
            "content": content,
            "content_length": len(content),
        }

    async def _get_text(
        self,
    ) -> dict[str, Any]:

        assert self.session is not None

        text = ""

        try:
            text = (
                await self.session.get_visible_text()
            )
        except Exception:
            text = ""

        text = text.strip()

        if text:

            return {
                "status": "success",
                "action": "get_text",
                "text": text,
                "content_type": "visible_text",
                "content_length": len(text),
            }

        # E-commerce SPAs can have useful structured data
        # even when body.inner_text() is empty.
        html = (
            await self.session.get_page_content()
        )

        if not html.strip():

            return {
                "status": "failed",
                "action": "get_text",
                "text": "",
                "content_type": "empty",
                "content_length": 0,
            }

        return {
            "status": "success",
            "action": "get_text",
            "text": html,
            "content_type": "html",
            "content_length": len(html),
        }

    async def _screenshot(
        self,
        path: str,
    ) -> dict[str, Any]:

        assert self.session is not None

        await self.session.screenshot(
            path
        )

        return {
            "status": "success",
            "action": "screenshot",
            "path": path,
        }