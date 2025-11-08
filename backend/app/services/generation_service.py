"""
Ad generation service using Google Vertex AI
"""

import os
import uuid
from typing import Dict, Any
from google.cloud import aiplatform
from vertexai.preview.vision_models import ImageGenerationModel
import google.generativeai as genai

from config import settings
from app.models.schemas import GenerateAdRequest
from app.services.brand_service import BrandService


class GenerationService:
    """
    Handles ad generation using Vertex AI models
    This is a SECONDARY feature - generation is lightweight
    The focus is on CRITIQUING the output
    """
    
    def __init__(self):
        """Initialize Vertex AI"""
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
        Generate image using Imagen 2 on Vertex AI
        """
        
        try:
            # Initialize Imagen model
            model = ImageGenerationModel.from_pretrained("imagegeneration@006")
            
            # Generate image
            response = model.generate_images(
                prompt=prompt,
                number_of_images=1,
                aspect_ratio="1:1",  # Square format for social media
                safety_filter_level="block_some",
                person_generation="allow_adult"
            )
            
            # Save generated image
            image_id = str(uuid.uuid4())
            image_path = os.path.join(
                settings.generated_ads_dir,
                f"{image_id}.png"
            )
            
            os.makedirs(settings.generated_ads_dir, exist_ok=True)
            response.images[0].save(image_path)
            
            return {
                "ad_id": image_id,
                "image_path": image_path,
                "prompt": prompt,
                "media_type": "image",
                "status": "generated"
            }
            
        except Exception as e:
            print(f"Error generating image: {e}")
            # Fallback: return placeholder info
            return {
                "error": str(e),
                "message": "Image generation failed - ensure Vertex AI is configured",
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
