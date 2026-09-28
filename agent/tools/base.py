from abc import ABC, abstractmethod
from typing import Any


class AgentTool(ABC):
    """
    Base interface for every tool available to the research agent.
    """

    name: str
    description: str

    @abstractmethod
    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        """
        Execute the tool and return structured data.
        """
        raise NotImplementedError