from .chunker import Chunked
from .errors import RagError
from pydantic import ValidationError


def main() -> None:
    try:
        pro: Chunked = Chunked()
        pro.chunk_files(2000)
        # chunks = pro.get_processed()
    except (KeyboardInterrupt, ValidationError, RagError) as error:
        print(error)


if __name__ == "__main__":
    main()
