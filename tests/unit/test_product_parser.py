from scraping.extraction.parser import ProductParser


def test_product_parser():

    parser = ProductParser()

    products = parser.parse(
        {
            "products": [
                {
                    "name": "Protein Shake",
                    "brand": "Example Brand",
                    "price": "99",
                    "mrp": "120",
                    "in_stock": "true",
                    "rank": 1,
                    "product_url": (
                        "https://example.com/product"
                    ),
                }
            ]
        }
    )

    assert len(products) == 1

    product = products[0]

    assert product.name == "Protein Shake"
    assert product.brand == "Example Brand"
    assert product.price == 99.0
    assert product.mrp == 120.0
    assert product.in_stock is True
    assert product.rank == 1
    assert (
        product.product_url
        == "https://example.com/product"
    )