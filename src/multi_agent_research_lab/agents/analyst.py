"""Analyst agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.observability.tracing import trace_span
from multi_agent_research_lab.services.llm_client import LLMClient


class AnalystAgent(BaseAgent):
    """Turns research notes into structured insights."""

    name = "analyst"

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.analysis_notes`."""
        with trace_span("AnalystAgent.run") as span:
            llm_client = LLMClient()

            research_notes = state.research_notes or "No research notes available."
            query = state.request.query

            system_prompt = (
                "You are an expert academic analyst. Your job is to critically review the research notes "
                "compiled for a query. Analyze the strength of the evidence, compare conflicting arguments, "
                "identify methodological pitfalls, and call out weak claims or lack of citation/sources. "
                "Structure your notes clearly. Use source numbers (e.g., [1], [2]) if referring back to claims."
            )
            user_prompt = (
                f"User Query: {query}\n\nResearch Notes:\n{research_notes}\n\nDraft Analysis Notes:"
            )

            llm_response = llm_client.complete(system_prompt, user_prompt)
            state.analysis_notes = llm_response.content

            # Record result and metadata
            metadata = {
                "input_tokens": llm_response.input_tokens,
                "output_tokens": llm_response.output_tokens,
                "cost_usd": llm_response.cost_usd,
            }
            agent_result = AgentResult(
                agent=AgentName.ANALYST, content=llm_response.content, metadata=metadata
            )
            state.agent_results.append(agent_result)
            state.add_trace_event("analyst_complete", metadata)

            span["attributes"].update(metadata)

            return state
