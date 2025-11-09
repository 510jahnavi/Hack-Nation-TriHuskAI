"""
Ad generation service using Google Vertex AI
"""

import os
import uuid
import logging
import requests
from typing import Dict, Any, Optional
from google.cloud import aiplatform
from vertexai.preview.vision_models import ImageGenerationModel
import google.generativeai as genai
from google.oauth2 import service_account
import vertexai
from vertexai.preview.vision_models import ImageGenerationModel

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
        logger.info(f"🔍 Loading brand kit with ID: {request.brand_id}")
        brand_kit = await self.brand_service.get_brand_kit(request.brand_id)
        logger.info(f"🔍 Brand kit loaded: {brand_kit is not None}, type: {type(brand_kit) if brand_kit else 'None'}")
        if brand_kit:
            logger.info(f"🔍 Brand: {brand_kit.brand_name if hasattr(brand_kit, 'brand_name') else 'unknown'}, Colors: {brand_kit.primary_colors if hasattr(brand_kit, 'primary_colors') else 'none'}")
        
        # Build generation prompt
        prompt = self._build_generation_prompt(request, brand_kit)
        
        if request.media_type == "image":
            result = await self._generate_image(prompt, request, brand_kit)
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
                    result = await self._generate_image(modified_prompt, request, brand_kit)
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
        request: GenerateAdRequest,
        brand_kit: Optional[object] = None
    ) -> Dict[str, Any]:
        """
        Generate image using Google Imagen 3 via Vertex AI or PIL fallback
        """
        
        # Extract brand colors if available
        brand_colors = []
        brand_name = "Brand"
        if brand_kit:
            brand_colors = brand_kit.primary_colors if hasattr(brand_kit, 'primary_colors') else []
            brand_name = brand_kit.brand_name if hasattr(brand_kit, 'brand_name') else "Brand"
        
        try:
            # Initialize Vertex AI
            vertexai.init(
                project=settings.google_cloud_project,
                location=settings.vertex_ai_location
            )
            
            # Use Gemini to enhance the prompt with ad-specific details and brand colors
            import google.generativeai as genai
            genai.configure(api_key=settings.gemini_api_key)
            text_model = genai.GenerativeModel('gemini-2.0-flash')
            
            brand_context = ""
            if brand_colors:
                brand_context = f"\nBrand colors to use: {', '.join(brand_colors)}"
            
            enhancement_prompt = f"""Based on this user request: "{prompt}"
{brand_context}

Create a detailed Imagen 3 prompt for a professional advertisement image. Include:
- Main subject/product
- Setting/background{"with brand colors: " + ", ".join(brand_colors) if brand_colors else ""}
- Colors and mood
- Text placement areas (but NO actual text - Imagen can't render text reliably)
- Composition and style
- Professional photography quality

Format as a single detailed prompt (max 1000 characters) suitable for Imagen 3 image generation.
Start directly with the prompt, no explanations."""

            response = text_model.generate_content(enhancement_prompt)
            enhanced_prompt = response.text.strip()
            
            logger.info(f"Enhanced Imagen prompt: {enhanced_prompt}")
            
            # Generate image using Imagen 3
            image_model = ImageGenerationModel.from_pretrained("imagegeneration@006")  # Imagen 3
            
            images = image_model.generate_images(
                prompt=enhanced_prompt,
                number_of_images=1,
                aspect_ratio="1:1",  # Square format for ads
                safety_filter_level="block_some",
                person_generation="allow_adult"
            )
            
            # Save the generated image
            image_id = str(uuid.uuid4())
            image_path = os.path.join(
                settings.generated_ads_dir,
                f"{image_id}.png"
            )
            
            os.makedirs(settings.generated_ads_dir, exist_ok=True)
            
            # Save the first generated image
            images[0].save(image_path)
            
            # Generate ad copy separately using Gemini
            ad_copy_prompt = f"""Based on this user request: "{prompt}"

Generate ONLY the following for an advertisement:
1. A catchy headline (max 6 words)
2. A compelling tagline (max 10 words)
3. A brief description (max 15 words)

Format as:
HEADLINE: [text]
TAGLINE: [text]
DESCRIPTION: [text]"""

            copy_response = text_model.generate_content(ad_copy_prompt)
            ai_copy = copy_response.text
            
            # Parse the AI response
            headline = "NEW PRODUCT"
            tagline = ""
            description = ""
            
            for line in ai_copy.split('\n'):
                if 'HEADLINE:' in line.upper():
                    headline = line.split(':', 1)[1].strip()
                elif 'TAGLINE:' in line.upper():
                    tagline = line.split(':', 1)[1].strip()
                elif 'DESCRIPTION:' in line.upper():
                    description = line.split(':', 1)[1].strip()
            
            logger.info(f"Generated ad image with Imagen 3: {image_path}")
            logger.info(f"AI-generated copy - Headline: {headline}, Tagline: {tagline}")
            
            return {
                "success": True,
                "ad_id": image_id,
                "image_path": image_path,
                "prompt": prompt,
                "enhanced_prompt": enhanced_prompt,
                "headline": headline,
                "tagline": tagline,
                "description": description,
                "media_type": "image",
                "status": "generated",
                "generation_model": "imagen-3"
            }
            
        except Exception as e:
            logger.error(f"Error generating image with Imagen 3: {str(e)}")
            logger.exception(e)
            
            # Fallback to PIL if Imagen fails
            return await self._generate_image_fallback(prompt, request, brand_kit)
    
    async def _generate_image_fallback(
        self,
        prompt: str,
        request: GenerateAdRequest,
        brand_kit: Optional[object] = None
    ) -> Dict[str, Any]:
        """
        Fallback PIL-based image generation if Imagen fails
        Uses brand kit colors if available
        """
        logger.info(f"🎨 PIL FALLBACK CALLED - brand_kit received: {brand_kit is not None}")
        try:
            from PIL import Image, ImageDraw, ImageFont
            import textwrap
            import google.generativeai as genai
            
            # Extract brand colors
            brand_colors = []
            brand_name = "Brand"
            if brand_kit:
                logger.info(f"🎨 Brand kit object: {type(brand_kit)}, attributes: {dir(brand_kit)}")
                brand_colors = brand_kit.primary_colors if hasattr(brand_kit, 'primary_colors') else []
                brand_name = brand_kit.brand_name if hasattr(brand_kit, 'brand_name') else "Brand"
                logger.info(f"🎨 Extracted from brand kit - Name: {brand_name}, Colors: {brand_colors}")
            
            # Use Gemini to generate creative ad copy
            genai.configure(api_key=settings.gemini_api_key)
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            # Build prompt with brand context
            color_context = ""
            if brand_colors:
                color_context = f"\nUse one of these brand colors: {', '.join(brand_colors)}"
            
            ad_copy_prompt = f"""Based on this user request: "{prompt}"
{color_context}

Generate ONLY the following for an advertisement:
1. A catchy headline (max 6 words)
2. A compelling tagline (max 10 words)
3. A brief description (max 15 words)
4. Primary background color as HEX code{' (MUST use one of: ' + ', '.join(brand_colors) + ')' if brand_colors else ' (based on product/theme, e.g., #4A90E2 for tech, #2E7D32 for eco, #D32F2F for food, #7B1FA2 for luxury)'}
5. Design style (modern/minimalist/bold/elegant/playful)

Format as:
HEADLINE: [text]
TAGLINE: [text]
DESCRIPTION: [text]
COLOR: [hex code]
STYLE: [style]"""

            response = model.generate_content(ad_copy_prompt)
            ai_response = response.text
            
            # Parse response
            headline = "NEW PRODUCT"
            tagline = ""
            description = ""
            bg_color = brand_colors[0] if brand_colors else "#4A90E2"  # Use first brand color or default
            style = "modern"
            
            for line in ai_response.split('\n'):
                if 'HEADLINE:' in line.upper():
                    headline = line.split(':', 1)[1].strip()
                elif 'TAGLINE:' in line.upper():
                    tagline = line.split(':', 1)[1].strip()
                elif 'DESCRIPTION:' in line.upper():
                    description = line.split(':', 1)[1].strip()
                elif 'COLOR:' in line.upper():
                    color_text = line.split(':', 1)[1].strip()
                    if '#' in color_text:
                        suggested_color = color_text.split('#')[1].split()[0]
                        suggested_color = '#' + suggested_color[:6]
                        # If brand colors exist, use closest match; otherwise use suggested
                        if brand_colors:
                            bg_color = brand_colors[0]  # Use primary brand color
                        else:
                            bg_color = suggested_color
                elif 'STYLE:' in line.upper():
                    style = line.split(':', 1)[1].strip().lower()
            
            # Create image
            image_id = str(uuid.uuid4())
            image_path = os.path.join(settings.generated_ads_dir, f"{image_id}.png")
            os.makedirs(settings.generated_ads_dir, exist_ok=True)
            
            logger.info(f"PIL Fallback - Using color: {bg_color}, Brand: {brand_name}, Brand colors: {brand_colors}")
            
            try:
                img = Image.new('RGB', (1024, 1024), color=bg_color)
            except:
                # If color parsing fails, use first brand color or default
                fallback_color = brand_colors[0] if brand_colors else '#4A90E2'
                img = Image.new('RGB', (1024, 1024), color=fallback_color)
                logger.warning(f"Color parsing failed for {bg_color}, using fallback: {fallback_color}")
            
            draw = ImageDraw.Draw(img)
            
            # Text colors based on brightness
            try:
                r = int(bg_color[1:3], 16)
                g = int(bg_color[3:5], 16)
                b = int(bg_color[5:7], 16)
                brightness = (r * 299 + g * 587 + b * 114) / 1000
                text_color = 'white' if brightness < 128 else 'black'
                accent_color = '#FFD700' if brightness < 128 else '#FF6B00'
            except:
                text_color = 'white'
                accent_color = '#FFD700'
            
            # Add fonts
            try:
                if style in ['bold', 'energetic']:
                    font_headline = ImageFont.truetype("arial.ttf", 80)
                    font_tagline = ImageFont.truetype("arial.ttf", 40)
                    font_description = ImageFont.truetype("arial.ttf", 28)
                elif style in ['minimalist', 'elegant']:
                    font_headline = ImageFont.truetype("arial.ttf", 65)
                    font_tagline = ImageFont.truetype("arial.ttf", 32)
                    font_description = ImageFont.truetype("arial.ttf", 22)
                else:
                    font_headline = ImageFont.truetype("arial.ttf", 70)
                    font_tagline = ImageFont.truetype("arial.ttf", 35)
                    font_description = ImageFont.truetype("arial.ttf", 25)
            except:
                font_headline = ImageFont.load_default()
                font_tagline = ImageFont.load_default()
                font_description = ImageFont.load_default()
            
            # Positioning
            if style in ['minimalist', 'elegant']:
                y_headline, y_tagline, y_description = 350, 470, 550
            elif style in ['bold', 'energetic']:
                y_headline, y_tagline, y_description = 280, 410, 510
            else:
                y_headline, y_tagline, y_description = 300, 420, 520
            
            # Draw text
            headline_bbox = draw.textbbox((0, 0), headline.upper(), font=font_headline)
            headline_width = headline_bbox[2] - headline_bbox[0]
            draw.text(((1024 - headline_width) / 2, y_headline), headline.upper(), fill=text_color, font=font_headline)
            
            if tagline:
                tagline_bbox = draw.textbbox((0, 0), tagline, font=font_tagline)
                tagline_width = tagline_bbox[2] - tagline_bbox[0]
                draw.text(((1024 - tagline_width) / 2, y_tagline), tagline, fill=accent_color, font=font_tagline)
            
            if description:
                wrapped_desc = textwrap.fill(description, width=40)
                desc_bbox = draw.textbbox((0, 0), wrapped_desc, font=font_description)
                desc_width = desc_bbox[2] - desc_bbox[0]
                draw.text(((1024 - desc_width) / 2, y_description), wrapped_desc, fill=text_color, font=font_description)
            
            img.save(image_path)
            
            logger.info(f"Generated fallback PIL image: {image_path}")
            
            return {
                "success": True,
                "ad_id": image_id,
                "image_path": image_path,
                "prompt": prompt,
                "headline": headline,
                "tagline": tagline,
                "description": description,
                "background_color": bg_color,
                "style": style,
                "media_type": "image",
                "status": "generated",
                "generation_model": "pil-fallback"
            }
            
        except Exception as e:
            logger.error(f"Error in fallback image generation: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "Image generation failed",
                "status": "failed"
            }
    
    async def _generate_video(
        self,
        prompt: str,
        request: GenerateAdRequest,
        brand_kit: Optional[object] = None
    ) -> Dict[str, Any]:
        """
        Generate video ad using Google Veo
        
        Creates 5-15 second video clips with:
        - Brand colors and style
        - Product focus
        - Professional quality
        """
        try:
            import vertexai
            from vertexai.preview.vision_models import VideoGenerationModel
            
            # Initialize Vertex AI
            vertexai.init(
                project=settings.google_cloud_project,
                location=settings.vertex_ai_location
            )
            
            logger.info(f"🎬 Generating video with Veo...")
            
            # Build video generation prompt with brand context
            video_prompt = self._build_video_prompt(prompt, request, brand_kit)
            
            # Load Veo model
            model = VideoGenerationModel.from_pretrained("veo-001")
            
            # Generate video
            logger.info(f"Veo prompt: {video_prompt[:200]}...")
            video_response = model.generate_videos(
                prompt=video_prompt,
                number_of_videos=1,
                aspect_ratio="16:9" if request.aspect_ratio == "16:9" else "9:16" if request.aspect_ratio == "9:16" else "1:1",
            )
            
            # Save video
            video_id = str(uuid.uuid4())
            video_path = os.path.join(settings.generated_ads_dir, f"{video_id}.mp4")
            os.makedirs(settings.generated_ads_dir, exist_ok=True)
            
            # Get first video from response
            generated_video = video_response[0]
            generated_video.save(location=video_path)
            
            logger.info(f"✅ Video generated successfully: {video_path}")
            
            return {
                "success": True,
                "video_path": video_path,
                "video_id": video_id,
                "duration": request.duration if hasattr(request, 'duration') else 10,
                "prompt": video_prompt,
                "generation_model": "veo-001"
            }
            
        except Exception as e:
            logger.error(f"Error generating video with Veo: {str(e)}")
            logger.exception(e)
            
            # Fallback: Create a simple video with PIL frames
            return await self._generate_video_fallback(prompt, request, brand_kit)
    
    def _build_video_prompt(
        self,
        prompt: str,
        request: GenerateAdRequest,
        brand_kit: Optional[object] = None
    ) -> str:
        """Build enhanced prompt for video generation"""
        
        # Extract brand context
        brand_colors = []
        brand_tone = []
        brand_name = "Product"
        
        if brand_kit:
            brand_colors = brand_kit.primary_colors if hasattr(brand_kit, 'primary_colors') else []
            brand_tone = brand_kit.tone_of_voice if hasattr(brand_kit, 'tone_of_voice') else []
            brand_name = brand_kit.brand_name if hasattr(brand_kit, 'brand_name') else "Product"
        
        # Build comprehensive video prompt
        video_prompt = f"""Create a professional {request.duration if hasattr(request, 'duration') else 10}-second video advertisement.

Product/Theme: {prompt}
Brand: {brand_name}

Visual Requirements:
- Cinematic quality with smooth camera movements
- Professional lighting and color grading
"""
        
        if brand_colors:
            video_prompt += f"- Color palette: {', '.join(brand_colors[:3])}\n"
        
        if brand_tone:
            video_prompt += f"- Tone/Mood: {', '.join(brand_tone)}\n"
        
        video_prompt += f"""
Style: {request.style if hasattr(request, 'style') else 'modern and professional'}

Key Elements:
- Clear product showcase
- Engaging visual storytelling
- Brand-appropriate aesthetics
- Call-to-action at end

Technical Specs:
- High resolution (1080p or better)
- Smooth transitions
- Professional composition
"""
        
        return video_prompt
    
    async def _generate_video_fallback(
        self,
        prompt: str,
        request: GenerateAdRequest,
        brand_kit: Optional[object] = None
    ) -> Dict[str, Any]:
        """
        Fallback: Create simple video using PIL images + ffmpeg
        """
        try:
            from PIL import Image, ImageDraw, ImageFont
            import subprocess
            
            logger.info("🎬 Using PIL+ffmpeg fallback for video generation")
            
            # Generate a static image first
            image_result = await self._generate_image_fallback(prompt, request, brand_kit)
            
            if not image_result.get("success"):
                return image_result
            
            image_path = image_result["image_path"]
            
            # Create video from static image using ffmpeg
            video_id = str(uuid.uuid4())
            video_path = os.path.join(settings.generated_ads_dir, f"{video_id}.mp4")
            
            duration = request.duration if hasattr(request, 'duration') else 10
            
            # ffmpeg command: create video from image with duration
            cmd = [
                'ffmpeg',
                '-loop', '1',
                '-i', image_path,
                '-c:v', 'libx264',
                '-t', str(duration),
                '-pix_fmt', 'yuv420p',
                '-vf', 'scale=1920:1080',
                '-y',
                video_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"✅ Fallback video created: {video_path}")
                return {
                    "success": True,
                    "video_path": video_path,
                    "video_id": video_id,
                    "duration": duration,
                    "prompt": prompt,
                    "generation_model": "pil-fallback",
                    "note": "Generated using PIL + ffmpeg (Veo unavailable)"
                }
            else:
                # If ffmpeg fails, just return the static image
                logger.warning("ffmpeg not available, returning static image")
                return {
                    "success": True,
                    "image_path": image_path,  # Return image as fallback
                    "video_id": video_id,
                    "duration": 0,
                    "prompt": prompt,
                    "generation_model": "pil-static",
                    "note": "Video generation unavailable, returning static image"
                }
                
        except Exception as e:
            logger.error(f"Video fallback error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
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
