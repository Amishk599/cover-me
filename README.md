# cover-me

An AI-powered tool to generate professional cover letters from job descriptions

> Simply copy a job description from any website, run `cover-me -c`, and get a personalized cover letter in seconds!

## Quick Start

### 1. Installation

Clone this repository and run the installer:

```bash
git clone git@github.com:Amishk599/cover-me.git
cd cover-me
./install.sh
```

The installer will:
- Install the `cover-me` command system-wide
- Set up your PATH if needed
- Guide you through dependency setup

### 2. Set API Key

Add your API key to your shell profile (`~/.bashrc`, `~/.zshrc`, etc.):

```bash
# For OpenAI
export OPENAI_API_KEY="your-openai-api-key-here"

# OR for Anthropic
export ANTHROPIC_API_KEY="your-anthropic-api-key-here"
```

Then restart your terminal or run `source ~/.bashrc` (or your shell config file).

### 3. Configure Your Details

Update the configuration files with your information:

- Edit `config/config.yaml` with your preferences
- Edit `config/professional_info.md` with your professional details

These files are used to personalize your cover letters.

### 4. Usage
> **NOTE:** By default generated cover letters will get stored in `Desktop/cover-letters`

Commands:

```bash
# Read job description from clipboard (most common usage)
cover-me -c

# If the job description is too large for clipboard, save it to a text file and use:
cover-me -f path/to/jd.txt

# Test your API connection
cover-me --test-api

# Verbose output
cover-me -c -v

# Custom output path
cover-me -c -o path/to/cover_letter.pdf

# Show all options
cover-me --help
```

## Manual Setup (Alternative)

<details>
<summary>Click to expand manual installation steps</summary>

If you prefer not to use the installer:

1. **Create virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run directly:**
   ```bash
   python3 -m src.main -c
   ```

</details>

## Configuration

The application uses configuration files in the `config/` directory:

- `config.yaml` - Main application settings
- `system_prompt.md` - AI prompt template
- `professional_info.md` - Your professional information

> Edit these files to customize the generated cover letters.

## Requirements

- Python 3.7+
- OpenAI API key OR Anthropic API key


## License

MIT License - see LICENSE file for details.