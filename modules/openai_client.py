from langchain_openai import ChatOpenAI
from langchain.schema import ChatMessage

class OpenAIClient:
    def __init__(self, 
                 api_key, 
                 evidence_prompt, 
                 feedback_prompt, 
                 model="o4-mini", 
                 transcript=None, 
                 kb_store=None):
        temperature = 1.0 if model == "o4-mini" else 0.7
        max_tokens = 4096 if model == "04-mini" else 2048
        self.client = ChatOpenAI(
            model_name=model,
            temperature=temperature,
            max_completion_tokens=max_tokens,
            openai_api_key=api_key
        )
        self.evidence_prompt = evidence_prompt
        self.feedback_prompt = feedback_prompt
        self.transcript = transcript
        self.kb_store = kb_store

    def generate_feedback(self, question: str, context: str = "", k: int = 3) -> str:
        kb_context = ""

        if self.kb_store:
            kb_docs = self.kb_store.similarity_search(question, k=k)
            kb_context = "\n".join([f"- {d.page_content}" for d in kb_docs])

        # Use full transcript + KB context
        full_context = ""
        if kb_context:
            full_context += "Relevant guidance:\n" + kb_context + "\n\n"
        if self.transcript:
            full_context += "Transcript:\n" + self.transcript

        messages = [
            ChatMessage(role="developer", content=self.feedback_prompt),
            ChatMessage(
                role="user",
                content=(
                    f"Context:\n{full_context}\n\n"
                    f"Question:\n{question}"
                )
            )
        ]
        response = self.client.invoke(messages)
        return response.content.strip()
    
    def generate_evidence(self, description: str, k: int = 2) -> str:
        """
        Given a description of an event, find the matching transcript snippets,
        then ask the LLM to format a single evidence sentence.
        """
        context_block = self.transcript

        messages = [
            ChatMessage(role="developer", content=self.evidence_prompt),
            ChatMessage(
                role="user",
                content=(
                    f"Transcription:\n{context_block}\n\n"
                    f"Description to check: {description}\n"
                )
            ),
        ]
        try:
            resp = self.client.invoke(messages)
        except Exception as e:
            print(f"Error occured while invoking LLM: {e}\nSkipping current iter")
        return resp.content.strip()
