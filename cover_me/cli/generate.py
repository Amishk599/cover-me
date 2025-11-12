import sys
import click

from ..cover_letter import CoverLetterGenerator
from ..config import ConfigManager
from ..exceptions import ConfigurationError, APIError


def generate_command():
    """Generate a cover letter from clipboard content."""
    try:
        # Early check for configuration and API keys
        config_manager = ConfigManager()
        config_manager.check_api_keys_early()
        
        # Initialize the cover letter generator
        generator = CoverLetterGenerator()
        
        # Generate cover letter from clipboard
        click.echo("📋 Reading job description from clipboard...")
        cover_letter = generator.generate_from_clipboard()
        
        # Show success message
        click.echo("\n✅ Cover letter generated successfully!")
        click.echo("📄 Check your configured output directory for the generated file.")
        
    except ConfigurationError as e:
        # Handle configuration errors with helpful guidance
        click.echo("❌ Configuration Error:", err=True)
        click.echo(f"   {str(e)}", err=True)
        sys.exit(1)
        
    except APIError as e:
        # Handle API-related errors
        click.echo("❌ API Error:", err=True)
        click.echo(f"   {str(e)}", err=True)
        click.echo("\n💡 To fix this:", err=True)
        click.echo("   1. Check your internet connection", err=True)
        click.echo("   2. Verify your API key is valid", err=True)
        click.echo("   3. Run 'cover-me test' to diagnose issues", err=True)
        sys.exit(1)
        
    except ValueError as e:
        # Handle clipboard or input validation errors
        click.echo(f"❌ Input Error: {str(e)}", err=True)
        click.echo("\n💡 Make sure you have:", err=True)
        click.echo("   1. Copied a job description to your clipboard", err=True) 
        click.echo("   2. The clipboard content is not empty", err=True)
        sys.exit(1)
        
    except Exception as e:
        # Handle any other errors
        click.echo(f"❌ Error: {str(e)}", err=True)
        click.echo("\n💡 If this persists:", err=True)
        click.echo("   1. Run 'cover-me test' to check your configuration", err=True)
        click.echo("   2. Try 'cover-me setup' to reconfigure", err=True)
        sys.exit(1)