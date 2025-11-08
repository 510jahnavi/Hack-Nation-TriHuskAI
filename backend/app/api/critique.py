"""
API routes for ad critique functionality
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
import os
import uuid
from typing import Optional

from config import settings
from app.models.schemas import CritiqueRequest, AdCritique
from app.core.critique_engine import CritiqueEngine
from app.services.brand_service import BrandService

router = APIRouter()
critique_engine = CritiqueEngine()
brand_service = BrandService()


@router.post("/critique-ad", response_model=AdCritique)
async def critique_ad(
    file: UploadFile = File(...),
    brand_id: Optional[str] = Form(None),
    ad_description: Optional[str] = Form(None)
):
    """
    Critique an uploaded ad image
    
    This is the core hero feature - evaluates the ad across:
    - Brand alignment
    - Visual quality  
    - Message clarity
    - Safety & ethics
    
    Returns a comprehensive critique with scores and suggestions.
    """
    
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Save uploaded file
    file_ext = os.path.splitext(file.filename)[1]
    file_id = str(uuid.uuid4())
    file_path = os.path.join(settings.upload_dir, f"{file_id}{file_ext}")
    
    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Get brand kit if provided
        brand_kit = None
        if brand_id:
            brand_kit = await brand_service.get_brand_kit(brand_id)
        
        # Perform critique
        critique = await critique_engine.critique_ad(
            image_path=file_path,
            brand_kit=brand_kit,
            ad_description=ad_description
        )
        
        return critique
        
    except Exception as e:
        # Clean up file on error
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Critique failed: {str(e)}")


@router.get("/critique/{critique_id}", response_model=AdCritique)
async def get_critique(critique_id: str):
    """
    Retrieve a previously generated critique
    """
    # TODO: Implement critique storage and retrieval
    raise HTTPException(status_code=501, detail="Not implemented - add database storage")


@router.post("/batch-critique")
async def batch_critique(files: list[UploadFile] = File(...), brand_id: Optional[str] = Form(None)):
    """
    Critique multiple ads in batch
    Useful for comparing multiple ad variations
    """
    results = []
    
    for file in files:
        try:
            # Reuse single critique endpoint logic
            file_ext = os.path.splitext(file.filename)[1]
            file_id = str(uuid.uuid4())
            file_path = os.path.join(settings.upload_dir, f"{file_id}{file_ext}")
            
            with open(file_path, "wb") as f:
                content = await file.read()
                f.write(content)
            
            brand_kit = None
            if brand_id:
                brand_kit = await brand_service.get_brand_kit(brand_id)
            
            critique = await critique_engine.critique_ad(
                image_path=file_path,
                brand_kit=brand_kit
            )
            
            results.append({
                "filename": file.filename,
                "critique": critique.dict()
            })
            
        except Exception as e:
            results.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return {"results": results, "total": len(files), "successful": len([r for r in results if "critique" in r])}
