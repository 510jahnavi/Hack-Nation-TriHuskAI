"""
API routes for ad generation (secondary feature)
"""

from fastapi import APIRouter, HTTPException, Form
from typing import Optional

from app.models.schemas import GenerateAdRequest
from app.services.generation_service import GenerationService

router = APIRouter()
generation_service = GenerationService()


@router.post("/generate-ad")
async def generate_ad(
    brand_id: str = Form(...),
    product_name: str = Form(...),
    product_description: str = Form(...),
    tagline: Optional[str] = Form(None),
    style: str = Form("modern"),
    media_type: str = Form("image")
):
    """
    Generate a basic ad using AI (secondary feature)
    
    This is a lightweight generation step.
    The main focus is on CRITIQUING the output, not generation quality.
    
    Supports:
    - Image generation via Imagen 2
    - Video generation via Veo (stretch goal)
    """
    
    request = GenerateAdRequest(
        brand_id=brand_id,
        product_name=product_name,
        product_description=product_description,
        tagline=tagline,
        style=style,
        media_type=media_type
    )
    
    try:
        result = await generation_service.generate_ad(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@router.post("/generate-variants")
async def generate_variants(
    brand_id: str = Form(...),
    product_name: str = Form(...),
    product_description: str = Form(...),
    tagline: Optional[str] = Form(None),
    style: str = Form("modern"),
    media_type: str = Form("image"),
    num_variants: int = Form(3)
):
    """
    Generate multiple ad variants (A, B, C) for comparison
    
    Returns 3 different versions with prompt variations:
    - Variant A: Bold and vibrant (product prominence)
    - Variant B: Minimal and clean (brand identity)
    - Variant C: Dynamic and energetic (CTA clarity)
    
    This allows comparing different approaches before critique.
    """
    
    request = GenerateAdRequest(
        brand_id=brand_id,
        product_name=product_name,
        product_description=product_description,
        tagline=tagline,
        style=style,
        media_type=media_type
    )
    
    try:
        result = await generation_service.generate_variants(request, num_variants)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Variant generation failed: {str(e)}")


@router.post("/improve-ad")
async def improve_ad(
    critique_id: str = Form(...),
    improvement_iterations: int = Form(1)
):
    """
    Auto-improve an ad based on critique feedback
    
    This implements the refinement loop:
    1. Get critique feedback
    2. Generate improved version with updated prompt
    3. Re-critique
    4. Repeat if needed
    """
    
    try:
        result = await generation_service.improve_ad(critique_id, improvement_iterations)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Improvement failed: {str(e)}")
