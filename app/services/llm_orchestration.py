"""LLM orchestration via OpenAI."""

from langchain_openai import ChatOpenAI

from app.config import settings

# Reference pricing for gpt-4o-mini (USD per token)
INPUT_COST_PER_TOKEN = 0.15 / 1_000_000
OUTPUT_COST_PER_TOKEN = 0.60 / 1_000_000


class LLMOrchestrator:
    """Manages LLM calls with cost tracking."""

    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            openai_api_key=settings.openai_api_key,
            temperature=0.1,
            max_tokens=500,
        )

    def generate(self, messages: list[dict]) -> dict:
        response = self.llm.invoke(messages)

        usage = response.response_metadata.get("token_usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", prompt_tokens + completion_tokens)

        cost = (
            prompt_tokens * INPUT_COST_PER_TOKEN
            + completion_tokens * OUTPUT_COST_PER_TOKEN
        )

        return {
            "answer": response.content,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "estimated_cost_usd": round(cost, 6),
        }
