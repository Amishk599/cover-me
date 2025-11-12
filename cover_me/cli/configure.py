import sys
import os
import click

from ..config import ConfigManager
from ..exceptions import ConfigurationError, APIError
from ..llm import create_llm_client
from .setup import select_llm_provider, test_api_connection_from_env


def configure_command():
    """Interactive configuration editor."""
    config_manager = ConfigManager()
    
    # Check if configuration exists
    if not config_manager.has_user_config():
        click.echo("❌ No configuration found.", err=True)
        click.echo("💡 Run 'cover-me setup' to create your initial configuration.", err=True)
        sys.exit(1)
    
    try:
        config = config_manager.load_config()
        config_manager.validate_config(config)
    except ConfigurationError as e:
        click.echo(f"❌ Configuration error:", err=True)
        click.echo(f"   {str(e)}", err=True)
        sys.exit(1)
    
    click.echo("⚙️  Cover-Me Configuration Editor")
    click.echo("=" * 35)
    
    # Configuration loop
    while True:
        show_current_config(config)
        choice = show_configuration_menu()
        
        if choice == '0':
            # Save and exit
            try:
                config_manager.save_config(config)
                click.echo("✅ Configuration saved!")
                break
            except Exception as e:
                click.echo(f"❌ Failed to save configuration: {str(e)}", err=True)
                if not click.confirm("Continue without saving?"):
                    continue
                break
                
        elif choice == '1':
            # Change LLM provider and model
            click.echo("\n📡 Changing AI Provider and Model...")
            try:
                new_llm_config = select_llm_provider()
                config['llm'].update(new_llm_config)
                click.echo("✅ AI provider updated!")
            except KeyboardInterrupt:
                click.echo("\nCancelled.")
                
        elif choice == '2':
            # Guide user to update environment variable
            current_provider = config['llm']['provider']
            click.echo(f"\n🔑 API Key Management for {current_provider.title()}...")
            show_api_key_guidance(current_provider)
                
        elif choice == '3':
            # Change output format
            click.echo("\n📄 Changing Output Format...")
            new_format = configure_output_format(config['output']['format'])
            if new_format:
                config['output']['format'] = new_format
                click.echo("✅ Output format updated!")
                
        elif choice == '4':
            # Change output directory
            click.echo("\n📂 Changing Output Directory...")
            new_dir = configure_output_directory(config['output']['output_dir'])
            if new_dir:
                config['output']['output_dir'] = new_dir
                click.echo("✅ Output directory updated!")
                
        elif choice == '5':
            # Test current configuration
            click.echo("\n🧪 Testing Current Configuration...")
            test_current_configuration(config)
            
        else:
            click.echo("❌ Invalid choice.")
        
        click.echo()  # Add spacing


def show_current_config(config):
    """Display the current configuration."""
    click.echo("\nCurrent Configuration:")
    click.echo(f"  📡 AI Provider: {config['llm']['provider'].title()}")
    click.echo(f"  🧠 Model: {config['llm']['model']}")
    click.echo(f"  📄 Output Format: {config['output']['format'].title()}")
    click.echo(f"  📂 Output Directory: {config['output']['output_dir']}")
    
    # Show API key status
    provider = config['llm']['provider']
    env_var = f'{provider.upper()}_API_KEY'
    env_key_configured = bool(os.environ.get(env_var))
    
    if env_key_configured:
        click.echo(f"  🔑 API Key: ✅ Configured (from {env_var})")
    else:
        click.echo(f"  🔑 API Key: ❌ Not configured ({env_var} not set)")


def show_configuration_menu():
    """Show configuration menu and get user choice."""
    click.echo("\nWhat would you like to change?")
    click.echo("[1] AI Provider and Model")
    click.echo("[2] API Key Management")
    click.echo("[3] Output Format")
    click.echo("[4] Output Directory")
    click.echo("[5] Test Configuration")
    click.echo("[0] Save and Exit")
    
    return click.prompt("\nChoice", type=str).strip()


def show_api_key_guidance(provider):
    """Show guidance for managing API key environment variables."""
    provider_name = "OpenAI" if provider == "openai" else "Anthropic"
    env_var = f"{provider.upper()}_API_KEY"
    api_url = "https://platform.openai.com/api-keys" if provider == "openai" else "https://console.anthropic.com/"
    
    # Check current status
    if os.environ.get(env_var):
        click.echo(f"✅ {env_var} environment variable is currently set.")
        click.echo("🔄 Testing current API key...")
        
        try:
            if test_api_connection_from_env(provider):
                click.echo("✅ Current API key is valid!")
                if not click.confirm("Do you want to update your API key?"):
                    return
            else:
                click.echo("❌ Current API key validation failed.")
                click.echo("Your API key may be invalid or expired.")
        except Exception as e:
            click.echo(f"❌ Error testing API key: {str(e)}")
    else:
        click.echo(f"❌ {env_var} environment variable is not set.")
    
    # Show guidance
    click.echo(f"\n🌐 Get your {provider_name} API key from: {api_url}")
    click.echo(f"\n🔧 Set the environment variable {env_var}:")
    click.echo("\n   For bash/zsh (add to ~/.bashrc or ~/.zshrc):")
    click.echo(f"   export {env_var}='your-api-key-here'")
    click.echo("\n   For fish shell (add to ~/.config/fish/config.fish):")
    click.echo(f"   set -x {env_var} 'your-api-key-here'")
    click.echo("\n   Or set it temporarily for this session:")
    click.echo(f"   export {env_var}='your-api-key-here'")
    click.echo("\n💡 After setting the environment variable, restart your terminal")
    click.echo("   or source your shell configuration file for changes to take effect.")


def configure_output_format(current_format):
    """Configure output format."""
    formats = ['pdf', 'text']
    
    click.echo("Select output format:")
    for i, fmt in enumerate(formats, 1):
        marker = "✓" if fmt == current_format else " "
        click.echo(f"[{i}] {fmt.title()} {marker}")
    
    try:
        choice = click.prompt("Choice (or Enter to keep current)", 
                            type=click.IntRange(1, len(formats)), 
                            default=None, show_default=False)
        if choice is not None:
            return formats[choice - 1]
    except click.Abort:
        pass
    
    return None


def configure_output_directory(current_dir):
    """Configure output directory."""
    click.echo(f"Current output directory: {current_dir}")
    
    try:
        new_dir = click.prompt("New output directory (or Enter to keep current)", 
                             default="", show_default=False).strip()
        if new_dir:
            # Expand tilde if present
            expanded_dir = os.path.expanduser(new_dir)
            
            # Create directory if it doesn't exist
            try:
                os.makedirs(expanded_dir, exist_ok=True)
                click.echo(f"✅ Directory verified/created: {expanded_dir}")
                return new_dir
            except Exception as e:
                click.echo(f"❌ Cannot create directory: {str(e)}")
                if click.confirm("Save this path anyway?"):
                    return new_dir
    except click.Abort:
        pass
    
    return None


def test_current_configuration(config):
    """Test the current configuration."""
    try:
        # Test LLM client creation
        client = create_llm_client(config['llm'])
        provider_info = client.get_provider_info()
        
        click.echo(f"📡 Provider: {provider_info['provider']}")
        click.echo(f"🧠 Model: {provider_info['model']}")
        click.echo(f"🔑 API Key: {provider_info['api_key']}")
        
        # Test API connectivity
        if client.validate_api_key():
            click.echo("✅ Configuration test successful!")
        else:
            raise APIError("API key validation failed!")
            
    except ConfigurationError as e:
        click.echo(f"❌ Configuration error: {str(e)}")
    except APIError as e:
        click.echo(f"❌ API error: {str(e)}")
    except Exception as e:
        click.echo(f"❌ Configuration test failed: {str(e)}")