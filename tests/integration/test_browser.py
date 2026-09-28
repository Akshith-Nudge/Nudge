import pytest

from scraping.browser.session import browser_session


@pytest.mark.asyncio
async def test_browser_session():

    async with browser_session() as browser:

        result = await browser.navigate(
            "https://example.com"
        )

        assert result["status_code"] == 200
        assert result["title"] == "Example Domain"

        text = await browser.get_visible_text()

        assert "Example Domain" in text