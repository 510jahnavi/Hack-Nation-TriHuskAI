# BrandAI - Technical Documentation

## Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (HTML/JS)                       │
│  - Upload Interface  - Brand Kit Manager  - Results Display │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/REST API
┌────────────────────▼────────────────────────────────────────┐
│                   FastAPI Backend                            │
│  ┌──────────────┬─────────────────┬──────────────────────┐ │
│  │ API Routes   │ Business Logic   │ Data Models          │ │
│  │ - critique.py│ - Services       │ - schemas.py         │ │
│  │ - brand_kit  │ - BrandService   │ - BrandKit          │ │
│  │ - generate   │ - GenService     │ - AdCritique        │ │
│  └──────────────┴─────────────────┴──────────────────────┘ │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│              AI Critique Engine (Hero Feature)               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Gemini Vision API - Brand Alignment & Safety Check  │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  OpenCV Analysis - Visual Quality & Composition      │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Color Matcher - Brand Color Alignment Detection     │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Core Features Implementation

### 1. AI Critique Engine (Hero Feature)

**File**: `backend/app/core/critique_engine.py`

The critique engine evaluates ads across 4 dimensions:

#### Brand Alignment (30% weight)
- **AI Analysis**: Gemini Vision evaluates brand consistency
- **Color Matching**: Compares dominant colors to brand palette
- **Tone Analysis**: Checks if visual tone matches brand voice
- **Logo Detection**: Verifies proper logo usage

**Key Metrics**:
```python
brand_score = (ai_brand_score + color_match_score) / 2
```

#### Visual Quality (25% weight)
- **Sharpness**: Laplacian variance analysis
- **Composition**: Rule of thirds evaluation
- **Artifacts**: Compression artifact detection
- **Watermarks**: Corner region analysis

**Implementation**:
```python
sharpness = laplacian_variance / 500.0  # Normalized
composition = section_std_dev / 50.0    # Rule of thirds
```

#### Message Clarity (25% weight)
- **Text Visibility**: Gemini evaluates readability
- **Product Visibility**: AI checks product prominence
- **CTA Detection**: Verifies call-to-action presence
- **Tagline Analysis**: Checks tagline clarity

#### Safety & Ethics (20% weight)
- **Content Safety**: Gemini flags harmful content
- **Bias Detection**: Checks for stereotypes
- **Truthfulness**: Validates claims aren't misleading
- **Compliance**: Ensures regulatory compliance

### 2. Scoring System

Each dimension receives:
- **Score**: 0.0 to 1.0 (float)
- **Level**: EXCELLENT (≥0.85), GOOD (≥0.70), FAIR (≥0.50), POOR (<0.50)
- **Feedback**: AI-generated text explanation
- **Issues**: List of specific problems
- **Suggestions**: Actionable improvements

**Overall Score Calculation**:
```python
overall_score = (
    brand_alignment * 0.30 +
    visual_quality * 0.25 +
    message_clarity * 0.25 +
    safety_ethics * 0.20
)
```

**Deployment Readiness**:
```python
ready_to_deploy = (
    brand_score >= 0.7 and
    quality_score >= 0.6 and
    safety_score >= 0.9 and  # High threshold for safety!
    clarity_score >= 0.7
)
```

### 3. Computer Vision Analysis

**File**: `backend/app/utils/image_analysis.py`

#### Sharpness Detection
Uses Laplacian operator to detect edges and calculate variance:
```python
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
sharpness = min(laplacian_var / 500.0, 1.0)
```

#### Composition Analysis
Divides image into 9 sections (rule of thirds):
```python
sections = [img[i*h/3:(i+1)*h/3, j*w/3:(j+1)*w/3] for i,j in grid]
std_dev = np.std([section.mean() for section in sections])
composition_score = min(std_dev / 50.0, 1.0)
```

#### Watermark Detection
Checks corners for semi-transparent overlays:
```python
for corner in [top_left, top_right, bottom_left, bottom_right]:
    if corner_std < center_std * 0.5:
        return True  # Watermark detected
```

### 4. Color Analysis

**File**: `backend/app/utils/color_analysis.py`

#### Dominant Color Extraction
K-means clustering to find main colors:
```python
pixels = img.reshape(-1, 3)
_, labels, centers = cv2.kmeans(pixels, k=5, ...)
dominant_colors = centers[sorted_by_frequency]
```

#### Brand Color Matching
Calculates similarity between image and brand colors:
```python
for brand_color in brand_palette:
    closest_distance = min(
        euclidean_distance(brand_color, img_color)
        for img_color in dominant_colors
    )
    similarity = 1 - (closest_distance / 441.0)
brand_match = average(similarities)
```

#### Color Harmony
Checks for color theory principles:
```python
# Convert to HSV
hsv_colors = [rgb_to_hsv(c) for c in colors]

# Check relationships
if 160 <= hue_diff <= 200:  # Complementary
    harmony_score += 0.3
elif hue_diff <= 30:  # Analogous
    harmony_score += 0.2
```

### 5. Gemini Integration

**Prompt Engineering**:
The critique prompt is carefully structured:

```python
prompt = f"""You are an expert Creative Director and Brand Compliance Officer.

Brand: {brand_name}
Colors: {primary_colors}
Tone: {tone_of_voice}

Analyze this ad and score (0-1):
1. Brand Alignment
2. Visual Quality
3. Message Clarity
4. Safety & Ethics

Return JSON only with scores, feedback, issues, and suggestions.
"""
```

**Response Parsing**:
- Removes markdown code blocks
- Validates JSON structure
- Falls back to baseline scores on error

### 6. Brand Kit Management

**File**: `backend/app/services/brand_service.py`

Brand kits stored as JSON files:
```json
{
  "brand_id": "nike-demo",
  "brand_name": "Nike",
  "primary_colors": ["#FF0000", "#000000"],
  "tone_of_voice": ["energetic", "bold"],
  "brand_values": ["innovation", "performance"],
  "guidelines": "Always show movement..."
}
```

## API Endpoints

### POST /api/critique-ad
**Purpose**: Main critique endpoint (Hero Feature)

**Request**:
- `file`: Image file (multipart/form-data)
- `brand_id`: Optional brand kit reference
- `ad_description`: Optional text description

**Response**:
```json
{
  "critique_id": "uuid",
  "overall_score": 0.85,
  "overall_level": "excellent",
  "ready_to_deploy": true,
  "brand_alignment": {
    "score": 0.88,
    "level": "excellent",
    "feedback": "Colors match brand perfectly",
    "issues": [],
    "suggestions": ["Consider larger logo"]
  },
  "visual_quality": {...},
  "message_clarity": {...},
  "safety_ethics": {...},
  "improvements_needed": [...]
}
```

### POST /api/brand-kit
**Purpose**: Create brand guidelines

**Request** (form-data):
- `brand_name`: Brand name
- `primary_colors`: Comma-separated hex codes
- `tone_of_voice`: Comma-separated adjectives
- `brand_values`: Optional values
- `logo`: Optional logo file

### POST /api/generate-ad
**Purpose**: Generate basic ad (secondary feature)

**Request**:
- `brand_id`: Brand kit to use
- `product_name`: Product name
- `product_description`: Description
- `tagline`: Optional tagline
- `style`: modern/minimal/bold/elegant
- `media_type`: image/video

## Data Flow

### Critique Flow
```
1. User uploads ad image
   ↓
2. Image saved to uploads/
   ↓
3. Load brand kit (if specified)
   ↓
4. Parallel analysis:
   - OpenCV: visual quality, sharpness, composition
   - ColorMatcher: color extraction, brand matching
   - Gemini Vision: AI critique across all dimensions
   ↓
5. Combine analyses:
   - Weight scores
   - Merge feedback
   - Generate suggestions
   ↓
6. Calculate deployment readiness
   ↓
7. Return JSON critique
   ↓
8. Frontend displays scorecard
```

### Generation Flow
```
1. User specifies product + brand
   ↓
2. Load brand kit
   ↓
3. Build generation prompt with brand context
   ↓
4. Call Imagen 2 API (or Veo for video)
   ↓
5. Save generated ad
   ↓
6. Optionally auto-critique
   ↓
7. Return ad URL + critique
```

## Configuration

### Environment Variables (.env)
```bash
# Google Cloud
GOOGLE_CLOUD_PROJECT=your-project
GEMINI_API_KEY=your-key
VERTEX_AI_LOCATION=us-central1

# Thresholds
MIN_BRAND_SCORE=0.7
MIN_QUALITY_SCORE=0.6
MIN_SAFETY_SCORE=0.9  # Highest threshold!
MIN_CLARITY_SCORE=0.7

# Models
GEMINI_MODEL=gemini-1.5-pro-latest
IMAGEN_MODEL=imagegeneration@006
```

### Threshold Tuning

Adjust thresholds based on brand tolerance:

**Strict Brand** (luxury, regulated):
```python
MIN_BRAND_SCORE = 0.85
MIN_SAFETY_SCORE = 0.95
```

**Casual Brand** (startup, experimental):
```python
MIN_BRAND_SCORE = 0.60
MIN_SAFETY_SCORE = 0.85
```

## Performance Optimization

### Critique Speed
- **Target**: < 5 seconds per image
- **Bottleneck**: Gemini API call (~2-3s)
- **Optimization**: Parallel CV analysis while waiting for AI

### Batch Processing
Use `/api/batch-critique` for multiple ads:
```python
results = await asyncio.gather(*[
    critique_engine.critique_ad(img) for img in images
])
```

## Error Handling

### Gemini API Failures
- Fallback to baseline scores
- Flag for manual review
- Log error details

### Invalid Images
- Check file type before processing
- Validate image can be loaded
- Return 400 with clear message

### Missing Brand Kit
- Allow critique without brand (generic mode)
- Skip brand-specific checks
- Note in feedback

## Testing

### Manual Testing
```bash
python test_critique.py
```

### API Testing
```bash
# Start server
python backend/main.py

# Test endpoint
curl -X POST "http://localhost:8000/api/critique-ad" \
  -F "file=@test_ad.jpg" \
  -F "brand_id=nike-demo"
```

### Unit Tests
```bash
pytest backend/tests/
```

## Deployment

### Local Development
```bash
python backend/main.py
```

### Production (Google Cloud Run)
```bash
gcloud run deploy brandai \
  --source . \
  --region us-central1 \
  --allow-unauthenticated
```

### Docker
```dockerfile
FROM python:3.11
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY backend/ /app/backend/
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0"]
```

## Future Enhancements

### Multi-Agent Workflow
```
Generator Agent → Critic Agent → Refiner Agent → Final Output
```

### Fine-Tuned Model
Train custom model on brand-specific data:
```python
# Collect training data
examples = [(ad_image, expert_critique), ...]

# Fine-tune Gemini or Llama-Vision
model.fine_tune(examples)
```

### Real-Time Video Critique
- Frame-by-frame analysis
- Motion tracking
- Audio analysis (for voiceover ads)

### A/B Testing Integration
- Compare multiple ad variations
- Rank by predicted performance
- Suggest optimal combination

## Conclusion

BrandAI's core innovation is the **critique engine** that combines:
1. **AI Vision** (Gemini) for semantic understanding
2. **Computer Vision** (OpenCV) for technical quality
3. **Color Science** for brand alignment
4. **Structured Scoring** for actionable feedback

This creates a **trust layer** that enables autonomous ad deployment at scale.
