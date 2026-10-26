from ast import Module, parse, ClassDef, walk, FunctionDef
from pathlib import Path
from .errors import (
    InvalidFileError
    )


class Processed():
    def __init__(self) -> None:
        self._files: list[Path]
        self._processed: list[list[dict[Path, str]]] = []

    def store_files(self) -> None:
        files: set[Path] = set(element for element in Path(
            "data/raw/vllm-0.10.1").rglob("*"))
        self._files = [x for x in sorted(files) if x.suffix in (
            ".py", ".txt", ".md")]

    @staticmethod
    def is_chunk_valid(chunk: str) -> bool:
        return True if len(chunk) <= 2000 else False

    def chunk_txt(self, file: Path) -> list[dict[Path, str]]:
        res: list[dict[Path, str]] = []
        with open(file, "r") as text:
            chunk: str = text.read()
        if not self.is_chunk_valid(chunk):
            sub_chunk: list[str] = chunk.split("\n\n")
            for part in sub_chunk:
                if not self.is_chunk_valid(part):
                    small_chunk: list[str] = part.split("\n")
                    for piece in small_chunk:
                        if not self.is_chunk_valid(piece):
                            smaller: list[str] = piece.split(". ")
                            for phrase in smaller:
                                res += [{file: phrase}]
                        else:
                            res += [{file: piece}]
                else:
                    res += [{file: part}]
        else:
            res += [{file: chunk}]
        return res

    def chunk_md(self, file: Path) -> list[dict[Path, str]]:
        # res: list[dict[Path, str]] = []
        with open(file, "r") as text:
            return [{file: text.read()}]
        # return res

    def chunk_py(self, file: Path) -> list[dict[Path, str]]:
        res: list[dict[Path, str]] = []
        with open(file, "r") as text:
            chunk: str = text.read()
        if not self.is_chunk_valid(chunk):
            tree: Module = parse(chunk, filename=file)
            lines: list[str] = chunk.splitlines(keepends=True)
            for node in tree.body:
                if isinstance(node, ClassDef):
                    start = node.lineno - 1
                    end = node.end_lineno if hasattr(
                        node, "end_lineno") else len(lines)
                    class_text: str = "".join(lines[start:end])
                    if not self.is_chunk_valid(class_text):
                        for part in 
                    else:
                        res += [{file: class_text}]
        else:
            res += [{file: chunk}]
        return res

    def chunk_files(self) -> None:
        self.store_files()
        for f in self._files:
            if f.suffix == ".txt":
                self._processed += [self.chunk_txt(f)]
            elif f.suffix == ".md":
                self._processed += [self.chunk_md(f)]
            elif f.suffix == ".py":
                self._processed += [self.chunk_py(f)]
            else:
                raise InvalidFileError()

    def get_files(self) -> list[Path]:
        return self._files

    def get_processed(self) -> list[list[dict[Path, str]]]:
        return self._processed
