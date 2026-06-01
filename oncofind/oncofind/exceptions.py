"""Custom exceptions for oncofind."""

class OncofindError(Exception):
    """Base exception class for all oncofind errors."""
    pass


class DataNotDownloadedError(OncofindError):
    """Raised when analysis is run on cancer data that has not been downloaded yet."""
    pass


class InsufficientSamplesError(OncofindError):
    """Raised when there are fewer than 3 samples in one or both of the comparison groups."""
    pass


class GeneNotFoundError(OncofindError):
    """Raised when a specified gene symbol is not found in the dataset."""
    pass


class ClinicalVariableNotFoundError(OncofindError):
    """Raised when a requested clinical grouping variable is not available in the metadata."""
    pass


class APIError(OncofindError):
    """Raised when the GDC API returns an error or is unreachable."""
    pass


class AnalysisError(OncofindError):
    """Raised when an analysis step (like PyDESeq2 convergence or Batch correction) fails."""
    pass


class VisualizationError(OncofindError):
    """Raised when plotting or HTML report generation fails."""
    pass
