from dataclasses import dataclass

from agent.state.models import ResearchRequest


@dataclass
class ResearchTask:
    name: str
    description: str
    priority: int


class ResearchPlanner:

    def create_plan(
        self,
        request: ResearchRequest,
    ) -> list[ResearchTask]:

        tasks = [
            ResearchTask(
                name="identify_products",
                description=(
                    f"Identify products belonging to "
                    f"{request.company} relevant to "
                    f"'{request.keyword}'."
                ),
                priority=1,
            ),
            ResearchTask(
                name="search_marketplaces",
                description=(
                    f"Search relevant e-commerce marketplaces "
                    f"for '{request.keyword}'."
                ),
                priority=2,
            ),
            ResearchTask(
                name="collect_product_observations",
                description=(
                    "Collect product names, rankings, prices, "
                    "availability and source evidence."
                ),
                priority=3,
            ),
            ResearchTask(
                name="verify_regions",
                description=(
                    "Check product availability across the "
                    "requested regions."
                ),
                priority=4,
            ),
        ]

        return sorted(
            tasks,
            key=lambda task: task.priority,
        )