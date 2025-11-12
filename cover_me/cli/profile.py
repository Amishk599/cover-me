import os
import sys
import subprocess
import shutil
import click

from ..config import ConfigManager
from ..exceptions import SetupError


def profile_command():
    """Open the professional profile for editing."""
    config_manager = ConfigManager()
    profile_file = config_manager.user_profile_file
    
    # Check if profile file exists
    if not profile_file.exists():
        raise SetupError(
            f"Profile file not found at {profile_file}.\n\n"
            "💡 Run 'cover-me setup' to create your profile."
        )
    
    # Detect and use appropriate editor
    editor = detect_editor()
    
    click.echo(f"📝 Opening {profile_file} in {editor}...")
    
    try:
        # Open the file in the detected editor
        if editor == 'open':  # macOS default app
            subprocess.run([editor, str(profile_file)], check=True)
        else:
            subprocess.run([editor, str(profile_file)], check=True)
            
        click.echo("✅ Profile opened successfully!")
        click.echo("\n💡 After editing:")
        click.echo("   • Save and close the file")
        click.echo("   • Run 'cover-me test' to verify your setup")
        click.echo("   • Generate a cover letter with 'cover-me generate'")
        
    except subprocess.CalledProcessError as e:
        click.echo(f"❌ Failed to open editor: {str(e)}", err=True)
        _show_manual_edit_instructions(profile_file)
        
    except FileNotFoundError:
        click.echo(f"❌ Editor not found: {editor}", err=True)
        _show_manual_edit_instructions(profile_file)
        
    except Exception as e:
        click.echo(f"❌ Unexpected error: {str(e)}", err=True)
        _show_manual_edit_instructions(profile_file)


def detect_editor() -> str:
    """Detect the user's preferred editor."""
    # Check environment variables first
    for env_var in ['VISUAL', 'EDITOR']:
        editor = os.environ.get(env_var)
        if editor and shutil.which(editor):
            return editor
    
    # Platform-specific defaults
    if sys.platform == 'darwin':  # macOS
        return 'open'  # Uses default app association
    elif sys.platform.startswith('linux'):
        # Try common editors in order of preference
        for editor in ['code', 'nano', 'vim', 'vi', 'emacs', 'gedit']:
            if shutil.which(editor):
                return editor
    elif sys.platform == 'win32':
        # Windows editors
        for editor in ['code', 'notepad', 'notepad++']:
            if editor == 'notepad' or shutil.which(editor):
                return editor
    
    # Fallback - vi should be available on most Unix systems
    return 'vi'


def _show_manual_edit_instructions(profile_file):
    """Show instructions for manual editing when editor fails."""
    click.echo("\n📝 Manual editing instructions:")
    click.echo(f"   1. Open this file in your preferred text editor:")
    click.echo(f"      {profile_file}")
    click.echo("   2. Replace the template placeholders with your information:")
    click.echo("      • [Your Company] → Your actual company")
    click.echo("      • [Achievement 1] → Your real achievements")
    click.echo("      • [Skill 1] → Your actual skills")
    click.echo("   3. Add detailed information about your experience")
    click.echo("   4. Save the file when done")
    click.echo("\n💡 The more detailed your profile, the better your cover letters!")