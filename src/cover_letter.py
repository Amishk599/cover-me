import os
import yaml
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from .llm.base import LLMClient
from .llm.openai_client import OpenAIClient
from .pdf_generator import PDFGenerator


class CoverLetterGenerator:
    """Main class for generating cover letters."""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the cover letter generator.
        
        Args:
            config_path: Path to the configuration YAML file
        """
        # Load environment variables
        load_dotenv()
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Initialize LLM client
        self.llm_client = self._create_llm_client()
        
        # Initialize PDF generator
        self.pdf_generator = PDFGenerator()
        
        # Load system prompt and professional info
        self.system_prompt = self._load_file("config/system_prompt.md")
        self.professional_info = self._load_file("config/professional_info.md")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            Configuration dictionary
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If config file is invalid YAML
        """
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Invalid YAML in configuration file: {e}")
    
    def _load_file(self, file_path: str) -> str:
        """Load content from a text file.
        
        Args:
            file_path: Path to the file to load
            
        Returns:
            File content as string
            
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except FileNotFoundError:
            raise FileNotFoundError(f"Required file not found: {file_path}")
    
    def _create_llm_client(self) -> LLMClient:
        """Create and configure the appropriate LLM client.
        
        Returns:
            Configured LLM client instance
            
        Raises:
            ValueError: If unsupported LLM provider is specified
        """
        provider = self.config.get("llm", {}).get("provider", "openai")
        llm_config = self.config.get("llm", {})
        
        if provider == "openai":
            return OpenAIClient(llm_config)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}")
    
    def generate_from_file(self, job_description_path: str, output_path: Optional[str] = None) -> str:
        """Generate cover letter from a job description file.
        
        Args:
            job_description_path: Path to file containing job description
            output_path: Optional path to save the generated cover letter
            
        Returns:
            Generated cover letter text
            
        Raises:
            FileNotFoundError: If job description file doesn't exist
        """
        # Load job description
        job_description = self._load_file(job_description_path)
        
        # Generate cover letter
        cover_letter = self.generate(job_description)
        
        # Save to file if output path specified or if configured to save
        if output_path or self.config.get("output", {}).get("save_to_file", True):
            self._save_cover_letter(cover_letter, output_path)
        
        return cover_letter
    
    def generate(self, job_description: str) -> str:
        """Generate cover letter from job description text.
        
        Args:
            job_description: The job description or requirements
            
        Returns:
            Generated cover letter text
            
        Raises:
            Exception: If cover letter generation fails
        """
        if not job_description.strip():
            raise ValueError("Job description cannot be empty")
        
        try:
            # Validate API connection
            if not self.llm_client.validate_api_key():
                raise Exception("Invalid API key or connection failed")
            
            # Generate cover letter
            cover_letter = self.llm_client.generate_cover_letter(
                system_prompt=self.system_prompt,
                professional_info=self.professional_info,
                job_description=job_description
            )
            
            return cover_letter
            
        except Exception as e:
            raise Exception(f"Failed to generate cover letter: {str(e)}")
    
    def _save_cover_letter(self, cover_letter: str, output_path: Optional[str] = None) -> str:
        """Save cover letter to file.
        
        Args:
            cover_letter: The generated cover letter text
            output_path: Optional specific path to save to
            
        Returns:
            Path where the file was saved
        """
        output_format = self.config.get("output", {}).get("format", "text")
        
        if output_path:
            file_path = output_path
        else:
            # Generate timestamped filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = self.config.get("output", {}).get("output_dir", "output")
            
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            
            # Set file extension based on format
            extension = "pdf" if output_format == "pdf" else "txt"
            file_path = os.path.join(output_dir, f"cover_letter_{timestamp}.{extension}")
        
        # Save based on format
        if output_format == "pdf":
            return self._save_as_pdf(cover_letter, file_path)
        else:
            return self._save_as_text(cover_letter, file_path)
    
    def _save_as_text(self, cover_letter: str, file_path: str) -> str:
        """Save cover letter as text file.
        
        Args:
            cover_letter: The generated cover letter text
            file_path: Path to save the file
            
        Returns:
            Path where the file was saved
        """
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(cover_letter)
        return file_path
    
    def _save_as_pdf(self, cover_letter: str, file_path: str) -> str:
        """Save cover letter as PDF file.
        
        Args:
            cover_letter: The generated cover letter text
            file_path: Path to save the PDF
            
        Returns:
            Path where the file was saved
        """
        # Get template variables from config
        template_vars = self.pdf_generator.get_default_template_variables(self.config)
        
        # Get template name from config
        template_name = self.config.get("pdf", {}).get("template", "default_template.html")
        
        # Generate PDF
        return self.pdf_generator.generate_pdf(
            content=cover_letter,
            template_variables=template_vars,
            output_path=file_path,
            template_name=template_name
        )