# 🎯 BrandAI - AI-Powered Ad Critique System

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)](https://fastapi.tiangolo.com/)
[![Google Gemini](https://img.shields.io/badge/Google-Gemini%20Vision-4285F4.svg)](https://ai.google.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Built for Hack Nation 2025 - VC Big Bets Track**  
> *The AI that critiques AI-generated ads - Building the trust layer for autonomous advertising*

## 🌟 Overview
BrandAI is an AI system that evaluates, critiques, and improves AI-generated advertisements. It acts as an automated **Creative Director + Brand Compliance Officer**, ensuring ads are on-brand, safe, high-quality, and ready for deployment.

**The Problem:** Millions of AI-generated ads exist, but brands can't deploy them without human review.  
**Our Solution:** An AI critique engine that judges if another AI did a good job - enabling autonomous ad deployment.

## 🚀 Quick Start

```powershell
# Windows
.\setup.ps1

# Or manually:
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
# Edit .env with your GEMINI_API_KEY

# Start server
cd backend
python main.py

# Open frontend
start ..\frontend\index.html
```

See [QUICKSTART.md](QUICKSTART.md) for detailed setup instructions.

## 📊 How It Works

```
┌─────────────┐
│  Upload Ad  │
└──────┬──────┘
       │
┌──────▼─────────────────────────┐
│    AI Critique Engine          │
│                                 │
│  ┌──────────────────────────┐ │
│  │ Gemini Vision API        │ │  ← Brand alignment, safety
│  └──────────────────────────┘ │
│  ┌──────────────────────────┐ │
│  │ Computer Vision (OpenCV) │ │  ← Visual quality
│  └──────────────────────────┘ │
│  ┌──────────────────────────┐ │
│  │ Color Matching           │ │  ← Brand color alignment
│  └──────────────────────────┘ │
└───────────┬────────────────────┘
            │
┌───────────▼────────────────┐
│  Structured Scorecard      │
│  • Overall: 85% (GOOD)     │
│  • Brand Fit: 88%          │
│  • Quality: 85%            │
│  • Clarity: 75%            │
│  • Safety: 100%            │
│  ✅ Ready to Deploy        │
└────────────────────────────┘
```

## ✨ Core Features

### Hero Feature: AI Critique Engine ⭐
- **Brand Alignment**: Evaluates color palette, logo usage, tone of voice
- **Visual Quality**: Checks for blurriness, composition, watermarks, artifacts
- **Message Clarity**: Validates product visibility and tagline accuracy
- **Safety & Ethics**: Detects harmful content, stereotypes, misleading claims
- **Structured Output**: JSON scorecard with actionable feedback

### Additional Features
- Minimal ad generation using Google Vertex AI (Imagen 2, Veo)
- Multi-agent workflow (Generator → Critic → Refinement)
- Brand kit extraction and management
- Auto-improvement loop with regeneration

## Architecture

```
BrandAI/
├── backend/
│   ├── app/
│   │   ├── api/              # FastAPI routes
│   │   ├── core/             # Core critique engine
│   │   ├── models/           # Data models
│   │   ├── services/         # Business logic
│   │   └── utils/            # Helper functions
│   ├── main.py
│   └── config.py
├── frontend/
│   ├── static/
│   └── templates/
├── brand_kits/               # Stored brand guidelines
├── uploads/                  # Temporary ad uploads
├── requirements.txt
└── .env
```

## Technology Stack

- **AI Models**: Google Gemini Vision, Imagen 2, Veo 3
- **Backend**: FastAPI (Python)
- **Image Processing**: OpenCV, PIL
- **ML Libraries**: Transformers, google-cloud-aiplatform
- **Frontend**: HTML/CSS/JavaScript with Tailwind CSS

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up environment variables in `.env`
4. Run the server: `python backend/main.py`

## API Endpoints

- `POST /api/generate-ad` - Generate a basic ad
- `POST /api/critique-ad` - Critique an uploaded ad
- `POST /api/improve-ad` - Auto-improve ad based on critique
- `POST /api/brand-kit` - Upload brand guidelines
- `GET /api/brand-kit/{brand_id}` - Retrieve brand kit

## Scoring System

Each ad receives scores (0-1) across:
- **BrandFit**: Alignment with brand guidelines
- **VisualQuality**: Technical and aesthetic quality
- **Safety**: Ethical and safety compliance
- **Clarity**: Message and product clarity

**Overall Score**: Weighted average of all dimensions

## License
MIT License

---

## 📁 Project Structure

```
BrandAI/
├── backend/
│   ├── main.py                      # FastAPI app entry
│   ├── config.py                    # Configuration
│   └── app/
│       ├── api/                     # API endpoints
│       │   ├── critique.py         # ⭐ Critique routes
│       │   ├── brand_kit.py        # Brand management
│       │   └── generate.py         # Ad generation
│       ├── core/
│       │   └── critique_engine.py  # ⭐ Hero Feature
│       ├── models/
│       │   └── schemas.py          # Data models
│       ├── services/               # Business logic
│       └── utils/                  # Helper functions
├── frontend/
│   └── index.html                  # Web interface
├── documentation/
│   ├── README.md                   # This file
│   ├── QUICKSTART.md              # Setup guide
│   ├── TECHNICAL_DOCS.md          # Architecture
│   ├── PITCH_DECK.md              # Presentation
│   ├── PROJECT_SUMMARY.md         # Complete summary
│   └── DEMO_CHECKLIST.md          # Demo preparation
├── setup.ps1                       # Windows setup script
├── setup.sh                        # Linux/Mac setup script
└── test_critique.py               # Demo script
```

## 🎓 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Get started in 5 minutes
- **[TECHNICAL_DOCS.md](TECHNICAL_DOCS.md)** - Deep dive into architecture
- **[PITCH_DECK.md](PITCH_DECK.md)** - Hackathon presentation slides
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Complete project overview
- **[DEMO_CHECKLIST.md](DEMO_CHECKLIST.md)** - Demo preparation guide

## 🤝 Contributing

This is a hackathon project, but contributions are welcome! Please read the code and documentation to understand the architecture first.

## 📧 Contact

- **Project**: BrandAI - AI Ad Critique System
- **Track**: VC Big Bets - Hack Nation 2025
- **Team**: TriHuskAI
- **Repository**: [GitHub](https://github.com/510jahnavi/Hack-Nation-TriHuskAI)

---

**Built with ❤️ for autonomous AI advertising**


