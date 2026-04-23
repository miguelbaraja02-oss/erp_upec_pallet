class IAError(Exception):
    """Base exception for IA app errors."""


class IAConfigurationError(IAError):
    """Raised when IA settings are invalid."""


class IAProviderError(IAError):
    """Raised when the configured IA provider fails."""
