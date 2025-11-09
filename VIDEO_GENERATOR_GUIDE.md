# 🎬 AI Video Ad Generator - Quick Start Guide

## What's New?

✅ **Upload Brand Logo & Product Images**  
✅ **Display Generated Videos/Images to User**  
✅ **Video Generation with Visual Assets**  
✅ **Beautiful Interactive UI**

---

## 🚀 How to Use

### Step 1: Start the Server

```powershell
# Server should already be running on http://127.0.0.1:8000
```

### Step 2: Open the Video Generator

Open in your browser:
```
http://127.0.0.1:8000/video_generator.html
```

Or directly navigate to:
```
frontend/video_generator.html
```

### Step 3: Create Your Video Ad

1. **Select a Brand Kit**
   - Choose from existing brand kits (PureVita, EcoFlow, FitPulse, etc.)
   - Or leave empty for generic generation

2. **Write Your Ad Prompt**
   ```
   Example: "Create a dynamic video ad showing fresh organic juice 
   being poured into a glass with vibrant fruits in the background"
   ```

3. **Upload Visual Assets (Optional)**
   - **Brand Logo**: Upload your brand's logo (PNG, JPG, WEBP)
   - **Product Image**: Upload product photo to include in video

4. **Configure Settings**
   - Duration: 5-15 seconds
   - Aspect Ratio: 16:9 (Landscape), 1:1 (Square), 9:16 (Vertical)
   - Max Iterations: 1-5 (more iterations = better quality)

5. **Click "Generate AI Video Ad"**

---

## 📊 What Happens Behind the Scenes?

```
1. Uploads → Server receives logo & product images
           ↓
2. Generator → Creates video using Google Veo with your assets
           ↓
3. Descriptor → Analyzes video content and elements
           ↓
4. Critique → Scores video on 4 dimensions (0-100%)
           ↓
5. Refinement → If score < 75%, improves and regenerates
           ↓
6. Display → Shows final video with scores & download option
```

---

## 🎯 Key Features

### 1. **File Uploads**
- API Endpoints:
  - `POST /api/upload/brand-logo` - Upload brand logo
  - `POST /api/upload/product-image` - Upload product image
- Supported formats: JPG, PNG, WEBP, GIF
- Files stored in: `backend/uploads/`

### 2. **Media Display**
- Generated videos/images displayed in browser
- Auto-play video with controls
- Download button for final asset
- Path: `http://localhost:8000/generated_ads/[filename]`

### 3. **Quality Scores**
- **Brand Alignment** (0-100%): Color match, tone, values
- **Visual Quality** (0-100%): Sharpness, composition
- **Message Clarity** (0-100%): Product visibility, CTA
- **Safety** (0-100%): No harmful/inappropriate content

### 4. **Iteration History**
- See all refinement attempts
- Compare before vs after
- Track score improvements

---

## 📁 API Endpoints

### Upload Files
```bash
# Upload brand logo
curl -X POST http://localhost:8000/api/upload/brand-logo \
  -F "file=@logo.png"

# Upload product image
curl -X POST http://localhost:8000/api/upload/product-image \
  -F "file=@product.jpg"
```

### Generate Video Ad
```bash
curl -X POST http://localhost:8000/api/multi-agent/generate-and-refine \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Fresh juice ad with vibrant colors",
    "brand_kit_id": "purevita_food",
    "media_type": "video",
    "duration": 10,
    "aspect_ratio": "16:9",
    "max_iterations": 3,
    "brand_logo_path": "backend/uploads/brand_logos/abc123.png",
    "product_image_path": "backend/uploads/product_images/xyz789.jpg"
  }'
```

### Access Generated Media
```
http://localhost:8000/generated_ads/video-uuid.mp4
http://localhost:8000/uploads/brand_logos/logo-uuid.png
http://localhost:8000/uploads/product_images/product-uuid.jpg
```

---

## 🎨 Sample Prompts

### PureVita (Organic Juice)
```
"Create a vibrant 10-second video ad showing cold-pressed organic juice 
being poured into a glass. Include fresh oranges, strawberries, and 
green leafy vegetables. Natural lighting with warm, appetizing tones. 
Brand colors: orange, gold, green."
```

### EcoFlow (Sustainable Products)
```
"Generate a video ad featuring a sustainable water bottle in a beautiful 
forest setting. Show morning sunlight through trees, clear mountain stream 
in background. Eco-friendly, natural aesthetic with green tones."
```

### FitPulse (Tech Wearables)
```
"Dynamic video showing a smartwatch on athlete's wrist during intense 
workout. Display heart rate data on screen. Modern, high-tech feel with 
blue and cyan accents. Fast-paced, energetic camera movements."
```

---

## 📂 File Structure

```
backend/
├── uploads/
│   ├── brand_logos/          # Uploaded brand logos
│   │   └── uuid.png
│   └── product_images/       # Uploaded product images
│       └── uuid.jpg
├── generated_ads/            # Generated videos/images
│   ├── uuid.mp4              # Video ads
│   └── uuid.png              # Image ads
└── brand_kits/               # Brand guidelines
    └── purevita_food.json

frontend/
├── index.html                # Original multi-agent UI
└── video_generator.html      # NEW: Video generator UI
```

---

## 🔧 Troubleshooting

### Video Not Displaying?
- Check browser console for errors
- Verify path: `http://localhost:8000/generated_ads/[filename]`
- Try refreshing the page

### Upload Failing?
- Check file size (< 10MB recommended)
- Verify file format (JPG, PNG, WEBP, GIF)
- Ensure server is running

### Low Quality Scores?
- Increase max iterations (3-5)
- Improve prompt specificity
- Add brand logo for better brand alignment
- Include product image for better clarity

---

## 🎯 Next Steps

1. **Test the UI**: Open `video_generator.html` in browser
2. **Upload Assets**: Add your brand logo and product image
3. **Generate Video**: Create your first AI video ad
4. **Review Scores**: Check the 4-dimension critique
5. **Download**: Save the final video for deployment

---

## 🌟 Pro Tips

✨ **Use Specific Prompts**: Include details like camera angles, lighting, mood  
✨ **Upload High-Quality Images**: Better inputs = better outputs  
✨ **Iterate**: Don't settle for first result, let refinement improve it  
✨ **Match Brand Colors**: Upload logo with brand colors for consistency  
✨ **Test Aspect Ratios**: 16:9 for YouTube, 1:1 for Instagram, 9:16 for TikTok

---

*Last Updated: November 8, 2025*  
*TriHuskAI - AI Video Ad Generation System*
