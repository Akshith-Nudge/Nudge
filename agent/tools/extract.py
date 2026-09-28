import json
import re
from html import unescape
from typing import Any

from agent.providers.base import AIProvider
from agent.tools.base import AgentTool


class ExtractionTool(AgentTool):

    name = "extract_structured_data"

    description = (
        "Extract structured information from rendered web page "
        "content using an AI provider and supplied schema."
    )

    MAX_CONTENT_CHARS = 10000

    def __init__(
        self,
        provider: AIProvider | None = None,
    ) -> None:

        self.provider = provider

    async def execute(
        self,
        content: str,
        schema: dict[str, Any],
        instructions: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:

        if not schema:
            raise ValueError(
                "Extraction schema cannot be empty."
            )

        raw_content = content
        content = self._prepare_content(content)

        if not content:

            return {
                "status": "failed",
                "error": (
                    "Content is empty after "
                    "preprocessing."
                ),
                "data": None,
                "schema": schema,
                "content_length": 0,
            }

        if self.provider is None:
            data = self._extract_without_ai(raw_content, schema)
            if data is None:
                return {
                    "status": "failed",
                    "error": (
                        "No AI provider is configured and the page did not "
                        "contain supported structured product data."
                    ),
                    "data": None,
                    "schema": schema,
                    "content_length": len(content),
                }
            return {
                "status": "success",
                "data": data,
                "schema": schema,
                "content_length": len(content),
                "extraction_method": "structured_data",
            }

        try:

            data = (
                await self.provider.extract_structured(
                    content=content,
                    schema=schema,
                    instructions=instructions,
                )
            )

        except Exception as exc:

            return {
                "status": "failed",
                "error": str(exc),
                "data": None,
                "schema": schema,
                "content_length": len(content),
            }

        return {
            "status": "success",
            "data": data,
            "schema": schema,
            "content_length": len(content),
        }

    @staticmethod
    def _extract_without_ai(
        content: str,
        schema: dict[str, Any],
    ) -> dict[str, Any] | None:
        """Extract Product/ItemList JSON-LD without inventing missing values."""
        properties = schema.get("properties", {})
        if "products" not in properties:
            result: dict[str, Any] = {}
            title = re.search(r"<title[^>]*>(.*?)</title>", content, re.I | re.S)
            if "title" in properties and title:
                result["title"] = " ".join(unescape(title.group(1)).split())
            description = re.search(
                r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']',
                content,
                re.I | re.S,
            )
            if "description" in properties and description:
                result["description"] = unescape(description.group(1)).strip()
            if "description" in properties and "description" not in result:
                body = re.search(r"<body[^>]*>(.*?)</body>", content, re.I | re.S)
                if body:
                    text = re.sub(r"<[^>]+>", " ", body.group(1))
                    text = " ".join(unescape(text).split())
                    if text:
                        result["description"] = text
            return result if all(
                key in result for key in schema.get("required", [])
            ) else None

        products: list[dict[str, Any]] = []
        scripts = re.findall(
            r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
            content,
            flags=re.IGNORECASE | re.DOTALL,
        )
        for raw_script in scripts:
            try:
                payload = json.loads(unescape(raw_script.strip()))
            except json.JSONDecodeError:
                continue
            candidates = payload if isinstance(payload, list) else [payload]
            for candidate in candidates:
                if not isinstance(candidate, dict):
                    continue
                candidates_to_add = (
                    candidate.get("itemListElement", [])
                    if candidate.get("@type") == "ItemList"
                    else [candidate]
                )
                for item in candidates_to_add:
                    if isinstance(item, dict) and isinstance(item.get("item"), dict):
                        item = item["item"]
                    if not isinstance(item, dict):
                        continue
                    item_type = item.get("@type")
                    is_product = (
                        "Product" in item_type
                        if isinstance(item_type, list)
                        else item_type == "Product"
                    )
                    if not is_product and not item.get("name"):
                        continue
                    offers = item.get("offers")
                    if isinstance(offers, list):
                        offers = offers[0] if offers else {}
                    if not isinstance(offers, dict):
                        offers = {}
                    product: dict[str, Any] = {"name": str(item["name"]).strip()}
                    for source, target in (("brand", "brand"), ("url", "product_url")):
                        value = item.get(source)
                        if isinstance(value, dict):
                            value = value.get("name")
                        if value:
                            product[target] = value
                    for source, target in (
                        ("price", "price"),
                        ("priceCurrency", "currency"),
                    ):
                        if offers.get(source) is not None:
                            product[target] = offers[source]
                    availability = str(offers.get("availability", "")).lower()
                    if availability:
                        product["in_stock"] = "outofstock" not in availability
                    products.append(product)
        return {"products": products} if products else None

    @classmethod
    def _prepare_content(
        cls,
        content: str,
    ) -> str:

        content = content.strip()

        if not content:
            return ""

        # Detect HTML.
        if (
            "<html" in content.lower()
            or "<body" in content.lower()
            or "<script" in content.lower()
        ):
            content = cls._html_to_text(
                content
            )

        # Normalize whitespace.
        lines = [
            " ".join(
                line.split()
            )
            for line in content.splitlines()
        ]

        lines = [
            line
            for line in lines
            if line
        ]

        cleaned = "\n".join(lines)

        if len(cleaned) <= cls.MAX_CONTENT_CHARS:
            return cleaned

        first_size = 7500
        last_size = 2500

        return (
            cleaned[:first_size]
            + "\n\n"
            + "[CONTENT TRUNCATED]\n\n"
            + cleaned[-last_size:]
        )

    @staticmethod
    def _html_to_text(
        html: str,
    ) -> str:

        # Preserve structured application data before removing scripts.
        # Modern e-commerce SPAs frequently render product information
        # through JSON-LD, Next.js/Nuxt state, or other application
        # bootstrap payloads rather than plain body text.
        preserved: list[str] = []

        for match in re.finditer(
            r"<script\\b[^>]*>(.*?)</script>",
            html,
            flags=re.IGNORECASE | re.DOTALL,
        ):
            tag = match.group(0)
            body = match.group(1).strip()
            if not body:
                continue

            tag_lower = tag.lower()

            if (
                'type="application/ld+json"' in tag_lower
                or "type='application/ld+json'" in tag_lower
                or "__next_data__" in tag_lower
                or "application/json" in tag_lower
                or "__nuxt" in tag_lower
                or "__initial_state__" in tag_lower
                or "__initialstate__" in tag_lower
            ):
                preserved.append(body)

        # Remove executable scripts and styles from the visible HTML.
        html = re.sub(
            r"<script\\b[^>]*>.*?</script>",
            " ",
            html,
            flags=re.IGNORECASE | re.DOTALL,
        )

        html = re.sub(
            r"<style\\b[^>]*>.*?</style>",
            " ",
            html,
            flags=re.IGNORECASE | re.DOTALL,
        )

        html = re.sub(
            r"<noscript\\b[^>]*>.*?</noscript>",
            " ",
            html,
            flags=re.IGNORECASE | re.DOTALL,
        )

        # Convert common structural tags into line breaks.
        html = re.sub(
            r"</(div|p|li|section|article|h1|h2|h3|h4|tr)>",
            "\\n",
            html,
            flags=re.IGNORECASE,
        )

        # Remove remaining tags.
        html = re.sub(
            r"<[^>]+>",
            " ",
            html,
        )

        visible_text = unescape(html)

        if preserved:
            visible_text += "\\n\\n[STRUCTURED APPLICATION DATA]\\n" + (
                "\\n".join(unescape(item) for item in preserved)
            )

        return visible_text
