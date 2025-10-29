from abc import ABC, abstractmethod
from typing import Dict, Any


def mask_api_key(api_key: str) -> str:
    """Safely display an API key by showing only first 4 and last 4 characters.
    
    Args:
        api_key: The API key to mask
        
    Returns:
        Masked API key string
    """
    if not api_key or len(api_key) < 8:
        return "****"
    return f"{api_key[:4]}...{api_key[-4:]}"


class LLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the LLM client with configuration.
        
        Args:
            config: Dictionary containing LLM configuration parameters
        """
        self.config = config
    
    @abstractmethod
    def generate_cover_letter(self, system_prompt: str, professional_info: str, job_description: str) -> str:
        """Generate a cover letter based on the provided inputs.
        
        Args:
            system_prompt: Instructions for the AI on how to write the cover letter
            professional_info: The candidate's professional background and experience
            job_description: The job posting or requirements
            
        Returns:
            Generated cover letter as a string
            
        Raises:
            Exception: If the API call fails or returns an error
        """
        pass
    
    @abstractmethod
    def validate_api_key(self) -> bool:
        """Validate that the API key is properly configured and working.
        
        Returns:
            True if API key is valid, False otherwise
        """
        pass
    
    @abstractmethod
    def get_provider_info(self) -> Dict[str, str]:
        """Get provider information for display/testing.
        
        Returns:
            Dictionary with provider name, model, and masked API key
        """
        pass