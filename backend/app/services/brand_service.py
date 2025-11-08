"""
Brand kit management service
"""

import json
import os
import uuid
from typing import List, Optional
from fastapi import UploadFile

from config import settings
from app.models.schemas import BrandKit


class BrandService:
    """Manages brand kits and brand assets"""
    
    def __init__(self):
        self.brand_kits_path = settings.brand_kit_dir
        os.makedirs(self.brand_kits_path, exist_ok=True)
    
    async def save_brand_kit(self, brand_kit: BrandKit) -> bool:
        """Save brand kit to disk"""
        file_path = os.path.join(
            self.brand_kits_path,
            f"{brand_kit.brand_id}.json"
        )
        
        try:
            with open(file_path, 'w') as f:
                json.dump(brand_kit.dict(), f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Error saving brand kit: {e}")
            return False
    
    async def get_brand_kit(self, brand_id: str) -> Optional[BrandKit]:
        """Load brand kit from disk"""
        file_path = os.path.join(self.brand_kits_path, f"{brand_id}.json")
        
        if not os.path.exists(file_path):
            return None
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return BrandKit(**data)
        except Exception as e:
            print(f"Error loading brand kit: {e}")
            return None
    
    async def list_brand_kits(self) -> List[BrandKit]:
        """List all brand kits"""
        brand_kits = []
        
        for filename in os.listdir(self.brand_kits_path):
            if filename.endswith('.json'):
                brand_id = filename.replace('.json', '')
                brand_kit = await self.get_brand_kit(brand_id)
                if brand_kit:
                    brand_kits.append(brand_kit)
        
        return brand_kits
    
    async def delete_brand_kit(self, brand_id: str) -> bool:
        """Delete brand kit"""
        file_path = os.path.join(self.brand_kits_path, f"{brand_id}.json")
        
        if not os.path.exists(file_path):
            return False
        
        try:
            os.remove(file_path)
            return True
        except Exception as e:
            print(f"Error deleting brand kit: {e}")
            return False
    
    async def save_logo(self, logo: UploadFile) -> str:
        """Save logo file and return URL"""
        file_ext = os.path.splitext(logo.filename)[1]
        file_id = str(uuid.uuid4())
        file_path = os.path.join(
            self.brand_kits_path,
            'logos',
            f"{file_id}{file_ext}"
        )
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        try:
            with open(file_path, 'wb') as f:
                content = await logo.read()
                f.write(content)
            return file_path
        except Exception as e:
            print(f"Error saving logo: {e}")
            return None
