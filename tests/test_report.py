from multi_agent_research_lab.core.schemas import BenchmarkMetrics, ResearchQuery
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.evaluation.report import render_markdown_report


def test_report_renders_markdown() -> None:
    query = ResearchQuery(query="Explain multi-agent systems")
    state = ResearchState(request=query)
    metric = BenchmarkMetrics(run_name="baseline", latency_seconds=1.23)
    report = render_markdown_report([(state, metric)])
    assert "Benchmark Report" in report
    assert "baseline" in report

