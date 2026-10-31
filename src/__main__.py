from .chunker import Chunked
from .models import Chunk
from .indexer import Indexer
from .errors import RagError
from pydantic import ValidationError


def personalized_print(chunk: Chunk) -> None:
    print(chunk.file_path, end="\t")
    # print(chunk.text)
    print(chunk.first_character_index, end="\t")
    print(chunk.last_character_index)


def main() -> None:
    try:
        pro: Chunked = Chunked()
        pro.chunk_files(2000)
        chunks: list[Chunk] = pro.get_processed()
        index: Indexer = Indexer()
        index.build_chunks(chunks)
        index.save_processed()
        test: Indexer = Indexer.load_processed()
        [personalized_print(chk) for chk in test.get_chunks()]
    except (KeyboardInterrupt, ValidationError, RagError) as error:
        print(error)


if __name__ == "__main__":
    main()
