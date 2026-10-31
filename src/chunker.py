from pathlib import Path
from tqdm import tqdm
from .models import Chunk
from langchain_text_splitters import (
    Language,
    RecursiveCharacterTextSplitter
    )
from .errors import (
    AccessFilesError,
    InvalidChunkSizeError
    )

LANGUAGES: dict[str, Language] = {
    ".py": Language.PYTHON,
    ".md": Language.MARKDOWN,
    ".txt": Language.MARKDOWN
}
MAX_ALLOWED_CHUNK_SIZE = 2000
OVERLAP_RATIO = 0.2


class Chunked():
    """Discovers, reads and chunks the corpus files."""
    def __init__(self, root: str = "data/raw") -> None:
        self._root: Path = Path(root)
        self._files: list[Path] = []
        self._processed: list[Chunk] = []
        self._skipped: list[Path] = []

    def collect_files(self) -> None:
        """Collects the files under the root, sorted."""
        self._files = [
            f for f in sorted(self._root.rglob("*"))
            if f.is_file() and f.suffix in LANGUAGES
        ]

    def file_reader(self, file: Path) -> str:
        """Return the raw content of a file (offsets stay untouched)."""
        try:
            with open(
                    file, encoding="utf-8",
                    errors="replace", newline="") as file_to_chunk:
                return file_to_chunk.read()
        except (OSError, UnicodeDecodeError):
            raise AccessFilesError

    @staticmethod
    def split_text(
            text: str, language: Language,
            max_chunk_size: int) -> list[tuple[str, int, int]]:
        """Split text into (content, start, end) tuples.

        The end index is exclusive, like a Python slice.
        """
        splitter = RecursiveCharacterTextSplitter.from_language(
            language=language,
            chunk_size=max_chunk_size,
            chunk_overlap=int(max_chunk_size * OVERLAP_RATIO),
            add_start_index=True)
        parts: list[tuple[str, int, int]] = []
        for doc in splitter.create_documents([text]):
            start = doc.metadata["start_index"]
            if start < 0:
                continue
            content: str = doc.page_content
            parts.append((content, start, start + len(content)))
        return parts

    def chunk_files(self, max_chunk_size: int) -> None:
        """Chunk every supported file with the given size limit."""
        if not isinstance(max_chunk_size, int) or \
                not (0 <= max_chunk_size <= MAX_ALLOWED_CHUNK_SIZE):
            raise InvalidChunkSizeError
        self.collect_files()
        self._processed = []
        self._skipped = []
        for file in tqdm(self._files, desc="Chunking", unit="file"):
            try:
                text: str = self.file_reader(file)
            except AccessFilesError:
                self._skipped += [file]
                continue
            language = LANGUAGES[file.suffix.lower()]
            for content, start, end in self.split_text(
                    text, language, max_chunk_size):
                self._processed += [Chunk(
                    file_path=file.as_posix(),
                    text=content,
                    first_character_index=start,
                    last_character_index=end)]

    def get_files(self) -> list[Path]:
        return self._files

    def get_processed(self) -> list[Chunk]:
        return self._processed
