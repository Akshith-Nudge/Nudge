from html.parser import HTMLParser
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

import httpx

from agent.tools.base import AgentTool


class WebSearchTool(AgentTool):

    name = "web_search"

    description = (
        "Search the public web for products, brands, marketplaces, "
        "competitors, pricing, availability, and other market intelligence."
    )

    SEARCH_URL = (
        "https://html.duckduckgo.com/html/"
    )

    def __init__(
        self,
        timeout: float = 20.0,
    ) -> None:

        self.timeout = timeout

    async def execute(
        self,
        query: str,
        **kwargs: Any,
    ) -> dict[str, Any]:

        query = query.strip()

        if not query:
            raise ValueError(
                "Search query cannot be empty."
            )

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/153.0.0.0 Safari/537.36"
            ),
            "Accept": (
                "text/html,application/xhtml+xml,"
                "application/xml;q=0.9,*/*;q=0.8"
            ),
            "Accept-Language": "en-IN,en;q=0.9",
        }

        async with httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
            headers=headers,
        ) as client:

            response = await client.get(
                self.SEARCH_URL,
                params={"q": query},
            )

            response.raise_for_status()

        results = self._parse_results(
            response.text
        )

        return {
            "status": "success",
            "query": query,
            "results": results,
            "result_count": len(results),
        }

    def _parse_results(
        self,
        html: str,
    ) -> list[dict[str, str]]:

        class SearchResultParser(
            HTMLParser
        ):

            def __init__(self) -> None:

                super().__init__()

                self.results: list[
                    dict[str, str]
                ] = []

                self.current: (
                    dict[str, str] | None
                ) = None

                self.capture_title = False
                self.capture_snippet = False

            def handle_starttag(
                self,
                tag: str,
                attrs: list[
                    tuple[str, str | None]
                ],
            ) -> None:

                attributes = dict(attrs)

                classes = (
                    attributes.get(
                        "class",
                        "",
                    )
                    or ""
                )

                # Search result title.
                if (
                    tag == "a"
                    and "result__a" in classes
                ):

                    self._finalize_current()
                    raw_url = (
                        attributes.get(
                            "href",
                            "",
                        )
                        or ""
                    )

                    self.current = {
                        "title": "",
                        "url": (
                            self._decode_result_url(
                                raw_url
                            )
                        ),
                        "snippet": "",
                    }

                    self.capture_title = True

                    return

                # Search result snippet.
                if (
                    tag == "a"
                    and "result__snippet"
                    in classes
                    and self.current is not None
                ):

                    self.capture_snippet = True

                    return

                # Some DDG responses use a div/span
                # around the snippet.
                if (
                    self.current is not None
                    and (
                        "result__snippet"
                        in classes
                    )
                ):

                    self.capture_snippet = True

            def handle_data(
                self,
                data: str,
            ) -> None:

                if self.current is None:
                    return

                text = data.strip()

                if not text:
                    return

                if self.capture_title:

                    self.current["title"] += (
                        text + " "
                    )

                elif self.capture_snippet:

                    self.current["snippet"] += (
                        text + " "
                    )

            def handle_endtag(
                self,
                tag: str,
            ) -> None:

                if tag == "a":
                    self.capture_title = False
                    self.capture_snippet = False

                elif self.capture_snippet:
                    self.capture_snippet = False

            def _finalize_current(
                self,
            ) -> None:

                if self.current is None:
                    return

                result = {
                    "title": self.current[
                        "title"
                    ].strip(),
                    "url": self.current[
                        "url"
                    ].strip(),
                    "snippet": self.current[
                        "snippet"
                    ].strip(),
                }

                if result["url"]:

                    self.results.append(
                        result
                    )

                self.current = None

            def close(self) -> None:
                super().close()
                self._finalize_current()

            @staticmethod
            def _decode_result_url(
                raw_url: str,
            ) -> str:

                raw_url = raw_url.strip()

                if not raw_url:
                    return ""

                # DDG redirect URL.
                if (
                    "duckduckgo.com/l/"
                    in raw_url
                ):

                    parsed = urlparse(
                        
                            "https:" + raw_url
                            if raw_url.startswith(
                                "//"
                            )
                            else raw_url
                        
                    )

                    query = parse_qs(
                        parsed.query
                    )

                    destination = query.get(
                        "uddg"
                    )

                    if destination:

                        return unquote(
                            destination[0]
                        )

                if raw_url.startswith(
                    "//"
                ):

                    return (
                        "https:" + raw_url
                    )

                return raw_url

        parser = SearchResultParser()

        parser.feed(html)
        parser.close()

        return [
            result
            for result in parser.results
            if result.get("url")
        ]