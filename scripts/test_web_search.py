import asyncio

from agent.tools.web_search import WebSearchTool


async def main() -> None:

    tool = WebSearchTool()

    result = await tool.execute(
        query="Yoga Bar protein bars site:swiggy.com"
    )

    print()
    print("SEARCH TEST")
    print("=" * 60)
    print(
        "Results:",
        result["result_count"],
    )

    for index, item in enumerate(
        result["results"],
        start=1,
    ):

        print()
        print(f"[{index}]")
        print(
            "Title:",
            item["title"],
        )
        print(
            "URL:",
            item["url"],
        )
        print(
            "Snippet:",
            item["snippet"],
        )


if __name__ == "__main__":
    asyncio.run(main())