class PersonioETLError(Exception):
    """Base exception for Personio ETL."""
    pass

class ConfigError(PersonioETLError):
    """Raised when there is an issue with the configuration."""
    pass

class AuthenticationError(PersonioETLError):
    """Raised when authentication fails."""
    pass

class APIError(PersonioETLError):
    """Raised when an API request fails."""
    pass

class FileWriteError(PersonioETLError):
    """Raised when writing a file fails."""
    pass

class TransformationError(PersonioETLError):
    """Raised when data transformation fails."""
    pass
