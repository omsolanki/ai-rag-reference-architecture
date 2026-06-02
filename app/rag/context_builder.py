"""Context builder for LLM prompt assembly."""


class ContextBuilder:
    """Assembles retrieved chunks into a structured context block."""

    MAX_CONTEXT_CHARS = 6000

    def build(self, chunks: list[dict]) -> str:
        if not chunks:
            return "No relevant context found."

        context_parts = []
        total_chars = 0

        for i, chunk in enumerate(chunks, 1):
            source = chunk.get("metadata", {}).get("source", "unknown")
            title = chunk.get("metadata", {}).get("title", "Untitled")
            header = f"[Source {i}: {title} ({source})]"
            body = chunk["content"]
            section = f"{header}\n{body}"

            if total_chars + len(section) > self.MAX_CONTEXT_CHARS:
                break

            context_parts.append(section)
            total_chars += len(section)

        return "\n\n---\n\n".join(context_parts)
