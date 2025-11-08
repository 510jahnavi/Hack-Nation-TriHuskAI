"""
API routes for brand kit management
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import List, Optional
import json
import uuid

from config import settings
from app.models.schemas import BrandKit
from app.services.brand_service import BrandService

router = APIRouter()
brand_service = BrandService()


@router.post("/brand-kit", response_model=BrandKit)
async def create_brand_kit(
    brand_name: str = Form(...),
    primary_colors: str = Form(..., description="Comma-separated hex codes"),
    secondary_colors: Optional[str] = Form(None),
    tone_of_voice: str = Form(..., description="Comma-separated values"),
    brand_values: Optional[str] = Form(None),
    guidelines: Optional[str] = Form(None),
    logo: Optional[UploadFile] = File(None)
):
    """
    Create a new brand kit with guidelines
    
    Brand kits define the rules for ad critique:
    - Colors, typography, visual style
    - Tone of voice and messaging
    - Logo and brand assets
    """
    
    # Parse comma-separated values
    primary_colors_list = [c.strip() for c in primary_colors.split(',')]
    secondary_colors_list = [c.strip() for c in secondary_colors.split(',')] if secondary_colors else []
    tone_list = [t.strip() for t in tone_of_voice.split(',')]
    values_list = [v.strip() for v in brand_values.split(',')] if brand_values else []
    
    # Handle logo upload
    logo_url = None
    if logo:
        logo_url = await brand_service.save_logo(logo)
    
    # Create brand kit
    brand_kit = BrandKit(
        brand_id=str(uuid.uuid4()),
        brand_name=brand_name,
        primary_colors=primary_colors_list,
        secondary_colors=secondary_colors_list if secondary_colors_list else None,
        logo_url=logo_url,
        tone_of_voice=tone_list,
        brand_values=values_list if values_list else None,
        guidelines=guidelines
    )
    
    # Save brand kit
    await brand_service.save_brand_kit(brand_kit)
    
    return brand_kit


@router.get("/brand-kit/{brand_id}", response_model=BrandKit)
async def get_brand_kit(brand_id: str):
    """
    Retrieve a brand kit by ID
    """
    brand_kit = await brand_service.get_brand_kit(brand_id)
    if not brand_kit:
        raise HTTPException(status_code=404, detail="Brand kit not found")
    return brand_kit


@router.get("/brand-kits", response_model=List[BrandKit])
async def list_brand_kits():
    """
    List all available brand kits
    """
    return await brand_service.list_brand_kits()


@router.delete("/brand-kit/{brand_id}")
async def delete_brand_kit(brand_id: str):
    """
    Delete a brand kit
    """
    success = await brand_service.delete_brand_kit(brand_id)
    if not success:
        raise HTTPException(status_code=404, detail="Brand kit not found")
    return {"message": "Brand kit deleted successfully"}


@router.post("/brand-kit/extract-from-url")
async def extract_brand_from_url(url: str = Form(...)):
    """
    STRETCH GOAL: Auto-extract brand colors and style from website
    """
    raise HTTPException(status_code=501, detail="Feature not yet implemented - stretch goal")
