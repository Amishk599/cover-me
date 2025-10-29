"""
Clipboard utility functions for validating and accessing clipboard content.
"""

from typing import Dict, Any, Optional


class ClipboardError(Exception):
    """Custom exception for clipboard-related errors."""
    pass


def validate_clipboard_content(content: str, max_size_bytes: int = 50000) -> str:
    """Validate clipboard content.
    
    Args:
        content: The clipboard content to validate
        max_size_bytes: Maximum allowed size in bytes
        
    Returns:
        Cleaned content string
        
    Raises:
        ClipboardError: If content is invalid
    """
    # Check if content is empty
    if not content or not content.strip():
        raise ClipboardError("Clipboard is empty. Please copy a job description to the clipboard first.")
    
    # Clean and validate the content
    content = content.strip()
    
    # Check size limit
    if len(content) > max_size_bytes:
        size_kb = max_size_bytes // 1000
        raise ClipboardError(f"Clipboard content is too large (>{size_kb}KB). Please use file input for large job descriptions.")
    
    return content


def get_and_validate_clipboard(config: Optional[Dict[str, Any]] = None) -> str:
    """Get content from clipboard and validate it.
    
    Args:
        config: Configuration dictionary containing clipboard settings
        
    Returns:
        Validated clipboard content
        
    Raises:
        ImportError: If pyperclip module is not installed
        ClipboardError: If clipboard access fails or content is invalid
    """
    try:
        import pyperclip
    except ImportError:
        raise ImportError("pyperclip module required for clipboard functionality. Install with: pip install pyperclip")
    
    try:
        # Get content from clipboard
        content = pyperclip.paste()
        
        # Get max size from config or use default
        max_size = 50000  # Default 50KB
        if config:
            max_size = config.get("clipboard", {}).get("max_size_bytes", 50000)
        
        # Validate content
        return validate_clipboard_content(content, max_size)
        
    except Exception as e:
        if isinstance(e, (ImportError, ClipboardError)):
            raise
        else:
            raise ClipboardError(f"Failed to access clipboard: {str(e)}")