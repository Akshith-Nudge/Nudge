from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from playwright.async_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    async_playwright,
)

from config.settings import settings


class BrowserSession:
    def __init__(self) -> None:
        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._page: Page | None = None

    async def start(self) -> None:

        if self._playwright is not None:
            return

        self._playwright = (
            await async_playwright().start()
        )

        self._browser = (
            await self._playwright.chromium.launch(
                headless=settings.browser_headless,
            )
        )

        self._context = (
            await self._browser.new_context(
                viewport={
                    "width": 1440,
                    "height": 900,
                },
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/153.0.0.0 Safari/537.36"
                ),
                locale="en-IN",
                timezone_id="Asia/Kolkata",
            )
        )

        self._page = (
            await self._context.new_page()
        )

        self._page.set_default_timeout(
            settings.browser_timeout_ms
        )

    async def close(self) -> None:

        if self._context is not None:
            await self._context.close()
            self._context = None

        if self._browser is not None:
            await self._browser.close()
            self._browser = None

        if self._playwright is not None:
            await self._playwright.stop()
            self._playwright = None

        self._page = None

    async def navigate(
        self,
        url: str,
    ) -> dict[str, Any]:

        page = self._require_page()

        response = None
        navigation_error: str | None = None

        try:

            response = await page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=settings.browser_timeout_ms,
            )

        except Exception as exc:

            navigation_error = str(exc)

            # Some SPA/e-commerce pages abort the navigation
            # after the document has already started loading.
            #
            # We intentionally continue and inspect the page
            # instead of immediately treating ERR_ABORTED as
            # a total failure.

            if "ERR_ABORTED" not in navigation_error:
                raise

        # Give client-side applications time to render.
        try:
            await page.wait_for_load_state(
                "networkidle",
                timeout=5000,
            )
        except Exception:
            # Network idle is not guaranteed on modern
            # e-commerce applications.
            pass

        # Small rendering grace period.
        await page.wait_for_timeout(1500)

        return {
            "url": page.url,
            "title": await page.title(),
            "status_code": (
                response.status
                if response
                else None
            ),
            "navigation_error": navigation_error,
        }

    async def get_page_content(self) -> str:

        page = self._require_page()

        return await page.content()

    async def get_visible_text(self) -> str:

        page = self._require_page()

        return await page.locator(
            "body"
        ).inner_text()

    async def screenshot(
        self,
        path: str,
    ) -> None:

        page = self._require_page()

        await page.screenshot(
            path=path,
            full_page=True,
        )

    def _require_page(self) -> Page:

        if self._page is None:
            raise RuntimeError(
                "Browser session has not been started."
            )

        return self._page


@asynccontextmanager
async def browser_session() -> AsyncIterator[
    BrowserSession
]:

    session = BrowserSession()

    await session.start()

    try:
        yield session

    finally:
        await session.close()