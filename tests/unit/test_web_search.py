from agent.tools.web_search import WebSearchTool


def test_decode_duckduckgo_redirect_url():
    tool = WebSearchTool()

    raw_url = (
        "//duckduckgo.com/l/"
        "?uddg=https%3A%2F%2Fwww.example.com%2Fproducts"
    )

    parser = tool._parse_results(
        f"""
        <a class="result__a" href="{raw_url}">
            Example Product
        </a>
        <a class="result__snippet">
            Example product description
        </a>
        """
    )

    assert len(parser) == 1

    assert parser[0]["url"] == (
        "https://www.example.com/products"
    )


def test_parse_normal_url():
    tool = WebSearchTool()

    html = """
    <a class="result__a" href="https://example.com/product">
        Example Product
    </a>
    <a class="result__snippet">
        Example product description
    </a>
    """

    results = tool._parse_results(html)

    assert len(results) == 1
    assert results[0]["title"] == "Example Product"
    assert results[0]["url"] == "https://example.com/product"
    assert results[0]["snippet"] == "Example product description"