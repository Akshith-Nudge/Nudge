from dataclasses import dataclass


@dataclass(frozen=True)
class MarketplaceTarget:
    name: str
    search_domains: tuple[str, ...]


MARKETPLACE_TARGETS = (
    MarketplaceTarget(
        name="Instamart",
        search_domains=(
            "swiggy.com",
        ),
    ),
    MarketplaceTarget(
        name="Zepto",
        search_domains=(
            "zepto.com",
        ),
    ),
    MarketplaceTarget(
        name="Blinkit",
        search_domains=(
            "blinkit.com",
        ),
    ),
)

MARKETPLACE_ALIASES = {
    "swiggy instamart": "Instamart",
    "instamart": "Instamart",
    "zepto": "Zepto",
    "blinkit": "Blinkit",
}


def resolve_marketplaces(names: list[str] | None = None) -> tuple[MarketplaceTarget, ...]:
    """Return configured targets, optionally filtered by user-facing names."""
    if not names:
        return MARKETPLACE_TARGETS

    requested = {
        MARKETPLACE_ALIASES.get(name.strip().lower(), name.strip().lower())
        for name in names
    }
    return tuple(target for target in MARKETPLACE_TARGETS if target.name.lower() in requested)