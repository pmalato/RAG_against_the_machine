from .processed import Processed
from .errors import RagError
from pydantic import ValidationError


def main() -> None:
    try:
        pro: Processed = Processed()
        pro.chunk_files()
        test = pro.get_processed()
        [print(x) for x in test[156]]
    except (KeyboardInterrupt, ValidationError, RagError) as error:
        print(error)


if __name__ == "__main__":
    main()
