"""Command-line entrypoint for the lab starter."""

from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel

from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.errors import StudentTodoError
from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.graph.workflow import MultiAgentWorkflow
from multi_agent_research_lab.observability.logging import configure_logging

app = typer.Typer(help="Multi-Agent Research Lab starter CLI")
console = Console()


def _init() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)


@app.command()
def baseline(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run a real single-agent baseline LLM call."""
    _init()
    from multi_agent_research_lab.services.llm_client import LLMClient

    request = ResearchQuery(query=query)
    state = ResearchState(request=request)

    llm_client = LLMClient()
    system_prompt = (
        "You are an expert research assistant. Answer the user query thoroughly and professionally. "
        "Structure your response logically and adhere to all instructions and constraints."
    )

    console.print("[bold]Running Single-Agent Baseline LLM Call...[/bold]")
    llm_response = llm_client.complete(system_prompt, query)
    state.final_answer = llm_response.content

    console.print(Panel.fit(state.final_answer, title="Single-Agent Baseline Result"))


@app.command("multi-agent")
def multi_agent(
    query: Annotated[str, typer.Option("--query", "-q", help="Research query")],
) -> None:
    """Run the multi-agent workflow."""
    _init()
    state = ResearchState(request=ResearchQuery(query=query))
    workflow = MultiAgentWorkflow()
    try:
        result = workflow.run(state)
    except StudentTodoError as exc:
        console.print(Panel.fit(str(exc), title="Expected TODO", style="yellow"))
        raise typer.Exit(code=2) from exc
    console.print(result.model_dump_json(indent=2))


@app.command("benchmark")
def benchmark() -> None:
    """Run the benchmark suite comparing Single-Agent vs Multi-Agent on all 4 prompts."""
    _init()
    import os

    from multi_agent_research_lab.core.schemas import AgentName, AgentResult
    from multi_agent_research_lab.evaluation.benchmark import run_benchmark
    from multi_agent_research_lab.evaluation.report import render_markdown_report
    from multi_agent_research_lab.services.llm_client import LLMClient

    prompts = [
        # Prompt 1
        "ResearchAgentBench Benchmark Design: Design ResearchAgentBench to evaluate AI research assistants. Must include: Goal, assumptions, categories, 12 example tasks, scoring rubric, baselines, failure modes/gaming risks, human eval protocol, limitations, v2 recommendations. Constraints: realistic for small lab, no expensive annotations, distinguish usefulness/correctness/judgment, adversarial stress-test, discuss gaming.",
        # Prompt 2
        "Research Briefing on Multi-Agent LLMs: Do multi-agent LLM systems actually outperform single-agent systems on complex tasks? Produce structured briefing: main claim, literature positions, arguments supporting/challenging, weak empirical evidence, distinguish multi-agent gains vs tokens/prompt engineering/reflection, 3 experiments, final judgment with uncertainty.",
        # Prompt 3
        "Experimental Design - Single-Call vs. Multi-Agent: Design research experiment. Must include: question, hypotheses, tasks, datasets, fair comparison, metrics, human eval, statistical considerations, expected results, red-team critique on token budget fairness/inference time bias, revised design.",
        # Prompt 4
        "Survey Paper Blueprint: Outline survey paper 'AI Agents for Research Assistance: Capabilities, Evaluation, and Open Problems'. Must produce: Title, draft abstract, 6-8 outline sections (purpose, themes, questions, pitfalls, open problems), evaluation gaps, future benchmark metrics.",
    ]

    results_list = []

    def baseline_runner(q: str) -> ResearchState:
        req = ResearchQuery(query=q)
        st = ResearchState(request=req)
        llm = LLMClient()
        system = "You are an expert research assistant. Answer the user query thoroughly and professionally, adhering to all instructions and constraints."
        resp = llm.complete(system, q)
        st.final_answer = resp.content
        st.agent_results.append(
            AgentResult(
                agent=AgentName.SUPERVISOR,
                content=resp.content,
                metadata={
                    "input_tokens": resp.input_tokens,
                    "output_tokens": resp.output_tokens,
                    "cost_usd": resp.cost_usd,
                },
            )
        )
        return st

    def multi_agent_runner(q: str) -> ResearchState:
        req = ResearchQuery(query=q)
        st = ResearchState(request=req)
        wf = MultiAgentWorkflow()
        return wf.run(st)

    for i, prompt in enumerate(prompts, 1):
        console.print(f"\n[bold green]Running Benchmark Task {i}/4...[/bold green]")

        # Run Baseline
        console.print("[blue]Running Single-Agent Baseline...[/blue]")
        state_base, metric_base = run_benchmark(f"Single-Agent (Task {i})", prompt, baseline_runner)
        results_list.append((state_base, metric_base))

        # Run Multi-Agent
        console.print("[blue]Running Multi-Agent Workflow...[/blue]")
        state_multi, metric_multi = run_benchmark(
            f"Multi-Agent (Task {i})", prompt, multi_agent_runner
        )
        results_list.append((state_multi, metric_multi))

    # Render report
    report_md = render_markdown_report(results_list)

    os.makedirs("reports", exist_ok=True)
    with open("reports/benchmark_report.md", "w", encoding="utf-8") as f:
        f.write(report_md)

    console.print(
        "\n[bold green]Benchmark completed! Report written to reports/benchmark_report.md[/bold green]"
    )
    console.print(report_md)


if __name__ == "__main__":
    app()
