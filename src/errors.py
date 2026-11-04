class RagError(Exception):
    """Main personalized exception for speficic project exceptions to
    inherit.
    """
    def __init__(self, message: str) -> None:
        """Defines and inherits the error properties."""
        super().__init__(message)


class InvalidFileError(RagError):
    """Reports in case invalid files have been forced to chunk."""
    def __init__(
            self, message: str = "Only files ending with '.txt',"
            " '.md' and '.py' should be accepted.") -> None:
        """Defines and inherits the error properties."""
        super().__init__(message)


class AccessFilesError(RagError):
    """Reports if file was unabled to be accessed."""
    def __init__(
            self, message: str = "Error while accessing file.") -> None:
        """Defines and inherits the error properties."""
        super().__init__(message)


class InvalidChunkSizeError(RagError):
    """Reports in case invalid chunk size has been attempted"""
    def __init__(
            self, message: str = "Invalid size for chunk,"
            "must be between 1 - 2000.") -> None:
        """Defines and inherits the error properties."""
        super().__init__(message)


class MissingattributesError(RagError):
    """Reports error for missing attributes"""
    def __init__(self, message: str = "Missing attributes.") -> None:
        """Defines and inherits the error properties."""
        super().__init__(message)


class MissingIndexError(RagError):
    """Reports error for missing index."""
    def __init__(self, message: str = "Missing index files.") -> None:
        """Defines and inherits the error properties."""
        super().__init__(message)


class MissingDirectoryError(RagError):
    """Reports error for missing directory."""
    def __init__(self, message: str = "Missing directory.") -> None:
        """Defines and inherits the error properties."""
        super().__init__(message)
