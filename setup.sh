#!/bin/bash
# BrandAI Setup Script for Linux/Mac

echo "╔══════════════════════════════════════════════════════════╗"
echo "║                       BrandAI                            ║"
echo "║          AI-Powered Ad Critique System                   ║"
echo "║                   Setup Script                           ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Check Python installation
echo "🔍 Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ Python found: $PYTHON_VERSION"
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version)
    echo "✅ Python found: $PYTHON_VERSION"
    PYTHON_CMD=python
else
    echo "❌ Python not found! Please install Python 3.9 or higher."
    exit 1
fi

# Create virtual environment
echo ""
echo "🔧 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "⚠️  Virtual environment already exists, skipping..."
else
    $PYTHON_CMD -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "🚀 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "📦 Installing dependencies (this may take a few minutes)..."
pip install -r requirements.txt --quiet
if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "⚠️  Some dependencies may have failed. Please check the output."
fi

# Create .env file if it doesn't exist
echo ""
echo "⚙️  Setting up environment configuration..."
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists, skipping..."
else
    cp .env.example .env
    echo "✅ .env file created from template"
    echo "⚠️  IMPORTANT: Edit .env file and add your GEMINI_API_KEY"
fi

# Create necessary directories
echo ""
echo "📁 Creating directories..."
mkdir -p uploads brand_kits generated_ads brand_kits/logos
echo "✅ Directories created"

# Display next steps
echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                  Setup Complete! 🎉                      ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Configure your API key:"
echo "   - Open .env file in a text editor"
echo "   - Add your GEMINI_API_KEY=your-actual-key"
echo "   - Get key from: https://makersuite.google.com/app/apikey"
echo ""
echo "2. Activate virtual environment (if not already active):"
echo "   source venv/bin/activate"
echo ""
echo "3. Start the server:"
echo "   cd backend"
echo "   python main.py"
echo ""
echo "4. Open the web interface:"
echo "   open frontend/index.html  # Mac"
echo "   xdg-open frontend/index.html  # Linux"
echo ""
echo "5. Or run the demo:"
echo "   python test_critique.py"
echo ""
echo "📚 Documentation:"
echo "   - README.md - Project overview"
echo "   - QUICKSTART.md - Detailed setup guide"
echo "   - TECHNICAL_DOCS.md - Architecture details"
echo "   - PITCH_DECK.md - Hackathon presentation"
echo ""
echo "🌐 API Documentation (after starting server):"
echo "   http://localhost:8000/docs"
echo ""
echo "💡 Need help? Check QUICKSTART.md for troubleshooting!"
echo ""
