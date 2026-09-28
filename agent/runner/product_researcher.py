from typing import Any
from urllib.parse import urlparse

from agent.runner.orchestrator import ResearchOrchestrator
from agent.runner.search_researcher import SearchResearcher
from agent.tools.registry import ToolRegistry
from config.marketplaces import resolve_marketplaces
from scraping.extraction.parser import ExtractedProduct, ProductParser

PRODUCT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "products": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                    },
                    "brand": {
                        "type": "string",
                    },
                    "price": {
                        "type": "number",
                    },
                    "mrp": {
                        "type": "number",
                    },
                    "in_stock": {
                        "type": "boolean",
                    },
                    "rank": {
                        "type": "integer",
                    },
                    "product_url": {
                        "type": "string",
                    },
                },
                "required": ["name"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["products"],
    "additionalProperties": False,
}


class ProductResearcher:
    """
    Performs generic web-based marketplace research.

    There are deliberately no marketplace-specific adapters.

    Marketplaces are simply research targets passed to the
    generic search and browser tools.
    """

    def __init__(
        self,
        tools: ToolRegistry,
    ) -> None:

        self.tools = tools

        self.searcher = SearchResearcher(
            tools
        )

        self.orchestrator = ResearchOrchestrator(
            tools
        )

        self.parser = ProductParser()

    async def research(
        self,
        company: str,
        keyword: str,
        max_urls_per_marketplace: int = 2,
        marketplaces: list[str] | None = None,
        regions: list[str] | None = None,
    ) -> dict[str, Any]:

        observations: list[ExtractedProduct] = []

        failures: list[dict[str, str]] = []

        sources: list[str] = []

        marketplace_results: dict[
            str,
            dict[str, Any],
        ] = {}

        targets = resolve_marketplaces(marketplaces)
        if not targets:
            raise ValueError("No supported marketplaces were requested.")

        requested_regions = [region.strip() for region in (regions or []) if region.strip()]

        for marketplace in targets:

            marketplace_sources: list[str] = []

            for domain in marketplace.search_domains:

                query = (
                    f"{company} {keyword} "
                    f"site:{domain}"
                )

                try:

                    discovery = await self.searcher.discover(
                        query=query,
                        max_urls=max_urls_per_marketplace,
                        allowed_domains=marketplace.search_domains,
                    )

                    selected_urls = discovery[
                        "selected_urls"
                    ]

                    for url in selected_urls:

                        if url not in sources:
                            sources.append(url)

                        if url not in marketplace_sources:
                            marketplace_sources.append(url)

                        try:

                            result = (
                                await self.orchestrator.research_page(
                                    url=url,
                                    schema=PRODUCT_SCHEMA,
                                    instructions=(
                                        f"You are researching "
                                        f"'{company}' products "
                                        f"for the keyword "
                                        f"'{keyword}'.\n\n"

                                        f"This page was discovered "
                                        f"for the marketplace "
                                        f"'{marketplace.name}'.\n\n"

                                        "Extract only products "
                                        "actually present on the "
                                        "page.\n"

                                        "Do not invent products, "
                                        "prices, brands, rankings, "
                                        "availability or URLs.\n"

                                        "If a field is not explicitly "
                                        "supported by the page, "
                                        "omit it.\n"

                                        "Return only products relevant "
                                        "to the requested keyword."
                                    ),
                                )
                            )

                            data = result[
                                "extraction"
                            ]["data"]

                            products = self.parser.parse(
                                data
                            )

                            for product in products:

                                product.raw_data[
                                    "source_url"
                                ] = url

                                product.raw_data[
                                    "marketplace"
                                ] = marketplace.name
                                product.raw_data[
                                    "regions"
                                ] = requested_regions
                                product.marketplace = marketplace.name
                                product.source_url = url
                                product.region = (
                                    requested_regions[0]
                                    if len(requested_regions) == 1
                                    else None
                                )

                                if (
                                    product.brand is None
                                    and self._is_company_domain(
                                        url=url,
                                        company=company,
                                    )
                                ):
                                    product.brand = company

                                observations.append(
                                    product
                                )

                        except Exception as exc:

                            failures.append(
                                {
                                    "marketplace": (
                                        marketplace.name
                                    ),
                                    "url": url,
                                    "error": str(exc),
                                }
                            )

                            print(
                                "Research failed for "
                                f"{url}: {exc}"
                            )

                except Exception as exc:

                    failures.append(
                        {
                            "marketplace": (
                                marketplace.name
                            ),
                            "url": domain,
                            "error": str(exc),
                        }
                    )

                    print(
                        "Marketplace discovery failed "
                        f"for {marketplace.name}: {exc}"
                    )

            marketplace_results[
                marketplace.name
            ] = {
                "sources": marketplace_sources,
                "source_count": len(
                    marketplace_sources
                ),
            }

        return {
            "company": company,
            "keyword": keyword,
            "observations": observations,
            "sources": sources,
            "marketplaces": marketplace_results,
            "failures": failures,
            "successful_sources": (
                len(sources) - len({
                    failure["url"]
                    for failure in failures
                    if failure["url"] in sources
                })
            ),
            "failed_sources": len(failures),
            "discovery": {
                "selected_urls": sources,
                "marketplaces": marketplace_results,
            },
            "regions": requested_regions,
        }

    @staticmethod
    def _is_company_domain(
        url: str,
        company: str,
    ) -> bool:

        try:

            hostname = urlparse(url).hostname

            if not hostname:
                return False

            hostname = hostname.lower()

            company_tokens = (
                company.lower()
                .replace("-", " ")
                .replace("_", " ")
                .split()
            )

            if not company_tokens:
                return False

            hostname_without_www = (
                hostname.removeprefix("www.")
            )

            return all(
                token in hostname_without_www
                for token in company_tokens
            )

        except ValueError:
            return False