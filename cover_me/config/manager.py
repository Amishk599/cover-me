import os
import yaml
import shutil
from pathlib import Path
from typing import Dict, Any, Optional

from ..exceptions import ConfigurationError, ValidationError


class ConfigManager:
    """Manages user configuration with priority-based loading."""
    
    def __init__(self):
        """Initialize configuration manager with default paths."""
        self.user_config_dir = Path.home() / ".cover-me"
        self.user_config_file = self.user_config_dir / "config.yaml"
        self.user_profile_file = self.user_config_dir / "profile.md"
        self.user_templates_dir = self.user_config_dir / "templates"
        
        # Installation defaults directory (relative to project root)
        self.project_root = Path(__file__).parent.parent.parent
        self.defaults_dir = self.project_root / "defaults"
        
    def ensure_user_config_dir(self) -> None:
        """Create user config directory if it doesn't exist."""
        self.user_config_dir.mkdir(exist_ok=True)
        self.user_templates_dir.mkdir(exist_ok=True)
        
    def has_user_config(self) -> bool:
        """Check if user configuration exists."""
        return self.user_config_file.exists()
        
    def load_config(self) -> Dict[str, Any]:
        """Load configuration with priority order.
        
        Priority:
        1. User config: ~/.cover-me/config.yaml (for settings only)
        2. Environment variables: OPENAI_API_KEY, ANTHROPIC_API_KEY (for API keys)
        3. Installation defaults: defaults/config.yaml
        
        Note: API keys are only read from environment variables, never stored in config files.
        
        Returns:
            Configuration dictionary
            
        Raises:
            ConfigurationError: If no configuration can be loaded
        """
        config = {}
        
        # 1. Try user config first
        if self.user_config_file.exists():
            try:
                with open(self.user_config_file, 'r') as f:
                    config = yaml.safe_load(f) or {}
            except yaml.YAMLError as e:
                raise ConfigurationError(f"Invalid YAML in user configuration: {e}")
        else:
            # 3. Fall back to installation defaults
            config = self._get_default_config()
            
        # 2. Apply environment variable overrides
        self._apply_env_overrides(config)
        
        return config
        
    def save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to user directory.
        
        Args:
            config: Configuration dictionary to save
        """
        self.ensure_user_config_dir()
        with open(self.user_config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
    
    def get_system_prompt_path(self) -> Path:
        """Get path to system prompt file.
        
        Returns:
            Path to system prompt (user or default)
        """
        user_system_prompt = self.user_config_dir / "system_prompt.md"
        if user_system_prompt.exists():
            return user_system_prompt
        return self.defaults_dir / "system_prompt.md"
    
    def get_profile_path(self) -> Path:
        """Get path to professional profile file.
        
        Returns:
            Path to profile file (user or default)
        """
        if self.user_profile_file.exists():
            return self.user_profile_file
        return self.defaults_dir / "profile.md"
    
    def get_template_path(self, template_name: str) -> Path:
        """Get path to PDF template file.
        
        Args:
            template_name: Name of the template file
            
        Returns:
            Path to template file (user or default)
        """
        user_template = self.user_templates_dir / template_name
        if user_template.exists():
            return user_template
        return self.defaults_dir / "templates" / template_name
    
    def copy_defaults_to_user(self) -> None:
        """Copy default configuration templates to user directory."""
        self.ensure_user_config_dir()
        
        # Copy default config if user config doesn't exist
        if not self.user_config_file.exists():
            default_config_path = self.defaults_dir / "config.yaml"
            if default_config_path.exists():
                shutil.copy2(default_config_path, self.user_config_file)
        
        # Copy default profile if user profile doesn't exist
        if not self.user_profile_file.exists():
            default_profile_path = self.defaults_dir / "profile.md"
            if default_profile_path.exists():
                shutil.copy2(default_profile_path, self.user_profile_file)
        
        # Copy default system prompt if user system prompt doesn't exist
        user_system_prompt = self.user_config_dir / "system_prompt.md"
        if not user_system_prompt.exists():
            default_system_prompt_path = self.defaults_dir / "system_prompt.md"
            if default_system_prompt_path.exists():
                shutil.copy2(default_system_prompt_path, user_system_prompt)
        
        # Copy default templates
        default_templates_dir = self.defaults_dir / "templates"
        if default_templates_dir.exists():
            for template_file in default_templates_dir.glob("*.html"):
                user_template_path = self.user_templates_dir / template_file.name
                if not user_template_path.exists():
                    shutil.copy2(template_file, user_template_path)
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Load default configuration from installation directory.
        
        Returns:
            Default configuration dictionary
            
        Raises:
            ConfigurationError: If default configuration cannot be loaded
        """
        default_config_path = self.defaults_dir / "config.yaml"
        if not default_config_path.exists():
            # Fallback to legacy config location for backwards compatibility during transition
            legacy_config_path = self.project_root / "config" / "config.yaml"
            if legacy_config_path.exists():
                default_config_path = legacy_config_path
            else:
                raise ConfigurationError(
                    "No default configuration found. "
                    "Please run setup to initialize configuration."
                )
        
        try:
            with open(default_config_path, 'r') as f:
                return yaml.safe_load(f) or {}
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in default configuration: {e}")
    
    def _apply_env_overrides(self, config: Dict[str, Any]) -> None:
        """Apply environment variable overrides to configuration.
        
        Args:
            config: Configuration dictionary to modify in-place
        """
        # Override LLM provider if environment variable is set
        if 'COVER_ME_LLM_PROVIDER' in os.environ:
            if 'llm' not in config:
                config['llm'] = {}
            config['llm']['provider'] = os.environ['COVER_ME_LLM_PROVIDER']
        
        # Override output directory if environment variable is set
        if 'COVER_ME_OUTPUT_DIR' in os.environ:
            if 'output' not in config:
                config['output'] = {}
            config['output']['output_dir'] = os.environ['COVER_ME_OUTPUT_DIR']

    def validate_config(self, config: Dict[str, Any]) -> None:
        """Validate configuration structure and required fields.
        
        Args:
            config: Configuration dictionary to validate
            
        Raises:
            ConfigurationError: If configuration is invalid
        """
        # Check for required sections
        required_sections = ['llm', 'output']
        for section in required_sections:
            if section not in config:
                raise ConfigurationError(
                    f"Missing required configuration section: {section}. "
                    f"Run 'cover-me setup' to initialize your configuration."
                )
        
        # Validate LLM configuration
        llm_config = config['llm']
        if 'provider' not in llm_config:
            raise ConfigurationError(
                "LLM provider not specified. Run 'cover-me setup' to configure your AI provider."
            )
        
        if llm_config['provider'] not in ['openai', 'anthropic']:
            raise ConfigurationError(
                f"Unsupported LLM provider: {llm_config['provider']}. "
                f"Supported providers: openai, anthropic"
            )
        
        if 'model' not in llm_config:
            raise ConfigurationError(
                "LLM model not specified. Run 'cover-me configure' to select a model."
            )
        
        # Check API key availability with helpful error messages
        self.validate_api_keys(config)
    
    def validate_api_keys(self, config: Dict[str, Any]) -> None:
        """Validate that required API keys are available.
        
        Args:
            config: Configuration dictionary to validate
            
        Raises:
            ConfigurationError: If required API keys are missing
        """
        provider = config['llm']['provider']
        
        if provider == 'openai':
            if 'OPENAI_API_KEY' not in os.environ:
                raise ConfigurationError(
                    "OpenAI API key not found.\n\n"
                    "To fix this, set your OpenAI API key as an environment variable:\n\n"
                    "  # For bash/zsh (add to ~/.bashrc or ~/.zshrc):\n"
                    "  export OPENAI_API_KEY='your-api-key-here'\n\n"
                    "  # For fish shell (add to ~/.config/fish/config.fish):\n"
                    "  set -x OPENAI_API_KEY 'your-api-key-here'\n\n"
                    "  # Or set it temporarily for this session:\n"
                    "  export OPENAI_API_KEY='your-api-key-here'\n\n"
                    "Get your API key from: https://platform.openai.com/api-keys"
                )
        
        elif provider == 'anthropic':
            if 'ANTHROPIC_API_KEY' not in os.environ:
                raise ConfigurationError(
                    "Anthropic API key not found.\n\n"
                    "To fix this, set your Anthropic API key as an environment variable:\n\n"
                    "  # For bash/zsh (add to ~/.bashrc or ~/.zshrc):\n"
                    "  export ANTHROPIC_API_KEY='your-api-key-here'\n\n"
                    "  # For fish shell (add to ~/.config/fish/config.fish):\n"
                    "  set -x ANTHROPIC_API_KEY 'your-api-key-here'\n\n"
                    "  # Or set it temporarily for this session:\n"
                    "  export ANTHROPIC_API_KEY='your-api-key-here'\n\n"
                    "Get your API key from: https://console.anthropic.com/"
                )
    
    def check_api_keys_early(self) -> None:
        """Early check for API keys before full configuration validation.
        
        This method can be called to quickly validate API key availability
        without loading the full configuration.
        
        Raises:
            ConfigurationError: If no configuration exists or API keys are missing
        """
        if not self.has_user_config():
            raise ConfigurationError(
                "No configuration found. Run 'cover-me setup' to get started."
            )
        
        config = self.load_config()
        self.validate_api_keys(config)