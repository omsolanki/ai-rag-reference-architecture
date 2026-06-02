"""Embedding generation service using OpenAI via LangChain."""

from langchain_openai import OpenAIEmbeddings

from app.config import Settings


class EmbeddingService:
    """Generates vector embeddings for text chunks and queries."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self._embeddings = OpenAIEmbeddings(
            model=settings.openai_embedding_model,
            openai_api_key=settings.openai_api_key,
        )

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a batch of texts."""
        if not texts:
            return []
        return self._embeddings.embed_documents(texts)

    def embed_query(self, query: str) -> list[float]:
        """Generate embedding for a single query."""
        return self._embeddings.embed_query(query)
