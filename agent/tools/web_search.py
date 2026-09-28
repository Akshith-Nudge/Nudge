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

    SEARCH_URLS = (
        ("bing-browser", "https://www.bing.com/search?q={query}&setlang=en-IN"),
        ("duckduckgo-browser", "https://html.duckduckgo.com/html/?q={query}&kl=us-en"),
    )

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

        for provider, template in self.SEARCH_URLS:
            url = template.format(query=quote_plus(query))

            try:
                result = await session.navigate(url)
                page = session._require_page()
                results = await self._extract_results(page, provider)
                results = self._filter_results(results, allowed_domains)

                if results:
                    return {
                        "status": "success",
                        "query": query,
                        "results": results,
                        "result_count": len(results),
                        "provider": provider,
                        "search_url": result.get("url", url),
                    }
            except Exception:
                continue

        raise RuntimeError(
            f"No relevant search results found for query: {query}"
        )

    @staticmethod
    async def _extract_results(page: Any, provider: str) -> list[dict[str, str]]:
        results: list[dict[str, str]] = []

        if provider == "bing-browser":
            items = await page.locator("li.b_algo").all()
            for item in items:
                anchor = item.locator("h2 a").first
                if await anchor.count() == 0:
                    continue
                href = await anchor.get_attribute("href")
                if not href:
                    continue
                snippet_node = item.locator(".b_caption p").first
                results.append({
                    "title": (await anchor.inner_text()).strip(),
                    "url": href.strip(),
                    "snippet": (await snippet_node.inner_text()).strip()
                    if await snippet_node.count() else "",
                })
            return results

        for item in await page.locator(".result").all():
            anchor = item.locator("a.result__a").first
            if await anchor.count() == 0:
                continue
            href = await anchor.get_attribute("href")
            if not href:
                continue
            snippet_node = item.locator(".result__snippet").first
            results.append({
                "title": (await anchor.inner_text()).strip(),
                "url": href.strip(),
                "snippet": (await snippet_node.inner_text()).strip()
                if await snippet_node.count() else "",
            })

        return results

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
