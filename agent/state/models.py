from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4


@dataclass
class ResearchRequest:
    company: str
    keyword: str
    regions: list[str] = field(default_factory=list)
    marketplaces: list[str] = field(default_factory=list)


@dataclass
class ResearchObservation:
    marketplace: str
    region: str | None
    product_name: str
    brand: str | None = None
    rank: int | None = None
    price: float | None = None
    mrp: float | None = None
    in_stock: bool | None = None
    product_url: str | None = None
    source_url: str | None = None
    raw_data: dict[str, Any] = field(default_factory=dict)
    observed_at: datetime = field(
        default_factory=lambda: datetime.now(UTC)
    )


@dataclass
class AgentState:
    request: ResearchRequest
    run_id: UUID = field(default_factory=uuid4)

    observations: list[ResearchObservation] = field(
        default_factory=list
    )

    completed_tasks: list[str] = field(
        default_factory=list
    )

    errors: list[str] = field(
        default_factory=list
    )

    status: str = "created"