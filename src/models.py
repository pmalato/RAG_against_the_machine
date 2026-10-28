from pydantic import BaseModel, Field
from uuid import uuid4


class MinimalSource(BaseModel):
    file_path: str
    text: str = Field(min_length=1)
    first_character_index: int
    last_character_index: int


class Chunk(MinimalSource):
    text: str = Field(min_length=1)


class UnansweredQuestion(BaseModel):
    question_id: str = Field(default_factory=lambda: str(uuid4()))
    question: str


class AnsweredQuestion(UnansweredQuestion):
    sources: list[MinimalSource]
    answer: str


class RagDataset(BaseModel):
    rag_questions: list[AnsweredQuestion | UnansweredQuestion]


class MinimalSearchResults(BaseModel):
    question_id: str
    question: str
    retrieved_sources: list[MinimalSource]


class MinimalAnswer(MinimalSearchResults):
    answer: str


class StudentSearchResults(BaseModel):
    search_results: list[MinimalSearchResults]
    k: int


class StudentSearchResultsAndAnswer(BaseModel):
    search_results: list[MinimalAnswer]
    k: int
