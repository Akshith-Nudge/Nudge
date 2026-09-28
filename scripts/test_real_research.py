import asyncio

from agent.runner.search_researcher import SearchResearcher
from agent.runner.orchestrator import ResearchOrchestrator
from agent.tools.bootstrap import create_tool_registry


async def main() -> None:
    registry = create_tool_registry()

    browser = registry.get("browser")

    try:
        searcher = SearchResearcher(registry)
        orchestrator = ResearchOrchestrator(registry)

        query = "protein bars India products"

        print(f"\nSearching: {query}\n")

        discovery = await searcher.discover(
            query=query,
            max_urls=3,
        )

        print("SEARCH RESULTS")
        print("=" * 60)

        for result in discovery["results"][:5]:
            print(
                f"\nTitle: {result.get('title')}"
                f"\nURL: {result.get('url')}"
                f"\nSnippet: {result.get('snippet')}"
            )

        print("\nSELECTED URLS")
        print("=" * 60)

        for url in discovery["selected_urls"]:
            print(url)

        if not discovery["selected_urls"]:
            print("\nNo URLs found.")
            return

        url = discovery["selected_urls"][0]

        print("\nRESEARCHING")
        print("=" * 60)
        print(url)

        result = await orchestrator.research_page(
            url=url,
            schema={
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
                            },
                            "required": [
                                "name",
                            ],
                            "additionalProperties": False,
                        },
                    }
                },
                "required": [
                    "products",
                ],
                "additionalProperties": False,
            },
            instructions=(
                "Extract products mentioned on the page. "
                "Only extract products actually supported by "
                "the page content. Do not invent products or prices."
            ),
        )

        print("\nEXTRACTED DATA")
        print("=" * 60)
        print(result["extraction"]["data"])

    finally:
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())