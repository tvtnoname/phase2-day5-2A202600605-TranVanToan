"""LLM client abstraction.

Production note: agents should depend on this interface instead of importing an SDK directly.
"""

import logging
import time
from dataclasses import dataclass

from openai import OpenAI, OpenAIError

from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.errors import AgentExecutionError


@dataclass(frozen=True)
class LLMResponse:
    content: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    cost_usd: float | None = None


class LLMClient:
    """Provider-agnostic LLM client implementation."""

    def __init__(self) -> None:
        self.settings = get_settings()
        if not self.settings.openai_api_key:
            logging.getLogger(__name__).warning("OPENAI_API_KEY is not set.")
        self.client = OpenAI(api_key=self.settings.openai_api_key)

    def complete(self, system_prompt: str, user_prompt: str) -> LLMResponse:
        """Return a model completion.

        Connects OpenAI API, handles retry, timeout, and token logging.
        """
        logger = logging.getLogger(__name__)
        model = self.settings.openai_model or "gpt-4o-mini"
        max_retries = 3
        delay = 2.0

        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                )

                content = response.choices[0].message.content or ""
                usage = response.usage
                input_tokens = usage.prompt_tokens if usage else None
                output_tokens = usage.completion_tokens if usage else None

                # Calculate estimated cost
                cost_usd = None
                if input_tokens is not None and output_tokens is not None:
                    if "gpt-4o-mini" in model:
                        cost_usd = (input_tokens * 0.15 + output_tokens * 0.60) / 1_000_000
                    elif "gpt-4o" in model:
                        cost_usd = (input_tokens * 5.00 + output_tokens * 15.00) / 1_000_000
                    else:
                        cost_usd = (input_tokens * 0.15 + output_tokens * 0.60) / 1_000_000

                return LLMResponse(
                    content=content,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    cost_usd=cost_usd,
                )

            except OpenAIError as e:
                logger.warning(f"OpenAI call attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise AgentExecutionError(
                        f"Failed to call OpenAI after {max_retries} attempts: {e}"
                    ) from e
                time.sleep(delay * (2**attempt))
            except Exception as e:
                logger.error(f"Unexpected error in LLMClient: {e}")
                raise AgentExecutionError(f"Unexpected error: {e}") from e
