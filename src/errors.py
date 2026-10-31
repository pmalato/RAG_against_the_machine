class RagError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class InvalidFileError(RagError):
    def __init__(self, message: str = "Only files ending with '.txt',"
                 " '.md' and '.py' should be accepted.") -> None:
        super().__init__(message)


class AccessFilesError(RagError):
    def __init__(self, message: str = "Error while accessing file."):
        super().__init__(message)


class InvalidChunkSizeError(RagError):
    def __init__(
            self, message: str = "Invalid size for chunk,"
            "must be between 1 - 2000.") -> None:
        super().__init__(message)


class MissingattributesError(RagError):
    def __init__(self, message: str = "Missing attributes.") -> None:
        super().__init__(message)


class MissingIndexError(RagError):
    def __init__(self, message: str = "Missing index files.") -> None:
        super().__init__(message)


class MissingDirectoryError(RagError):
    def __init__(self, message: str = "Missing directory.") -> None:
        super().__init__(message)
