import sys
import click

from ..config import ConfigManager
from ..exceptions import ConfigurationError, APIError
from ..llm import create_llm_client


def test_command():
    """Test Cover-Me configuration and connectivity."""
    click.echo("🧪 Testing Cover-Me Configuration")
    click.echo("=" * 35)
    
    config_manager = ConfigManager()
    
    # Test 1: Check if user configuration exists
    click.echo("📁 Checking configuration...")
    if not config_manager.has_user_config():
        click.echo("❌ No user configuration found.", err=True)
        click.echo(f"   Expected location: {config_manager.user_config_file}", err=True)
        click.echo("\n💡 Run 'cover-me setup' to create your configuration.", err=True)
        sys.exit(1)
    click.echo(f"✅ Configuration found: {config_manager.user_config_file}")
    
    # Test 2: Load and validate configuration
    click.echo("\n🔧 Loading configuration...")
    try:
        config = config_manager.load_config()
        config_manager.validate_config(config)
        click.echo("✅ Configuration loaded and validated successfully")
    except ConfigurationError as e:
        click.echo(f"❌ Configuration error:", err=True)
        click.echo(f"   {str(e)}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Failed to load configuration: {str(e)}", err=True)
        sys.exit(1)
    
    # Test 3: Display current configuration
    click.echo("\n⚙️ Current Configuration:")
    click.echo(f"   📡 Provider: {config['llm']['provider']}")
    click.echo(f"   🧠 Model: {config['llm']['model']}")
    click.echo(f"   📄 Output Format: {config['output']['format']}")
    click.echo(f"   📂 Output Directory: {config['output']['output_dir']}")
    
    # Test 4: Check API connectivity
    click.echo("\n🔗 Testing API connection...")
    try:
        client = create_llm_client(config['llm'])
        provider_info = client.get_provider_info()
        click.echo(f"   🤖 Using {provider_info['provider']} with model {provider_info['model']}")
        click.echo(f"   🔑 API Key: {provider_info['api_key']}")
        
        if client.validate_api_key():
            click.echo("✅ API connection successful!")
        else:
            raise APIError("API connection failed. Check your API key and internet connection.")
            
    except ConfigurationError as e:
        click.echo(f"❌ Configuration error:", err=True)
        click.echo(f"   {str(e)}", err=True)
        sys.exit(1)
    except APIError as e:
        click.echo(f"❌ API error:", err=True)
        click.echo(f"   {str(e)}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ API connection test failed: {str(e)}", err=True)
        click.echo("\n💡 Troubleshooting:", err=True)
        click.echo("   1. Check your API key environment variable", err=True)
        click.echo("   2. Verify internet connectivity", err=True)
        click.echo("   3. Check API service status", err=True)
        sys.exit(1)
    
    # Test 5: Check profile file
    click.echo("\n📝 Checking professional profile...")
    profile_path = config_manager.get_profile_path()
    if profile_path.exists():
        click.echo(f"✅ Profile found: {profile_path}")
        
        # Check if it's the default template (needs customization)
        with open(profile_path, 'r') as f:
            content = f.read()
            if "[Your Company]" in content or "[Achievement 1]" in content:
                click.echo("⚠️  Profile contains template placeholders")
                click.echo("   Run 'cover-me profile' to customize your professional information")
            else:
                click.echo("✅ Profile appears to be customized")
    else:
        click.echo(f"❌ Profile file not found: {profile_path}", err=True)
        click.echo("   Run 'cover-me setup' to create your profile.", err=True)
        sys.exit(1)
    
    # Test 6: Check system prompt (optional)
    system_prompt_path = config_manager.get_system_prompt_path()
    if system_prompt_path.exists():
        click.echo(f"✅ System prompt found: {system_prompt_path}")
    else:
        click.echo("⚠️  System prompt not found, using defaults")
    
    # Success summary
    click.echo("\n🎉 All tests passed!")
    click.echo("Your Cover-Me setup is ready to use.")
    click.echo("\n📋 To generate a cover letter:")
    click.echo("   1. Copy a job description to your clipboard")
    click.echo("   2. Run 'cover-me' or 'cover-me generate'")
    click.echo("\n🔧 To modify settings:")
    click.echo("   • 'cover-me configure' - Change AI provider, output format, etc.")
    click.echo("   • 'cover-me profile' - Edit your professional information")