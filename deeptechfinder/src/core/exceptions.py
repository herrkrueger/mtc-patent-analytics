"""
Custom exceptions for DeepTechFinder Patent Analytics.
"""

class PatentAnalyticsError(Exception):
    """Base exception for patent analytics errors."""
    pass

class DataExtractionError(PatentAnalyticsError):
    """Raised when data extraction fails."""
    pass

class DataTransformationError(PatentAnalyticsError):
    """Raised when data transformation fails."""
    pass

class EPOOPSError(PatentAnalyticsError):
    """Raised when EPO OPS API calls fail."""
    pass

class AuthenticationError(EPOOPSError):
    """Raised when EPO OPS authentication fails."""
    pass

class RateLimitError(EPOOPSError):
    """Raised when EPO OPS rate limits are exceeded."""
    pass

class UniversityNotFoundError(DataExtractionError):
    """Raised when specified university is not found in dataset."""
    pass

class ExportError(PatentAnalyticsError):
    """Raised when data export fails."""
    pass

class ConfigurationError(PatentAnalyticsError):
    """Raised when configuration is invalid."""
    pass