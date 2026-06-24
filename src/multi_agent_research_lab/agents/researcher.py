"""Researcher agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.observability.tracing import trace_span
from multi_agent_research_lab.services.llm_client import LLMClient
from multi_agent_research_lab.services.search_client import SearchClient


class ResearcherAgent(BaseAgent):
    """Collects sources and creates concise research notes."""

    name = "researcher"

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.sources` and `state.research_notes`."""
        with trace_span("ResearcherAgent.run") as span:
            search_client = SearchClient()
            llm_client = LLMClient()

            query = state.request.query
            max_sources = state.request.max_sources

            # 1. Search for sources
            sources = search_client.search(query, max_results=max_sources)
            state.sources = sources

            # 2. Synthesize research notes
            sources_text = "\n\n".join(
                [
                    f"Source [{i + 1}]: {src.title}\nURL: {src.url}\nContent: {src.snippet}"
                    for i, src in enumerate(sources)
                ]
            )

            system_prompt = (
                "You are an expert academic researcher. Your job is to analyze the provided search results "
                "and draft concise, structured research notes. Highlight key findings, methodologies, "
                "and data points. Always attribute facts to their source numbers (e.g., [1], [2]). "
                "Be factual, precise, and objective."
            )
            user_prompt = (
                f"User Query: {query}\n\nSearch Results:\n{sources_text}\n\nDraft Research Notes:"
            )

            llm_response = llm_client.complete(system_prompt, user_prompt)
            state.research_notes = llm_response.content

            # Record result and metadata
            metadata = {
                "sources_count": len(sources),
                "input_tokens": llm_response.input_tokens,
                "output_tokens": llm_response.output_tokens,
                "cost_usd": llm_response.cost_usd,
            }
            agent_result = AgentResult(
                agent=AgentName.RESEARCHER, content=llm_response.content, metadata=metadata
            )
            state.agent_results.append(agent_result)
            state.add_trace_event("researcher_complete", metadata)

            span["attributes"].update(metadata)

            return state
