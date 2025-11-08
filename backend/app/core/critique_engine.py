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
            self.model = genai.GenerativeModel('gemini-1.5-pro-latest')
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
            return self._get_fallback_critique()
    
    def _build_critique_prompt(
        self,
        brand_kit: Optional[BrandKit],
        ad_description: Optional[str]
    ) -> str:
        """Build a detailed prompt for Gemini to critique the ad"""
        
        brand_context = ""
        if brand_kit:
            brand_context = f"""
Brand: {brand_kit.brand_name}
Primary Colors: {', '.join(brand_kit.primary_colors)}
Tone of Voice: {', '.join(brand_kit.tone_of_voice)}
Brand Values: {', '.join(brand_kit.brand_values) if brand_kit.brand_values else 'Not specified'}
"""
        
        prompt = f"""You are an expert Creative Director and Brand Compliance Officer evaluating an advertisement.

{brand_context}

Ad Description: {ad_description or 'Not provided'}

Analyze this advertisement and provide a structured critique across these dimensions:

1. **Brand Alignment** (0-1 score):
   - Does it match the brand colors and visual identity?
   - Is the tone appropriate for the brand?
   - Are brand elements (logo, typography) used correctly?
   
2. **Visual Quality** (0-1 score):
   - Is the image sharp and well-composed?
   - Are there any visual artifacts or issues?
   - Is the layout professional and balanced?
   
3. **Message Clarity** (0-1 score):
   - Is the product/service clearly visible?
   - Is the message/tagline clear and readable?
   - Is the call-to-action obvious?
   
4. **Safety & Ethics** (0-1 score):
   - Any harmful, offensive, or misleading content?
   - Any stereotypes or bias?
   - Is it truthful and compliant?

Return ONLY a valid JSON object with this structure:
{{
  "brand_alignment": {{
    "score": 0.85,
    "feedback": "Colors match well but logo placement could be improved",
    "issues": ["Logo slightly off-center"],
    "suggestions": ["Center the logo", "Increase logo size by 20%"]
  }},
  "visual_quality": {{
    "score": 0.90,
    "feedback": "High quality image with good composition",
    "issues": [],
    "suggestions": ["Consider adding more contrast"]
  }},
  "message_clarity": {{
    "score": 0.75,
    "feedback": "Product visible but tagline is small",
    "issues": ["Text too small", "CTA not prominent"],
    "suggestions": ["Increase tagline font size", "Make CTA button larger"]
  }},
  "safety_ethics": {{
    "score": 1.0,
    "feedback": "No safety or ethical concerns detected",
    "issues": [],
    "suggestions": []
  }},
  "detected_elements": {{
    "has_logo": true,
    "has_product": true,
    "has_tagline": true,
    "has_cta": false,
    "text_content": ["visible text in the ad"]
  }},
  "overall_assessment": "Good ad but needs minor improvements to text visibility"
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
    
    def _get_fallback_critique(self) -> Dict:
        """Provide a fallback critique if AI analysis fails"""
        return {
            "brand_alignment": {
                "score": 0.5,
                "feedback": "AI analysis unavailable - manual review recommended",
                "issues": ["Could not perform AI analysis"],
                "suggestions": ["Review manually"]
            },
            "visual_quality": {
                "score": 0.5,
                "feedback": "AI analysis unavailable",
                "issues": [],
                "suggestions": []
            },
            "message_clarity": {
                "score": 0.5,
                "feedback": "AI analysis unavailable",
                "issues": [],
                "suggestions": []
            },
            "safety_ethics": {
                "score": 0.5,
                "feedback": "AI analysis unavailable - manual safety review required",
                "issues": ["Manual review needed"],
                "suggestions": ["Conduct manual safety review"]
            },
            "detected_elements": {},
            "overall_assessment": "AI analysis failed - manual review required"
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
        
        return critique
    
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
