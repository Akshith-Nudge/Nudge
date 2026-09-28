from scraping.extraction.parser import ExtractedProduct
from normalization.products.normalizer import ProductNormalizer


def test_same_product_is_grouped():
    products = [
        ExtractedProduct(
            name="Yoga Bar Protein Bar - 60g",
            brand="Yoga Bar",
            price=120,
        ),
        ExtractedProduct(
            name="Yoga Bar Protein Bar 60 g",
            brand="Yoga Bar",
            price=125,
        ),
    ]

    normalizer = ProductNormalizer()

    groups = normalizer.normalize(products)

    assert len(groups) == 1
    assert len(groups[0].observations) == 2


def test_different_brands_are_not_grouped():
    products = [
        ExtractedProduct(
            name="Protein Bar",
            brand="Yoga Bar",
        ),
        ExtractedProduct(
            name="Protein Bar",
            brand="RiteBite",
        ),
    ]

    normalizer = ProductNormalizer()

    groups = normalizer.normalize(products)

    assert len(groups) == 2


def test_different_products_are_not_grouped():
    products = [
        ExtractedProduct(
            name="Protein Bar Chocolate",
            brand="Yoga Bar",
        ),
        ExtractedProduct(
            name="Protein Bar Peanut Butter",
            brand="Yoga Bar",
        ),
    ]

    normalizer = ProductNormalizer()

    groups = normalizer.normalize(products)

    assert len(groups) == 2