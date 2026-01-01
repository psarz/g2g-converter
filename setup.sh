#!/bin/bash
# Quick Setup Script for GitLab to GitHub CI/CD Converter

set -e

echo "🚀 GitLab to GitHub CI/CD Converter - Setup Script"
echo "=================================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check Python
echo -e "${BLUE}Checking Python installation...${NC}"
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi
python_version=$(python3 --version)
echo -e "${GREEN}✓ Found $python_version${NC}"
echo ""

# Setup Backend
echo -e "${BLUE}Setting up backend...${NC}"
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt > /dev/null 2>&1

echo -e "${GREEN}✓ Backend setup complete${NC}"
echo ""

# Create .env file if not exists
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo -e "${GREEN}✓ .env created (configure as needed)${NC}"
fi

cd ..

# Display next steps
echo ""
echo -e "${BLUE}Setup Complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Start backend API:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   python run.py"
echo ""
echo "2. In another terminal, start frontend:"
echo "   cd frontend"
echo "   python -m http.server 8000"
echo ""
echo "3. Open http://localhost:8000 in your browser"
echo ""
echo "For Docker setup:"
echo "   docker-compose up"
echo ""
echo -e "${GREEN}Happy converting! 🎉${NC}"
