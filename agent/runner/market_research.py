from dataclasses import asdict
from typing import Any

from agent.runner.product_researcher import ProductResearcher
from agent.tools.registry import ToolRegistry
from analytics.sov.calculator import SOVCalculator
from normalization.products.normalizer import ProductNormalizer


class MarketResearchPipeline:
    """
    End-to-end market intelligence pipeline.

    Research:
        Generic web search + browser + AI extraction.

    Normalization:
        Deterministic.

    Analytics:
        Deterministic.

    The LLM does not calculate market metrics.
    """

    def __init__(
        self,
        tools: ToolRegistry,
    ) -> None:

        self.product_researcher = (
            ProductResearcher(tools)
        )

        self.sov_calculator = SOVCalculator()

    async def run(
        self,
        company: str,
        keyword: str,
        max_urls: int = 2,
        marketplaces: list[str] | None = None,
        regions: list[str] | None = None,
    ) -> dict[str, Any]:

        research = (
            await self.product_researcher.research(
                company=company,
                keyword=keyword,
                max_urls_per_marketplace=max_urls,
                marketplaces=marketplaces,
                regions=regions,
            )
        )

        observations = research[
            "observations"
        ]

        normalizer = ProductNormalizer(
            canonical_company=company,
        )

        normalized_products = (
            normalizer.normalize(
                observations
            )
        )

        sov = self.sov_calculator.calculate(
            company=company,
            products=normalized_products,
        )

        final_params = [
            asdict(product)
            for product in observations
        ]
        availability = {
            "observed": sum(
                product.in_stock is not None
                for product in observations
            ),
            "in_stock": sum(
                product.in_stock is True
                for product in observations
            ),
            "out_of_stock": sum(
                product.in_stock is False
                for product in observations
            ),
        }
        availability["rate_percent"] = round(
            availability["in_stock"]
            / availability["observed"]
            * 100,
            2,
        ) if availability["observed"] else None

        return {
            "company": company,
            "keyword": keyword,
            "sources": research[
                "sources"
            ],
            "marketplaces": research[
                "marketplaces"
            ],
            "successful_sources": research[
                "successful_sources"
            ],
            "failed_sources": research[
                "failed_sources"
            ],
            "failures": research[
                "failures"
            ],
            "observations": observations,
            "normalized_products": (
                normalized_products
            ),
            "sov": sov,
            "final_params": final_params,
            "availability": availability,
        }