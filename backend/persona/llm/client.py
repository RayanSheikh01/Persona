import asyncio
import json
import re
from dataclasses import dataclass, field
from typing import AsyncIterator, Dict, List, Protocol

from huggingface_hub import InferenceClient


class LLMBackend(Protocol):
    def chat_stream(
        self, system: str, messages: List[Dict[str, str]]
    ) -> AsyncIterator[str]: ...

    async def embed(self, text: str) -> List[float]: ...

    async def extract(self, prompt: str) -> list[dict]: ...


@dataclass
class FakeLLMBackend:
    chat_chunks: List[str] = field(default_factory=lambda: ["fake ", "response"])
    embedding: List[float] = field(default_factory=lambda: [0.0] * 768)
    extraction: List[dict] = field(default_factory=list)

    async def chat_stream(
        self, system: str, messages: List[Dict[str, str]]
    ) -> AsyncIterator[str]:
        for chunk in self.chat_chunks:
            yield chunk

    async def embed(self, text: str) -> List[float]:
        return list(self.embedding)

    async def extract(self, prompt: str) -> list[dict]:
        return list(self.extraction)


_FENCE = re.compile(r"^```(?:json)?\s*|\s*```$", re.IGNORECASE | re.MULTILINE)


def _strip_fences(text: str) -> str:
    return _FENCE.sub("", text).strip()


class HFBackend:
    def __init__(self, *, hf_token: str, chat_model: str, embed_model: str):
        self._client = InferenceClient(model=chat_model, token=hf_token)
        self._embed_model_name = embed_model
        self._embedder = None

    def _load_embedder(self):
        if self._embedder is None:
            from sentence_transformers import SentenceTransformer
            self._embedder = SentenceTransformer(self._embed_model_name)
        return self._embedder

    async def chat_stream(
        self, system: str, messages: List[Dict[str, str]]
    ) -> AsyncIterator[str]:
        chat_messages = [{"role": "system", "content": system}, *messages]
        queue: asyncio.Queue = asyncio.Queue()
        loop = asyncio.get_running_loop()

        def producer():
            try:
                for chunk in self._client.chat_completion(
                    messages=chat_messages,
                    stream=True,
                    max_tokens=1024,
                    temperature=0.7,
                ):
                    delta = chunk.choices[0].delta.content
                    if delta:
                        asyncio.run_coroutine_threadsafe(queue.put(delta), loop)
            except Exception as e:
                asyncio.run_coroutine_threadsafe(queue.put(e), loop)
            finally:
                asyncio.run_coroutine_threadsafe(queue.put(None), loop)

        task = asyncio.create_task(asyncio.to_thread(producer))
        try:
            while True:
                item = await queue.get()
                if item is None:
                    break
                if isinstance(item, Exception):
                    raise item
                yield item
        finally:
            await task

    async def embed(self, text: str) -> List[float]:
        embedder = await asyncio.to_thread(self._load_embedder)
        vec = await asyncio.to_thread(
            embedder.encode, text, normalize_embeddings=True
        )
        return vec.tolist()

    async def _chat_once(self, messages: list[dict]) -> str:
        def call():
            return self._client.chat_completion(
                messages=messages,
                stream=False,
                max_tokens=1024,
                temperature=0.2,
            )
        resp = await asyncio.to_thread(call)
        return resp.choices[0].message.content or ""

    async def extract(self, prompt: str) -> list[dict]:
        messages = [{"role": "user", "content": prompt}]
        text = await self._chat_once(messages)
        try:
            parsed = json.loads(_strip_fences(text))
            if isinstance(parsed, list):
                return parsed
        except (json.JSONDecodeError, ValueError):
            pass

        messages += [
            {"role": "assistant", "content": text},
            {
                "role": "user",
                "content": "Your previous reply was not valid JSON. Reply with only a JSON array.",
            },
        ]
        try:
            text = await self._chat_once(messages)
            parsed = json.loads(_strip_fences(text))
            if isinstance(parsed, list):
                return parsed
        except (json.JSONDecodeError, ValueError):
            pass
        return []


class LLMClient:
    def __init__(self, backend: LLMBackend):
        self.backend = backend

    def chat_stream(
        self, system: str, messages: List[Dict[str, str]]
    ) -> AsyncIterator[str]:
        return self.backend.chat_stream(system, messages)

    async def embed(self, text: str) -> List[float]:
        return await self.backend.embed(text)

    async def extract_memories(
        self, user_msg: str, assistant_msg: str, *, extract_prompt: str
    ) -> list[dict]:
        prompt = (
            f"{extract_prompt}\n\n"
            f"User message:\n{user_msg}\n\n"
            f"Assistant response:\n{assistant_msg}"
        )
        return await self.backend.extract(prompt)
