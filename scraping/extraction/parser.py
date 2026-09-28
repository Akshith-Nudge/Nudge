from dataclasses import dataclass, field
from typing import Any
from urllib.parse import urlparse


@dataclass
class ExtractedProduct:
    name: str
    brand: str | None = None
    price: float | None = None
    mrp: float | None = None
    in_stock: bool | None = None
    rank: int | None = None
    product_url: str | None = None
    marketplace: str | None = None
    region: str | None = None
    source_url: str | None = None
    raw_data: dict[str, Any] = field(
        default_factory=dict,
    )


class ProductParser:
    """
    Generic product parser.

    This class deliberately does not contain marketplace-specific
    selectors or assumptions.
    """

    def parse(
        self,
        data: dict[str, Any],
    ) -> list[ExtractedProduct]:

        products = data.get("products", [])

        if not isinstance(products, list):
            raise ValueError(
                "Expected 'products' to be a list."
            )

        extracted: list[ExtractedProduct] = []

        for item in products:

            if not isinstance(item, dict):
                continue

            name = str(
                item.get("name", "")
            ).strip()

            if not name:
                continue

            extracted.append(
                ExtractedProduct(
                    name=name,
                    brand=self._string_or_none(
                        item.get("brand")
                    ),
                    price=self._number_or_none(
                        item.get("price")
                    ),
                    mrp=self._number_or_none(
                        item.get("mrp")
                    ),
                    in_stock=self._bool_or_none(
                        item.get("in_stock")
                    ),
                    rank=self._int_or_none(
                        item.get("rank")
                    ),
                    product_url=self._url_or_none(
                        item.get("product_url")
                    ),
                    raw_data=item,
                )
            )

        return extracted

    @staticmethod
    def _string_or_none(
        value: Any,
    ) -> str | None:

        if value is None:
            return None

        value = str(value).strip()

        return value or None

    @staticmethod
    def _number_or_none(
        value: Any,
    ) -> float | None:

        if value is None:
            return None

        try:
            if isinstance(value, str):
                value = value.replace(",", "")
                value = value.replace("₹", "").strip()
            number = float(value)
            return number if number >= 0 else None
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _int_or_none(
        value: Any,
    ) -> int | None:

        if value is None:
            return None

        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _bool_or_none(
        value: Any,
    ) -> bool | None:

        if value is None:
            return None

        if isinstance(value, bool):
            return value

        if isinstance(value, str):
            normalized = value.strip().lower()

            if normalized in {
                "true",
                "yes",
                "available",
                "in stock",
                "in_stock",
            }:
                return True

            if normalized in {
                "false",
                "no",
                "unavailable",
                "out of stock",
                "out_of_stock",
            }:
                return False

        return None

    @staticmethod
    def _url_or_none(
        value: Any,
    ) -> str | None:

        if not value:
            return None

        value = str(value).strip()

        parsed = urlparse(value)

        if parsed.scheme not in {
            "http",
            "https",
        }:
            return None

        if not parsed.netloc:
            return None

        return value