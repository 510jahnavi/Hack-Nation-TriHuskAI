"""
Ad generation service using Google Vertex AI
"""

import os
import uuid
import logging
from typing import Dict, Any
from google.cloud import aiplatform
from vertexai.preview.vision_models import ImageGenerationModel
import google.generativeai as genai
from google.oauth2 import service_account

from config import settings
from app.models.schemas import GenerateAdRequest
from app.services.brand_service import BrandService

logger = logging.getLogger(__name__)


class GenerationService:
    """
    Handles ad generation using Vertex AI models
    This is a SECONDARY feature - generation is lightweight
    The focus is on CRITIQUING the output
    """
    
    def __init__(self):
        """Initialize Vertex AI with authentication"""
        # Set up authentication
        if settings.google_application_credentials:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = settings.google_application_credentials
        
        if settings.google_cloud_project:
            aiplatform.init(
                project=settings.google_cloud_project,
                location=settings.vertex_ai_location
            )
        
        self.brand_service = BrandService()
    
    async def generate_ad(self, request: GenerateAdRequest) -> Dict[str, Any]:
        """
        Generate a basic ad image or video
        
        Uses:
        - Imagen 2 for images
        - Veo for videos (stretch goal)
        """
        
        # Get brand kit for context
        brand_kit = await self.brand_service.get_brand_kit(request.brand_id)
        
        # Build generation prompt
        prompt = self._build_generation_prompt(request, brand_kit)
        
        if request.media_type == "image":
            result = await self._generate_image(prompt, request)
        elif request.media_type == "video":
            result = await self._generate_video(prompt, request)
        else:
            raise ValueError(f"Unsupported media type: {request.media_type}")
        
        return result
    
    async def generate_variants(self, request: GenerateAdRequest, num_variants: int = 3) -> Dict[str, Any]:
        """
        Generate multiple ad variants with slight prompt variations
        
        Returns 3 variants (A, B, C) for comparison
        """
        brand_kit = await self.brand_service.get_brand_kit(request.brand_id)
        base_prompt = self._build_generation_prompt(request, brand_kit)
        
        # Create prompt variations
        variations = [
            {"id": "A", "style": "bold and vibrant", "emphasis": "product prominence"},
            {"id": "B", "style": "minimal and clean", "emphasis": "brand identity"},
            {"id": "C", "style": "dynamic and energetic", "emphasis": "call-to-action clarity"}
        ]
        
        results = []
        for variant in variations:
            # Modify prompt for each variant
            modified_prompt = f"{base_prompt}\n\nStyle emphasis: {variant['style']}, Focus on: {variant['emphasis']}"
            
            try:
                if request.media_type == "image":
                    result = await self._generate_image(modified_prompt, request)
                else:
                    result = await self._generate_video(modified_prompt, request)
                
                results.append({
                    "variant_id": variant["id"],
                    "variant_name": f"Variant {variant['id']}",
                    "style_emphasis": variant["style"],
                    "focus": variant["emphasis"],
                    **result
                })
            except Exception as e:
                results.append({
                    "variant_id": variant["id"],
                    "error": str(e),
                    "success": False
                })
        
        return {
            "success": True,
            "variants": results,
            "total_variants": len(results),
            "base_prompt": base_prompt
        }
    
    def _build_generation_prompt(
        self,
        request: GenerateAdRequest,
        brand_kit: Any
    ) -> str:
        """Build a prompt for ad generation"""
        
        brand_context = ""
        if brand_kit:
            colors = ', '.join(brand_kit.primary_colors)
            tone = ', '.join(brand_kit.tone_of_voice)
            brand_context = f"""
Brand: {brand_kit.brand_name}
Colors: {colors}
Tone: {tone}
"""
        
        prompt = f"""Create a {request.style} advertisement for {request.product_name}.

{brand_context}

Product: {request.product_name}
Description: {request.product_description}
Tagline: {request.tagline or 'Not specified'}

Style: {request.style}, professional, high-quality
Requirements:
- Show the product prominently
- Include the tagline if provided
- Use brand colors
- Clean, professional composition
- No watermarks or artifacts
"""
        return prompt
    
    async def _generate_image(
        self,
        prompt: str,
        request: GenerateAdRequest
    ) -> Dict[str, Any]:
        """
        Generate image using Gemini to create ad copy from the user prompt
        """
        
        try:
            from PIL import Image, ImageDraw, ImageFont
            import textwrap
            import google.generativeai as genai
            
            # Use Gemini to generate creative ad copy from the user prompt
            genai.configure(api_key=settings.gemini_api_key)
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            ad_copy_prompt = f"""Based on this user request: "{prompt}"
            
Generate ONLY the following for an advertisement:
1. A catchy headline (max 6 words)
2. A compelling tagline (max 10 words)
3. A brief description (max 15 words)

Format as:
HEADLINE: [text]
TAGLINE: [text]
DESCRIPTION: [text]"""

            response = model.generate_content(ad_copy_prompt)
            ai_response = response.text
            
            # Parse the AI response
            headline = "NEW PRODUCT"
            tagline = ""
            description = ""
            
            for line in ai_response.split('\n'):
                if 'HEADLINE:' in line.upper():
                    headline = line.split(':', 1)[1].strip()
                elif 'TAGLINE:' in line.upper():
                    tagline = line.split(':', 1)[1].strip()
                elif 'DESCRIPTION:' in line.upper():
                    description = line.split(':', 1)[1].strip()
            
            # Create a placeholder image
            image_id = str(uuid.uuid4())
            image_path = os.path.join(
                settings.generated_ads_dir,
                f"{image_id}.png"
            )
            
            os.makedirs(settings.generated_ads_dir, exist_ok=True)
            
            # Create a 1024x1024 image with gradient background
            img = Image.new('RGB', (1024, 1024), color='#4A90E2')
            draw = ImageDraw.Draw(img)
            
            # Add fonts
            try:
                font_headline = ImageFont.truetype("arial.ttf", 70)
                font_tagline = ImageFont.truetype("arial.ttf", 35)
                font_description = ImageFont.truetype("arial.ttf", 25)
            except:
                font_headline = ImageFont.load_default()
                font_tagline = ImageFont.load_default()
                font_description = ImageFont.load_default()
            
            # Draw headline centered at top
            headline_bbox = draw.textbbox((0, 0), headline.upper(), font=font_headline)
            headline_width = headline_bbox[2] - headline_bbox[0]
            draw.text(
                ((1024 - headline_width) / 2, 300),
                headline.upper(),
                fill='white',
                font=font_headline
            )
            
            # Draw tagline
            if tagline:
                tagline_bbox = draw.textbbox((0, 0), tagline, font=font_tagline)
                tagline_width = tagline_bbox[2] - tagline_bbox[0]
                draw.text(
                    ((1024 - tagline_width) / 2, 420),
                    tagline,
                    fill='#FFD700',
                    font=font_tagline
                )
            
            # Draw description wrapped
            if description:
                wrapped_desc = textwrap.fill(description, width=40)
                desc_bbox = draw.textbbox((0, 0), wrapped_desc, font=font_description)
                desc_width = desc_bbox[2] - desc_bbox[0]
                draw.text(
                    ((1024 - desc_width) / 2, 520),
                    wrapped_desc,
                    fill='white',
                    font=font_description
                )
            
            # Save the image
            img.save(image_path)
            
            logger.info(f"Generated ad image: {image_path}")
            logger.info(f"AI-generated copy - Headline: {headline}, Tagline: {tagline}")
            
            return {
                "success": True,
                "ad_id": image_id,
                "image_path": image_path,
                "prompt": prompt,
                "headline": headline,
                "tagline": tagline,
                "description": description,
                "media_type": "image",
                "status": "generated"
            }
            
        except Exception as e:
            print(f"Error generating image: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Image generation failed",
                "status": "failed"
            }
    
    async def _generate_video(
        self,
        prompt: str,
        request: GenerateAdRequest
    ) -> Dict[str, Any]:
        """
        Generate video using Veo (stretch goal)
        """
        # TODO: Implement Veo video generation
        return {
            "message": "Video generation not yet implemented - stretch goal",
            "prompt": prompt,
            "media_type": "video",
            "status": "not_implemented"
        }
    
    async def improve_ad(
        self,
        critique_id: str,
        iterations: int = 1
    ) -> Dict[str, Any]:
        """
        Improve an ad based on critique feedback
        
        This implements the auto-improvement loop:
        1. Load original critique
        2. Extract improvement suggestions
        3. Generate improved version
        4. Re-critique
        """
        
        # TODO: Implement improvement loop
        # This requires:
        # 1. Critique storage/retrieval
        # 2. Prompt refinement based on feedback
        # 3. Multi-agent workflow
        
        return {
            "message": "Auto-improvement not yet implemented",
            "critique_id": critique_id,
            "iterations": iterations,
            "status": "not_implemented"
        }
