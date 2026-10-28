from pathlib import Path
from .models import MinimalSource
from langchain_text_splitters import (
    Language,
    RecursiveCharacterTextSplitter
    )
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

    def chunk_md(
            self, file: Path, text: str,
            max_chunk_size: int) -> None:
        splitter = RecursiveCharacterTextSplitter.from_language(
            language=Language.MARKDOWN,
            chunk_size=max_chunk_size,
            chunk_overlap=int(max_chunk_size * 0.2),
            add_start_index=True)
        docs = splitter.create_documents([text])
        for d in docs:
            script: str = d.page_content
            start = d.metadata["start-index"]
            end = start + len(script)
            self._processed += [MinimalSource(
                file_path=str(file),
                text=script,
                first_character_index=start,
                last_character_index=end)]

    def chunk_py(
            self, file: Path, code: str,
            max_chunk_size: int) -> None:
        splitter = RecursiveCharacterTextSplitter.from_language(
            language=Language.PYTHON,
            chunk_size=max_chunk_size,
            chunk_overlap=(max_chunk_size * 0.2),
            add_start_index=True)
        docs = splitter.create_documents([code])
        for d in docs:
            script: str = d.page_content
            start: int = d.metadata["start_index"]
            end: int = start + len(script)
            self._processed += [MinimalSource(
                file_path=str(file),
                text=script,
                first_character_index=start,
                last_character_index=end)]

    def chunk_files(self, max_chunk_size: int) -> None:
        self.store_files()
        for f in self._files:
            text = self.file_reader(f)
            if f.suffix == ".txt" or f.suffix == ".md":
                self._processed += self.chunk_md(f, text, max_chunk_size)
            elif f.suffix == ".py":
                self._processed += self.chunk_py(f, text, max_chunk_size)
            else:
                raise InvalidFileError()

    def get_files(self) -> list[Path]:
        return self._files

    def get_processed(self) -> list[MinimalSource]:
        return self._processed
