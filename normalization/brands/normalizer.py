import re


class BrandNormalizer:
    """
    Deterministically normalizes brand names.

    The requested company is treated as the canonical company.
    Known formatting variants such as:

        Yoga Bar
        Yogabar
        yoga-bar
        YOGABAR

    are treated as the same brand.

    No LLM is used here.
    """

    def normalize(
        self,
        brand: str | None,
        canonical_company: str | None = None,
    ) -> str | None:

        if not brand:
            return None

        normalized_brand = self._compact(brand)

        if not normalized_brand:
            return None

        if canonical_company:
            normalized_company = self._compact(
                canonical_company
            )

            if normalized_brand == normalized_company:
                return canonical_company.strip()

        return brand.strip()

    @staticmethod
    def _compact(value: str) -> str:
        value = value.lower().strip()

        # Remove punctuation and whitespace.
        value = re.sub(
            r"[^a-z0-9]",
            "",
            value,
        )

        return value