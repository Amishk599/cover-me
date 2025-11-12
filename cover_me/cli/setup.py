import os
import sys
from pathlib import Path
from typing import Dict, Any, Tuple

import click
import yaml

from ..config import ConfigManager
from ..exceptions import ConfigurationError, SetupError, APIError
from ..llm import create_llm_client


def setup_command():
    """Interactive setup wizard for Cover-Me configuration."""
    click.echo("🚀 Welcome to Cover-Me! Let's set up your profile and preferences.")
    click.echo("This will only take a few minutes.\n")
    
    config_manager = ConfigManager()
    
    # Check if config already exists
    if config_manager.has_user_config():
        if not click.confirm("Configuration already exists. Do you want to overwrite it?"):
            click.echo("Setup cancelled.")
            return
    
    try:
        # Step 1: LLM Provider Selection
        click.echo("📡 Step 1: AI Provider Setup")
        llm_config = select_llm_provider()
        
        # Step 2: API Key Configuration
        click.echo("\n🔑 Step 2: API Key Configuration")
        configure_api_key_environment(llm_config['provider'])
        
        # Step 3: Professional Information Collection
        click.echo("\n👤 Step 3: Professional Information")
        user_config = collect_professional_info()
        
        # Step 4: Output Preferences
        click.echo("\n📄 Step 4: Output Preferences")
        output_config = configure_output_preferences()
        
        # Step 5: Save Configuration
        click.echo("\n💾 Step 5: Saving Configuration")
        complete_config = {
            'user': user_config,
            'llm': llm_config,
            'output': output_config
        }
        
        save_configuration(config_manager, complete_config)
        
        # Step 6: Create Profile Template
        create_profile_template(config_manager, user_config)
        
        # Success message
        click.echo("\n✅ Setup complete! Your configuration has been saved to ~/.cover-me/")
        click.echo("\n📝 Next steps:")
        click.echo("   1. Edit your detailed professional profile:")
        click.echo("      cover-me profile")
        click.echo("   2. Test your setup:")
        click.echo("      cover-me test")
        click.echo("   3. Generate your first cover letter:")
        click.echo("      cover-me generate")
        click.echo("\n💡 Copy a job description to your clipboard, then run 'cover-me' to generate!")
        
    except KeyboardInterrupt:
        click.echo("\n\nSetup cancelled by user.")
        sys.exit(1)
    except (ConfigurationError, SetupError, APIError) as e:
        click.echo(f"\n❌ Setup failed: {str(e)}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"\n❌ Unexpected error during setup: {str(e)}", err=True)
        click.echo("Please try again or report this issue.", err=True)
        sys.exit(1)


def select_llm_provider() -> Dict[str, Any]:
    """Provider selection with model choice."""
    providers = {
        'openai': {
            'name': 'OpenAI',
            'models': [
                ('gpt-4.1-mini', 'GPT-4.1 Mini (Recommended)'),
                ('gpt-4.1-nano', 'GPT-4.1 Nano (Cheapest)'),
                ('gpt-4o-mini', 'GPT-4o Mini'),
                ('gpt-4.1', 'GPT-4.1')
            ]
        },
        'anthropic': {
            'name': 'Anthropic',
            'models': [
                ('claude-3-5-haiku-latest', 'Claude 3.5 Haiku (Cheapest)'),
                ('claude-haiku-4-5-20251001', 'Claude 4.5 Haiku (Recommended)'),
                ('claude-sonnet-4-5-20250929', 'Claude 4.5 Sonnet')
            ]
        }
    }
    
    click.echo("Which AI provider would you like to use?")
    choices = []
    for i, (key, info) in enumerate(providers.items(), 1):
        click.echo(f"[{i}] {info['name']}")
        choices.append(key)
    
    while True:
        choice = click.prompt("\nChoice", type=click.IntRange(1, len(choices)))
        provider_key = choices[choice - 1]
        break
    
    # Model selection
    provider_info = providers[provider_key]
    click.echo(f"\nWhich {provider_info['name']} model would you like to use?")
    
    for i, (model_id, description) in enumerate(provider_info['models'], 1):
        click.echo(f"[{i}] {description}")
    
    while True:
        model_choice = click.prompt("\nChoice", type=click.IntRange(1, len(provider_info['models'])))
        model_id = provider_info['models'][model_choice - 1][0]
        break
    
    return {
        'provider': provider_key,
        'model': model_id,
        'max_tokens': 1000,
        'temperature': 0.7
    }


def configure_api_key_environment(provider: str) -> None:
    """Guide user to set up API key environment variables."""
    provider_name = "OpenAI" if provider == "openai" else "Anthropic"
    env_var = "OPENAI_API_KEY" if provider == "openai" else "ANTHROPIC_API_KEY"
    api_url = "https://platform.openai.com/api-keys" if provider == "openai" else "https://console.anthropic.com/"
    
    # Check if API key is already set
    if env_var in os.environ:
        click.echo(f"✅ {provider_name} API key found in environment variable {env_var}")
        # Test the existing key
        click.echo("🔄 Testing API connection...")
        if test_api_connection_from_env(provider):
            click.echo("✅ Success! API key is valid.")
            return
        else:
            click.echo("❌ API key validation failed. Please check your key.")
    
    # Guide user to set up environment variable
    click.echo(f"📋 {provider_name} API Key Setup Required")
    click.echo(f"You need to set up your {provider_name} API key as an environment variable.")
    click.echo(f"\\n🌐 Get your API key from: {api_url}")
    click.echo(f"\\n🔧 Set the environment variable {env_var}:")
    click.echo("\\n   For bash/zsh (add to ~/.bashrc or ~/.zshrc):")
    click.echo(f"   export {env_var}='your-api-key-here'")
    click.echo("\\n   For fish shell (add to ~/.config/fish/config.fish):")
    click.echo(f"   set -x {env_var} 'your-api-key-here'")
    click.echo("\\n   Or set it temporarily for this session:")
    click.echo(f"   export {env_var}='your-api-key-here'")
    
    if click.confirm(f"\\nHave you set the {env_var} environment variable?"):
        # Reload environment and test
        if env_var in os.environ:
            click.echo("🔄 Testing API connection...")
            if test_api_connection_from_env(provider):
                click.echo("✅ Success! API key is valid.")
                return
            else:
                raise ConfigurationError(f"API key validation failed for {provider_name}")
        else:
            raise ConfigurationError(
                f"Environment variable {env_var} not found. "
                f"Please set it and restart your terminal, then run 'cover-me setup' again."
            )
    else:
        raise SetupError(
            f"Setup cannot continue without {provider_name} API key. "
            f"Please set the {env_var} environment variable and run 'cover-me setup' again."
        )


def test_api_connection_from_env(provider: str) -> bool:
    """Test API connection using environment variables."""
    try:
        # Create a minimal config for testing
        test_config = {
            'provider': provider,
            'model': 'gpt-4o-mini' if provider == 'openai' else 'claude-3-5-haiku-20241022',
            'max_tokens': 10,
            'temperature': 0.7
        }
        
        client = create_llm_client(test_config)
        result = client.validate_api_key()
        return result
                
    except Exception as e:
        click.echo(f"Connection test error: {str(e)}")
        return False


def collect_professional_info() -> Dict[str, str]:
    """Collect basic professional information."""
    click.echo("Please provide your professional contact information:")
    
    user_info = {}
    
    user_info['name'] = click.prompt("Full Name").strip()
    user_info['email'] = click.prompt("Email").strip()
    user_info['phone'] = click.prompt("Phone (optional)", default="").strip()
    user_info['title'] = click.prompt("Professional Title").strip()
    
    # Optional social links
    linkedin = click.prompt("LinkedIn URL (optional)", default="").strip()
    if linkedin and not linkedin.startswith(('http://', 'https://')):
        linkedin = f"https://linkedin.com/in/{linkedin}"
    user_info['linkedin'] = linkedin
    
    github = click.prompt("GitHub URL (optional)", default="").strip() 
    if github and not github.startswith(('http://', 'https://')):
        github = f"https://github.com/{github}"
    user_info['github'] = github
    
    return user_info


def configure_output_preferences() -> Dict[str, Any]:
    """Configure output format and location preferences."""
    # Output format
    click.echo("Select your preferred output format:")
    click.echo("[1] PDF (recommended)")
    click.echo("[2] Plain text")
    
    format_choice = click.prompt("Choice", type=click.IntRange(1, 2))
    output_format = "pdf" if format_choice == 1 else "text"
    
    # Output directory
    default_dir = "~/Desktop/cover-letters"
    output_dir = click.prompt("Save location", default=default_dir).strip()
    
    return {
        'format': output_format,
        'save_to_file': True,
        'output_dir': output_dir
    }


def save_configuration(config_manager: ConfigManager, config: Dict[str, Any]) -> None:
    """Save configuration to user directory."""
    try:
        # Copy default templates to user directory first
        config_manager.copy_defaults_to_user()
        
        config_manager.save_config(config)
        click.echo(f"✅ Configuration saved to {config_manager.user_config_file}")
        click.echo("💡 Note: API keys are read from environment variables, not stored in config files")
    except Exception as e:
        raise SetupError(f"Failed to save configuration: {str(e)}")


def create_profile_template(config_manager: ConfigManager, user_info: Dict[str, str]) -> None:
    """Create initial professional profile template."""
    try:
        config_manager.ensure_user_config_dir()
        
        # Create profile template
        profile_content = f"""# Professional Profile

## Summary
Write a brief professional summary highlighting your key skills and experience.

## Experience
### Current/Recent Position
- **Company**: [Your Company]
- **Title**: {user_info.get('title', '[Your Title]')}
- **Duration**: [Start Date] - Present
- **Key Achievements**:
  - [Achievement 1]
  - [Achievement 2]
  - [Achievement 3]

### Previous Experience
Add your previous roles and key accomplishments here.

## Skills
### Technical Skills
- [Skill 1]
- [Skill 2] 
- [Skill 3]

### Soft Skills
- [Skill 1]
- [Skill 2]
- [Skill 3]

## Education
### Degree
- **Institution**: [University Name]
- **Degree**: [Degree Type and Major]
- **Year**: [Graduation Year]

## Certifications
- [Certification 1]
- [Certification 2]

---
*Edit this file with 'cover-me profile' to add your detailed professional background.*
"""
        
        with open(config_manager.user_profile_file, 'w') as f:
            f.write(profile_content)
            
        click.echo(f"✅ Profile template created at {config_manager.user_profile_file}")
        
    except Exception as e:
        raise Exception(f"Failed to create profile template: {str(e)}")