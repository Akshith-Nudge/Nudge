import asyncio

from agent.runner.market_research import MarketResearchPipeline
from agent.tools.bootstrap import create_tool_registry


async def main() -> None:
    registry = create_tool_registry()

    browser = registry.get("browser")

    pipeline = MarketResearchPipeline(
        tools=registry,
    )

    try:
        company = "Yoga Bar"
        keyword = "protein bars"

        print("\nMARKET INTELLIGENCE")
        print("=" * 60)

        print(f"Company: {company}")
        print(f"Keyword: {keyword}")

        result = await pipeline.run(
            company=company,
            keyword=keyword,
            max_urls=3,
        )

        print("\nSOURCES")
        print("=" * 60)

        for source in result["sources"]:
            print(source)

        print("\nOBSERVATIONS")
        print("=" * 60)

        for product in result["observations"]:
            print(
                f"{product.name} | "
                f"{product.brand} | "
                f"{product.price}"
            )

        print("\nNORMALIZED PRODUCTS")
        print("=" * 60)

        for product in result["normalized_products"]:
            print(
                f"{product.canonical_name} | "
                f"brand={product.brand} | "
                f"observations="
                f"{len(product.observations)}"
            )

        sov = result["sov"]

        print("\nSHARE OF VOICE")
        print("=" * 60)

        print(
            f"Company: {sov.company}"
        )

        print(
            f"Company observations: "
            f"{sov.company_observations}"
        )

        print(
            f"Total observations: "
            f"{sov.total_observations}"
        )

        print(
            f"SOV: "
            f"{sov.share_of_voice}%"
        )

    finally:
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())