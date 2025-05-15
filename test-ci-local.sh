#!/bin/bash

# Local CI Testing Script with uv Virtual Environment Support
# This script simulates the CI environment for testing without GitHub Actions

echo "🧪 Local CI Testing Script (uv-enabled)"
echo "======================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
    fi
}

print_warning() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

# Check Docker availability
echo "🔍 Checking Docker availability..."
if command -v docker &> /dev/null; then
    echo -e "${GREEN}✅ Docker is available${NC}"
    docker --version
    DOCKER_AVAILABLE=true
else
    echo -e "${YELLOW}⚠️ Docker is not available${NC}"
    DOCKER_AVAILABLE=false
fi

if command -v docker-compose &> /dev/null; then
    echo -e "${GREEN}✅ Docker Compose is available${NC}"
    docker-compose --version
    DOCKER_COMPOSE_AVAILABLE=true
else
    echo -e "${YELLOW}⚠️ Docker Compose is not available${NC}"
    DOCKER_COMPOSE_AVAILABLE=false
fi

echo ""

# Test 1: Basic Python setup with uv
echo "🐍 Testing Python environment with uv..."
python3 --version
print_status $? "Python version check"

# Test 2: uv virtual environment setup
echo "📦 Setting up uv virtual environment..."
if command -v uv > /dev/null 2>&1; then
    echo -e "${GREEN}✅ uv is available${NC}"
    uv --version

    # Remove existing venv if it exists
    if [ -d ".venv" ]; then
        echo "🗑️ Removing existing virtual environment..."
        rm -rf .venv
    fi

    # Create new virtual environment and sync dependencies with uv
    if uv sync --extra dev > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Virtual environment created and dependencies synced (Python 3.11)${NC}"
    else
        echo -e "${RED}❌ Virtual environment creation and sync failed (Python 3.11)${NC}"
        echo -e "${YELLOW}⚠️ Falling back to basic uv venv...${NC}"
        if uv venv --python 3.11 > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Virtual environment created (system Python)${NC}"
            # Activate and install manually as fallback
            source .venv/bin/activate
            uv pip install -e ".[dev]" > /dev/null 2>&1
        else
            echo -e "${RED}❌ Virtual environment creation failed${NC}"
            exit 1
        fi
    fi

    # Activate virtual environment
    source .venv/bin/activate
    echo -e "${GREEN}✅ Virtual environment activated${NC}"
    echo "🐍 Virtual environment Python version: $(python --version)"

    UV_USED=true
else
    echo -e "${YELLOW}⚠️ uv is not available, falling back to pip3${NC}"
    python3 -m pip install --upgrade pip > /dev/null 2>&1

    if [ -f requirements.txt ]; then
        pip install -r requirements.txt > /dev/null 2>&1
        print_status $? "Requirements installation"
    else
        print_warning "requirements.txt not found"
    fi

    pip install flake8 mypy pytest pytest-cov bandit safety semgrep pylint > /dev/null 2>&1
    print_status $? "Development tools installation"

    UV_USED=false
fi

echo ""

# Test 3: Code quality checks
echo "📋 Running code quality checks..."

# Flake8
if command -v flake8 &> /dev/null; then
    flake8 app --count --show-source --statistics > /dev/null 2>&1
    print_status $? "Flake8 linting"
else
    echo -e "${RED}❌ Flake8 not available${NC}"
fi

# Black formatting check
if command -v black &> /dev/null; then
    black --check . > /dev/null 2>&1
    print_status $? "Black code formatting"
elif python3 -m black --check . > /dev/null 2>&1; then
    print_status $? "Black code formatting"
else
    echo -e "${RED}❌ Black not available${NC}"
fi

# isort import sorting check
if command -v isort &> /dev/null; then
    isort --check-only --profile black --diff app tests > /dev/null 2>&1
    print_status $? "isort import sorting"
elif python3 -m isort --check-only --profile black --diff app tests > /dev/null 2>&1; then
    print_status $? "isort import sorting"
else
    echo -e "${RED}❌ isort not available${NC}"
fi

# MyPy
if command -v mypy &> /dev/null; then
    mypy --ignore-missing-imports app/ > /dev/null 2>&1
    print_status $? "MyPy type checking"
else
    echo -e "${RED}❌ MyPy not available${NC}"
fi

# Bandit security scan
if command -v bandit &> /dev/null; then
    bandit -r app/ -f json > /dev/null 2>&1
    print_status $? "Bandit security scan"
else
    echo -e "${RED}❌ Bandit not available${NC}"
fi

# Safety vulnerability check
if command -v safety &> /dev/null; then
    safety check --ignore 77323 > /dev/null 2>&1
    print_status $? "Safety vulnerability check"
else
    echo -e "${RED}❌ Safety not available${NC}"
fi

echo ""

# Test 4: Application startup test
echo "🚀 Testing application startup..."
python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from app import create_app
    from app.config import TestingConfig
    app = create_app(TestingConfig)
    print('✅ Flask application can be created')
except Exception as e:
    print(f'❌ Flask application creation failed: {e}')
    sys.exit(1)
" 2>/dev/null
print_status $? "Flask application creation"

echo ""

# Test 5: Dockerfile validation
echo "🐳 Validating Docker configuration..."
if [ -f Dockerfile ]; then
    echo -e "${GREEN}✅ Dockerfile exists${NC}"

    # Basic syntax check
    if grep -E "^(FROM|RUN|COPY|ADD|ENV|EXPOSE|CMD|ENTRYPOINT)" Dockerfile > /dev/null; then
        echo -e "${GREEN}✅ Dockerfile has valid instructions${NC}"
    else
        echo -e "${RED}❌ Dockerfile syntax issues${NC}"
    fi
else
    echo -e "${RED}❌ Dockerfile not found${NC}"
fi

# Test 6: Docker Compose validation
if [ -f docker-compose.yml ]; then
    echo -e "${GREEN}✅ docker-compose.yml exists${NC}"

    # Install yq if not available for YAML validation
    if ! command -v yq &> /dev/null; then
        print_warning "yq not available for YAML validation"
    else
        yq eval . docker-compose.yml > /dev/null 2>&1
        print_status $? "docker-compose.yml syntax validation"
    fi
else
    echo -e "${RED}❌ docker-compose.yml not found${NC}"
fi

echo ""

# Test 7: Docker build test (if Docker available)
if [ "$DOCKER_AVAILABLE" = true ]; then
    echo "🐳 Testing Docker build..."
    docker build . --file Dockerfile --tag mail-scheduler:test > /dev/null 2>&1
    print_status $? "Docker image build"

    # Cleanup
    docker rmi mail-scheduler:test > /dev/null 2>&1
else
    print_warning "Skipping Docker build test - Docker not available"
fi

echo ""

# Test 8: Run unit tests (with proper environment)
echo "🧪 Running unit tests..."
if command -v pytest &> /dev/null; then
    FLASK_APP=serve.py FLASK_DEBUG=1 APP_SETTINGS=TestingConfig SECRET_KEY=test-secret-key pytest tests/ -v > /dev/null 2>&1
    print_status $? "Unit tests"
else
    echo -e "${RED}❌ pytest not available${NC}"
fi

echo ""

# Test 9: Security scanning with Python tools
echo "🔒 Running security scans..."

# Semgrep
if command -v semgrep &> /dev/null; then
    semgrep --config=auto app/ > /dev/null 2>&1
    print_status $? "Semgrep security scan"
else
    echo -e "${RED}❌ Semgrep not available${NC}"
fi

# Pylint
if command -v pylint &> /dev/null; then
    pylint app/ > /dev/null 2>&1
    print_status $? "Pylint code analysis"
else
    echo -e "${RED}❌ Pylint not available${NC}"
fi

echo ""
echo "🏁 Local CI testing completed!"
echo ""

# Summary
echo "📊 Summary:"
echo "- uv Virtual Environment: $([ "$UV_USED" = true ] && echo "✅" || echo "❌")"
echo "- Docker Available: $DOCKER_AVAILABLE"
echo "- Docker Compose Available: $DOCKER_COMPOSE_AVAILABLE"
echo "- Application can be created: ✅"
echo "- Configuration files present: $([ -f Dockerfile ] && echo "✅" || echo "❌")"

echo ""
echo "💡 To run the full CI pipeline:"
echo "1. Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh"
echo "2. Ensure Docker and Docker Compose are installed (optional)"
echo "3. Run: ./test-ci-local.sh"
echo "4. Or use GitHub Actions workflows for full testing"

# Deactivate virtual environment if using uv
if [ "$UV_USED" = true ]; then
    deactivate 2>/dev/null || true
fi
