class CLIConfig():
    def __init__(self) -> None:
        ...

    def index(self, max_chunk_size: int) -> None:
        ...

    def search(self, query: str, k: int = 10) -> None:
        ...

    def search_dataset(
            self, dataset_path: str,
            save_directory: str, k: int = 10) -> None:
        ...

    def answer(self, query: str, k: int = 10) -> None:
        ...

    def answer_dataset(
            self, student_search_results_path: str,
            save_directory: str, k: int = 10) -> None:
        ...

    def evaluate(
            self, student_search_results_path: str,
            dataset_path: str) -> None:
        ...
