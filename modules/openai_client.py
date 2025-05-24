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
        docs = self.transcript_store.similarity_search(description, k=k)
        if not docs:
            return f'No evidence found for “{description}.”'
        snippets = []
        for d in docs:
            start = d.metadata["start"]
            end   = d.metadata["end"]
            text  = d.page_content
            snippets.append(f"[{start:.2f}→{end:.2f}] SPEAKER: {text}")
        context_block = "\n".join(snippets)

        messages = [
            ChatMessage(role="system", content=self.prompt),
            ChatMessage(
                role="user",
                content=(
                    f"Relevant transcript excerpts:\n{context_block}\n\n"
                    f"Description to check: {description}"
                )
            ),
        ]
        resp = self.client.invoke(messages)
        return resp.content.strip()
