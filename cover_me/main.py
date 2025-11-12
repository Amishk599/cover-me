import sys
import click
from dotenv import load_dotenv

from .cli import setup_command, configure_command, profile_command, test_command, generate_command


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """Generate professional cover letters using AI.
    
    This tool helps you create personalized cover letters by reading job descriptions
    from your clipboard and generating tailored responses using AI.
    
    First-time setup: Run 'cover-me setup' to configure your preferences.
    """
    # Load environment variables
    load_dotenv()
    
    # If no subcommand is provided, default to generate
    if ctx.invoked_subcommand is None:
        ctx.invoke(generate_command)


@cli.command()
def setup():
    """Set up Cover-Me with your preferences and API keys.
    
    This interactive wizard will guide you through:
    - Choosing your AI provider (OpenAI or Anthropic)
    - Configuring your API key
    - Setting up your professional information
    - Configuring output preferences
    
    Your configuration will be saved to ~/.cover-me/
    """
    setup_command()


@cli.command()
def generate():
    """Generate a cover letter from clipboard content.
    
    This command reads a job description from your clipboard and generates
    a personalized cover letter based on your professional profile.
    
    Make sure you have:
    1. Copied a job description to your clipboard
    2. Completed setup (run 'cover-me setup' if needed)
    """
    generate_command()


@cli.command()
def configure():
    """Modify your Cover-Me configuration.
    
    Interactively change your settings such as:
    - AI provider and model
    - Output format and location
    - API keys
    
    Your current settings will be shown as defaults.
    """
    configure_command()


@cli.command()
def profile():
    """Edit your professional profile.
    
    Opens your detailed professional profile (skills, experience, education)
    in your system's default editor.
    
    The profile is stored at ~/.cover-me/profile.md
    """
    profile_command()


@cli.command()
def test():
    """Test your Cover-Me configuration.
    
    Validates:
    - Configuration file integrity
    - API key connectivity
    - Professional profile existence
    
    Use this command to troubleshoot any setup issues.
    """
    test_command()


def main():
    """Main entry point for the Cover-Me CLI."""
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("\nOperation cancelled by user.", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()