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

    DEFAULT_SEARXNG_URLS = (
        "https://search.inetol.net",
        "https://baresearch.org",
        "https://search.mectov.my.id",
    )

    def __init__(self, timeout: float = 20.0) -> None:
        self.timeout = timeout
        configured = os.getenv("SEARXNG_URL", "").strip().rstrip("/")
        self.search_urls = (
            (configured,) if configured else self.DEFAULT_SEARXNG_URLS
        )

        for search_url in self.search_urls:
            parsed_url = urlparse(search_url)
            if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
                raise ValueError(
                    "Every SEARXNG_URL must be a valid HTTP or HTTPS base URL."
                )

    async def execute(self, query: str, **kwargs: Any) -> dict[str, Any]:
        query = query.strip()
        if not query:
            raise ValueError("Search query cannot be empty.")

        headers = {
            "User-Agent": "NudgeMarketResearch/1.0",
            "Accept": "application/json",
        }

        last_error: Exception | None = None

        async with httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
            headers=headers,
        ) as client:
            for search_url in self.search_urls:
                try:
                    response = await client.get(
                        f"{search_url}/search",
                        params={
                            "q": query,
                            "format": "json",
                            "language": "en",
                            "pageno": 1,
                        },
                    )

                    if response.status_code in {403, 406}:
                        raise RuntimeError(
                            f"SearXNG instance rejected JSON search: {search_url}"
                        )

                    response.raise_for_status()

                    try:
                        payload = response.json()
                    except ValueError as exc:
                        raise RuntimeError(
                            f"SearXNG returned non-JSON response: {search_url}"
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
                                    item.get("content")
                                    or item.get("snippet")
                                    or ""
                                ).strip(),
                            }
                        )

                    if results:
                        return {
                            "status": "success",
                            "query": query,
                            "results": results,
                            "result_count": len(results),
                            "provider": search_url,
                        }

                    last_error = RuntimeError(
                        f"SearXNG returned no results: {search_url}"
                    )

                except (httpx.HTTPError, RuntimeError, ValueError) as exc:
                    last_error = exc

        raise RuntimeError(
            f"All configured SearXNG instances failed for query: {query}"
        ) from last_error
