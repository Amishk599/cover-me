import os
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from .llm import create_llm_client
from .pdf_generator import PDFGenerator
from .config import ConfigManager
from .exceptions import ConfigurationError


class CoverLetterGenerator:
    """Main class for generating cover letters."""
    
    def __init__(self):
        """Initialize the cover letter generator.
        
        Raises:
            ConfigurationError: If no user configuration is found
        """
        # Load environment variables
        load_dotenv()
        
        # Initialize configuration manager
        self.config_manager = ConfigManager()
        
        # Check if user config exists, if not provide helpful message
        if not self.config_manager.has_user_config():
            raise ConfigurationError(
                "No configuration found. Run 'cover-me setup' to get started.\n"
                "This will create your configuration in ~/.cover-me/"
            )
        
        # Load configuration
        try:
            self.config = self.config_manager.load_config()
            self.config_manager.validate_config(self.config)
        except ConfigurationError as e:
            raise ConfigurationError(f"Configuration error: {e}")
        
        # Initialize LLM client
        self.llm_client = self._create_llm_client()
        
        # Initialize PDF generator
        self.pdf_generator = PDFGenerator()
        
        # Load system prompt and professional info
        self.system_prompt = self._load_file(self.config_manager.get_system_prompt_path())
        self.professional_info = self._load_file(self.config_manager.get_profile_path())
    
    
    def _load_file(self, file_path) -> str:
        """Load content from a text file.
        
        Args:
            file_path: Path to the file to load (Path object or string)
            
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
    
    def _create_llm_client(self):
        """Create and configure the appropriate LLM client.
        
        Returns:
            Configured LLM client instance
            
        Raises:
            ValueError: If unsupported LLM provider is specified
        """
        llm_config = self.config.get("llm", {})
        return create_llm_client(llm_config)
    
    def generate_from_clipboard(self) -> str:
        """Generate cover letter from clipboard content.
        
        Returns:
            Generated cover letter text
            
        Raises:
            ImportError: If pyperclip module is not installed
            ValueError: If clipboard is empty or invalid
            Exception: If clipboard access fails or cover letter generation fails
        """
        # Use shared clipboard validation
        from .utils.clipboard import get_and_validate_clipboard, ClipboardError
        
        try:
            job_description = get_and_validate_clipboard(self.config)
            
            # Generate cover letter using the base generate method
            cover_letter = self.generate(job_description)
            
            # Always save the generated cover letter
            self._save_cover_letter(cover_letter)
            
            return cover_letter
            
        except (ImportError, ClipboardError) as e:
            raise ValueError(str(e))
        except Exception as e:
            raise Exception(f"Failed to generate cover letter from clipboard: {str(e)}")

    
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
            output_dir = os.path.expanduser(self.config.get("output", {}).get("output_dir", "output"))
            
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
        template_name = self.config.get("pdf", {}).get("template", "modern_template.html")
        
        # Get template path from config manager
        template_path = self.config_manager.get_template_path(template_name)
        
        # Generate PDF
        return self.pdf_generator.generate_pdf(
            content=cover_letter,
            template_variables=template_vars,
            output_path=file_path,
            template_path=str(template_path)
        )