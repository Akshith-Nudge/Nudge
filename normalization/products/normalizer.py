import re
from dataclasses import dataclass
from difflib import SequenceMatcher

from normalization.brands.normalizer import BrandNormalizer
from scraping.extraction.parser import ExtractedProduct


@dataclass
class NormalizedProduct:
    canonical_name: str
    brand: str | None
    observations: list[ExtractedProduct]


class ProductNormalizer:
    """
    Groups observations that appear to represent the same product.

    Product identity is deterministic.
    No LLM is used for normalization.
    """

    def __init__(
        self,
        canonical_company: str | None = None,
    ) -> None:

        self.canonical_company = canonical_company
        self.brand_normalizer = BrandNormalizer()

    def normalize(
        self,
        products: list[ExtractedProduct],
    ) -> list[NormalizedProduct]:

        groups: list[NormalizedProduct] = []

        for product in products:

            product.brand = (
                self.brand_normalizer.normalize(
                    product.brand,
                    canonical_company=self.canonical_company,
                )
            )

            matched_group = self._find_matching_group(
                product,
                groups,
            )

            if matched_group is None:

                groups.append(
                    NormalizedProduct(
                        canonical_name=product.name,
                        brand=product.brand,
                        observations=[product],
                    )
                )

            else:

                matched_group.observations.append(
                    product
                )

        return groups

    def _find_matching_group(
        self,
        product: ExtractedProduct,
        groups: list[NormalizedProduct],
    ) -> NormalizedProduct | None:

        normalized_name = self._normalize_name(
            product.name
        )

        normalized_brand = self._normalize_brand(
            product.brand
        )

        for group in groups:

            group_name = self._normalize_name(
                group.canonical_name
            )

            group_brand = self._normalize_brand(
                group.brand
            )

            if (
                normalized_brand
                and group_brand
                and normalized_brand != group_brand
            ):
                continue

            similarity = SequenceMatcher(
                None,
                normalized_name,
                group_name,
            ).ratio()

            if similarity >= 0.85:
                return group

        return None

    @staticmethod
    def _normalize_name(
        name: str,
    ) -> str:

        value = name.lower()

        value = re.sub(
            r"[^a-z0-9\s]",
            " ",
            value,
        )

        value = re.sub(
            r"\s+",
            " ",
            value,
        )

        return value.strip()

    @staticmethod
    def _normalize_brand(
        brand: str | None,
    ) -> str | None:

        if not brand:
            return None

        value = brand.lower()

        value = re.sub(
            r"[^a-z0-9]",
            "",
            value,
        )

        return value or None