import re
from typing import Any
from urllib.parse import quote_plus, urlparse

from agent.tools.base import AgentTool
from scraping.browser.session import BrowserSession


class WebSearchTool(AgentTool):
    name = "web_search"

    description = (
        "Search the public web using the Playwright browser for products, brands, "
        "marketplaces, competitors, pricing, availability, and other market intelligence."
    )

    SEARCH_URL = "https://www.bing.com/search"

    def __init__(self, timeout: float = 30.0) -> None:
        self.timeout = timeout
        self.session: BrowserSession | None = None

    async def _start(self) -> BrowserSession:
        if self.session is None:
            self.session = BrowserSession()
            await self.session.start()
        return self.session

    async def close(self) -> None:
        if self.session is not None:
            await self.session.close()
            self.session = None

    async def execute(self, query: str, **kwargs: Any) -> dict[str, Any]:
        query = query.strip()
        if not query:
            raise ValueError("Search query cannot be empty.")

        allowed_domains = self._extract_site_domains(query)
        session = await self._start()

        url = f"{self.SEARCH_URL}?q={quote_plus(query)}&setlang=en-IN"
        result = await session.navigate(url)

        page = session._require_page()

        results: list[dict[str, str]] = []

        for item in await page.locator("li.b_algo").all():
            anchor = item.locator("h2 a").first
            if await anchor.count() == 0:
                continue

            href = await anchor.get_attribute("href")
            title = (await anchor.inner_text()).strip()

            if not href:
                continue

            snippet_node = item.locator(".b_caption p").first
            snippet = (
                (await snippet_node.inner_text()).strip()
                if await snippet_node.count()
                else ""
            )

            results.append(
                {
                    "title": title,
                    "url": href.strip(),
                    "snippet": snippet,
                }
            )

        results = self._filter_results(results, allowed_domains)

        if not results:
            raise RuntimeError(
                f"No relevant search results found for query: {query}"
            )

        return {
            "status": "success",
            "query": query,
            "results": results,
            "result_count": len(results),
            "provider": "bing-browser",
            "search_url": result.get("url", url),
        }

    @staticmethod
    def _extract_site_domains(query: str) -> tuple[str, ...]:
        return tuple(
            dict.fromkeys(
                match.lower().removeprefix("www.")
                for match in re.findall(
                    r"(?:^|\s)site:([a-zA-Z0-9.-]+)",
                    query,
                )
            )
        )

    @classmethod
    def _filter_results(
        cls,
        results: list[dict[str, str]],
        allowed_domains: tuple[str, ...],
    ) -> list[dict[str, str]]:
        filtered: list[dict[str, str]] = []

        for result in results:
            url = result.get("url", "")
            if not cls._is_valid_research_url(url):
                continue

            if allowed_domains:
                hostname = (
                    urlparse(url).hostname or ""
                ).lower().removeprefix("www.")

                if not any(
                    hostname == domain or hostname.endswith(f".{domain}")
                    for domain in allowed_domains
                ):
                    continue

            filtered.append(result)

        return filtered

    @staticmethod
    def _is_valid_research_url(url: str) -> bool:
        try:
            parsed = urlparse(url)

            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                return False

            hostname = (parsed.hostname or "").lower()

            blocked_hosts = {
                "duckduckgo.com",
                "www.duckduckgo.com",
                "bing.com",
                "www.bing.com",
                "google.com",
                "www.google.com",
            }

            return hostname not in blocked_hosts

        except ValueError:
            return False
