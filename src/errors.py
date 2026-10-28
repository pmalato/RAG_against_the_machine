class RagError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class InvalidFileError(RagError):
    def __init__(self, message: str = "Only files ending with '.txt',"
                 " '.md' and '.py' should be accepted"):
        super().__init__(message)


class ReadingFilesError(RagError):
    def __init__(self, message: str = "Error while reading file"):
        super().__init__(message)


class InvalidChunkSizeError(RagError):
    def __init__(
            self, message: str = "Invalid size for chunk,"
            "must be between 1 - 2000"):
        super().__init__(message)
