# Test Prompts & Brand Kits for BrandAI Demo

## 🎯 Quick Test Scenarios

### 1. **Tech Product - Smart Fitness Watch**

**Brand Kit:**
```json
{
  "brand_name": "FitPulse",
  "primary_colors": ["#0066FF", "#00D4FF", "#1A1A1A"],
  "tone_of_voice": ["innovative", "energetic", "motivational"],
  "brand_values": ["health", "technology", "performance"],
  "logo_url": ""
}
```

**Test Prompts:**
- "Create a sleek ad for a smart fitness watch that tracks heart rate and sleep"
- "Design a modern advertisement for a waterproof fitness tracker for athletes"
- "Generate an energetic ad showing a smartwatch for marathon runners"

**Expected:** Blue/cyan colors, modern tech aesthetic, clear product visibility

---

### 2. **Eco-Friendly - Sustainable Water Bottles**

**Brand Kit:**
```json
{
  "brand_name": "EcoFlow",
  "primary_colors": ["#2E7D32", "#66BB6A", "#F5F5DC"],
  "tone_of_voice": ["authentic", "caring", "natural"],
  "brand_values": ["sustainability", "environment", "organic", "eco-friendly"],
  "logo_url": ""
}
```

**Test Prompts:**
- "Create an ad for eco-friendly reusable water bottles made from recycled materials"
- "Design a natural-looking advertisement for sustainable bamboo water bottles"
- "Generate a green ad promoting plastic-free stainless steel bottles"

**Expected:** Green/earth tones, natural aesthetic, environmental messaging

---

### 3. **Luxury - Premium Watch Brand**

**Brand Kit:**
```json
{
  "brand_name": "Chronos Elite",
  "primary_colors": ["#1A1A1A", "#C9B037", "#FFFFFF"],
  "tone_of_voice": ["sophisticated", "elegant", "exclusive"],
  "brand_values": ["luxury", "craftsmanship", "heritage", "premium"],
  "logo_url": ""
}
```

**Test Prompts:**
- "Create an elegant ad for a luxury Swiss automatic watch"
- "Design a sophisticated advertisement for premium handcrafted timepieces"
- "Generate an exclusive ad showcasing high-end designer watches"

**Expected:** Black/gold colors, premium feel, sophisticated composition

---

### 4. **Food & Beverage - Organic Juice**

**Brand Kit:**
```json
{
  "brand_name": "PureVita",
  "primary_colors": ["#FF6B00", "#FFD700", "#228B22"],
  "tone_of_voice": ["fresh", "vibrant", "healthy"],
  "brand_values": ["organic", "natural", "health", "wellness"],
  "logo_url": ""
}
```

**Test Prompts:**
- "Create a vibrant ad for freshly squeezed organic orange juice"
- "Design a colorful advertisement for cold-pressed fruit smoothies"
- "Generate a fresh ad showing healthy green detox juice"

**Expected:** Bright orange/red/green colors, appetizing presentation, fresh look

---

### 5. **Fashion - Streetwear Clothing**

**Brand Kit:**
```json
{
  "brand_name": "UrbanThread",
  "primary_colors": ["#000000", "#FFFFFF", "#FF0000"],
  "tone_of_voice": ["bold", "trendy", "confident"],
  "brand_values": ["style", "individuality", "fashion", "urban culture"],
  "logo_url": ""
}
```

**Test Prompts:**
- "Create a bold ad for urban streetwear hoodies and sneakers"
- "Design a trendy advertisement for modern athletic street fashion"
- "Generate a stylish ad showcasing minimalist black and white clothing"

**Expected:** Bold colors, model/lifestyle imagery, fashion-forward

---

### 6. **Health & Wellness - Yoga Studio**

**Brand Kit:**
```json
{
  "brand_name": "ZenFlow Studio",
  "primary_colors": ["#8B7355", "#F5DEB3", "#E6E6FA"],
  "tone_of_voice": ["calm", "peaceful", "welcoming"],
  "brand_values": ["wellness", "mindfulness", "health", "balance"],
  "logo_url": ""
}
```

**Test Prompts:**
- "Create a calm ad for yoga classes and meditation sessions"
- "Design a peaceful advertisement for wellness and mindfulness studio"
- "Generate a serene ad promoting holistic health and yoga retreats"

**Expected:** Soft earth tones, peaceful aesthetic, trustworthy feel

---

## 🧪 **Testing Workflow**

### Step 1: Create Brand Kit
1. Go to **Brand Kits** tab
2. Paste one of the JSON examples above
3. Click "Create Brand Kit"
4. Copy the returned Brand ID

### Step 2: Run Multi-Agent Workflow
1. Go to **Multi-Agent Workflow** tab
2. Paste the Brand ID
3. Enter one of the test prompts
4. Set iterations to 2-3
5. Click "Generate & Critique"

### Step 3: Observe Results
- ✅ **Image Generation**: Should use Imagen 3 (or PIL fallback with dynamic colors)
- ✅ **Category Detection**: Check if it detected correct category (tech/eco/luxury/food/fashion/health)
- ✅ **Descriptor**: Should return detailed analysis + summary text
- ✅ **Critique**: Should show 4 scores with confidence levels
- ✅ **Confidence Indicators**: 🟢 (high) or 🟡 (medium) next to each score
- ✅ **Manual Review Flag**: Should appear if overall confidence <65%
- ✅ **Refinement**: Should suggest specific improvements based on category
- ✅ **Iterations**: Each iteration should improve scores

---

## 🎭 **Edge Case Testing**

### Test 1: Conflicting Brand Colors
```json
{
  "brand_name": "TestBrand",
  "primary_colors": ["#FF0000", "#00FF00"],
  "tone_of_voice": ["professional"],
  "brand_values": ["quality"]
}
```
**Prompt:** "Create a professional corporate ad"
**Expected:** Critique should flag color clash issues

### Test 2: Minimal Brand Info
```json
{
  "brand_name": "MinimalBrand",
  "primary_colors": ["#000000"],
  "tone_of_voice": ["modern"],
  "brand_values": []
}
```
**Prompt:** "Create any ad"
**Expected:** Should work with fallback to general category

### Test 3: Complex Multi-Category
**Prompt:** "Create an ad for luxury eco-friendly tech smartwatch"
**Expected:** Should detect multiple categories and apply combined criteria

---

## 📊 **Success Metrics**

| Metric | Target | Test |
|--------|--------|------|
| Image Generation | <10s | Imagen 3 or PIL fallback |
| Category Detection | 90%+ accuracy | Check detected_elements.category_detected |
| Critique Scores | 0.5-1.0 range | All 4 metrics populated |
| Confidence Scores | Present | All 4 confidence values shown |
| Manual Review Flag | Triggers at <65% | Test with vague prompts |
| Iteration Improvement | +5-15% per iteration | Compare iteration 1 vs 3 |
| Download Function | Works | Click download button |

---

## 🚀 **Demo Script for Hackathon**

### **Opening (30 seconds)**
"BrandAI uses Google's Gemini 2.0 Flash and Imagen 3 to automatically critique ad creatives. Let me show you..."

### **Demo Flow (2-3 minutes)**

1. **Create Brand Kit** (20s)
   - Use EcoFlow (eco-friendly) example
   - Show simple JSON input → Brand ID output

2. **Generate Ad** (60s)
   - Enter prompt: "Create an ad for eco-friendly water bottles"
   - Show multi-agent workflow running
   - Point out: "Watch the 4 agents working - Generator, Descriptor, Critic, Refinement"

3. **Review Results** (60s)
   - **Iteration 1:** 
     - Show generated image
     - Point to category detection: "It auto-detected ECO category"
     - Show 4 scores with confidence: "Notice the confidence indicators"
     - Read issues/suggestions
   
   - **Iteration 2:**
     - Show improved image
     - Compare scores: "Brand alignment improved from 72% to 85%"
     - Show confidence increased

4. **Highlight Features** (30s)
   - **Category-Specific Evaluation:** "It judges eco ads differently than tech ads"
   - **Confidence Transparency:** "Shows when to trust AI vs manual review"
   - **Iterative Refinement:** "Automatically improves across iterations"
   - **Download Ready Ads:** Click download button

### **Closing**
"This saves creative teams hours of manual review while ensuring brand compliance!"

---

## 💡 **Pro Tips**

1. **For Best Results:**
   - Be specific in prompts ("vibrant", "minimalist", "bold")
   - Use brand values that match the product
   - Run 2-3 iterations for optimal refinement

2. **Impressive Demo Moments:**
   - Show low confidence warning triggering
   - Compare before/after scores in comparison view
   - Show category auto-detection working

3. **Backup Plan:**
   - If Imagen 3 quota exhausted → PIL fallback still works
   - If one agent fails → Show intelligent CV fallback scores
   - If network slow → Pre-generate 1-2 examples

---

## 📝 **Quick Copy-Paste Test Set**

**Rapid Fire Testing (5 prompts, 5 brand kits):**

1. FitPulse + "smart fitness watch" → Tech category, blue colors
2. EcoFlow + "sustainable bottles" → Eco category, green colors  
3. Chronos Elite + "luxury watch" → Luxury category, black/gold
4. PureVita + "organic juice" → Food category, orange/yellow
5. ZenFlow + "yoga classes" → Health category, earth tones

**Run all 5 in sequence to show versatility across industries!**
