from bm25s import BM25, tokenize
from .chunker import Chunk


class Indexer():
    def __init__(self, chunks: list[Chunk]) -> None:
        self._corpus: list[str] = [chk.text for chk in chunks]
        self._retriever: BM25 = BM25()

    def build_index(self) -> None:
        ...
