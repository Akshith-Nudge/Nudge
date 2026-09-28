import asyncio

from agent.runner.product_researcher import ProductResearcher
from agent.tools.bootstrap import create_tool_registry


async def main() -> None:
    registry = create_tool_registry()

    browser = registry.get("browser")
    researcher = ProductResearcher(registry)

    try:
        company = "Yoga Bar"
        keyword = "protein bars"

        print("\nPRODUCT RESEARCH")
        print("=" * 60)

        print(f"Company: {company}")
        print(f"Keyword: {keyword}")

        result = await researcher.research(
            company=company,
            keyword=keyword,
            max_urls_per_marketplace=3,
        )

        print("\nSELECTED SOURCES")
        print("=" * 60)

        for url in result["sources"]:
            print(url)

        print("\nPRODUCT OBSERVATIONS")
        print("=" * 60)

        for index, product in enumerate(
            result["observations"],
            start=1,
        ):
            print(f"\nProduct #{index}")
            print(f"Name: {product.name}")
            print(f"Brand: {product.brand}")
            print(f"Price: {product.price}")
            print(f"MRP: {product.mrp}")
            print(f"In stock: {product.in_stock}")
            print(f"Rank: {product.rank}")
            print(f"URL: {product.product_url}")
            print(
                f"Source: "
                f"{product.raw_data.get('source_url')}"
            )

        print("\nTOTAL PRODUCTS")
        print("=" * 60)
        print(len(result["observations"]))

    finally:
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())