# cover-me

An AI-powered tool to generate professional cover letters from job descriptions

> Simply copy a job description from any website, run `cover-me`, and get a personalized cover letter in seconds!

## Quick Start

### 1. Installation

#### Using pipx (Recommended)

pipx is designed for installing Python CLI tools like cover-me.

**Install pipx first:**
```bash
# macOS
brew install pipx
pipx ensurepath

# Linux/WSL
python -m pip install --user pipx
pipx ensurepath

# Windows
python -m pip install --user pipx
pipx ensurepath
```

**Install cover-me:**
```bash
pipx install git+https://github.com/Amishk599/cover-me.git
```

The pipx installation will:
- Install `cover-me` command system-wide
- Manage dependencies automatically
- Keep the tool isolated from your system Python

### 2. Initial Setup

Run the interactive setup wizard:

```bash
cover-me setup
```

This will guide you through:
- Choosing your AI provider (OpenAI or Anthropic)
- Setting up your API key environment variables
- Configuring your professional information
- Setting output preferences

Your configuration will be saved to `~/.cover-me/`

### 3. Usage
> **NOTE:** By default generated cover letters will get stored in `Desktop/cover-letters`

Commands:

```bash
# Generate cover letter from clipboard (most common usage)
cover-me
# or
cover-me generate

# Configure your settings
cover-me configure

# Edit your professional profile
cover-me profile

# Test your configuration and API connectivity
cover-me test

# Show all options
cover-me --help
```

## Development Installation (Alternative)

<details>
<summary>Click to expand development installation steps</summary>

For development or if you prefer to install from source:

1. **Clone the repository:**
   ```bash
   git clone git@github.com:Amishk599/cover-me.git
   cd cover-me
   ```

2. **Install in editable mode:**
   ```bash
   pip install -e .
   ```

3. **Or install with pipx from local directory:**
   ```bash
   pipx install .
   ```

4. **Or run directly (legacy method):**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   python3 -m src.main
   ```

</details>

## Configuration

The application stores your configuration in `~/.cover-me/`:

- `config.yaml` - Main application settings (AI provider, output format, etc.)
- `profile.md` - Your professional information and experience
- `templates/` - PDF templates and customizations

Use these commands to manage your configuration:

```bash
cover-me configure      # Interactive configuration editor
cover-me profile        # Edit your professional profile
cover-me test          # Validate your configuration
```

### Advanced Configuration

You can also set environment variables to override config settings:

```bash
export OPENAI_API_KEY="your-key"           # Required for OpenAI
export ANTHROPIC_API_KEY="your-key"        # Required for Anthropic
export COVER_ME_LLM_PROVIDER="openai"      # Override provider
export COVER_ME_OUTPUT_DIR="~/Documents"   # Override output directory
```

## Requirements

- Python 3.7+
- OpenAI API key OR Anthropic API key


## License

MIT License - see LICENSE file for details.