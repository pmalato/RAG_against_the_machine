from pathlib import Path


class Processed():
    def __init__(self) -> None:
        self._files: list[Path]
        self.store_files()

    def store_files(self) -> None:
        files: set[Path] = set(element for element in Path(
            "data/raw/vllm-0.10.1").rglob("*"))
        self._files = [x for x in sorted(files) if x.suffix in (
            ".py", ".txt", ".md")]

    def get_files(self) -> list[Path]:
        return self._files
