# from ast import Module, parse, ClassDef, walk, FunctionDef
from pathlib import Path
from .models import MinimalSource
from .errors import (
    InvalidFileError,
    ReadingFilesError
    )


class Chunked():
    def __init__(self) -> None:
        self._files: list[Path]
        self._processed: list[MinimalSource] = []

    def store_files(self) -> None:
        files: set[Path] = set(element for element in Path(
            "data/raw/vllm-0.10.1").rglob("*"))
        self._files = [x for x in sorted(files) if x.suffix in (
            ".py", ".txt", ".md")]

    def file_reader(self, file: Path) -> str:
        try:
            with open(
                    file, encoding="utf-8",
                    errors="replace", newline="") as file_to_chunk:
                return str(file_to_chunk)
        except (OSError, UnicodeDecodeError):
            raise ReadingFilesError

    def chunk_txt(self, text: str, max_chunk_size: int) -> list[MinimalSource]:
        return []

    def chunk_py(self, text: str, max_chunk_size: int) -> list[MinimalSource]:
        return []

    def chunk_files(self, max_chunk_size: int) -> None:
        self.store_files()
        for f in self._files:
            text = self.file_reader(f)
            if f.suffix == ".txt" or f.suffix == ".md":
                self._processed += self.chunk_txt(text, max_chunk_size)
            elif f.suffix == ".py":
                self._processed += self.chunk_py(text, max_chunk_size)
            else:
                raise InvalidFileError()

    def get_files(self) -> list[Path]:
        return self._files

    def get_processed(self) -> list[MinimalSource]:
        return self._processed
