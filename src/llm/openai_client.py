import os
from typing import Dict, Any
from openai import OpenAI
from .base import LLMClient


class OpenAIClient(LLMClient):
    """OpenAI API client for cover letter generation."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize OpenAI client with configuration.
        
        Args:
            config: Dictionary containing OpenAI configuration parameters
        """
        super().__init__(config)
        
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client = OpenAI(
            api_key=api_key,
            organization=os.getenv("OPENAI_ORG_ID"),  # Optional
            project=os.getenv("OPENAI_PROJECT_ID"),   # Optional
        )
        
        # Configuration parameters
        self.model = config.get("model", "gpt-4o")
        self.max_tokens = config.get("max_tokens", 1000)
        self.temperature = config.get("temperature", 0.7)
    
    def generate_cover_letter(self, system_prompt: str, professional_info: str, job_description: str) -> str:
        """Generate a cover letter using OpenAI's API.
        
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
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            # Extract and return the generated cover letter
            if response.choices and response.choices[0].message:
                return response.choices[0].message.content.strip()
            else:
                raise Exception("No response received from OpenAI API")
                
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def validate_api_key(self) -> bool:
        """Validate that the API key is properly configured and working.
        
        Returns:
            True if API key is valid, False otherwise
        """
        try:
            # Make a simple test API call
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=5
            )
            return True
        except Exception:
            return False