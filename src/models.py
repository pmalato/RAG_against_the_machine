from pydantic import BaseModel, Field
from uuid import uuid4


class MinimalSource(BaseModel):
    """A location in the corpus that supports an answer.

    Attributes:
        file_path: Path of the source file, written exactly as in the
            ingested corpus (e.g. ``data/raw/vllm-0.10.1/...``). It is
            compared verbatim by the grader.
        first_character_index: Index of the first character of the span.
        last_character_index: End index of the span (exclusive, like a
            Python slice).
    """
    file_path: str
    first_character_index: int
    last_character_index: int


class Chunk(MinimalSource):
    """A piece of a source file, stored together with its text.

    Internal model used by the chunker, the indexer and the generator.
    It is never written to the output files, which only carry
    ``MinimalSource`` objects.

    Attributes:
        text: Content of the chunk. It must not be empty.
    """
    text: str = Field(min_length=1)


class UnansweredQuestion(BaseModel):
    """A question without a reference answer.

    Attributes:
        question_id: Unique identifier of the question. A UUID4 is
            generated when none is provided.
        question: Text of the question.
    """
    question_id: str = Field(default_factory=lambda: str(uuid4()))
    question: str


class AnsweredQuestion(UnansweredQuestion):
    """A question with its ground-truth sources and answer.

    Attributes:
        sources: Reference locations that contain the answer.
        answer: Reference answer to the question.
    """
    sources: list[MinimalSource]
    answer: str


class RagDataset(BaseModel):
    """A dataset of RAG questions, answered or not.

    Attributes:
        rag_questions: The questions of the dataset.
    """
    rag_questions: list[AnsweredQuestion | UnansweredQuestion]


class MinimalSearchResults(BaseModel):
    """The retrieval result for a single question.

    Attributes:
        question_id: Identifier of the question (used to match it with
            the ground truth).
        question: Text of the question.
        retrieved_sources: Retrieved locations, best match first.
    """
    question_id: str
    question: str
    retrieved_sources: list[MinimalSource]


class MinimalAnswer(MinimalSearchResults):
    """A retrieval result together with the generated answer.

    Attributes:
        answer: Answer generated from the retrieved context.
    """
    answer: str


class StudentSearchResults(BaseModel):
    """Output of ``search_dataset``: retrieval results for a dataset.

    Attributes:
        search_results: One entry per question.
        k: Number of results requested per question.
    """
    search_results: list[MinimalSearchResults]
    k: int


class StudentSearchResultsAndAnswer(BaseModel):
    """Output of ``answer_dataset``: retrieval results plus answers.

    Attributes:
        search_results: One entry per question, including its answer.
        k: Number of results requested per question.
    """
    search_results: list[MinimalAnswer]
    k: int
