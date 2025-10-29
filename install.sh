#!/bin/bash

# Cover Letter Generator Installation Script
# This script installs the cover-me CLI tool for system-wide access

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to detect the user's shell
detect_shell() {
    if [ -n "$ZSH_VERSION" ]; then
        echo "zsh"
    elif [ -n "$BASH_VERSION" ]; then
        echo "bash"
    else
        # Fallback to checking SHELL environment variable
        case "$SHELL" in
            */zsh) echo "zsh" ;;
            */bash) echo "bash" ;;
            *) echo "unknown" ;;
        esac
    fi
}

# Function to get shell config file
get_shell_config() {
    local shell_type="$(detect_shell)"
    case "$shell_type" in
        "zsh") echo "$HOME/.zshrc" ;;
        "bash") echo "$HOME/.bashrc" ;;
        *) echo "$HOME/.profile" ;;
    esac
}

# Main installation function
install_cover_me() {
    print_status "Installing Cover Letter Generator CLI..."
    
    # Get the directory where this script is located
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    
    # Check if cover-me script exists
    if [ ! -f "$SCRIPT_DIR/cover-me" ]; then
        print_error "cover-me script not found in $SCRIPT_DIR"
        exit 1
    fi
    
    # Check if src/main.py exists
    if [ ! -f "$SCRIPT_DIR/src/main.py" ]; then
        print_error "src/main.py not found. Please run this script from the project root directory."
        exit 1
    fi
    
    # Determine installation method
    print_status "Determining installation method..."
    
    # Function to install script with embedded project path
    install_script() {
        local target_dir="$1"
        local script_name="cover-me"
        
        # Create a temporary modified version of the script
        local temp_script=$(mktemp)
        
        # Replace the placeholder in the script with the actual project directory
        sed "s|PROJECT_DIR_PLACEHOLDER|$SCRIPT_DIR|g" "$SCRIPT_DIR/cover-me" > "$temp_script"
        
        # Copy the modified script to the target directory
        cp "$temp_script" "$target_dir/$script_name"
        chmod +x "$target_dir/$script_name"
        
        # Clean up temporary file
        rm "$temp_script"
    }
    
    # Option 1: Install to /usr/local/bin (requires sudo)
    if [ -w "/usr/local/bin" ] || [ "$EUID" -eq 0 ]; then
        INSTALL_DIR="/usr/local/bin"
        print_status "Installing to $INSTALL_DIR (system-wide)"
        install_script "$INSTALL_DIR"
        print_success "Installed cover-me to $INSTALL_DIR"
        
    # Option 2: Install to ~/.local/bin (user-only)
    elif [ -d "$HOME/.local/bin" ] || mkdir -p "$HOME/.local/bin" 2>/dev/null; then
        INSTALL_DIR="$HOME/.local/bin"
        print_status "Installing to $INSTALL_DIR (user-only)"
        install_script "$INSTALL_DIR"
        print_success "Installed cover-me to $INSTALL_DIR"
        
        # Check if ~/.local/bin is in PATH
        if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
            print_warning "$HOME/.local/bin is not in your PATH"
            
            # Offer to add it to shell config
            local shell_config="$(get_shell_config)"
            print_status "Adding $HOME/.local/bin to PATH in $shell_config"
            
            echo "" >> "$shell_config"
            echo "# Added by cover-me installer" >> "$shell_config"
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$shell_config"
            
            print_success "Added $HOME/.local/bin to PATH in $shell_config"
            print_warning "Please restart your terminal or run: source $shell_config"
        fi
        
    # Option 3: Try with sudo
    else
        print_status "Attempting installation with sudo..."
        if command_exists sudo; then
            # Create a temporary modified version of the script
            local temp_script=$(mktemp)
            sed "s|PROJECT_DIR_PLACEHOLDER|$SCRIPT_DIR|g" "$SCRIPT_DIR/cover-me" > "$temp_script"
            
            sudo cp "$temp_script" "/usr/local/bin/cover-me"
            sudo chmod +x "/usr/local/bin/cover-me"
            
            # Clean up temporary file
            rm "$temp_script"
            
            INSTALL_DIR="/usr/local/bin"
            print_success "Installed cover-me to /usr/local/bin with sudo"
        else
            print_error "Cannot install: no write access to /usr/local/bin and sudo not available"
            print_error "Please manually copy the cover-me script to a directory in your PATH"
            exit 1
        fi
    fi
    
    # Verify installation
    print_status "Verifying installation..."
    if command_exists cover-me; then
        print_success "cover-me is now available in your PATH"
    else
        print_warning "cover-me not found in PATH. You may need to restart your terminal."
    fi
    
    # Check Python dependencies
    print_status "Checking Python dependencies..."
    cd "$SCRIPT_DIR"
    
    # Check if virtual environment exists
    if [ -d ".venv" ] || [ -d "venv" ]; then
        print_success "Virtual environment found"
    else
        print_warning "No virtual environment found. Consider creating one with:"
        echo "  python3 -m venv .venv"
        echo "  source .venv/bin/activate"
        echo "  pip install -r requirements.txt"
    fi
    
    # Check environment variables
    print_status "Checking environment variables..."
    if [ -z "$OPENAI_API_KEY" ] && [ -z "$ANTHROPIC_API_KEY" ]; then
        print_warning "No API keys found in environment variables"
        print_status "Please set one of the following in your shell profile:"
        echo "  export OPENAI_API_KEY='your-openai-key-here'"
        echo "  export ANTHROPIC_API_KEY='your-anthropic-key-here'"
        
        local shell_config="$(get_shell_config)"
        echo ""
        echo "Add to $shell_config and restart your terminal, or run:"
        echo "  source $shell_config"
    else
        print_success "API key environment variable found"
    fi
    
    # Final instructions
    echo ""
    print_success "Installation completed!"
    echo ""
    echo "Usage examples:"
    echo "  cover-me -c                    # Read job description from clipboard"
    echo "  cover-me -f job_desc.txt       # Read from file" 
    echo "  cover-me --test-api            # Test API connection"
    echo "  cover-me -c -v                 # Verbose output"
    echo "  cover-me --help                # Show all options"
    echo ""
    
    if [ "$INSTALL_DIR" = "$HOME/.local/bin" ] && [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        print_warning "Please restart your terminal or run: source $(get_shell_config)"
    fi
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Python
    if ! command_exists python3; then
        print_error "python3 is not installed. Please install Python 3.7 or later."
        exit 1
    fi
    
    print_success "All prerequisites met"
}

# Main execution
main() {
    echo "Cover Letter Generator CLI Installer"
    echo "==================================="
    echo ""
    
    check_prerequisites
    install_cover_me
}

# Run main function
main "$@"