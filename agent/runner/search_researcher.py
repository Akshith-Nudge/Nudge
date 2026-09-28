from typing import Any
from urllib.parse import urlparse

from agent.tools.registry import ToolRegistry


class SearchResearcher:
    def __init__(
        self,
        tools: ToolRegistry,
    ) -> None:
        self.tools = tools

    async def search(
        self,
        query: str,
    ) -> list[dict[str, str]]:
        tool = self.tools.get("web_search")

        result = await tool.execute(
            query=query,
        )

        if result.get("status") != "success":
            raise RuntimeError(
                f"Web search failed for query: {query}"
            )

        results = result.get("results", [])

        if not isinstance(results, list):
            raise RuntimeError(
                "Web search returned invalid results."
            )

        return [
            item
            for item in results
            if isinstance(item, dict)
            and item.get("url")
            and self._is_valid_research_url(item["url"])
        ]

    @staticmethod
    def _is_valid_research_url(url: str) -> bool:
        """
        Reject search-engine tracking, advertising and redirect URLs.

        The research agent should only send actual destination
        websites to the browser.
        """

        try:
            parsed = urlparse(url)

            if parsed.scheme not in {"http", "https"}:
                return False

            if not parsed.netloc:
                return False

            hostname = parsed.hostname

            if hostname is None:
                return False

            hostname = hostname.lower()

            blocked_hosts = {
                "duckduckgo.com",
                "www.duckduckgo.com",
                "bing.com",
                "www.bing.com",
                "google.com",
                "www.google.com",
            }

            if hostname in blocked_hosts:
                return False

            return True

        except ValueError:
            return False

    @classmethod
    def select_urls(
        cls,
        results: list[dict[str, str]],
        max_urls: int = 5,
        allowed_domains: tuple[str, ...] = (),
    ) -> list[str]:
        urls: list[str] = []

        for result in results:
            url = result.get("url")

            if not url:
                continue

            if not cls._is_valid_research_url(url):
                continue

            if allowed_domains:
                hostname = (urlparse(url).hostname or "").lower()
                if not any(
                    hostname == domain or hostname.endswith(f".{domain}")
                    for domain in allowed_domains
                ):
                    continue

            if url in urls:
                continue

            urls.append(url)

            if len(urls) >= max_urls:
                break

        return urls

    async def discover(
        self,
        query: str,
        max_urls: int = 5,
        allowed_domains: tuple[str, ...] = (),
    ) -> dict[str, Any]:
        results = await self.search(query)

        urls = self.select_urls(
            results,
            max_urls=max_urls,
            allowed_domains=allowed_domains,
        )

        return {
            "query": query,
            "results": results,
            "selected_urls": urls,
        }