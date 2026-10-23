class RagError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class InvalidFileError(RagError):
    def __init__(self, message: str = "Only files ending with '.txt',"
                 " '.md' and '.py' should be accepted"):
        super().__init__(message)
