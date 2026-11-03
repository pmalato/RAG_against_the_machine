from re import sub, S
from typing import Any
from transformers import AutoTokenizer, AutoModelForCausalLM
from .models import Chunk
from .indexer import Indexer
from .errors import (
    RagError,
    InvalidChunkSizeError)


CHUNKS_THRESHOLD: int = 256


def build_message(question: str, chunks: list[Chunk]) -> list[dict[str, str]]:
    """Builds the chat messages for the llm model."""
    context: str = "\n\n".join(
        f"[{i}] {chk.file_path}\n{chk.text}"
        for i, chk in enumerate(chunks, start=1))
    system: str = (
        "You answer questions about the vLLM codebase. "
        "Use only the provided context. If the context does not "
        "contain the answer, say so. Be concise.")
    user: str = f"Context:\n{context}\n\nQuestion:\n{question}"
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user}]


def answer_aux(query: str, k: int = 10) -> str:
    """Answer a single query using the retrieved context."""
    if not isinstance(k, int) or k <= 0 or not query.strip():
        raise ValueError("invalid query or k for answer CLI command.")
    try:
        indexer: Indexer = Indexer.load_processed()
        chunks: list[Chunk] = indexer.search(query, k)
        if not chunks:
            raise InvalidChunkSizeError("No valid information found.")
        prompt: list[dict[str, str]] = build_message(
            query, chunks[:CHUNKS_THRESHOLD])
        return Generator().generate(prompt)
    except RagError:
        raise RagError("Something went wrong with the answer")


class Generator():
    def __init__(self, model_name: str = "Qwen/Qwen3-0.6B") -> None:
        self._tokenizer = AutoTokenizer.from_pretrained(model_name)
        self._model: Any = AutoModelForCausalLM.from_pretrained(model_name)

    def generate(
            self, messages: list[dict[str, str]],
            max_new_tokens: int = 256) -> str:
        text = self._tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True,
            enable_thinking=False)
        inputs = self._tokenizer(text, return_tensors="pt")
        output = self._model.generate(
            **inputs, max_new_tokens=max_new_tokens, do_sample=False)
        new_tokens = output[0][inputs["input_ids"].shape[1]:]
        answer = self._tokenizer.decode(new_tokens, skip_special_tokens=True)
        return sub(r"<think>.*?</think>", "", str(answer), flags=S).strip()
