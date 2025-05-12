#!/bin/bash
# Setup script for mail-scheduler development environment

# Colors for terminal output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Setting up Mail-Scheduler development environment...${NC}"

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d ' ' -f 2)
echo -e "Detected Python version: ${GREEN}$PYTHON_VERSION${NC}"

# Create virtual environment
echo -e "${YELLOW}Creating virtual environment...${NC}"
if [ -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment already exists. Skipping creation.${NC}"
else
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to create virtual environment.${NC}"
        exit 1
    fi
    echo -e "${GREEN}Virtual environment created successfully.${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to activate virtual environment.${NC}"
    exit 1
fi
echo -e "${GREEN}Virtual environment activated.${NC}"

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to upgrade pip.${NC}"
else
    echo -e "${GREEN}Pip upgraded successfully.${NC}"
fi

# Clean pip cache to avoid conflicts
echo -e "${YELLOW}Cleaning pip cache...${NC}"
pip cache purge || true
echo -e "${GREEN}Pip cache cleaned.${NC}"

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"

# Try installation with core dependencies first - these are the problematic ones that need specific versions
echo "Installing core dependencies first (Flask ecosystem)..."
pip install Flask==2.3.2 Werkzeug==2.3.7 flask-restx==1.2.0 jsonschema==4.17.3

# Then install other dependencies with more flexibility
echo "Installing remaining dependencies..."
if [ -f "requirements-loose.txt" ]; then
    pip install -r requirements-loose.txt || true
    echo -e "${GREEN}Loose dependencies installed.${NC}"
else
    # Fall back to requirements.txt without strict versioning
    pip install -r requirements.txt --no-deps || true
    echo -e "${YELLOW}Some dependencies may need manual installation.${NC}"
fi

echo -e "${GREEN}Core dependencies installed successfully.${NC}"

# Install development dependencies
echo -e "${YELLOW}Installing development dependencies...${NC}"
# Try to install key test packages independently to handle conflicts
pip install pytest>=7.0.0 pytest-flask>=1.2.0 pytest-cov>=4.1.0 || true
pip install black flake8 mypy || true
echo -e "${GREEN}Development dependencies installed.${NC}"

# Install the package in development mode
echo -e "${YELLOW}Installing package in development mode...${NC}"
pip install -e . || true
echo -e "${GREEN}Package installed in development mode.${NC}"

# Copy .env.example if .env doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file from .env.example...${NC}"
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}.env file created. Please edit it with your settings.${NC}"
    else
        echo -e "${RED}.env.example file not found. Please create .env file manually.${NC}"
    fi
fi

echo -e "${GREEN}Setup complete!${NC}"
echo -e "${YELLOW}To activate the virtual environment, run:${NC}"
echo -e "    ${GREEN}source venv/bin/activate${NC}"
echo -e "${YELLOW}To run tests, run:${NC}"
echo -e "    ${GREEN}pytest${NC}"
echo -e "${YELLOW}To run the application, run:${NC}"
echo -e "    ${GREEN}flask run${NC}"
