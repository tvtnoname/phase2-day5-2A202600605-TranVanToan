"""LangGraph workflow skeleton."""

from langgraph.graph import END, StateGraph

from multi_agent_research_lab.agents.analyst import AnalystAgent
from multi_agent_research_lab.agents.researcher import ResearcherAgent
from multi_agent_research_lab.agents.supervisor import SupervisorAgent
from multi_agent_research_lab.agents.writer import WriterAgent
from multi_agent_research_lab.core.state import ResearchState


class MultiAgentWorkflow:
    """Builds and runs the multi-agent graph.

    Keep orchestration here; keep agent internals in `agents/`.
    """

    def build(self) -> object:
        """Create a LangGraph graph."""
        # Initialize StateGraph with the ResearchState schema
        workflow = StateGraph(ResearchState)

        # Add agent nodes
        workflow.add_node("supervisor", lambda state: SupervisorAgent().run(state))
        workflow.add_node("researcher", lambda state: ResearcherAgent().run(state))
        workflow.add_node("analyst", lambda state: AnalystAgent().run(state))
        workflow.add_node("writer", lambda state: WriterAgent().run(state))

        # Supervisor is the entrypoint
        workflow.set_entry_point("supervisor")

        # Routing function based on Supervisor's decision
        def route_decision(state: ResearchState) -> str:
            if state.route_history:
                return state.route_history[-1]
            return "done"

        # Conditional routing from supervisor
        workflow.add_conditional_edges(
            "supervisor",
            route_decision,
            {
                "researcher": "researcher",
                "analyst": "analyst",
                "writer": "writer",
                "done": END,
            },
        )

        # Non-supervisor nodes always route back to supervisor
        workflow.add_edge("researcher", "supervisor")
        workflow.add_edge("analyst", "supervisor")
        workflow.add_edge("writer", "supervisor")

        return workflow.compile()

    def run(self, state: ResearchState) -> ResearchState:
        """Execute the graph and return final state."""
        compiled_graph = self.build()
        result = compiled_graph.invoke(state)

        # Ensure the result is converted back to ResearchState
        if isinstance(result, ResearchState):
            return result
        elif isinstance(result, dict):
            return ResearchState(**result)
        return result
