# TriHuskAI - Video Ad Generation Workflow

## 🎬 Complete AI Video Ad Workflow

**Updated:** November 8, 2025

---

## 🎯 Final Workflow: Generate VIDEO → Describe → Critique → Refine

### Process Flow

```
User Input:
├── Prompt: "Create an ad for eco-friendly water bottles"
├── Brand Kit: EcoFlow (colors: #2E7D32, #66BB6A, tone: natural)
├── Media Type: "video"
└── Duration: 10 seconds

                    ↓

Step 1: GENERATOR AGENT
├── Primary: Google Veo (veo-001) - Text-to-Video
│   └── Generates 5-15 second professional video ad
│   └── Incorporates brand colors, tone, style
│   └── Cinematic quality with smooth camera movements
│
└── Fallback: PIL + ffmpeg
    └── Generates static image with brand colors
    └── Converts to video using ffmpeg (if available)
    └── Returns static image if ffmpeg unavailable

                    ↓

Step 2: DESCRIPTOR AGENT  
├── Analyzes video/image content
│   ├── Dominant colors extracted
│   ├── Text elements detected (OCR)
│   ├── Objects identified
│   ├── Mood/style assessed
│   └── Composition analyzed
│
└── Output: Description JSON
    {
      "summary": "Eco-friendly water bottle video...",
      "colors": ["#2E7D32", "#66BB6A"],
      "text_elements": ["EcoFlow", "Sustainable"],
      "detected_objects": ["water bottle", "nature"],
      "mood": "natural, calm, eco-conscious"
    }

                    ↓

Step 3: CRITIQUE AGENT
├── Evaluates against brand kit
│   ├── Brand Alignment Score (0-1)
│   │   └── Color match, tone alignment, values consistency
│   ├── Visual Quality Score (0-1)
│   │   └── Sharpness, composition, contrast, production quality
│   ├── Message Clarity Score (0-1)
│   │   └── Product visibility, tagline readability, CTA clarity
│   └── Safety & Ethics Score (0-1)
│       └── No harmful content, stereotypes, misleading claims
│
└── Output: Critique with scores + feedback
    {
      "brand_alignment_score": 0.87,
      "visual_quality_score": 0.72,
      "message_clarity_score": 0.90,
      "safety_score": 0.95,
      "overall_score": 0.86,
      "feedback": { ... },
      "issues": [ ... ],
      "suggestions": [ ... ]
    }

                    ↓

Step 4: REFINEMENT AGENT (if score < 0.75)
├── Analyzes critique feedback
├── Identifies weak areas
├── Generates improved prompt
│   └── Addresses brand alignment issues
│   └── Enhances visual quality requirements
│   └── Clarifies message elements
│   └── Adds safety constraints
│
└── Loop back to Step 1 with improved prompt

                    ↓

Final Output:
├── Best video ad (highest score across iterations)
├── Complete iteration history
├── Detailed critique for each iteration
└── Recommendation: Deploy or refine further
```

---

## 📡 API Endpoint

### POST /api/multi-agent/generate-and-refine

**Request:**
```json
{
  "prompt": "Create a professional ad for eco-friendly water bottles showcasing sustainability",
  "brand_kit_id": "7de3d58f-e632-47c1-a77e-5127b04f9d45",
  "media_type": "video",
  "duration": 10,
  "aspect_ratio": "16:9",
  "max_iterations": 3,
  "score_threshold": 0.75
}
```

**Response:**
```json
{
  "success": true,
  "iterations_count": 2,
  "final_score": 0.86,
  "threshold_met": true,
  
  "best_ad": {
    "iteration": 2,
    "media_path": "generated_ads/abc123.mp4",
    "media_type": "video",
    "score": 0.86,
    "duration": 10,
    
    "critique": {
      "brand_alignment_score": 0.87,
      "visual_quality_score": 0.82,
      "message_clarity_score": 0.90,
      "safety_score": 0.95,
      "overall_score": 0.86,
      
      "brand_alignment": {
        "score": 0.87,
        "feedback": "Excellent color palette match with brand",
        "issues": [],
        "suggestions": ["Consider adding brand logo overlay"]
      },
      
      "visual_quality": {
        "score": 0.82,
        "feedback": "Professional cinematic quality",
        "issues": ["Slight motion blur in frame 3-5"],
        "suggestions": ["Increase stabilization"]
      },
      
      "message_clarity": {
        "score": 0.90,
        "feedback": "Product clearly showcased, strong CTA",
        "issues": [],
        "suggestions": []
      },
      
      "safety_ethics": {
        "score": 0.95,
        "feedback": "No safety or ethical concerns",
        "issues": [],
        "suggestions": []
      }
    },
    
    "description": {
      "summary": "10-second video showing eco-friendly water bottle in natural setting with green tones",
      "colors": ["#2E7D32", "#66BB6A", "#E8F5E9"],
      "text_elements": ["EcoFlow", "Sustainable Hydration", "Shop Now"],
      "detected_objects": ["water bottle", "leaves", "water splash"],
      "mood": "natural, calming, eco-conscious",
      "camera_movement": "slow pan, product focus"
    },
    
    "prompt": "Create a professional 10-second video advertisement for eco-friendly water bottles. Brand: EcoFlow. Visual Requirements: Cinematic quality with smooth camera movements, professional lighting and color grading, color palette: #2E7D32, #66BB6A. Tone/Mood: natural. Style: modern and professional. Key Elements: Clear product showcase, engaging visual storytelling, brand-appropriate aesthetics, call-to-action at end."
  },
  
  "iterations": [
    {
      "iteration": 1,
      "overall_score": 0.68,
      "status": "refined",
      "generation": { "success": true, "media_path": "generated_ads/xyz789.mp4" },
      "critique": { "overall_score": 0.68, "issues": ["Color mismatch", "Unclear product"] },
      "refinement": {
        "improved_prompt": "Enhanced version with brand colors explicitly specified...",
        "changes_made": ["Added explicit color constraints", "Enhanced product focus"]
      }
    },
    {
      "iteration": 2,
      "overall_score": 0.86,
      "status": "success",
      "reason": "threshold_met",
      "generation": { "success": true, "media_path": "generated_ads/abc123.mp4" }
    }
  ],
  
  "workflow_duration_seconds": 45.3,
  "message": "✅ Success! Achieved 0.86 score in 2 iteration(s)"
}
```

---

## 🎬 Video Generation Details

### Google Veo Integration

**Model:** `veo-001` (Google's text-to-video model)

**Capabilities:**
- 5-15 second high-quality videos
- 1080p resolution minimum
- Multiple aspect ratios (1:1, 16:9, 9:16)
- Brand color integration
- Cinematic camera movements
- Professional lighting and composition

**Prompt Structure:**
```python
video_prompt = f"""
Create a professional {duration}-second video advertisement.

Product/Theme: {user_prompt}
Brand: {brand_name}

Visual Requirements:
- Cinematic quality with smooth camera movements
- Professional lighting and color grading
- Color palette: {brand_colors}
- Tone/Mood: {brand_tone}

Style: {style}

Key Elements:
- Clear product showcase
- Engaging visual storytelling
- Brand-appropriate aesthetics
- Call-to-action at end

Technical Specs:
- High resolution (1080p or better)
- Smooth transitions
- Professional composition
"""
```

### Fallback Options

**Level 1: PIL + ffmpeg**
```python
# Generate static image with brand colors (PIL)
# Convert to video using ffmpeg
ffmpeg -loop 1 -i image.png -c:v libx264 -t 10 -pix_fmt yuv420p output.mp4
```

**Level 2: Static Image**
```python
# If ffmpeg unavailable, return high-quality static image
# System still runs descriptor + critique on image
```

---

## 🤖 Agent Specifications

### 1. Generator Agent

**File:** `backend/app/services/generation_service.py`

**Video Generation Method:**
```python
async def _generate_video(
    prompt: str,
    request: GenerateAdRequest,
    brand_kit: Optional[object] = None
) -> Dict[str, Any]:
    """
    Generate video ad using Google Veo
    
    Returns:
      - video_path: Path to generated MP4
      - duration: Video length in seconds
      - generation_model: "veo-001" or "pil-fallback"
    """
```

**Brand Integration:**
- Injects brand colors into Veo prompt
- Applies brand tone (natural, professional, energetic)
- Includes brand values in visual style
- Adds brand name to composition

### 2. Descriptor Agent

**File:** `backend/app/core/descriptor_agent.py`

**Video Analysis:**
- Extracts key frames for analysis
- Identifies dominant colors across frames
- Detects text overlays (OCR)
- Recognizes objects and scenes
- Assesses camera movement style
- Evaluates overall mood/tone

**Output:** Structured description for critique

### 3. Critique Agent

**File:** `backend/app/core/critique_engine.py`

**Video Evaluation:**
- **Brand Alignment (0-1)**
  - Color consistency across frames
  - Brand logo visibility
  - Tone alignment with brand values
  
- **Visual Quality (0-1)**
  - Video sharpness/clarity
  - Composition quality
  - Camera movement smoothness
  - Production value
  
- **Message Clarity (0-1)**
  - Product visibility throughout
  - Text readability
  - Call-to-action effectiveness
  - Visual storytelling flow
  
- **Safety & Ethics (0-1)**
  - No harmful content
  - Appropriate imagery
  - Truthful claims
  - Stereotype avoidance

### 4. Refinement Agent

**File:** `backend/app/core/refinement_agent.py`

**Video Prompt Improvement:**
- Analyzes critique weak points
- Adds specific visual constraints
- Enhances camera movement descriptions
- Clarifies brand integration requirements
- Specifies color usage more explicitly

---

## 🔧 Technical Requirements

### Dependencies

```python
# requirements.txt additions for video
google-cloud-aiplatform>=1.38.0
vertexai>=1.38.0
ffmpeg-python>=0.2.0  # For fallback video creation
opencv-python>=4.8.0  # Video frame analysis
```

### Google Cloud Setup

```bash
# Enable Vertex AI API
gcloud services enable aiplatform.googleapis.com

# Set project
export GOOGLE_CLOUD_PROJECT=lucid-vector-477619-a6

# Authenticate (if needed)
gcloud auth application-default login
```

### Environment Variables

```env
# .env file
GOOGLE_CLOUD_PROJECT=lucid-vector-477619-a6
VERTEX_AI_LOCATION=us-central1
GEMINI_API_KEY=AIzaSyCdWfpIa8Ur8VfuJwr4xM0jDAAApE1s0Kc
```

---

## 📊 Scoring System

### Overall Score Calculation

```python
overall_score = (
    brand_alignment * 0.30 +  # 30% - Most important for brand consistency
    visual_quality * 0.25 +   # 25% - Video production quality
    message_clarity * 0.25 +  # 25% - Communication effectiveness
    safety_ethics * 0.20      # 20% - Critical but usually high
)
```

### Video-Specific Metrics

**Visual Quality includes:**
- Frame sharpness (per frame analysis)
- Motion blur detection
- Camera stability
- Color grading quality
- Transition smoothness
- Production value (lighting, composition)

**Message Clarity includes:**
- Product screen time percentage
- Text overlay readability
- CTA prominence
- Story arc coherence
- Pacing effectiveness

---

## 🚀 Usage Examples

### Example 1: Generate Eco Video Ad

```python
import requests

url = "http://127.0.0.1:8000/api/multi-agent/generate-and-refine"

request_data = {
    "prompt": "Create a professional video ad for sustainable water bottles featuring ocean waves and nature",
    "brand_kit_id": "7de3d58f-e632-47c1-a77e-5127b04f9d45",  # EcoFlow
    "media_type": "video",
    "duration": 10,
    "aspect_ratio": "16:9",
    "max_iterations": 3,
    "score_threshold": 0.75
}

response = requests.post(url, json=request_data)
result = response.json()

print(f"✅ Final Score: {result['final_score']}")
print(f"📹 Video: {result['best_ad']['media_path']}")
print(f"🔄 Iterations: {result['iterations_count']}")
```

### Example 2: Tech Product Video

```python
request_data = {
    "prompt": "Showcase innovative smartwatch with health tracking features in modern tech environment",
    "brand_kit_id": "fitpulse-tech-brand-id",
    "media_type": "video",
    "duration": 15,
    "aspect_ratio": "9:16",  # Vertical for social media
    "max_iterations": 3,
    "score_threshold": 0.80
}

response = requests.post(url, json=request_data)
```

### Example 3: cURL Command

```bash
curl -X POST http://127.0.0.1:8000/api/multi-agent/generate-and-refine \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Luxury fashion ad with elegant model in urban setting",
    "brand_kit_id": "urbanthread-fashion-id",
    "media_type": "video",
    "duration": 12,
    "aspect_ratio": "1:1",
    "max_iterations": 3,
    "score_threshold": 0.75
  }'
```

---

## 🎯 Key Features

✅ **AI Video Generation** - Google Veo text-to-video  
✅ **Brand Integration** - Colors, tone, values in video  
✅ **Multi-Agent Workflow** - 4 agents working together  
✅ **Automatic Refinement** - Improves until threshold met  
✅ **Detailed Critique** - 4 dimensions, 0-1 scale  
✅ **Iteration Tracking** - Complete workflow history  
✅ **Fallback System** - PIL + ffmpeg when Veo unavailable  
✅ **Multiple Formats** - 1:1, 16:9, 9:16 aspect ratios  
✅ **Flexible Duration** - 5-15 second videos  

---

## ✅ System Status

**Server:** ✅ Running on http://127.0.0.1:8000  
**Veo Integration:** ✅ Implemented (requires Vertex AI auth)  
**Fallback:** ✅ PIL + ffmpeg ready  
**API Key:** ✅ Gemini 2.0 Flash configured  
**Vertex AI:** ✅ Project lucid-vector-477619-a6  

**Test Now:**
```bash
# Test video generation workflow
curl -X POST http://127.0.0.1:8000/api/multi-agent/generate-and-refine \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Eco-friendly water bottle ad",
    "brand_kit_id": "7de3d58f-e632-47c1-a77e-5127b04f9d45",
    "media_type": "video",
    "duration": 10
  }'
```

---

*Last Updated: November 8, 2025*  
*TriHuskAI - Video Ad Generation System*
