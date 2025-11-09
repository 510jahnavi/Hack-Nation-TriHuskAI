"""
Core AI Critique Engine - Hero Feature

This module implements the main critique functionality using Gemini Vision API
to evaluate AI-generated ads across multiple dimensions.
"""

import google.generativeai as genai
from google.cloud import aiplatform
from PIL import Image
import json
import os
from typing import Dict, Tuple, Optional
import cv2
import numpy as np

from config import settings
from app.models.schemas import (
    AdCritique, CritiqueScore, ScoreLevel, BrandKit,
    ColorAnalysis, VisualAnalysis
)
from app.utils.image_analysis import ImageAnalyzer
from app.utils.color_analysis import ColorMatcher


class CritiqueEngine:
    """
    Main critique engine that evaluates ads using AI vision models
    and traditional computer vision techniques.
    """
    
    def __init__(self):
        """Initialize the critique engine with Gemini API"""
        if settings.gemini_api_key:
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
        else:
            # Use Vertex AI if no API key
            aiplatform.init(
                project=settings.google_cloud_project,
                location=settings.vertex_ai_location
            )
            self.model = None
        
        self.image_analyzer = ImageAnalyzer()
        self.color_matcher = ColorMatcher()
    
    async def critique_ad(
        self,
        image_path: str,
        brand_kit: Optional[BrandKit] = None,
        ad_description: Optional[str] = None
    ) -> AdCritique:
        """
        Main critique function that evaluates an ad comprehensively.
        
        Args:
            image_path: Path to the ad image
            brand_kit: Brand guidelines for comparison
            ad_description: Optional description of the ad content
            
        Returns:
            AdCritique: Comprehensive critique with scores and feedback
        """
        
        # Analyze image using computer vision
        visual_analysis = await self._analyze_visual_quality(image_path)
        color_analysis = await self._analyze_colors(image_path, brand_kit)
        
        # Get AI-powered critique using Gemini
        ai_critique = await self._get_gemini_critique(
            image_path, brand_kit, ad_description
        )
        
        # Combine analyses into final critique
        critique = await self._compile_critique(
            image_path,
            brand_kit,
            visual_analysis,
            color_analysis,
            ai_critique
        )
        
        return critique
    
    async def _analyze_visual_quality(self, image_path: str) -> VisualAnalysis:
        """Analyze visual quality using OpenCV"""
        return self.image_analyzer.analyze_quality(image_path)
    
    async def _analyze_colors(
        self,
        image_path: str,
        brand_kit: Optional[BrandKit]
    ) -> ColorAnalysis:
        """Analyze color palette and brand alignment"""
        return self.color_matcher.analyze_colors(image_path, brand_kit)
    
    async def _get_gemini_critique(
        self,
        image_path: str,
        brand_kit: Optional[BrandKit],
        ad_description: Optional[str]
    ) -> Dict:
        """
        Get AI-powered critique using Gemini Vision.
        This is the core AI evaluation component.
        """
        
        # Load image
        image = Image.open(image_path)
        
        # Build critique prompt
        prompt = self._build_critique_prompt(brand_kit, ad_description)
        
        try:
            # Generate critique using Gemini
            response = self.model.generate_content([prompt, image])
            
            # Parse JSON response
            critique_data = self._parse_gemini_response(response.text)
            
            return critique_data
            
        except Exception as e:
            print(f"Error getting Gemini critique: {e}")
            return self._get_fallback_critique(image_path)
    
    def _detect_ad_category(self, brand_kit: Optional[BrandKit], ad_description: Optional[str]) -> str:
        """
        Detect the category/industry of the ad to apply specialized evaluation criteria.
        Returns: 'fashion', 'tech', 'food', 'luxury', 'eco', 'health', or 'general'
        """
        
        category_keywords = {
            'fashion': ['clothing', 'apparel', 'wear', 'fashion', 'style', 'outfit', 'dress', 'shoes'],
            'tech': ['technology', 'software', 'app', 'device', 'gadget', 'digital', 'tech', 'ai', 'smart'],
            'food': ['food', 'restaurant', 'cuisine', 'meal', 'drink', 'beverage', 'snack', 'cafe'],
            'luxury': ['luxury', 'premium', 'exclusive', 'elegant', 'sophisticated', 'high-end'],
            'eco': ['eco', 'sustainable', 'green', 'environment', 'organic', 'natural', 'earth'],
            'health': ['health', 'wellness', 'fitness', 'medical', 'care', 'therapy', 'clinic']
        }
        
        # Check description and brand values
        text_to_check = (ad_description or "").lower()
        if brand_kit:
            text_to_check += " " + " ".join(brand_kit.brand_values or []).lower()
            text_to_check += " " + brand_kit.brand_name.lower()
        
        # Count keyword matches
        category_scores = {}
        for category, keywords in category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_to_check)
            if score > 0:
                category_scores[category] = score
        
        # Return category with highest score, or 'general'
        if category_scores:
            return max(category_scores.items(), key=lambda x: x[1])[0]
        return 'general'
    
    def _build_critique_prompt(
        self,
        brand_kit: Optional[BrandKit],
        ad_description: Optional[str]
    ) -> str:
        """Build a detailed prompt for Gemini to critique the ad with category-specific criteria"""
        
        # Detect ad category
        category = self._detect_ad_category(brand_kit, ad_description)
        
        brand_context = ""
        if brand_kit:
            brand_context = f"""
Brand: {brand_kit.brand_name}
Primary Colors: {', '.join(brand_kit.primary_colors)}
Tone of Voice: {', '.join(brand_kit.tone_of_voice)}
Brand Values: {', '.join(brand_kit.brand_values) if brand_kit.brand_values else 'Not specified'}
"""
        
        # Category-specific evaluation criteria
        category_guidelines = {
            'fashion': """
**Fashion-Specific Criteria:**
- Model presentation and styling appropriateness
- Clothing visibility and appeal
- Seasonal/trend alignment
- Lifestyle context and aspirational quality""",
            
            'tech': """
**Tech-Specific Criteria:**
- Product features clearly visible
- Modern, innovative aesthetic
- Clean, minimalist design preferred
- UI/screen clarity if applicable""",
            
            'food': """
**Food-Specific Criteria:**
- Food presentation and appeal (looks delicious)
- Freshness perception
- Appropriate lighting and colors
- Appetite appeal and mouth-watering quality""",
            
            'luxury': """
**Luxury-Specific Criteria:**
- Premium quality perception
- Sophisticated composition
- Exclusivity and refinement
- Attention to detail and craftsmanship""",
            
            'eco': """
**Eco/Sustainability-Specific Criteria:**
- Natural, organic visual style
- Green/earth tones appropriateness
- Authenticity (avoid greenwashing)
- Connection to nature/environment""",
            
            'health': """
**Health/Wellness-Specific Criteria:**
- Clean, trustworthy presentation
- Professional medical imagery if applicable
- Calm, reassuring aesthetic
- Clarity of health benefits""",
            
            'general': """
**General Advertising Criteria:**
- Clear value proposition
- Appropriate target audience appeal
- Professional quality"""
        }
        
        category_note = category_guidelines.get(category, category_guidelines['general'])
        
        prompt = f"""You are an expert Creative Director and Brand Compliance Officer evaluating a {category.upper()} advertisement.

{brand_context}

Ad Description: {ad_description or 'Not provided'}

{category_note}

Analyze this advertisement and provide a structured critique across these dimensions:

1. **Brand Alignment** (0-1 score):
   - Does it match the brand colors and visual identity?
   - Is the tone appropriate for the brand and {category} industry?
   - Are brand elements (logo, typography) used correctly?
   
2. **Visual Quality** (0-1 score):
   - Is the image sharp and well-composed?
   - Are there any visual artifacts or issues?
   - Is the layout professional and balanced?
   - {category}-specific quality standards met?
   
3. **Message Clarity** (0-1 score):
   - Is the product/service clearly visible?
   - Is the message/tagline clear and readable?
   - Is the call-to-action obvious?
   - Does it communicate the value proposition?
   
4. **Safety & Ethics** (0-1 score):
   - Any harmful, offensive, or misleading content?
   - Any stereotypes or bias?
   - Is it truthful and compliant?
   - Industry-specific compliance (e.g., health claims, etc.)

**IMPORTANT:** For each score, also provide a confidence level (0-1) indicating how certain you are of your evaluation.

For each dimension, provide DETAILED analysis:
- **Score explanation**: Why this specific score (what's good, what's lacking)
- **Specific observations**: What you see in the ad
- **Measurable issues**: Concrete problems (e.g., "Logo is 40% too small", "Tagline font size is 12px, should be 18px")
- **Actionable suggestions**: Specific steps to improve (with measurements when possible)

Return ONLY a valid JSON object with this structure:
{{
  "brand_alignment": {{
    "score": 0.85,
    "confidence": 0.90,
    "feedback": "Colors match well with brand palette. Primary brand color (#2E7D32 green) is present in 60% of the composition. Logo is visible but positioned slightly off-center (15px to the left). Tone matches the brand's natural, eco-friendly voice effectively.",
    "score_explanation": "High score due to strong color matching and appropriate tone. Deducted 15% for logo positioning issues.",
    "specific_observations": [
      "Brand green (#2E7D32) dominates composition at 60% coverage",
      "Logo present in top-left corner, size: 120x40px",
      "Tone of voice aligns with 'natural' and 'eco-friendly' brand values",
      "Typography uses sans-serif matching brand guidelines"
    ],
    "issues": [
      "Logo positioned 15px off-center from optimal placement",
      "Secondary brand color (#66BB6A) underutilized (only 10% coverage)"
    ],
    "suggestions": [
      "Center the logo horizontally (move 15px right)",
      "Increase logo size by 20% to 144x48px for better visibility",
      "Increase secondary color usage to 25-30% of composition",
      "Add brand tagline in brand font below logo"
    ]
  }},
  "visual_quality": {{
    "score": 0.90,
    "confidence": 0.95,
    "feedback": "Excellent image quality with sharp focus and professional composition. Resolution is 1920x1080px with no visible artifacts. Lighting is balanced with good contrast (measured at 78%). Rule of thirds applied effectively. Minor improvement possible in background detail.",
    "score_explanation": "Near-perfect technical quality. Professional composition and lighting. Minimal deduction for slightly plain background.",
    "specific_observations": [
      "Resolution: 1920x1080px (Full HD)",
      "Sharpness score: 0.92 (excellent)",
      "Contrast ratio: 78% (well-balanced)",
      "Composition follows rule of thirds",
      "No watermarks or artifacts detected",
      "Color balance: Neutral (not oversaturated)"
    ],
    "issues": [],
    "suggestions": [
      "Consider adding subtle texture to background for depth",
      "Slight vignette effect could improve focus on product (10% opacity)"
    ]
  }},
  "message_clarity": {{
    "score": 0.75,
    "confidence": 0.85,
    "feedback": "Product is clearly visible occupying 40% of frame. Tagline present but rendered at 12px font size, which is below recommended 18px minimum for readability. CTA button missing entirely. Value proposition unclear - needs explicit messaging.",
    "score_explanation": "Good product visibility (40% frame coverage). Significant deductions for undersized text (33% below standard) and missing CTA (20% penalty).",
    "specific_observations": [
      "Product occupies 40% of frame (good proportion)",
      "Tagline text: 12px font size (below 18px standard)",
      "Tagline contrast ratio: 3.5:1 (below WCAG AA standard of 4.5:1)",
      "No call-to-action button present",
      "Value proposition not explicitly stated",
      "Product name visible but small (14px font)"
    ],
    "issues": [
      "Tagline font size too small: 12px (should be minimum 18px)",
      "Text contrast insufficient: 3.5:1 (needs 4.5:1 for readability)",
      "Missing call-to-action button",
      "No explicit value proposition or benefit statement",
      "Product name undersized at 14px"
    ],
    "suggestions": [
      "Increase tagline font size from 12px to 20-24px",
      "Improve text contrast to 4.5:1 or higher (use darker text or lighter background)",
      "Add prominent CTA button (minimum 140x40px) with action verb",
      "Include value proposition headline in 28-32px bold font",
      "Increase product name to 18-20px",
      "Position text in upper 1/3 or lower 1/3 for optimal reading flow"
    ]
  }},
  "safety_ethics": {{
    "score": 1.0,
    "confidence": 1.0,
    "feedback": "No safety, ethical, or compliance concerns detected. Content is appropriate for all audiences. No misleading claims, stereotypes, or harmful imagery. Truthful product representation. Complies with advertising standards.",
    "score_explanation": "Perfect score - no violations detected across all safety and ethics criteria.",
    "specific_observations": [
      "No harmful or offensive content",
      "No stereotypes or bias detected",
      "Product claims appear truthful",
      "Age-appropriate imagery (suitable for all ages)",
      "No misleading health/environmental claims",
      "No copyright violations visible"
    ],
    "issues": [],
    "suggestions": []
  }},
  "detected_elements": {{
    "has_logo": true,
    "has_product": true,
    "has_tagline": true,
    "has_cta": false,
    "text_content": ["EcoFlow Water Bottle", "Sustainable Hydration"],
    "dominant_colors": ["#2E7D32", "#FFFFFF", "#66BB6A"],
    "category_detected": "{category}",
    "estimated_resolution": "1920x1080",
    "composition_type": "product-centered"
  }},
  "overall_assessment": "Strong advertisement with excellent visual quality and good brand alignment. Primary weakness is text readability - tagline and product name are undersized. Missing call-to-action is critical gap. Recommended to increase text sizes by 50-80% and add prominent CTA button. With these fixes, ad would score 90%+.",
  "overall_confidence": 0.88,
  "improvement_priority": [
    "HIGH: Add call-to-action button with action verb",
    "HIGH: Increase tagline font size to 20-24px",
    "MEDIUM: Improve text contrast to 4.5:1",
    "MEDIUM: Add value proposition headline",
    "LOW: Center logo placement"
  ]
}}

Respond ONLY with valid JSON. No markdown, no explanations outside the JSON.
"""
        return prompt
    
    def _parse_gemini_response(self, response_text: str) -> Dict:
        """Parse and validate Gemini's JSON response"""
        try:
            # Remove markdown code blocks if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            # Parse JSON
            critique_data = json.loads(response_text.strip())
            return critique_data
            
        except json.JSONDecodeError as e:
            print(f"Error parsing Gemini response: {e}")
            print(f"Response text: {response_text}")
            return self._get_fallback_critique()
    
    def _get_fallback_critique(self, image_path: str = None) -> Dict:
        """
        Provide intelligent fallback critique using CV metrics if AI analysis fails.
        Uses actual image quality metrics instead of generic 0.5 scores.
        """
        
        # Try to get actual CV metrics
        quality_score = 0.5
        clarity_score = 0.5
        feedback_notes = []
        
        if image_path and os.path.exists(image_path):
            try:
                # Analyze image quality using OpenCV
                visual_analysis = self.image_analyzer.analyze_quality(image_path)
                
                # Quality score based on sharpness and composition
                quality_score = (visual_analysis.sharpness + visual_analysis.composition) / 2
                
                # Clarity score based on contrast
                clarity_score = visual_analysis.contrast
                
                # Add specific feedback based on metrics
                if visual_analysis.sharpness < 0.6:
                    feedback_notes.append("Image appears blurry or out of focus")
                if visual_analysis.contrast < 0.5:
                    feedback_notes.append("Low contrast detected - text may be hard to read")
                if visual_analysis.has_watermark:
                    feedback_notes.append("Watermark detected in image")
                    
            except Exception as e:
                print(f"Error in fallback CV analysis: {e}")
        
        return {
            "brand_alignment": {
                "score": 0.5,  # Cannot assess without AI
                "feedback": "AI analysis unavailable - brand alignment cannot be automatically verified",
                "issues": ["Could not perform AI brand analysis"],
                "suggestions": ["Manually verify brand colors and logo placement"]
            },
            "visual_quality": {
                "score": quality_score,
                "feedback": f"Computer vision analysis: Quality score {quality_score:.2f}. " + 
                           (" ".join(feedback_notes) if feedback_notes else "Image quality appears acceptable."),
                "issues": feedback_notes if feedback_notes else [],
                "suggestions": ["Consider improving image sharpness"] if quality_score < 0.6 else []
            },
            "message_clarity": {
                "score": clarity_score,
                "feedback": f"Contrast-based analysis: Clarity score {clarity_score:.2f}. AI text analysis unavailable.",
                "issues": ["Text visibility could not be verified by AI"] if clarity_score < 0.6 else [],
                "suggestions": ["Increase text contrast for better readability"] if clarity_score < 0.6 else []
            },
            "safety_ethics": {
                "score": 0.7,  # Neutral - assume safe unless proven otherwise
                "feedback": "AI safety analysis unavailable - manual safety review required for sensitive content",
                "issues": ["Manual safety review needed"],
                "suggestions": ["Conduct manual review for brand compliance and safety"]
            },
            "detected_elements": {
                "cv_analysis_used": True,
                "ai_analysis_available": False
            },
            "overall_assessment": f"Using computer vision fallback (Quality: {quality_score:.2f}, Clarity: {clarity_score:.2f}). AI critique unavailable - manual review recommended for brand and safety verification."
        }
    
    async def _compile_critique(
        self,
        image_path: str,
        brand_kit: Optional[BrandKit],
        visual_analysis: VisualAnalysis,
        color_analysis: ColorAnalysis,
        ai_critique: Dict
    ) -> AdCritique:
        """Compile all analyses into final critique"""
        
        import uuid
        
        # Enhance AI critique with CV analysis
        brand_score_data = ai_critique.get("brand_alignment", {})
        quality_score_data = ai_critique.get("visual_quality", {})
        clarity_score_data = ai_critique.get("message_clarity", {})
        safety_score_data = ai_critique.get("safety_ethics", {})
        
        # Extract confidence scores
        brand_confidence = brand_score_data.get("confidence", 0.5)
        quality_confidence = quality_score_data.get("confidence", 0.5)
        clarity_confidence = clarity_score_data.get("confidence", 0.5)
        safety_confidence = safety_score_data.get("confidence", 0.5)
        overall_confidence = ai_critique.get("overall_confidence", 
                                            (brand_confidence + quality_confidence + 
                                             clarity_confidence + safety_confidence) / 4)
        
        # Flag for manual review if confidence is low
        needs_manual_review = overall_confidence < 0.65
        low_confidence_areas = []
        if brand_confidence < 0.7:
            low_confidence_areas.append("brand_alignment")
        if quality_confidence < 0.7:
            low_confidence_areas.append("visual_quality")
        if clarity_confidence < 0.7:
            low_confidence_areas.append("message_clarity")
        if safety_confidence < 0.7:
            low_confidence_areas.append("safety_ethics")
        
        # Adjust brand alignment score based on color analysis
        brand_score = brand_score_data.get("score", 0.5)
        if brand_kit:
            brand_score = (brand_score + color_analysis.brand_color_match) / 2
        
        # Adjust quality score based on visual analysis
        quality_score = quality_score_data.get("score", 0.5)
        quality_score = (quality_score + visual_analysis.sharpness + visual_analysis.composition) / 3
        
        # Build critique scores
        brand_alignment = CritiqueScore(
            score=brand_score,
            level=self._get_score_level(brand_score),
            feedback=brand_score_data.get("feedback", ""),
            issues=brand_score_data.get("issues", []),
            suggestions=brand_score_data.get("suggestions", [])
        )
        
        visual_quality = CritiqueScore(
            score=quality_score,
            level=self._get_score_level(quality_score),
            feedback=quality_score_data.get("feedback", ""),
            issues=quality_score_data.get("issues", []) + 
                   (["Watermark detected"] if visual_analysis.has_watermark else []),
            suggestions=quality_score_data.get("suggestions", [])
        )
        
        message_clarity = CritiqueScore(
            score=clarity_score_data.get("score", 0.5),
            level=self._get_score_level(clarity_score_data.get("score", 0.5)),
            feedback=clarity_score_data.get("feedback", ""),
            issues=clarity_score_data.get("issues", []),
            suggestions=clarity_score_data.get("suggestions", [])
        )
        
        safety_ethics = CritiqueScore(
            score=safety_score_data.get("score", 0.5),
            level=self._get_score_level(safety_score_data.get("score", 0.5)),
            feedback=safety_score_data.get("feedback", ""),
            issues=safety_score_data.get("issues", []),
            suggestions=safety_score_data.get("suggestions", [])
        )
        
        # Calculate overall score (weighted average)
        overall_score = (
            brand_alignment.score * 0.3 +
            visual_quality.score * 0.25 +
            message_clarity.score * 0.25 +
            safety_ethics.score * 0.20
        )
        
        # Determine if ready to deploy
        ready_to_deploy = (
            brand_alignment.score >= settings.min_brand_score and
            visual_quality.score >= settings.min_quality_score and
            safety_ethics.score >= settings.min_safety_score and
            message_clarity.score >= settings.min_clarity_score
        )
        
        # Compile improvements needed
        improvements = []
        for score in [brand_alignment, visual_quality, message_clarity, safety_ethics]:
            improvements.extend(score.suggestions)
        
        critique = AdCritique(
            critique_id=str(uuid.uuid4()),
            ad_url=image_path,
            brand_id=brand_kit.brand_id if brand_kit else None,
            brand_alignment=brand_alignment,
            visual_quality=visual_quality,
            message_clarity=message_clarity,
            safety_ethics=safety_ethics,
            overall_score=overall_score,
            overall_level=self._get_score_level(overall_score),
            ready_to_deploy=ready_to_deploy,
            detected_elements={
                **ai_critique.get("detected_elements", {}),
                "color_analysis": color_analysis.dict(),
                "visual_analysis": visual_analysis.dict()
            },
            improvements_needed=improvements,
            approval_status="approved" if ready_to_deploy else "pending"
        )
        
        # Convert to dict with proper structure for frontend
        critique_result = {
            "critique_id": critique.critique_id,
            "overall_score": critique.overall_score,
            "overall_level": critique.overall_level,
            "ready_to_deploy": critique.ready_to_deploy,
            "scores": {
                "brand_alignment": critique.brand_alignment.score,
                "visual_quality": critique.visual_quality.score,
                "message_clarity": critique.message_clarity.score,
                "safety": critique.safety_ethics.score
            },
            "confidence_scores": {
                "brand_alignment": brand_confidence,
                "visual_quality": quality_confidence,
                "message_clarity": clarity_confidence,
                "safety": safety_confidence,
                "overall": overall_confidence
            },
            "needs_manual_review": needs_manual_review,
            "low_confidence_areas": low_confidence_areas,
            "feedback": {
                "brand_alignment": {
                    "feedback": critique.brand_alignment.feedback,
                    "score_explanation": brand_score_data.get("score_explanation", ""),
                    "specific_observations": brand_score_data.get("specific_observations", []),
                    "issues": critique.brand_alignment.issues,
                    "suggestions": critique.brand_alignment.suggestions
                },
                "visual_quality": {
                    "feedback": critique.visual_quality.feedback,
                    "score_explanation": quality_score_data.get("score_explanation", ""),
                    "specific_observations": quality_score_data.get("specific_observations", []),
                    "issues": critique.visual_quality.issues,
                    "suggestions": critique.visual_quality.suggestions
                },
                "message_clarity": {
                    "feedback": critique.message_clarity.feedback,
                    "score_explanation": clarity_score_data.get("score_explanation", ""),
                    "specific_observations": clarity_score_data.get("specific_observations", []),
                    "issues": critique.message_clarity.issues,
                    "suggestions": critique.message_clarity.suggestions
                },
                "safety_ethics": {
                    "feedback": critique.safety_ethics.feedback,
                    "score_explanation": safety_score_data.get("score_explanation", ""),
                    "specific_observations": safety_score_data.get("specific_observations", []),
                    "issues": critique.safety_ethics.issues,
                    "suggestions": critique.safety_ethics.suggestions
                },
                "overall_assessment": ai_critique.get("overall_assessment", ""),
                "improvement_priority": ai_critique.get("improvement_priority", [])
            },
            "issues": brand_alignment.issues + visual_quality.issues + message_clarity.issues + safety_ethics.issues,
            "suggestions": improvements,
            "detected_elements": critique.detected_elements,
            "approval_status": critique.approval_status
        }
        
        # Add warning if manual review needed
        if needs_manual_review:
            critique_result["issues"].insert(0, 
                f"⚠️ Low confidence ({overall_confidence:.0%}) - Manual review recommended for: {', '.join(low_confidence_areas)}")
        
        return critique_result
    
    def _get_score_level(self, score: float) -> ScoreLevel:
        """Convert numeric score to level category"""
        if score >= 0.85:
            return ScoreLevel.EXCELLENT
        elif score >= 0.70:
            return ScoreLevel.GOOD
        elif score >= 0.50:
            return ScoreLevel.FAIR
        else:
            return ScoreLevel.POOR
