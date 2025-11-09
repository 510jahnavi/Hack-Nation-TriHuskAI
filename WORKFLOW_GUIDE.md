# TriHuskAI - Complete Workflow Guide

## 🎯 System Overview

Your system supports **TWO complete workflows**:

### Workflow 1: Generate → Describe → Critique → Refine (Auto-Generation)
### Workflow 2: Upload → Describe → Critique (User-Provided Ad)

---

## 📊 Workflow 1: Auto-Generation with Refinement

**Use Case:** Generate AI ads from prompts and automatically improve them

**API Endpoint:** `POST /api/multi-agent/generate-and-refine`

**Process:**
```
1. User provides prompt + brand kit
   ↓
2. Generator Agent creates ad image
   ↓
3. Descriptor Agent analyzes components (colors, text, objects, mood)
   ↓
4. Critique Agent evaluates across 4 dimensions:
   - Brand Alignment (0-1)
   - Visual Quality (0-1)
   - Message Clarity (0-1)
   - Safety & Ethics (0-1)
   ↓
5. IF score < threshold (default 0.75):
   - Refinement Agent improves prompt
   - Loop back to step 2
   ↓
6. Return best ad after max iterations (default 3)
```

**Request Example:**
```json
{
  "prompt": "Create an ad for sustainable water bottles",
  "brand_kit_id": "7de3d58f-e632-47c1-a77e-5127b04f9d45",
  "max_iterations": 3,
  "score_threshold": 0.75,
  "aspect_ratio": "1:1"
}
```

**Response Example:**
```json
{
  "success": true,
  "iterations_count": 3,
  "best_ad": {
    "iteration": 2,
    "image_path": "generated_ads/abc123.png",
    "score": 0.86,
    "critique": {
      "brand_alignment_score": 0.87,
      "visual_quality_score": 0.82,
      "message_clarity_score": 0.90,
      "safety_score": 0.85,
      "overall_score": 0.86
    }
  },
  "threshold_met": true,
  "final_score": 0.86,
  "iterations": [/* full history */]
}
```

**Agents Involved:**
- ✅ **Generator Agent** (`generation_service.py`) - Imagen 3 / PIL
- ✅ **Descriptor Agent** (`descriptor_agent.py`) - Gemini Vision analysis
- ✅ **Critique Agent** (`critique_engine.py`) - Multi-dimensional scoring
- ✅ **Refinement Agent** (`refinement_agent.py`) - Prompt improvement

---

## 📤 Workflow 2: User Upload Critique

**Use Case:** User provides existing ad clip, system evaluates it

**API Endpoint:** `POST /api/multi-agent/critique-uploaded-ad`

**Process:**
```
1. User uploads ad file (image/video) + selects brand kit
   ↓
2. Descriptor Agent analyzes ad components:
   - Dominant colors
   - Text elements (OCR)
   - Objects detected
   - Overall mood/style
   - Visual composition
   ↓
3. Critique Agent evaluates:
   - Brand Alignment (vs brand kit colors, tone, values)
   - Visual Quality (sharpness, composition, contrast)
   - Message Clarity (product visibility, tagline readability)
   - Safety & Ethics (harmful content, stereotypes, claims)
   ↓
4. Return detailed critique with scores + recommendations
```

**Request (Form Data):**
```
file: [uploaded image/video file]
brand_kit_id: "7de3d58f-e632-47c1-a77e-5127b04f9d45"  // optional
```

**Response Example:**
```json
{
  "success": true,
  "filename": "my_ad.jpg",
  "file_path": "uploads/xyz789.jpg",
  "brand_kit": {
    "id": "7de3d58f-e632-47c1-a77e-5127b04f9d45",
    "name": "EcoFlow",
    "colors": ["#2E7D32", "#66BB6A"]
  },
  "description": {
    "summary": "Eco-friendly water bottle ad with green nature theme...",
    "colors": ["#2E7D32", "#66BB6A", "#E8F5E9"],
    "text_elements": ["EcoFlow", "Sustainable Hydration"],
    "detected_objects": ["water bottle", "leaves", "logo"],
    "mood": "natural, calm, eco-conscious"
  },
  "critique": {
    "brand_alignment_score": 0.92,
    "visual_quality_score": 0.78,
    "message_clarity_score": 0.85,
    "safety_score": 0.95,
    "overall_score": 0.88,
    
    "brand_alignment": {
      "score": 0.92,
      "level": "excellent",
      "feedback": "Perfect brand color match! Green palette aligns with eco values.",
      "issues": [],
      "suggestions": ["Consider adding brand logo"]
    },
    
    "visual_quality": {
      "score": 0.78,
      "level": "good",
      "feedback": "Good composition and clarity",
      "issues": ["Slight blur in background"],
      "suggestions": ["Increase contrast by 10%"]
    },
    
    "message_clarity": {
      "score": 0.85,
      "level": "excellent",
      "feedback": "Clear product visibility and tagline",
      "issues": [],
      "suggestions": ["Make tagline slightly larger"]
    },
    
    "safety_ethics": {
      "score": 0.95,
      "level": "excellent",
      "feedback": "No safety or ethical concerns",
      "issues": [],
      "suggestions": []
    },
    
    "confidence_scores": {
      "brand_alignment": 0.91,
      "visual_quality": 0.85,
      "message_clarity": 0.88,
      "safety": 0.95,
      "overall": 0.90
    },
    
    "needs_manual_review": false
  },
  
  "workflow": {
    "step_1": "Descriptor Agent - Analyzed ad components",
    "step_2": "Critique Agent - Evaluated quality and alignment"
  }
}
```

**Agents Involved:**
- ✅ **Descriptor Agent** (`descriptor_agent.py`) - Analyzes uploaded ad
- ✅ **Critique Agent** (`critique_engine.py`) - Scores across 4 dimensions

---

## 🔧 Technical Implementation

### Descriptor Agent
**File:** `backend/app/core/descriptor_agent.py`

**Capabilities:**
- **Color Extraction:** OpenCV + ColorThief (top 5 dominant colors)
- **Text Detection:** Gemini Vision OCR
- **Object Recognition:** Gemini Vision object detection
- **Mood Analysis:** AI-powered sentiment analysis
- **Composition:** Rule of thirds, golden ratio analysis

**Example Output:**
```python
{
  "summary": "Professional tech ad featuring sleek smartwatch...",
  "colors": ["#1E3A8A", "#3B82F6", "#F3F4F6", "#FFFFFF"],
  "text_elements": ["FitPulse Pro", "Track Your Health", "Buy Now"],
  "detected_objects": ["smartwatch", "wrist", "UI display", "heart rate icon"],
  "mood": "modern, tech-focused, aspirational",
  "composition_score": 0.82
}
```

---

### Critique Agent  
**File:** `backend/app/core/critique_engine.py`

**Evaluation Dimensions:**

#### 1. Brand Alignment (BrandFit) - 0-1 Scale
**Checks:**
- ✅ Color palette match (HEX color distance)
- ✅ Logo usage (AI vision detection)
- ✅ Tone of voice alignment (keyword matching)
- ✅ Brand values consistency

**Tools:**
- OpenCV for color extraction
- Delta-E color distance algorithm
- Gemini Vision for semantic analysis

**Example:**
```python
brand_alignment = {
  "score": 0.87,  # 87%
  "feedback": "Colors match brand palette perfectly. Tone aligns with brand values.",
  "issues": ["Logo placement could be improved"],
  "suggestions": ["Move logo to top-right corner"]
}
```

#### 2. Visual Quality (VisualQuality) - 0-1 Scale
**Checks:**
- ✅ Sharpness (Laplacian variance)
- ✅ Composition (Rule of thirds)
- ✅ Contrast (Histogram analysis)
- ✅ Artifacts detection (AI vision)

**Tools:**
- OpenCV cv2.Laplacian for sharpness
- Histogram equalization for contrast
- Gemini Vision for blur/watermark detection

**Example:**
```python
visual_quality = {
  "score": 0.72,  # 72%
  "feedback": "Good sharpness and composition",
  "issues": ["Contrast could be higher", "Slight edge blur"],
  "suggestions": ["Increase contrast by 15%", "Apply sharpening filter"]
}
```

#### 3. Message Clarity (Clarity) - 0-1 Scale
**Checks:**
- ✅ Product visibility (object detection)
- ✅ Tagline readability (OCR + font size analysis)
- ✅ Call-to-action clarity
- ✅ Visual hierarchy

**Tools:**
- Gemini Vision OCR
- AI semantic analysis
- Text size detection

**Example:**
```python
message_clarity = {
  "score": 0.90,  # 90%
  "feedback": "Product clearly visible, tagline is readable and impactful",
  "issues": [],
  "suggestions": ["Consider adding urgency indicator ('Limited Time')"]
}
```

#### 4. Safety & Ethics (Safety) - 0-1 Scale
**Checks:**
- ✅ No harmful content
- ✅ No stereotypes
- ✅ No misleading claims
- ✅ Appropriate imagery

**Tools:**
- Gemini Vision safety filters
- Custom ethical guidelines
- Category-specific rules (food, health, etc.)

**Example:**
```python
safety_ethics = {
  "score": 0.95,  # 95%
  "feedback": "No safety or ethical concerns detected",
  "issues": [],
  "suggestions": []
}
```

---

## 🎯 Scoring System

### Overall Score Calculation
```python
overall_score = (
    brand_alignment * 0.30 +  # 30% weight
    visual_quality * 0.25 +   # 25% weight
    message_clarity * 0.25 +  # 25% weight
    safety_ethics * 0.20      # 20% weight
)
```

### Confidence Scoring
```python
# Each metric includes confidence (0-1)
brand_confidence = 0.91
quality_confidence = 0.85
clarity_confidence = 0.88
safety_confidence = 0.95

overall_confidence = average([brand, quality, clarity, safety])

# Flag for manual review if confidence < 0.65
needs_manual_review = overall_confidence < 0.65
```

### Score Levels
```python
if score >= 0.85:  level = "excellent"  # 🟢
elif score >= 0.70:  level = "good"     # 🔵
elif score >= 0.50:  level = "fair"     # 🟡
else:  level = "poor"                   # 🔴
```

---

## 🚀 API Endpoints Summary

| Endpoint | Method | Purpose | Workflow |
|----------|--------|---------|----------|
| `/api/multi-agent/generate-and-refine` | POST | Generate ad from prompt + auto-refine | Workflow 1 (4 agents) |
| `/api/multi-agent/critique-uploaded-ad` | POST | Critique user-uploaded ad | Workflow 2 (2 agents) |
| `/api/critique-ad` | POST | Simple critique (no descriptor) | Legacy |
| `/api/brand-kits` | GET | List all brand kits | Support |
| `/api/brand-kits` | POST | Create new brand kit | Support |

---

## 📝 Usage Examples

### Example 1: Generate & Auto-Refine (Python)
```python
import requests

url = "http://127.0.0.1:8000/api/multi-agent/generate-and-refine"
data = {
    "prompt": "Create an ad for eco-friendly water bottles",
    "brand_kit_id": "7de3d58f-e632-47c1-a77e-5127b04f9d45",
    "max_iterations": 3,
    "score_threshold": 0.75
}

response = requests.post(url, json=data)
result = response.json()

print(f"Final Score: {result['final_score']}")
print(f"Iterations: {result['iterations_count']}")
print(f"Best Ad: {result['best_ad']['image_path']}")
```

### Example 2: Upload & Critique (Python)
```python
import requests

url = "http://127.0.0.1:8000/api/multi-agent/critique-uploaded-ad"
files = {"file": open("my_ad.jpg", "rb")}
data = {"brand_kit_id": "7de3d58f-e632-47c1-a77e-5127b04f9d45"}

response = requests.post(url, files=files, data=data)
result = response.json()

print(f"Overall Score: {result['critique']['overall_score']}")
print(f"Brand Alignment: {result['critique']['brand_alignment_score']}")
print(f"Description: {result['description']['summary']}")
```

### Example 3: cURL Commands
```bash
# Generate & Refine
curl -X POST http://127.0.0.1:8000/api/multi-agent/generate-and-refine \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Tech ad for smartwatch",
    "brand_kit_id": "7de3d58f-e632-47c1-a77e-5127b04f9d45",
    "max_iterations": 3,
    "score_threshold": 0.75
  }'

# Upload & Critique
curl -X POST http://127.0.0.1:8000/api/multi-agent/critique-uploaded-ad \
  -F "file=@my_ad.jpg" \
  -F "brand_kit_id=7de3d58f-e632-47c1-a77e-5127b04f9d45"
```

---

## 🎓 Agent Details

### Generator Agent
- **Model:** Imagen 3 (imagegeneration@006) with PIL fallback
- **Input:** Prompt + brand kit
- **Output:** Generated ad image (1024x1024)
- **Brand Integration:** Uses brand colors in generation

### Descriptor Agent  
- **Model:** Gemini 2.0 Flash Vision
- **Input:** Image path
- **Output:** Component analysis (colors, text, objects, mood)
- **Fallback:** ColorThief + OpenCV if Gemini unavailable

### Critique Agent
- **Model:** Gemini 2.0 Flash Vision + OpenCV
- **Input:** Image + brand kit + description
- **Output:** 4 scores (0-1 scale) + detailed feedback
- **Features:** Category-specific evaluation, confidence scoring

### Refinement Agent
- **Model:** Gemini 2.0 Flash
- **Input:** Original prompt + critique feedback
- **Output:** Improved prompt for next iteration
- **Strategy:** Addresses weak areas, adds constraints

---

## ✅ System Status

**Server:** ✅ Running on http://127.0.0.1:8000  
**Auto-reload:** ✅ Enabled  
**API Key:** ✅ Configured (Gemini 2.0 Flash)  
**Vertex AI:** ✅ Project lucid-vector-477619-a6  
**Brand Kits:** ✅ 4 kits available  

**Test It Now:**
```
Workflow 1: Open http://127.0.0.1:8000 → Multi-Agent tab → Generate
Workflow 2: Open http://127.0.0.1:8000 → Critique tab → Upload
```

---

*Last Updated: November 8, 2025*  
*TriHuskAI - Complete Workflow Guide*
