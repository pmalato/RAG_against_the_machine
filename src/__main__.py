from .errors import RagError
from pydantic import ValidationError
from fire import Fire
from .cli import CLIConfig


def main() -> None:
    try:
        Fire(CLIConfig)
    except (KeyboardInterrupt, ValidationError,
            TypeError, ValueError, RagError) as error:
        print(error)


if __name__ == "__main__":
    main()
