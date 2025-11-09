"""
File Upload API - Handle brand logo and product image uploads
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Optional
import logging
import os
import uuid
from pathlib import Path
import shutil

logger = logging.getLogger(__name__)
router = APIRouter()

# Upload directories
UPLOAD_DIR = Path("backend/uploads")
BRAND_LOGOS_DIR = UPLOAD_DIR / "brand_logos"
PRODUCT_IMAGES_DIR = UPLOAD_DIR / "product_images"

# Create directories if they don't exist
BRAND_LOGOS_DIR.mkdir(parents=True, exist_ok=True)
PRODUCT_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}


def validate_image_file(filename: str) -> bool:
    """Validate if file has allowed extension"""
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


@router.post("/brand-logo")
async def upload_brand_logo(file: UploadFile = File(...)):
    """
    Upload a brand logo image
    
    Returns:
        - file_path: Relative path to uploaded file
        - filename: Generated filename
    """
    try:
        # Validate file extension
        if not validate_image_file(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Generate unique filename
        file_extension = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = BRAND_LOGOS_DIR / unique_filename
        
        # Save file
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"✅ Brand logo uploaded: {file_path}")
        
        return {
            "success": True,
            "file_path": str(file_path),
            "filename": unique_filename,
            "original_filename": file.filename,
            "message": "Brand logo uploaded successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Error uploading brand logo: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/product-image")
async def upload_product_image(file: UploadFile = File(...)):
    """
    Upload a product image
    
    Returns:
        - file_path: Relative path to uploaded file
        - filename: Generated filename
    """
    try:
        # Validate file extension
        if not validate_image_file(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Generate unique filename
        file_extension = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = PRODUCT_IMAGES_DIR / unique_filename
        
        # Save file
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"✅ Product image uploaded: {file_path}")
        
        return {
            "success": True,
            "file_path": str(file_path),
            "filename": unique_filename,
            "original_filename": file.filename,
            "message": "Product image uploaded successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Error uploading product image: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list-uploads")
async def list_uploads():
    """List all uploaded files"""
    try:
        brand_logos = [
            {
                "filename": f.name,
                "path": str(f),
                "size": f.stat().st_size
            }
            for f in BRAND_LOGOS_DIR.glob("*")
            if f.is_file()
        ]
        
        product_images = [
            {
                "filename": f.name,
                "path": str(f),
                "size": f.stat().st_size
            }
            for f in PRODUCT_IMAGES_DIR.glob("*")
            if f.is_file()
        ]
        
        return {
            "brand_logos": brand_logos,
            "product_images": product_images,
            "total_brand_logos": len(brand_logos),
            "total_product_images": len(product_images)
        }
        
    except Exception as e:
        logger.error(f"❌ Error listing uploads: {e}")
        raise HTTPException(status_code=500, detail=str(e))
