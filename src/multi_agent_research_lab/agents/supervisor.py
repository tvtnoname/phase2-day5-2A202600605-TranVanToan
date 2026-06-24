"""Supervisor / router skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.state import ResearchState


class SupervisorAgent(BaseAgent):
    """Decides which worker should run next and when to stop."""

    name = "supervisor"

    def run(self, state: ResearchState) -> ResearchState:
        """Update `state.route_history` with the next route.

        Sequences Researcher -> Analyst -> Writer -> Done and guards against infinite loops.
        """
        from multi_agent_research_lab.core.config import get_settings

        settings = get_settings()

        # Max iterations guardrail
        if state.iteration >= settings.max_iterations:
            state.record_route("done")
            return state

        # Routing decision
        if not state.research_notes:
            next_route = "researcher"
        elif not state.analysis_notes:
            next_route = "analyst"
        elif not state.final_answer:
            next_route = "writer"
        else:
            next_route = "done"

        state.record_route(next_route)
        return state
