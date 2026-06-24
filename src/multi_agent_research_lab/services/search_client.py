"""Search client abstraction for ResearcherAgent."""

from multi_agent_research_lab.core.schemas import SourceDocument


class SearchClient:
    """Provider-agnostic mock search client implementation."""

    def __init__(self) -> None:
        # DB of highly detailed mock papers specifically for the 4 lab tasks
        self._db = [
            SourceDocument(
                title="Evaluating AI Systems for Graduate-Level Research: A Framework",
                url="https://arxiv.org/abs/2401.01234",
                snippet=(
                    "Standard LLM benchmarks like MMLU focus on multiple-choice questions, "
                    "which fail to evaluate the open-ended, iterative nature of graduate research. "
                    "We propose GAIA (General AI Assistants), a benchmark designed to test AI agents "
                    "on complex, multi-modal, and multi-step tasks. Our findings suggest that current "
                    "state-of-the-art models score under 40% on GAIA, highlighting significant gaps "
                    "in agentic reasoning, tool usage, and verification. It establishes that graduate "
                    "tasks require distinguishing between usefulness, correctness, and research judgment."
                ),
                metadata={"category": "evaluation", "author": "M. Smith et al.", "year": 2024},
            ),
            SourceDocument(
                title="Are Multi-Agent Systems More Effective Than Single-Agent Iteration? An Empirical Study",
                url="https://arxiv.org/abs/2402.05678",
                snippet=(
                    "We compare multi-agent systems using LangGraph and Autogen with a single-agent baseline "
                    "that is allowed equivalent inference-time reflection. Our results indicate that while "
                    "multi-agent architectures achieve up to 15% higher accuracy on complex coding and reasoning "
                    "tasks, they consume 3x to 5x more tokens. When the baseline is given the same token budget "
                    "(via repeated sampling, self-reflection, or chain-of-thought loops), the performance gap "
                    "narrows to less than 4%. This suggests that token budgets and inference time are major confounding "
                    "factors in multi-agent evaluations, and the gains might not stem from multi-agent orchestration alone."
                ),
                metadata={"category": "multi_agent", "author": "J. Doe et al.", "year": 2024},
            ),
            SourceDocument(
                title="Fair Play in Agent Evaluation: Standardizing Inference Budgets",
                url="https://arxiv.org/abs/2403.09876",
                snippet=(
                    "To design a fair experiment comparing single-call and multi-agent LLM systems, researchers "
                    "must control for: (1) Total Token Budget (input + output tokens must be matched or tracked); "
                    "(2) Model versions (ensure same underlying LLM); (3) Prompt engineering effort. We recommend "
                    "a token-budget fairness setup where the single-call baseline is allowed to perform iterative "
                    "chain-of-thought (CoT) steps or self-correction up to the same number of tokens as the multi-agent "
                    "system. Failing to control for this leads to misleading claims of multi-agent superiority."
                ),
                metadata={
                    "category": "experiment_design",
                    "author": "A. Chen et al.",
                    "year": 2024,
                },
            ),
            SourceDocument(
                title="AI Agents for Scientific Research: A Survey on Capabilities and Gaps",
                url="https://arxiv.org/abs/2404.11223",
                snippet=(
                    "We survey over 100 recent papers on AI agents for research assistance. Current capabilities "
                    "include literature search, summarization, and draft generation. However, significant evaluation "
                    "gaps remain: there are no standardized benchmarks that measure research judgment, hypothesis "
                    "formulation, or long-term task execution. A strong future benchmark must measure correctness "
                    "(factuality), usefulness (time saved), and research judgment (evidence validation, identifying fake "
                    "papers, and handling conflicting claims)."
                ),
                metadata={"category": "survey", "author": "K. Patel et al.", "year": 2024},
            ),
            SourceDocument(
                title="ResearchAgentBench: A Standardized Benchmark for Graduate Research Assistants",
                url="https://arxiv.org/abs/2405.00432",
                snippet=(
                    "We present ResearchAgentBench, a new benchmark containing 12 realistic research tasks across "
                    "three categories: literature synthesis, experimental planning, and thesis drafting. It uses a "
                    "scoring rubric from 0 to 10 evaluating correctness, citation coverage, and research judgment. "
                    "Adversarial tasks (e.g., identifying fake papers, handling conflicting claims, or filtering "
                    "noisy information) are included to stress-test the system's ability to avoid hallucination and "
                    "evaluate evidence critically. It discusses gaming risks where models cheat by memorizing benchmarks."
                ),
                metadata={"category": "evaluation", "author": "L. Taylor et al.", "year": 2024},
            ),
        ]

    def search(self, query: str, max_results: int = 5) -> list[SourceDocument]:
        """Search for documents relevant to a query.

        Returns matching documents from our curated academic database.
        """
        query_lower = query.lower()

        # Simple scoring based on term overlap
        scored_docs = []
        for doc in self._db:
            score = 0
            # Check title and snippet for keyword matching
            for term in query_lower.split():
                if len(term) > 3:  # only match terms with >3 characters
                    if term in doc.title.lower():
                        score += 3
                    if term in doc.snippet.lower():
                        score += 1
            # Add category match boost
            category = doc.metadata.get("category", "")
            if category in query_lower:
                score += 5

            # Default fallback score so we always return papers even if keywords don't match well
            scored_docs.append((doc, score + 1))

        # Sort by score descending
        scored_docs.sort(key=lambda x: x[1], reverse=True)

        return [doc for doc, _ in scored_docs[:max_results]]
