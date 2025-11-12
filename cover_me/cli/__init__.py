"""CLI module for Cover-Me application commands."""

from .setup import setup_command
from .configure import configure_command
from .profile import profile_command
from .test import test_command
from .generate import generate_command

__all__ = [
    "setup_command",
    "configure_command", 
    "profile_command",
    "test_command",
    "generate_command"
]