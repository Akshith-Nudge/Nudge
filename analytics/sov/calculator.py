from dataclasses import dataclass

from normalization.products.normalizer import NormalizedProduct


@dataclass
class SOVResult:
    company: str
    company_observations: int
    total_observations: int
    share_of_voice: float


class SOVCalculator:
    """
    Deterministically calculates Share of Voice.

    SOV is calculated using normalized product groups rather
    than raw page observations.

    This prevents the same product appearing on multiple
    pages from artificially increasing its contribution.
    """

    def calculate(
        self,
        company: str,
        products: list[NormalizedProduct],
    ) -> SOVResult:

        total_observations = len(products)

        if total_observations == 0:
            return SOVResult(
                company=company,
                company_observations=0,
                total_observations=0,
                share_of_voice=0.0,
            )

        company_normalized = self._normalize(
            company
        )

        company_observations = 0

        for product in products:

            if not product.brand:
                continue

            if (
                self._normalize(product.brand)
                == company_normalized
            ):
                company_observations += 1

        share_of_voice = (
            company_observations
            / total_observations
            * 100
        )

        return SOVResult(
            company=company,
            company_observations=company_observations,
            total_observations=total_observations,
            share_of_voice=round(
                share_of_voice,
                2,
            ),
        )

    @staticmethod
    def _normalize(
        value: str,
    ) -> str:

        return " ".join(
            value.lower().strip().split()
        )