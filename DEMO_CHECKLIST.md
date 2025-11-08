# BrandAI - Demo Checklist for Hackathon

## Pre-Demo Setup ✅

### 1. Environment Setup
- [ ] Python 3.9+ installed
- [ ] Virtual environment created (`python -m venv venv`)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file configured with `GEMINI_API_KEY`
- [ ] Google Cloud credentials set up (if using Vertex AI)

### 2. Test the System
- [ ] Run `python test_critique.py` to verify setup
- [ ] Start server: `python backend/main.py`
- [ ] Server accessible at `http://localhost:8000`
- [ ] API docs visible at `http://localhost:8000/docs`
- [ ] Frontend opens correctly (`frontend/index.html`)

### 3. Prepare Demo Assets
- [ ] 3-5 sample ad images ready (good and bad quality)
- [ ] 2-3 brand kits pre-created (Nike, Coca-Cola, etc.)
- [ ] Screenshots of critique results prepared
- [ ] Demo script rehearsed

---

## Demo Flow (7 Minutes) 🎯

### Minute 1: Problem Statement
**Show:**
- "Millions of AI ads generated daily"
- "But brands can't deploy them - no trust"
- "Human review is the bottleneck"

**Say:**
> "AI can generate beautiful ads in seconds, but brands still need humans to review every single one. Why? Because there's no trust layer. That's what we built."

---

### Minute 2: Solution Overview
**Show:** Architecture diagram (from TECHNICAL_DOCS.md)

**Say:**
> "BrandAI is the AI that critiques other AI. It's like a Creative Director + Compliance Officer rolled into one automated system."

**Highlight:**
- 4 evaluation dimensions
- Hybrid AI + Computer Vision
- Structured feedback, not just scores

---

### Minute 3-4: Live Demo - Critique Engine (Hero Feature)
**Steps:**
1. Open frontend (`frontend/index.html`)
2. Upload a "good" ad image
3. Select brand kit (pre-created)
4. Click "Critique Ad"
5. Show results appearing in real-time

**Point Out:**
- Overall score: 85% (Good)
- Individual dimension scores
- Specific issues identified
- Actionable suggestions
- "Ready to Deploy" decision

**Say:**
> "In under 5 seconds, we get a comprehensive critique across brand alignment, visual quality, message clarity, and safety. Notice it doesn't just give scores - it tells you exactly what to fix."

---

### Minute 5: Show a "Bad" Ad
**Steps:**
1. Upload a "bad" ad (blurry, wrong colors, etc.)
2. Show lower scores
3. Highlight issues detected
4. Point out "Not Ready to Deploy"

**Say:**
> "Here's an ad that would've been a PR disaster. Our system catches it automatically - wrong brand colors, poor quality, unclear message. No human review needed."

---

### Minute 6: Brand Kit Management
**Steps:**
1. Go to "Brand Kits" tab
2. Show pre-created brand kits
3. Quickly create a new one:
   - Brand: "TechCorp"
   - Colors: #0066CC, #FFFFFF
   - Tone: innovative, professional

**Say:**
> "Brands define their guidelines once - colors, tone, values. Then every ad is evaluated against these rules. It's like teaching the AI your brand identity."

---

### Minute 7: Technical Highlights & Close
**Show:** Quick code walkthrough (optional)
- Open `critique_engine.py`
- Show Gemini prompt
- Show scoring calculation

**Say:**
> "Under the hood, we combine Gemini Vision for semantic understanding with OpenCV for technical quality. The result? An AI that can truly judge if another AI did a good job."

**Close:**
> "This solves the last blocker for autonomous AI advertising. With BrandAI, brands can finally trust AI to create AND approve content at scale."

---

## Demo Success Metrics 📊

### Must Show:
- ✅ Critique completes in < 5 seconds
- ✅ All 4 dimensions display scores
- ✅ Specific issues and suggestions shown
- ✅ Deploy/reject decision is clear
- ✅ Works with different brands

### Bonus Points:
- ✅ Show batch critique (multiple ads)
- ✅ Demonstrate API endpoint (Postman/curl)
- ✅ Show color analysis visualization
- ✅ Discuss stretch goals (multi-agent, fine-tuning)

---

## Q&A Preparation 💬

### Expected Questions & Answers

**Q: How accurate is it compared to human reviewers?**
A: "We're targeting 85%+ agreement with expert reviewers. Currently testing with beta users to measure this. The key is it's consistent - humans vary, our system doesn't."

**Q: What if it makes a mistake?**
A: "Two safeguards: 1) We set high thresholds for safety (90%), and 2) There's an optional human approval step before final deploy. As the system learns, we can increase automation."

**Q: Can it handle video ads?**
A: "Framework is in place. We can process video frame-by-frame and analyze motion/audio. Full support is on our Month 2 roadmap."

**Q: How do you prevent bias in the critique?**
A: "Our safety module explicitly checks for stereotypes and bias. Plus, we can fine-tune on diverse training data to improve detection."

**Q: What's the business model?**
A: "SaaS pricing: $99-499/mo for small brands, enterprise custom pricing for agencies. Also exploring API partnerships with ad platforms."

**Q: How is this different from content moderation APIs?**
A: "Content moderation just checks safety. We do full quality control - brand alignment, visual quality, message clarity, AND safety. Plus, we give actionable improvement suggestions."

**Q: What happens if Google increases API pricing?**
A: "We're model-agnostic. Can switch to OpenAI Vision, Anthropic Claude, or fine-tune our own model. Google gives us the best value today."

**Q: How long did this take to build?**
A: "Core critique engine in 48 hours for the hackathon. Production-ready version with fine-tuning would be 3 months."

---

## Backup Plans 🔧

### If Internet Fails:
- [ ] Have offline demo video ready
- [ ] Show screenshots of results
- [ ] Walk through code locally

### If API Quota Exceeded:
- [ ] Have pre-generated critique results saved as JSON
- [ ] Load and display mock data
- [ ] Explain it would work with proper quota

### If Live Demo Glitches:
- [ ] Have backup sample results ready
- [ ] Focus on architecture explanation
- [ ] Show code quality and documentation

---

## Post-Demo Actions ✨

### Immediately After:
- [ ] Share GitHub repo link
- [ ] Provide demo URL (if deployed)
- [ ] Collect judge feedback
- [ ] Note questions for later improvement

### Follow-Up:
- [ ] Send thank you email with materials
- [ ] Share detailed documentation
- [ ] Offer to answer additional questions
- [ ] Connect on LinkedIn

---

## Judge Evaluation Criteria 🏆

### Technical Excellence (35%)
**Highlight:**
- Hybrid AI + CV approach
- Production-ready code
- Proper error handling
- Well-documented

### Innovation (30%)
**Highlight:**
- Novel "AI critiquing AI" approach
- Solves real pain point
- Clear competitive advantage

### Business Potential (20%)
**Highlight:**
- Large market ($650B advertising)
- Clear monetization path
- Scalable SaaS model

### Presentation (15%)
**Highlight:**
- Clear problem statement
- Live demo works flawlessly
- Confident Q&A responses

---

## Resources to Have Open 📂

### On Laptop:
1. Frontend (`frontend/index.html`)
2. Backend running (`python backend/main.py`)
3. API docs (`localhost:8000/docs`)
4. This checklist
5. PITCH_DECK.md (for reference)
6. Sample ad images folder

### On Phone/Backup:
1. Demo video
2. Screenshots of results
3. GitHub repo link
4. Contact information

---

## Time Allocation ⏱️

- **Setup/Introduction**: 1 min
- **Problem Statement**: 1 min
- **Solution Overview**: 1 min
- **Live Demo (Critique)**: 3 min
- **Technical Highlights**: 1 min
- **Q&A**: Remaining time

**Total**: 7 min presentation + 3-5 min Q&A

---

## Confidence Boosters 💪

**Remember:**
- ✅ You built a working AI system in 48 hours
- ✅ The critique engine actually works
- ✅ This solves a real $650B market problem
- ✅ The code is clean and documented
- ✅ You have multiple successful demo paths

**You got this!** 🚀

---

## Final Checklist Before Stage ✅

5 Minutes Before:
- [ ] Server running and responding
- [ ] Frontend tested and working
- [ ] Sample ads ready to upload
- [ ] Brand kits pre-created
- [ ] Internet connection stable
- [ ] Laptop charged / plugged in
- [ ] Water nearby
- [ ] Deep breath taken 😊

**Good luck! Go show them what BrandAI can do!** 🎯
