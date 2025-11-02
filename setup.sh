#!/bin/bash

# Flow Manager Setup and Verification Script
# This script sets up the environment and verifies the installation

echo "=========================================="
echo "Flow Manager - Setup & Verification"
echo "=========================================="
echo ""

# Check Python version
echo "1. Checking Python version..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi
echo "✅ Python check passed"
echo ""

# Create virtual environment
echo "2. Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "ℹ️  Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "3. Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Install dependencies
echo "4. Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi
echo "✅ Dependencies installed"
echo ""

# Verify project structure
echo "5. Verifying project structure..."
required_dirs=("app" "app/models" "app/services" "app/tasks" "app/api" "app/config" "app/utils" "flows")
for dir in "${required_dirs[@]}"; do
    if [ ! -d "$dir" ]; then
        echo "❌ Missing directory: $dir"
        exit 1
    fi
done
echo "✅ Project structure verified"
echo ""

# Check required files
echo "6. Checking required files..."
required_files=(
    "app/main.py"
    "app/models/flow.py"
    "app/models/execution.py"
    "app/services/flow_manager.py"
    "app/services/task_registry.py"
    "app/tasks/sample_tasks.py"
    "app/api/routes.py"
    "flows/sample_flow.json"
    "requirements.txt"
)
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Missing file: $file"
        exit 1
    fi
done
echo "✅ All required files present"
echo ""

# Create .env file if it doesn't exist
echo "7. Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ Created .env file from template"
else
    echo "ℹ️  .env file already exists"
fi
echo ""

echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "To start the server:"
echo "  1. Make sure virtual environment is activated: source venv/bin/activate"
echo "  2. Run: uvicorn app.main:app --reload"
echo ""
echo "To test the server:"
echo "  python test_flow.py"
echo ""
echo "API Documentation will be available at:"
echo "  http://localhost:8000/docs"
echo ""
