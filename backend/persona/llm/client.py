from typing import AsyncIterator, Dict, List, Protocol

from huggingface_hub import AsyncInferenceClient


class LLMBackend(Protocol):
    async def chat_stream(
        self, system: str, messages: List[Dict[str, str]]
    ) -> AsyncIterator[str]: ...

    async def embed(self, text: str) -> List[float]: ...

    async def extract(self, prompt: str) -> list[dict]: ...


class FakeLLMBackend:
    chat_chunksize: int = 1024
    embedding: bool = False
    extraction: bool = False

    async def chat_stream(
        self, system: str, messages: List[Dict[str, str]]
    ) -> AsyncIterator[str]:
        yield "fake response"

    async def embed(self, text: str) -> List[float]:
        if not self.embedding:
            raise NotImplementedError("Embedding not supported in FakeLLMBackend")
        return [0.0] * 768

    async def extract(self, prompt: str) -> list[dict]:
        if not self.extraction:
            raise NotImplementedError("Extraction not supported in FakeLLMBackend")
        return [{"type": "fact", "content": "example value", "importance": 3}]


class HFBackend:
    def __init__(self, hf_token: str, chat_model: str, embed_model: str):
        self.hf_token = hf_token
        self.chat_model = chat_model
        self.embed_model = embed_model
        self._chat_client = AsyncInferenceClient(model=chat_model, token=hf_token)
        self._embed_client = AsyncInferenceClient(model=embed_model, token=hf_token)

    async def chat_stream(
        self, system: str, messages: List[Dict[str, str]]
    ) -> AsyncIterator[str]:
        chat_messages = [{"role": "system", "content": system}, *messages]
        stream = await self._chat_client.chat_completion(
            messages=chat_messages,
            max_tokens=1024,
            temperature=0.7,
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

    async def embed(self, text: str) -> List[float]:
        vec = await self._embed_client.feature_extraction(text)
        return vec.tolist() if hasattr(vec, "tolist") else list(vec)

    async def extract(self, prompt: str) -> list[dict]:
        response = await self._chat_client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1024,
            temperature=0.0,
        )
        return [{"name": "example", "value": response.choices[0].message.content}]


class LLMClient(LLMBackend):
    def __init__(self, backend: LLMBackend):
        self.backend = backend

    async def extract_memories(self, user_msg, assistant_msg, *, extract_prompt):
        prompt = extract_prompt.format(user_msg=user_msg, assistant_msg=assistant_msg)
        return await self.backend.extract(prompt)
