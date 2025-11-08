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

### Single Ad Critique
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

### 🤖 Multi-Agent Workflow (Auto-Refinement)
```
User Prompt: "Create a Nike ad for Air Max shoes"
      │
      ▼
┌─────────────────────┐
│ 1. GENERATOR AGENT  │ → Creates initial ad (Imagen 2)
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│ 2. DESCRIPTOR AGENT │ → Analyzes: colors, text, objects, mood
└──────────┬──────────┘   "Blue/red, Nike swoosh, 'Just Do It'"
           ▼
┌─────────────────────┐
│ 3. CRITIC AGENT     │ → Scores: Brand 0.65, Quality 0.80, 
└──────────┬──────────┘   Clarity 0.70, Safety 1.0 = 0.74 ❌
           ▼
    Score < 0.75? → YES
           ▼
┌─────────────────────┐
│ 4. REFINEMENT AGENT │ → Improves prompt: "Add brand colors 
└──────────┬──────────┘   (red #DC143C), larger logo, bold CTA"
           │
           └──→ Back to Generator (Iteration 2)
                     ↓
                Score 0.82 ✅ → Success!
```

## ✨ Core Features

### 🎯 Hero Feature: AI Critique Engine ⭐
- **Brand Alignment**: Evaluates color palette, logo usage, tone of voice
- **Visual Quality**: Checks for blurriness, composition, watermarks, artifacts
- **Message Clarity**: Validates product visibility and tagline accuracy
- **Safety & Ethics**: Detects harmful content, stereotypes, misleading claims
- **Structured Output**: JSON scorecard with actionable feedback

### 🤖 Multi-Agent Workflow (NEW!)
**Automatic ad generation and refinement pipeline:**

1. **Generator Agent** - Creates initial ad using Imagen 2 / Vertex AI
2. **Descriptor Agent** - Analyzes all ad components (colors, objects, text, mood, brand elements)
3. **Critic Agent** - Scores the ad across 4 dimensions (brand, quality, clarity, safety)
4. **Refinement Agent** - Generates improved prompts based on critique feedback

**How it works:**
- Set target score threshold (e.g., 0.75) and max iterations (e.g., 3)
- System automatically generates → describes → critiques → refines
- Loops until score meets threshold or max iterations reached
- Tracks all iterations and selects best result
- Returns complete history with score progression

**API Endpoint:** `POST /api/multi-agent/generate-and-refine`

### Additional Features
- Minimal ad generation using Google Vertex AI (Imagen 2, Veo)
- Brand kit extraction and management
- Real-time critique feedback with visual score cards
- Iteration history tracking and comparison

## Architecture

```
BrandAI/
├── backend/
│   ├── app/
│   │   ├── api/              # FastAPI routes
│   │   │   ├── critique.py   # Ad critique endpoints
│   │   │   ├── generate.py   # Ad generation endpoints
│   │   │   ├── brand_kit.py  # Brand management
│   │   │   └── multi_agent.py # 🤖 Multi-agent workflow
│   │   ├── core/             # Core engines
│   │   │   ├── critique_engine.py      # ⭐ Hero: Critique logic
│   │   │   ├── descriptor_agent.py     # 🤖 Component analysis
│   │   │   ├── refinement_agent.py     # 🤖 Prompt improvement
│   │   │   └── multi_agent_orchestrator.py # 🤖 Workflow manager
│   │   ├── models/           # Data models
│   │   ├── services/         # Business logic
│   │   └── utils/            # Helper functions
│   ├── main.py
│   └── config.py
├── frontend/
│   └── index.html            # Web UI (4 tabs including Multi-Agent)
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

### Critique & Analysis
- `POST /api/critique-ad` - Critique an uploaded ad
- `POST /api/generate-ad` - Generate a basic ad
- `POST /api/improve-ad` - Auto-improve ad based on critique

### 🤖 Multi-Agent Workflow
- `POST /api/multi-agent/generate-and-refine` - Run full auto-refinement pipeline
- `GET /api/multi-agent/workflow-status` - Check agent system status

### Brand Management
- `POST /api/brand-kit` - Upload brand guidelines
- `GET /api/brand-kit/{brand_id}` - Retrieve brand kit
- `GET /api/brand-kits` - List all brand kits

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
│       │   ├── generate.py         # Ad generation
│       │   └── multi_agent.py      # 🤖 Multi-agent workflow
│       ├── core/
│       │   ├── critique_engine.py  # ⭐ Hero Feature: AI Critic
│       │   ├── descriptor_agent.py # 🤖 Component analyzer
│       │   ├── refinement_agent.py # 🤖 Prompt improver
│       │   └── multi_agent_orchestrator.py # 🤖 Workflow manager
│       ├── models/
│       │   └── schemas.py          # Data models
│       ├── services/               # Business logic
│       └── utils/                  # Helper functions
├── frontend/
│   └── index.html                  # Web interface (4 tabs)
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


