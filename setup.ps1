# BrandAI Setup Script for Windows PowerShell
# Run this script to set up the project automatically

Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                       BrandAI                            ║" -ForegroundColor Cyan
Write-Host "║          AI-Powered Ad Critique System                   ║" -ForegroundColor Cyan
Write-Host "║                   Setup Script                           ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
Write-Host "🔍 Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found! Please install Python 3.9 or higher." -ForegroundColor Red
    Write-Host "   Download from: https://www.python.org/downloads/" -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host ""
Write-Host "🔧 Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "⚠️  Virtual environment already exists, skipping..." -ForegroundColor Yellow
} else {
    python -m venv venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host ""
Write-Host "🚀 Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Install dependencies
Write-Host ""
Write-Host "📦 Installing dependencies (this may take a few minutes)..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Dependencies installed successfully" -ForegroundColor Green
} else {
    Write-Host "⚠️  Some dependencies may have failed. Please check the output." -ForegroundColor Yellow
}

# Create .env file if it doesn't exist
Write-Host ""
Write-Host "⚙️  Setting up environment configuration..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "⚠️  .env file already exists, skipping..." -ForegroundColor Yellow
} else {
    Copy-Item ".env.example" ".env"
    Write-Host "✅ .env file created from template" -ForegroundColor Green
    Write-Host "⚠️  IMPORTANT: Edit .env file and add your GEMINI_API_KEY" -ForegroundColor Yellow
}

# Create necessary directories
Write-Host ""
Write-Host "📁 Creating directories..." -ForegroundColor Yellow
$dirs = @("uploads", "brand_kits", "generated_ads", "brand_kits\logos")
foreach ($dir in $dirs) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}
Write-Host "✅ Directories created" -ForegroundColor Green

# Display next steps
Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                  Setup Complete! 🎉                      ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Configure your API key:" -ForegroundColor White
Write-Host "   - Open .env file in a text editor" -ForegroundColor Gray
Write-Host "   - Add your GEMINI_API_KEY=your-actual-key" -ForegroundColor Gray
Write-Host "   - Get key from: https://makersuite.google.com/app/apikey" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Start the server:" -ForegroundColor White
Write-Host "   cd backend" -ForegroundColor Gray
Write-Host "   python main.py" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Open the web interface:" -ForegroundColor White
Write-Host "   start ..\frontend\index.html" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Or run the demo:" -ForegroundColor White
Write-Host "   python test_critique.py" -ForegroundColor Gray
Write-Host ""
Write-Host "📚 Documentation:" -ForegroundColor Yellow
Write-Host "   - README.md - Project overview" -ForegroundColor Gray
Write-Host "   - QUICKSTART.md - Detailed setup guide" -ForegroundColor Gray
Write-Host "   - TECHNICAL_DOCS.md - Architecture details" -ForegroundColor Gray
Write-Host "   - PITCH_DECK.md - Hackathon presentation" -ForegroundColor Gray
Write-Host ""
Write-Host "🌐 API Documentation (after starting server):" -ForegroundColor Yellow
Write-Host "   http://localhost:8000/docs" -ForegroundColor Gray
Write-Host ""
Write-Host "💡 Need help? Check QUICKSTART.md for troubleshooting!" -ForegroundColor Cyan
Write-Host ""
