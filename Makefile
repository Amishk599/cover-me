.PHONY: help setup-dev clean-dev

# Default target
help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

dev: ## Set up development environment
	@echo "Setting up development environment..."
	@python3 -m venv .dev-venv
	@echo "Virtual environment created at .dev-venv"
	@.dev-venv/bin/pip install --upgrade pip
	@.dev-venv/bin/pip install -e .
	@echo "Project installed in editable mode"
	@echo "Verifying installation..."
	@.dev-venv/bin/cover-me --help > /dev/null && echo "✅ Installation verified successfully!" || echo "❌ Installation verification failed"
	@echo ""
	@echo "To activate the virtual environment, run:"
	@echo "  source .dev-venv/bin/activate"

clean-dev: ## Clean up development environment
	@echo "Cleaning development environment..."
	@rm -rf .dev-venv
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@find . -name "*.pyo" -delete 2>/dev/null || true
	@echo "✅ Development environment cleaned"