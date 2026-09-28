from abc import ABC, abstractmethod
from typing import Any


class AIProvider(ABC):
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        instructions: str | None = None,
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    async def extract_structured(
        self,
        content: str,
        schema: dict[str, Any],
        instructions: str | None = None,
    ) -> dict[str, Any]:
        raise NotImplementedError