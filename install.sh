#!/bin/bash

# Installation script for Agentic Integration Platform
# This script handles the PyTorch compatibility issues

set -e

echo "🚀 Installing Agentic Integration Platform..."

# Check if Poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry is not installed. Please install Poetry first:"
    echo "   curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

# Check Python version
python_version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.12"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python $required_version or higher is required. Found: $python_version"
    exit 1
fi

echo "✅ Python version: $python_version"

# Remove existing lock file to avoid conflicts
if [ -f "poetry.lock" ]; then
    echo "🧹 Removing existing poetry.lock file..."
    rm poetry.lock
fi

# Install core dependencies (without ML extras)
echo "📦 Installing core dependencies..."
if ! poetry install --no-cache; then
    echo "⚠️  Standard installation failed. Trying without installing the current project..."
    poetry install --no-cache --no-root
fi

# Check if user wants ML features
read -p "🤖 Do you want to install ML features (PyTorch, sentence-transformers)? This requires more disk space and may have compatibility issues. (y/N): " install_ml

if [[ $install_ml =~ ^[Yy]$ ]]; then
    echo "🧠 Installing ML dependencies..."
    
    # Try to install ML extras
    if poetry install --extras ml --no-cache; then
        echo "✅ ML dependencies installed successfully!"
    else
        echo "⚠️  ML dependencies failed to install. You can continue without them."
        echo "   The platform will work but without local embedding generation."
        echo "   You can use OpenAI embeddings instead."
        
        read -p "Continue without ML dependencies? (Y/n): " continue_without_ml
        if [[ $continue_without_ml =~ ^[Nn]$ ]]; then
            exit 1
        fi
    fi
else
    echo "⏭️  Skipping ML dependencies. You can install them later with:"
    echo "   poetry install --extras ml"
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p data/sessions
mkdir -p data/uploads
mkdir -p logs
mkdir -p app/services/ai/prompts

# Copy environment file
if [ ! -f ".env" ]; then
    echo "⚙️  Creating environment file..."
    cp .env.example .env
    echo "📝 Please edit .env file with your configuration"
fi

# Run basic health check
echo "🔍 Running basic health check..."
if poetry run python -c "import fastapi, pydantic, sqlalchemy; print('✅ Core dependencies working')"; then
    echo "✅ Installation completed successfully!"
    echo ""
    echo "🎉 Next steps:"
    echo "   1. Edit .env file with your configuration"
    echo "   2. Start the development server: make dev"
    echo "   3. Visit http://localhost:8000/docs for API documentation"
    echo ""
    echo "📚 For more information, see README.md"
else
    echo "❌ Health check failed. Please check the installation."
    exit 1
fi
