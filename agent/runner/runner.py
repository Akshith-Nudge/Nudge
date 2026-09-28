from agent.planner.planner import ResearchPlanner
from agent.runner.orchestrator import ResearchOrchestrator
from agent.state.models import AgentState, ResearchRequest
from agent.tools.registry import ToolRegistry


class ResearchAgent:
    def __init__(
        self,
        tools: ToolRegistry,
    ) -> None:
        self.tools = tools
        self.planner = ResearchPlanner()
        self.orchestrator = ResearchOrchestrator(tools)

    async def run(
        self,
        request: ResearchRequest,
    ) -> AgentState:
        state = AgentState(
            request=request,
            status="planning",
        )

        plan = self.planner.create_plan(request)

        state.status = "researching"

        state.completed_tasks.append(
            f"plan_created:{len(plan)}"
        )

        for task in plan:
            state.completed_tasks.append(
                task.name
            )

        state.status = "completed"

        return state