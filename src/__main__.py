from .chunker import Chunked
from .errors import RagError
from pydantic import ValidationError


def main() -> None:
    try:
        pro: Chunked = Chunked()
        pro.chunk_files(2000)
        [print(x.first_character_index, x.last_character_index)
         for x in pro.get_processed()]
    except (KeyboardInterrupt, ValidationError, RagError) as error:
        print(error)


if __name__ == "__main__":
    main()
