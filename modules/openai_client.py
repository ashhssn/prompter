from langchain_openai import ChatOpenAI
from langchain.schema import ChatMessage

class OpenAIClient:
    def __init__(self, api_key, transcript_store, prompt):
        self.client = ChatOpenAI(
            model_name="o4-mini",
            temperature=1.0,
            max_completion_tokens=2048,
            openai_api_key=api_key
        )
        self.transcript_store = transcript_store
        self.prompt = prompt

    def generate_evidence(self, description: str, k: int = 3) -> str:
        """
        Given a description of an event, retrieve the top-k matching transcript snippets,
        then ask the LLM to format a single evidence sentence.
        """
        docs = self.transcript_store.similarity_search_with_relevance_scores(description, k=k)
        if not docs:
            return f'No evidence found for “{description}.”'

        snippets = []
        i = 0
        for d, score in docs:
            # threshold for similarity
            if score >= 0.5:
                snippets.append(f"{d.page_content}")
        context_block = "\n".join(snippets)

        messages = [
            ChatMessage(role="developer", content=self.prompt),
            ChatMessage(
                role="user",
                content=(
                    f"Relevant transcript excerpts:\n{context_block}\n\n"
                    f"Description to check: {description}\n"
                )
            ),
        ]

        resp = self.client.invoke(messages)
        return resp.content.strip()
