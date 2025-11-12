"""Custom exceptions for Cover-Me application.

This module defines the exception hierarchy used throughout the Cover-Me application
to provide clear, actionable error messages to users.
"""


class CoverMeException(Exception):
    """Base exception for all Cover-Me related errors."""
    pass


class ConfigurationError(CoverMeException):
    """Raised when there are configuration-related issues.
    
    This includes missing configuration files, invalid configuration values,
    missing API keys, or other setup-related problems.
    """
    pass


class APIError(CoverMeException):
    """Raised when there are API-related issues.
    
    This includes network connectivity problems, invalid API responses,
    authentication failures, or rate limiting issues.
    """
    pass


class SetupError(CoverMeException):
    """Raised when there are issues during the setup process.
    
    This includes problems creating configuration directories, writing files,
    or other setup-related failures.
    """
    pass


class ValidationError(CoverMeException):
    """Raised when validation of user input or configuration fails.
    
    This includes invalid file paths, malformed configuration values,
    or other validation-related issues.
    """
    pass