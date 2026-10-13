"""Custom exceptions for the GraphRAG pipeline enforcing fail-fast boundaries."""


class GraphRAGException(Exception):
    """Base exception for all GraphRAG pipeline errors."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class EntityResolutionError(GraphRAGException):
    """Raised when an entity anchor cannot be resolved deterministically."""
    pass


class TraversalError(GraphRAGException):
    """Raised when topological graph traversal fails or violates invariants."""
    pass


class ModelInferenceError(GraphRAGException):
    """Raised when LLM synthesis fails or returns an error."""
    pass


class ModelAuthenticationError(ModelInferenceError):
    """Raised when Hugging Face API authentication fails (401)."""
    pass


class ModelRateLimitError(ModelInferenceError):
    """Raised when Hugging Face API rate limit is exceeded (429)."""
    pass


class GraphValidationError(GraphRAGException):
    """Raised when graph invariants (e.g., INV-UNBROKEN-ANCESTRY) are violated."""
    pass
