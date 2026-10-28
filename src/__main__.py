from .chunker import Chunked
from .errors import RagError
from pydantic import ValidationError


def main() -> None:
    try:
        pro: Chunked = Chunked()
        pro.store_files()
        for f in pro.get_files():
            text: str = pro.file_reader(f)
            if f.suffix == ".md":
                pro.chunk_md(text, 2000)
    except (KeyboardInterrupt, ValidationError, RagError) as error:
        print(error)


if __name__ == "__main__":
    main()
