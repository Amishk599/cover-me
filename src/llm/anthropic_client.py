import os
from typing import Dict, Any
from anthropic import Anthropic
from .base import LLMClient


class AnthropicClient(LLMClient):
    """Anthropic Claude API client for cover letter generation."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Anthropic client with configuration.
        
        Args:
            config: Dictionary containing Anthropic configuration parameters
        """
        super().__init__(config)
        
        # Initialize Anthropic client
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        
        self.client = Anthropic(
            api_key=api_key,
        )
        
        # Configuration parameters
        self.model = config.get("model", "claude-3-5-sonnet-20241022")
        self.max_tokens = config.get("max_tokens", 1000)
        self.temperature = config.get("temperature", 0.7)
    
    def generate_cover_letter(self, system_prompt: str, professional_info: str, job_description: str) -> str:
        """Generate a cover letter using Anthropic's Claude API.
        
        Args:
            system_prompt: Instructions for the AI on how to write the cover letter
            professional_info: The candidate's professional background and experience
            job_description: The job posting or requirements
            
        Returns:
            Generated cover letter as a string
            
        Raises:
            Exception: If the API call fails or returns an error
        """
        try:
            # Construct the user message
            user_message = f"""
Please generate a cover letter based on the following information:

**Job Description:**
{job_description}

**Professional Information:**
{professional_info}

Generate a professional cover letter that highlights the most relevant experience and skills for this position.
"""
            
            # Make API call
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )
            
            # Extract and return the generated cover letter
            if response.content and len(response.content) > 0:
                # Claude returns content as a list of content blocks
                content_text = ""
                for content_block in response.content:
                    if hasattr(content_block, 'text'):
                        content_text += content_block.text
                return content_text.strip()
            else:
                raise Exception("No response received from Anthropic API")
                
        except Exception as e:
            raise Exception(f"Anthropic API error: {str(e)}")
    
    def validate_api_key(self) -> bool:
        """Validate that the API key is properly configured and working.
        
        Returns:
            True if API key is valid, False otherwise
        """
        try:
            # Make a simple test API call
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=5,
                messages=[{"role": "user", "content": "Test"}]
            )
            return True
        except Exception:
            return False