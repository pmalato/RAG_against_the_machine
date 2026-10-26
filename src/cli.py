from typing import Any


class CLIConfig():
    def __init__(self):
        ...

    def index(self, max_chun_size: int) -> None:
        ...

    def search(self, query: str, *params: Any, k: int = 10) -> None:
        ...

    def search_dataset(
            self, *params: Any, dataset_path: str,
            save_directory: str, k: int = 10) -> None:
        ...

    def answer(self, query: str, *params: Any, k: int = 10) -> None:
        ...

    def answer_dataset(
            self, *params: Any, dataset_path: str,
            save_directory: str, k: int = 10) -> None:
        ...

    def evaluate(
            self, *params: Any,
            student_search_results_path: str, dataset_path: str) -> None:
        ...
