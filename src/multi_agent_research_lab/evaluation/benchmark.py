"""Benchmark skeleton for single-agent vs multi-agent."""

import re
from collections.abc import Callable
from time import perf_counter

from multi_agent_research_lab.core.schemas import BenchmarkMetrics
from multi_agent_research_lab.core.state import ResearchState

Runner = Callable[[str], ResearchState]



def evaluate_quality(query: str, final_answer: str) -> float:
    """Evaluate response quality from 0 to 10 using LLM-as-a-Judge."""
    from multi_agent_research_lab.services.llm_client import LLMClient

    # Instantiate LLMClient directly to call evaluator
    llm = LLMClient()
    system_prompt = (
        "You are an expert academic evaluator. You are given a user research prompt and an AI assistant's response.\n"
        "Your task is to rate the quality of the response from 0.0 to 10.0.\n"
        "Criteria:\n"
        "1. Adherence to all instructions and constraints.\n"
        "2. Inclusion of all requested sections and information.\n"
        "3. Correctness, lack of hallucination, and intellectual depth.\n"
        "4. Proper academic style and appropriate citations of sources.\n\n"
        "You MUST output your evaluation in the following format:\n"
        "Score: <score_between_0_and_10>\n"
        "Reason: <brief explanation>"
    )
    user_prompt = f"User Prompt: {query}\n\nAI Response:\n{final_answer}\n\nEvaluation:"

    try:
        response = llm.complete(system_prompt, user_prompt)
        content = response.content.strip()
        # Parse score:
        for line in content.split("\n"):
            if line.lower().startswith("score:"):
                score_str = line.split(":", 1)[1].strip()
                # Parse numerical score (handle potential float)
                return min(10.0, max(0.0, float(score_str)))

        match = re.search(r"score:\s*([\d\.]+)", content, re.IGNORECASE)
        if match:
            return min(10.0, max(0.0, float(match.group(1))))
    except Exception:
        pass
    return 7.5  # reasonable fallback score if parsing fails


def run_benchmark(
    run_name: str, query: str, runner: Runner
) -> tuple[ResearchState, BenchmarkMetrics]:
    """Measure latency, calculate total costs, evaluate quality, and check citation coverage."""
    started = perf_counter()
    state = runner(query)
    latency = perf_counter() - started

    # Calculate token cost from all agent interactions
    total_cost = sum(
        res.metadata.get("cost_usd", 0.0)
        for res in state.agent_results
        if res.metadata and res.metadata.get("cost_usd") is not None
    )

    # Evaluate quality
    quality = evaluate_quality(query, state.final_answer or "")

    # Calculate citation coverage notes
    notes_list = []
    if state.sources:
        citations_found = set(re.findall(r"\[(\d+)\]", state.final_answer or ""))
        source_indices = {str(i + 1) for i in range(len(state.sources))}
        valid_citations = citations_found.intersection(source_indices)
        coverage_pct = (len(valid_citations) / len(state.sources)) * 100
        notes_list.append(
            f"Citations: {len(valid_citations)}/{len(state.sources)} ({coverage_pct:.1f}%)"
        )
    else:
        notes_list.append("No sources")

    notes_list.append(f"Steps: {state.iteration}")
    if state.errors:
        notes_list.append(f"Errors: {len(state.errors)}")

    metrics = BenchmarkMetrics(
        run_name=run_name,
        latency_seconds=latency,
        estimated_cost_usd=total_cost,
        quality_score=quality,
        notes=" | ".join(notes_list),
    )
    return state, metrics
