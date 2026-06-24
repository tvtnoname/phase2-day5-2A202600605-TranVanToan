"""Writer agent skeleton."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.observability.tracing import trace_span
from multi_agent_research_lab.services.llm_client import LLMClient


class WriterAgent(BaseAgent):
    """Produces final answer from research and analysis notes."""

    name = "writer"

    def run(self, state: ResearchState) -> ResearchState:
        """Populate `state.final_answer`."""
        with trace_span("WriterAgent.run") as span:
            llm_client = LLMClient()

            research_notes = state.research_notes or "No research notes available."
            analysis_notes = state.analysis_notes or "No analysis notes available."
            query = state.request.query
            audience = state.request.audience or "technical learners"

            # Formulate system and user prompts
            system_prompt = (
                f"You are a professional research writer. Your task is to produce the final, comprehensive response "
                f"to the user query. The output must be tailored to the audience: '{audience}'.\n"
                f"You must incorporate facts from the research notes and critical insights from the analysis notes.\n"
                f"Strictly adhere to all formatting, structural, and semantic constraints specified in the user query.\n"
                f"Ensure you cite source documents using bracketed numbers corresponding to the original sources "
                f"(e.g., [1], [2]). Do not invent citations. At the end of the text, append a 'Sources' section "
                f"listing all cited references with their Title and URL."
            )

            sources_ref = "\n".join(
                [
                    f"[{i + 1}] Title: {src.title} (URL: {src.url})"
                    for i, src in enumerate(state.sources)
                ]
            )

            user_prompt = (
                f"User Query: {query}\n\n"
                f"Research Notes:\n{research_notes}\n\n"
                f"Analysis Notes:\n{analysis_notes}\n\n"
                f"Original Sources:\n{sources_ref}\n\n"
                f"Final Draft Answer:"
            )

            llm_response = llm_client.complete(system_prompt, user_prompt)
            state.final_answer = llm_response.content

            # Record result and metadata
            metadata = {
                "input_tokens": llm_response.input_tokens,
                "output_tokens": llm_response.output_tokens,
                "cost_usd": llm_response.cost_usd,
            }
            agent_result = AgentResult(
                agent=AgentName.WRITER, content=llm_response.content, metadata=metadata
            )
            state.agent_results.append(agent_result)
            state.add_trace_event("writer_complete", metadata)

            span["attributes"].update(metadata)

            return state
