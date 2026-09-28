from agent.tools.base import AgentTool


class ToolRegistry:

    def __init__(self) -> None:
        self._tools: dict[str, AgentTool] = {}

    def register(self, tool: AgentTool) -> None:
        if tool.name in self._tools:
            raise ValueError(
                f"Tool already registered: {tool.name}"
            )

        self._tools[tool.name] = tool

    def get(self, name: str) -> AgentTool:
        try:
            return self._tools[name]
        except KeyError:
            raise KeyError(
                f"Unknown agent tool: {name}"
            ) from None

    def list(self) -> list[str]:
        return list(self._tools.keys())