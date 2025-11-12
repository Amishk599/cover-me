# 🪶 cover-me

**✨ Generate professional, personalized cover letters instantly.**

`cover-me` is an AI-powered tool that crafts job-specific cover letters in **upload-ready PDF format** - using your **resume** and the **job description**.

> 🪄 Copy any job description, run `cover-me`, and get a tailored cover letter in seconds.

## Get Started

### 1. Installation

#### 🧰 Using pipx (Recommended)

`pipx` is for installing Python CLI tools like cover-me.

---

#### 💿 Step 1: Install `pipx`
```bash
# macOS
brew install pipx
pipx ensurepath

# Linux
python -m pip install --user pipx
pipx ensurepath

# Windows
python -m pip install --user pipx
pipx ensurepath
```

#### 💿 Step 2: Install cover-me
```bash
pipx install git+https://github.com/Amishk599/cover-me.git
```

#### 🔄 Update to Latest Version
```bash
pipx upgrade cover-me
```

### 2. 🔑 Set Environment Variables

You must provide **at least one API key** — either **OpenAI** or **Anthropic**.

```bash
# At least one of the following is required
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"
```

This will guide you through:
- Choosing your AI provider (OpenAI or Anthropic)
- Setting up your API key environment variables
- Configuring your professional / Resume information
- Setting output preferences

---

### 3. 🚀 Usage


1. 🗒️ **Copy** a job description from any website.  
2. 💫 **Run** the following command in your terminal:

```bash
cover-me
```


Other Commands:

```bash
# Configure your settings
cover-me configure

# Edit your professional profile
cover-me profile

# Test your configuration and API connectivity
cover-me test

# Show all options
cover-me --help
```

## ⚙️ Configuration Details

All configuration files are stored in:  
`~/.cover-me/`

| File | Purpose |
|------|----------|
| `config.yaml` | Main application settings — AI provider, output format, and other preferences |
| `profile.md` | Your professional profile containing experience, skills, and summary |
| `templates/` | Folder for PDF templates and visual customizations |

You can **manually edit** these files using any text editor of your choice.

---
## 🧱 Requirements

- **Python 3.7+**
- At least one of the following API keys:
  - `OPENAI_API_KEY` (for OpenAI models)  
  - `ANTHROPIC_API_KEY` (for Anthropic models)

---

## 📜 License

This project is licensed under the **MIT License**.  
See the [LICENSE](./LICENSE) file for full details.