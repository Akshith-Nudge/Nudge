import os
import re
from typing import Any
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

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
    BING_SEARCH_URL = "https://www.bing.com/search"

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

        allowed_domains = self._extract_site_domains(query)
        headers = {
            "User-Agent": "NudgeMarketResearch/1.0",
            "Accept": "text/html,application/xhtml+xml,application/json",
        }

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
                    response.raise_for_status()
                    payload = response.json()
                    results = self._normalize_results(payload.get("results", []))
                    results = self._filter_results(results, allowed_domains)

                    if results:
                        return self._success(query, results, search_url)

                except (httpx.HTTPError, ValueError):
                    continue

            try:
                response = await client.get(
                    self.BING_SEARCH_URL,
                    params={"q": query, "count": 10, "setlang": "en-IN"},
                    headers={
                        "User-Agent": (
                            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 Chrome/154.0 Safari/537.36"
                        ),
                        "Accept": "text/html,application/xhtml+xml",
                    },
                )
                response.raise_for_status()

                soup = BeautifulSoup(response.text, "html.parser")
                results = []

                for item in soup.select("li.b_algo"):
                    anchor = item.select_one("h2 a")
                    if anchor is None:
                        continue

                    url = str(anchor.get("href") or "").strip()
                    title = anchor.get_text(" ", strip=True)
                    snippet_node = item.select_one(".b_caption p")
                    snippet = (
                        snippet_node.get_text(" ", strip=True)
                        if snippet_node
                        else ""
                    )

                    if url:
                        results.append(
                            {
                                "title": title,
                                "url": url,
                                "snippet": snippet,
                            }
                        )

                results = self._filter_results(results, allowed_domains)

                if results:
                    return self._success(query, results, "bing")

            except (httpx.HTTPError, ValueError):
                pass

        raise RuntimeError(
            f"No relevant search results found for query: {query}"
        )

    @staticmethod
    def _extract_site_domains(query: str) -> tuple[str, ...]:
        return tuple(
            dict.fromkeys(
                match.lower().removeprefix("www.")
                for match in re.findall(
                    r"(?:^|\\s)site:([a-zA-Z0-9.-]+)",
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
        filtered = []

        for result in results:
            url = result.get("url", "")
            if not cls._is_valid_research_url(url):
                continue

            if allowed_domains:
                hostname = (urlparse(url).hostname or "").lower().removeprefix("www.")
                if not any(
                    hostname == domain or hostname.endswith(f".{domain}")
                    for domain in allowed_domains
                ):
                    continue

            filtered.append(result)

        return filtered

    @staticmethod
    def _normalize_results(raw_results: Any) -> list[dict[str, str]]:
        results = []

        if not isinstance(raw_results, list):
            return results

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

        return results

    @staticmethod
    def _success(
        query: str,
        results: list[dict[str, str]],
        provider: str,
    ) -> dict[str, Any]:
        return {
            "status": "success",
            "query": query,
            "results": results,
            "result_count": len(results),
            "provider": provider,
        }

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
