import os
from typing import Any
from urllib.parse import urlparse

import httpx

from agent.tools.base import AgentTool


class WebSearchTool(AgentTool):

    name = "web_search"

    description = (
        "Search the public web for products, brands, marketplaces, "
        "competitors, pricing, availability, and other market intelligence."
    )

    DEFAULT_SEARXNG_URL = "https://search.mectov.my.id"

    def __init__(
        self,
        timeout: float = 20.0,
    ) -> None:
        self.timeout = timeout
        self.search_url = os.getenv(
            "SEARXNG_URL",
            self.DEFAULT_SEARXNG_URL,
        ).strip().rstrip("/")

        parsed_url = urlparse(self.search_url)
        if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
            raise ValueError(
                "SEARXNG_URL must be a valid HTTP or HTTPS base URL."
            )

    async def execute(
        self,
        query: str,
        **kwargs: Any,
    ) -> dict[str, Any]:

        query = query.strip()

        if not query:
            raise ValueError("Search query cannot be empty.")

        headers = {
            "User-Agent": "NudgeMarketResearch/1.0",
            "Accept": "application/json",
        }

        async with httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
            headers=headers,
        ) as client:
            response = await client.get(
                f"{self.search_url}/search",
                params={
                    "q": query,
                    "format": "json",
                    "language": "en",
                    "pageno": 1,
                },
            )

            if response.status_code in {403, 406}:
                raise RuntimeError(
                    "The configured SearXNG instance rejected JSON search "
                    "requests. Set SEARXNG_URL to another instance that "
                    "allows the /search?format=json endpoint."
                )

            response.raise_for_status()

            try:
                payload = response.json()
            except ValueError as exc:
                raise RuntimeError(
                    "SearXNG returned a non-JSON response. The instance may "
                    "have JSON output disabled; choose another SEARXNG_URL."
                ) from exc

        raw_results = payload.get("results", [])
        results: list[dict[str, str]] = []

        for item in raw_results:
            if not isinstance(item, dict):
                continue

            url = str(item.get("url") or "").strip()
            if not url:
                continue

            results.append(
                {
                    "title": str(item.get("title") or "").strip(),
                    "url": url,
                    "snippet": str(
                        item.get("content") or item.get("snippet") or ""
                    ).strip(),
                }
            )

        return {
            "status": "success",
            "query": query,
            "results": results,
            "result_count": len(results),
        }
