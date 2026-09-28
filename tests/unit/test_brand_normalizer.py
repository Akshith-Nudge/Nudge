from normalization.brands.normalizer import BrandNormalizer


def test_yoga_bar_variants_are_canonicalized():

    normalizer = BrandNormalizer()

    assert (
        normalizer.normalize(
            "Yoga Bar",
            "Yoga Bar",
        )
        == "Yoga Bar"
    )

    assert (
        normalizer.normalize(
            "Yogabar",
            "Yoga Bar",
        )
        == "Yoga Bar"
    )

    assert (
        normalizer.normalize(
            "yoga-bar",
            "Yoga Bar",
        )
        == "Yoga Bar"
    )

    assert (
        normalizer.normalize(
            "YOGABAR",
            "Yoga Bar",
        )
        == "Yoga Bar"
    )


def test_unrelated_brand_is_preserved():

    normalizer = BrandNormalizer()

    assert (
        normalizer.normalize(
            "RiteBite",
            "Yoga Bar",
        )
        == "RiteBite"
    )