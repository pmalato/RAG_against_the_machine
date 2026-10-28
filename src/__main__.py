from .chunker import Chunked
from .errors import RagError
from pydantic import ValidationError


def main() -> None:
    try:
        pro: Chunked = Chunked()
        pro.store_files()
        test = pro.get_files()
        print(len(test))
    except (KeyboardInterrupt, ValidationError, RagError) as error:
        print(error)


if __name__ == "__main__":
    main()
