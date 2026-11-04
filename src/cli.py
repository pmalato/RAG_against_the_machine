from pathlib import Path
from json import load, dump, JSONDecodeError
from tqdm import tqdm
from .chunker import Chunked
from .indexer import Indexer
from .generator import (
    Generator,
    answer_aux,
    sources_to_chunks)
from .models import (
    Chunk,
    MinimalSource,
    MinimalSearchResults,
    MinimalAnswer,
    StudentSearchResults,
    StudentSearchResultsAndAnswer,
    AnsweredQuestion,
    RagDataset
    )
from .errors import (
    RagError,
    InvalidChunkSizeError,
    MissingDirectoryError,
    )

CODE: str = "dataset_code_public.json"
DOCS: str = "dataset_docs_public.json"
IOU_THRESHOLD: float = 0.05
RECALL_K: tuple[int, int, int, int] = (1, 3, 5, 10)


def iou(start_a: int, end_a: int, start_b: int, end_b: int) -> float:
    """Calculates the Intersection Over Union (IOU) for each give pair
    of text/code intervals
    """
    intersection: int = max(0, min(end_a, end_b) - max(start_a, start_b))
    union: int = (end_a - start_a) + (end_b - start_b) - intersection
    return intersection / union if union > 0 else 0.0


def question_recall(
        ref: list[MinimalSource], retrv: list[MinimalSource], k: int) -> float:
    top = retrv[:k]
    found = sum(
        1 for rf in ref if any(res.file_path == rf.file_path and iou(
            res.first_character_index, res.last_character_index,
            rf.first_character_index, rf.last_character_index
            ) > IOU_THRESHOLD for res in top))
    return found / len(ref)


class CLIConfig():
    """Responsible for hanlding all Fire inputs (from the terminal).
    This means that each method acts as its own isolated command having
    no connection whatsoever with each other. This is a design choice
    rather than a 'must follow' structure.
    """
    def index(self, max_chunk_size: int = 2000) -> None:
        """Takes all files in 'data/raw' accepting only '.md', '.txt'
        and '.py' formats. Using the LangChain module, separates every
        valid file into chunks with size up to inputed 'max_chunk_size'.
        These chunks are validated with the help of the pydantic module.
        Finally, uses bm25s module to store every chunk into 'data/processed/'.
        Adittional informative files are added in 'data/processed' folder
        as well.
        """
        if max_chunk_size <= 0 or max_chunk_size > 2000:
            raise InvalidChunkSizeError
        builder: Chunked = Chunked()
        builder.chunk_files(max_chunk_size)
        chunks: list[Chunk] = builder.get_processed()
        indexer: Indexer = Indexer()
        indexer.build_chunks(chunks)
        indexer.save_processed()

    def search(self, query: str, k: int = 10) -> None:
        """Return the top-k sources for a single query."""
        indexer: Indexer = Indexer.load_processed()
        chunks: list[Chunk] = indexer.search_aux(query, k)
        [print(
            f"{chk.file_path} [{chk.first_character_index}"
            f":{chk.last_character_index}]") for chk in chunks]

    def search_dataset(
            self, dataset_path: str,
            save_directory: str = "data/output/"
            "search_results/UnansweredQuestions", k: int = 10) -> None:
        """Run search over a whole dataset and write a StudentSearchResults
        JSON file.
        """
        if not save_directory.startswith("data/output/"):
            raise MissingDirectoryError(
                "Your answers must go to 'data/output/'")
        if not dataset_path:
            raise MissingDirectoryError("Invalid path for 'dataset_path'")
        if not save_directory:
            raise MissingDirectoryError("Invalid path for 'save_directory'")
        end: str = DOCS if dataset_path.endswith(DOCS) else CODE
        source: Path = Path(dataset_path)
        target: Path = Path(save_directory)
        indexer: Indexer = Indexer.load_processed()
        std_search_res: list[MinimalSearchResults] = []
        res: StudentSearchResults
        try:
            with open(source, encoding="utf-8") as file:
                data: dict[str, list[dict[str, str]]] = load(file)
            for d in data["rag_questions"]:
                id: str = d["question_id"]
                query: str = d["question"]
                chunks: list[MinimalSource] = [MinimalSource(
                    **chk.model_dump(exclude={"text"}))
                    for chk in indexer.search_aux(query, k)]
                std_search_res += [MinimalSearchResults(
                    question_id=id, question=query, retrieved_sources=chunks)]
            res = StudentSearchResults(search_results=std_search_res, k=k)
            target.mkdir(parents=True, exist_ok=True)
            with open(target / end, "w", encoding="utf-8") as resolve:
                dump(res.model_dump(), resolve)
            print(f"Saved student_search_results to '{save_directory}'")
        except OSError as e:
            print(e)

    def answer(self, query: str, k: int = 10) -> None:
        """Answer a single query using the retrieved context."""
        if not isinstance(k, int) or k <= 0 or not query.strip():
            raise ValueError("Invalid query or k value.")
        indexer: Indexer = Indexer.load_processed()
        chunks: list[Chunk] = indexer.search_aux(query, k)
        if not chunks:
            raise InvalidChunkSizeError("Empty chunks.")
        print(answer_aux(Generator(), query, chunks))

    def answer_dataset(
            self, student_search_results_path: str,
            save_directory: str, k: int = 10) -> None:
        """Generate answers for a dataset, producing a
        StudentSearchResultsAndAnswer JSON file.
        """
        if not student_search_results_path:
            raise MissingDirectoryError(
                "Invalid path for 'student_search_results_path'")
        if not save_directory:
            raise MissingDirectoryError("Invalid path for 'save_directory'")
        source: Path = Path(student_search_results_path)
        gen: Generator = Generator()
        reader = Chunked()
        cache: dict[str, str] = {}
        answers: list[MinimalAnswer] = []
        res: StudentSearchResultsAndAnswer
        try:
            with open(source, encoding="utf-8") as file:
                data: StudentSearchResults = (
                    StudentSearchResults.model_validate(load(file)))
        except OSError as e:
            raise OSError(f"Cannot read {e}")
        for item in tqdm(
                data.search_results, desc="Answering", unit="question"):
            chunks = sources_to_chunks(
                item.retrieved_sources, reader, cache)
            try:
                text = answer_aux(gen, item.question, chunks)
            except (RagError, RuntimeError):
                text = "No relevant information."
            answers.append(
                MinimalAnswer(
                    question=item.question,
                    question_id=item.question_id,
                    retrieved_sources=item.retrieved_sources,
                    answer=text))
        res = StudentSearchResultsAndAnswer(
            search_results=answers, k=k)
        output = Path(save_directory) / source.name
        try:
            output.parent.mkdir(parents=True, exist_ok=True)
            with open(output, "w", encoding="utf-8") as file:
                file.write(res.model_dump_json())
        except OSError as e:
            raise OSError(f"Cannot open file {e}")
        print(f"Saved student_search_results_and_answer to {output}")

    def evaluate(
            self, student_search_results_path: str,
            dataset_path: str) -> None:
        try:
            with open(student_search_results_path, encoding="utf-8") as file:
                student: StudentSearchResults = (
                    StudentSearchResults.model_validate(load(file)))
            with open(dataset_path, encoding="utf-8") as file2:
                truth: RagDataset = RagDataset.model_validate(load(file2))
        except (OSError, JSONDecodeError) as e:
            print(e)
            return
        retrv: dict[str, list[MinimalSource]] = {
            ret.question_id: ret.retrieved_sources
            for ret in student.search_results}
        questions: list[AnsweredQuestion] = [
            q for q in truth.rag_questions if isinstance(
                q, AnsweredQuestion) and q.sources]
        if not questions:
            print("No reference to evaluate with")
            return
        missing: int = sum(1 for q in questions if q.question_id not in retrv)
        print(f"Total number of questions evaluated: {len(questions)}")
        print(f"Missing questions: {missing}")
        for k in (x for x in RECALL_K if x <= student.k):
            scores: list[float] = [
                question_recall(q.sources, retrv.get(q.question_id, []), k)
                for q in questions]
            mean = sum(scores) / len(scores)
            print(f"Recall@{k}: {mean:.3f} ({mean * 100:.1f}%)")
