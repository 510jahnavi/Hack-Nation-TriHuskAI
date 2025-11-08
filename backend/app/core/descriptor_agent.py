"""
Descriptor Agent - Analyzes generated ads and extracts all components
"""
import google.generativeai as genai
from typing import Dict, Any, List, Optional
import base64
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


class DescriptorAgent:
    """
    Analyzes AI-generated ads and extracts detailed components:
    - Visual elements (colors, objects, composition)
    - Text content (headlines, taglines, CTAs)
    - Mood and tone
    - Brand elements (logos, typography)
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None
            logger.warning("Descriptor Agent initialized without Gemini API key - using fallback mode")
    
    def describe_ad(self, image_path: str) -> Dict[str, Any]:
        """
        Analyze an ad image and extract all components
        
        Args:
            image_path: Path to the ad image
            
        Returns:
            Dictionary with detailed ad description
        """
        if not self.model:
            return self._fallback_description(image_path)
        
        try:
            # Load image
            image_data = self._load_image(image_path)
            
            # Create detailed analysis prompt
            prompt = self._create_descriptor_prompt()
            
            # Generate description
            response = self.model.generate_content([prompt, image_data])
            
            # Parse response
            description = self._parse_description(response.text)
            
            logger.info(f"Generated description for ad: {image_path}")
            return description
            
        except Exception as e:
            logger.error(f"Error describing ad: {str(e)}")
            return self._fallback_description(image_path)
    
    def _create_descriptor_prompt(self) -> str:
        """Create detailed prompt for ad description"""
        return """You are an expert Ad Analyzer. Analyze this advertisement image in extreme detail.

Extract and describe the following components:

1. **Visual Elements:**
   - Dominant colors (list HEX codes if possible, or color names)
   - Objects and subjects visible
   - Composition and layout (rule of thirds, symmetry, focal points)
   - Visual style (modern, vintage, minimalist, bold, etc.)
   - Image quality (sharp, blurry, professional, amateur)

2. **Text Content:**
   - Headline/main text
   - Tagline or slogan
   - Call-to-action (CTA) text
   - Any other visible text
   - Font style description

3. **Brand Elements:**
   - Logo presence and placement
   - Brand name visibility
   - Brand colors usage
   - Brand typography

4. **Mood and Tone:**
   - Overall emotional tone (exciting, calm, urgent, playful, etc.)
   - Target audience impression
   - Messaging tone (formal, casual, humorous, serious)

5. **Technical Aspects:**
   - Image dimensions/aspect ratio impression
   - Watermarks or artifacts
   - Visual hierarchy
   - Readability of text

6. **Product/Service:**
   - What is being advertised
   - How clearly is the product shown
   - Product placement and prominence

Output your analysis as a JSON object with the following structure:
{
  "visual_elements": {
    "colors": ["color1", "color2", ...],
    "objects": ["object1", "object2", ...],
    "composition": "description",
    "style": "description",
    "quality": "sharp/blurry/professional/amateur"
  },
  "text_content": {
    "headline": "text or null",
    "tagline": "text or null",
    "cta": "text or null",
    "other_text": ["text1", "text2", ...],
    "font_style": "description"
  },
  "brand_elements": {
    "logo_present": true/false,
    "logo_placement": "description or null",
    "brand_name_visible": true/false,
    "brand_colors_used": ["color1", "color2", ...],
    "typography_style": "description"
  },
  "mood_and_tone": {
    "emotional_tone": "description",
    "target_audience": "description",
    "messaging_tone": "formal/casual/humorous/serious/etc"
  },
  "technical_aspects": {
    "aspect_ratio": "landscape/portrait/square",
    "has_watermarks": true/false,
    "visual_hierarchy": "description",
    "text_readability": "excellent/good/poor"
  },
  "product_info": {
    "product_description": "what is being advertised",
    "product_visibility": "clear/moderate/unclear",
    "product_prominence": "high/medium/low"
  }
}

Return ONLY the JSON object, no additional text."""
    
    def _load_image(self, image_path: str):
        """Load image for Gemini API"""
        from PIL import Image
        img = Image.open(image_path)
        return img
    
    def _parse_description(self, response_text: str) -> Dict[str, Any]:
        """Parse Gemini response into structured description"""
        try:
            # Try to extract JSON from response
            # Remove markdown code blocks if present
            clean_text = response_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.startswith("```"):
                clean_text = clean_text[3:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            
            description = json.loads(clean_text.strip())
            
            # Add metadata
            description["source"] = "gemini_vision"
            description["raw_response"] = response_text[:500]  # First 500 chars
            
            return description
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {e}")
            # Return raw text analysis
            return {
                "source": "gemini_vision_raw",
                "raw_analysis": response_text,
                "parsing_error": str(e)
            }
    
    def _fallback_description(self, image_path: str) -> Dict[str, Any]:
        """Fallback description using basic image analysis"""
        from PIL import Image
        import numpy as np
        
        try:
            img = Image.open(image_path)
            width, height = img.size
            
            # Basic color analysis
            img_array = np.array(img)
            avg_color = img_array.mean(axis=(0, 1))
            
            return {
                "source": "fallback",
                "visual_elements": {
                    "dimensions": f"{width}x{height}",
                    "aspect_ratio": "landscape" if width > height else "portrait" if height > width else "square",
                    "average_color_rgb": avg_color.tolist() if isinstance(avg_color, np.ndarray) else "unknown",
                    "quality": "unknown - API key required for detailed analysis"
                },
                "text_content": {
                    "note": "Text extraction requires Gemini API key"
                },
                "brand_elements": {
                    "note": "Brand analysis requires Gemini API key"
                },
                "mood_and_tone": {
                    "note": "Tone analysis requires Gemini API key"
                },
                "technical_aspects": {
                    "aspect_ratio": "landscape" if width > height else "portrait" if height > width else "square",
                    "note": "Detailed analysis requires Gemini API key"
                },
                "product_info": {
                    "note": "Product analysis requires Gemini API key"
                }
            }
        except Exception as e:
            logger.error(f"Fallback description failed: {e}")
            return {
                "source": "error",
                "error": str(e)
            }
