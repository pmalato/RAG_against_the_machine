from ast import parse
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
            sub_chunk: list[str] = "\n\n".split(chunk)
            for part in sub_chunk:
                if not self.is_chunk_valid(part):
                    small_chunk: list[str] = '\n'.split(part)
                    for piece in small_chunk:
                        if not self.is_chunk_valid(piece):
                            smaller: list[str] = ". ".split(piece)
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
            tree = parse(chunk, filename=file)
            lines: list[str] = chunk.splitlines(keepends=True)
            class_str: list[str] = []
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
