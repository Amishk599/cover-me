"""Cover-Me: Generate professional cover letters using AI."""

__version__ = "1.0.0"
__author__ = "Amish Kushwaha"
__email__ = "amishkushwaha59@gmail.com"

from .exceptions import (
    CoverMeException,
    ConfigurationError,
    APIError,
    SetupError,
    ValidationError,
)

__all__ = [
    "CoverMeException",
    "ConfigurationError", 
    "APIError",
    "SetupError",
    "ValidationError",
]