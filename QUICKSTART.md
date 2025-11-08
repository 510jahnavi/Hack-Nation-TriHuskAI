# BrandAI - Quick Start Guide

## 🎯 Project Overview

BrandAI is an AI critique system that evaluates AI-generated ads across:
- **Brand Alignment**: Colors, logo, tone of voice
- **Visual Quality**: Sharpness, composition, artifacts
- **Message Clarity**: Product visibility, tagline readability
- **Safety & Ethics**: Harmful content, bias detection

**Hero Feature**: AI Critique Engine using Gemini Vision + Computer Vision

## 📋 Prerequisites

1. **Python 3.9+**
2. **Google Cloud Account** with Vertex AI enabled (for Gemini & Imagen)
3. **API Keys**:
   - Gemini API key OR Google Cloud service account
   - Optional: OpenAI API key for comparison

## 🚀 Quick Setup

### 1. Install Dependencies

```powershell
# Navigate to project directory
cd c:\Users\popli\OneDrive\Desktop\hacknation\Hack-Nation-TriHuskAI

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install packages
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your credentials:

```powershell
Copy-Item .env.example .env
```

Edit `.env` with your values:
```
GEMINI_API_KEY=your-actual-gemini-key
GOOGLE_CLOUD_PROJECT=your-project-id
# ... other settings
```

### 3. Run the Server

```powershell
# Make sure virtual environment is activated
cd backend
python main.py
```

The server will start at `http://localhost:8000`

### 4. Open the Frontend

Open `frontend/index.html` in your browser, or use:
```powershell
start frontend/index.html
```

## 🎨 Usage Workflow

### Creating a Brand Kit

1. Go to "Brand Kits" tab
2. Fill in:
   - Brand name (e.g., "Nike")
   - Primary colors (e.g., "#FF0000, #000000")
   - Tone of voice (e.g., "energetic, inspiring, bold")
   - Brand values (optional)
3. Click "Create Brand Kit"

### Critiquing an Ad

1. Go to "Critique Ad" tab
2. Upload an image (ad you want to critique)
3. Select a brand kit (optional - for brand-specific critique)
4. Add description (optional)
5. Click "Critique Ad"
6. View detailed results with scores and suggestions

### Generating an Ad (Optional)

1. Go to "Generate Ad" tab
2. Select a brand kit
3. Enter product details
4. Click "Generate Ad"
5. Ad will be generated and can then be critiqued

## 📊 API Endpoints

- `POST /api/critique-ad` - Critique an ad
- `POST /api/brand-kit` - Create brand kit
- `GET /api/brand-kits` - List all brand kits
- `POST /api/generate-ad` - Generate ad (requires Vertex AI)
- `GET /docs` - Interactive API documentation

## 🛠️ Testing Without Full Setup

If you don't have Google Cloud credentials yet:

1. The critique engine will use fallback mode
2. You can still:
   - Upload and analyze images using OpenCV
   - Extract color palettes
   - Analyze visual quality
   - Create brand kits
3. AI-powered critique will show placeholder feedback

## 🎯 Key Files

- `backend/app/core/critique_engine.py` - **Hero Feature**: Main critique logic
- `backend/app/utils/image_analysis.py` - Computer vision analysis
- `backend/app/utils/color_analysis.py` - Color matching
- `backend/app/api/critique.py` - Critique API endpoints
- `frontend/index.html` - Web interface

## 🔧 Troubleshooting

### Import Errors
```powershell
# Reinstall packages
pip install -r requirements.txt --upgrade
```

### Google Cloud Authentication
```powershell
# Set up authentication
gcloud auth application-default login

# Or use service account
$env:GOOGLE_APPLICATION_CREDENTIALS="path\to\service-account-key.json"
```

### Port Already in Use
Edit `backend/config.py` or `.env` to change `APP_PORT`

## 📈 Next Steps - Stretch Goals

1. **Multi-agent Workflow**: Implement Generator → Critic → Refiner pipeline
2. **Auto Brand Extraction**: Extract brand colors from website
3. **Fine-tune Model**: Train custom critique model
4. **Video Support**: Add video ad critique with Veo
5. **Database**: Add PostgreSQL for storing critiques
6. **Deployment**: Deploy to Google Cloud Run

## 🎓 Challenge Focus

Remember: **The critique engine is the hero feature**, not generation!

Focus on:
- ✅ Accurate brand alignment scoring
- ✅ Comprehensive safety detection
- ✅ Actionable improvement suggestions
- ✅ Trust layer for autonomous deployment

Generation is secondary - just enough to create test ads.

## 📚 Resources

- [Gemini API Docs](https://ai.google.dev/docs)
- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenCV Tutorials](https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html)

---

**Built for Hack Nation - VC Big Bets Track** 🚀
