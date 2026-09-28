from analytics.sov.calculator import SOVCalculator
from normalization.products.normalizer import NormalizedProduct
from scraping.extraction.parser import ExtractedProduct


def test_sov_calculation():

    products = [
        NormalizedProduct(
            canonical_name="Yoga Bar Protein Bar",
            brand="Yoga Bar",
            observations=[
                ExtractedProduct(
                    name="Yoga Bar Protein Bar",
                    brand="Yoga Bar",
                )
            ],
        ),
        NormalizedProduct(
            canonical_name="RiteBite Protein Bar",
            brand="RiteBite",
            observations=[
                ExtractedProduct(
                    name="RiteBite Protein Bar",
                    brand="RiteBite",
                )
            ],
        ),
        NormalizedProduct(
            canonical_name="MuscleBlaze Protein Bar",
            brand="MuscleBlaze",
            observations=[
                ExtractedProduct(
                    name="MuscleBlaze Protein Bar",
                    brand="MuscleBlaze",
                )
            ],
        ),
        NormalizedProduct(
            canonical_name="Yoga Bar Choco Bar",
            brand="Yoga Bar",
            observations=[
                ExtractedProduct(
                    name="Yoga Bar Choco Bar",
                    brand="Yoga Bar",
                )
            ],
        ),
    ]

    calculator = SOVCalculator()

    result = calculator.calculate(
        company="Yoga Bar",
        products=products,
    )

    assert result.company_observations == 2
    assert result.total_observations == 4
    assert result.share_of_voice == 50.0


def test_sov_with_no_products():

    calculator = SOVCalculator()

    result = calculator.calculate(
        company="Yoga Bar",
        products=[],
    )

    assert result.company_observations == 0
    assert result.total_observations == 0
    assert result.share_of_voice == 0.0