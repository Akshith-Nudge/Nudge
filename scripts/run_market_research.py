import argparse
import asyncio
import json
from dataclasses import asdict

from agent.runner.market_research import MarketResearchPipeline
from agent.tools.bootstrap import create_tool_registry


async def run(args: argparse.Namespace) -> None:
    registry = create_tool_registry()
    pipeline = MarketResearchPipeline(registry)
    browser = registry.get("browser")
    try:
        result = await pipeline.run(
            company=args.company,
            keyword=args.keyword,
            max_urls=args.max_urls,
            marketplaces=args.marketplace,
            regions=args.region,
        )
        result["observations"] = [
            asdict(observation)
            for observation in result["observations"]
        ]
        result["normalized_products"] = [
            {
                "canonical_name": product.canonical_name,
                "brand": product.brand,
                "observation_count": len(product.observations),
            }
            for product in result["normalized_products"]
        ]
        result["sov"] = asdict(result["sov"])
        print(json.dumps(result, indent=2, default=str))
    finally:
        await browser.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scrape marketplace product observations and output JSON."
    )
    parser.add_argument("--company", required=True)
    parser.add_argument("--keyword", required=True)
    parser.add_argument("--marketplace", action="append")
    parser.add_argument("--region", action="append")
    parser.add_argument("--max-urls", type=int, default=2)
    asyncio.run(run(parser.parse_args()))


if __name__ == "__main__":
    main()
