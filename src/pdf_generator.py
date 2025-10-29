import os
import re
from datetime import datetime
from typing import Dict, Any, Optional
from weasyprint import HTML, CSS


class PDFGenerator:
    """Handles PDF generation from HTML templates."""
    
    def __init__(self, template_dir: str = "templates"):
        """Initialize the PDF generator.
        
        Args:
            template_dir: Directory containing HTML templates
        """
        self.template_dir = template_dir
    
    def generate_pdf(
        self,
        content: str,
        template_variables: Dict[str, str],
        output_path: str,
        template_name: str = "default_template.html"
    ) -> str:
        """Generate a PDF from HTML template and content.
        
        Args:
            content: The main cover letter content
            template_variables: Variables to substitute in template
            output_path: Path where the PDF should be saved
            template_name: Name of the HTML template file
            
        Returns:
            Path to the generated PDF file
            
        Raises:
            FileNotFoundError: If template file doesn't exist
            Exception: If PDF generation fails
        """
        try:
            # Load and process the HTML template
            html_content = self._load_template(template_name)
            
            # Add the main content to template variables
            template_variables['cover_letter_content'] = self._format_content_as_html(content)
            
            # Substitute variables in template
            html_content = self._substitute_variables(html_content, template_variables)
            
            # Generate PDF
            self._create_pdf_from_html(html_content, output_path)
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Failed to generate PDF: {str(e)}")
    
    def _load_template(self, template_name: str) -> str:
        """Load HTML template from file.
        
        Args:
            template_name: Name of the template file
            
        Returns:
            HTML template content as string
            
        Raises:
            FileNotFoundError: If template file doesn't exist
        """
        template_path = os.path.join(self.template_dir, template_name)
        
        if not os.path.isfile(template_path):
            raise FileNotFoundError(f"Template file not found: {template_path}")
        
        try:
            with open(template_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            raise Exception(f"Failed to read template file: {str(e)}")
    
    def _substitute_variables(self, html_content: str, variables: Dict[str, str]) -> str:
        """Substitute template variables in HTML content.
        
        Args:
            html_content: HTML template content
            variables: Dictionary of variables to substitute
            
        Returns:
            HTML content with variables substituted
        """
        # Use regex to find and replace {{ variable_name }} patterns
        def replacer(match):
            var_name = match.group(1).strip()
            return variables.get(var_name, f"{{{{ {var_name} }}}}")  # Keep original if not found
        
        # Replace all {{ variable }} patterns
        return re.sub(r'\{\{\s*([^}]+)\s*\}\}', replacer, html_content)
    
    def _format_content_as_html(self, content: str) -> str:
        """Format plain text content as HTML paragraphs.
        
        Args:
            content: Plain text content
            
        Returns:
            HTML formatted content
        """
        if not content.strip():
            return ""
        
        # Split into paragraphs and wrap each in <p> tags
        paragraphs = content.strip().split('\n\n')
        html_paragraphs = []
        
        for paragraph in paragraphs:
            # Clean up whitespace and line breaks within paragraphs
            cleaned = ' '.join(paragraph.split())
            if cleaned:
                html_paragraphs.append(f"<p>{cleaned}</p>")
        
        return '\n'.join(html_paragraphs)
    
    def _create_pdf_from_html(self, html_content: str, output_path: str) -> None:
        """Create PDF file from HTML content.
        
        Args:
            html_content: HTML content to convert
            output_path: Path where PDF should be saved
            
        Raises:
            Exception: If PDF creation fails
        """
        try:
            # Ensure output directory exists
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            # Create PDF with optimization settings
            HTML(string=html_content).write_pdf(
                output_path,
                optimize_images=True,
                jpeg_quality=85,
                dpi=300  # High quality for printing
            )
            
        except Exception as e:
            raise Exception(f"Failed to create PDF: {str(e)}")
    
    def get_default_template_variables(self, config: Dict[str, Any]) -> Dict[str, str]:
        """Get default template variables from configuration.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Dictionary of default template variables
        """
        # Get current date
        current_date = datetime.now().strftime("%B %d, %Y")
        
        # Extract template variables from config, with sensible defaults
        template_vars = {
            'date': current_date,
            'applicant_name': '',
            'applicant_email': '',
            'applicant_phone': '',
            'professional_title': ''
        }
        
        # Override with any configured values
        pdf_config = config.get('pdf', {})
        if 'template_variables' in pdf_config:
            template_vars.update(pdf_config['template_variables'])
        
        return template_vars