from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ScoreLevel(str, Enum):
    """Score level categories"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"


class BrandKit(BaseModel):
    """Brand guidelines and identity information"""
    brand_id: str
    brand_name: str
    primary_colors: List[str] = Field(description="Hex color codes")
    secondary_colors: Optional[List[str]] = None
    logo_url: Optional[str] = None
    typography: Optional[Dict[str, str]] = None
    tone_of_voice: List[str] = Field(description="E.g., professional, friendly, energetic")
    brand_values: Optional[List[str]] = None
    guidelines: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)


class CritiqueScore(BaseModel):
    """Individual score component"""
    score: float = Field(ge=0.0, le=1.0, description="Score from 0 to 1")
    level: ScoreLevel
    feedback: str
    issues: List[str] = []
    suggestions: List[str] = []


class AdCritique(BaseModel):
    """Complete critique analysis of an ad"""
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    critique_id: str
    ad_url: str
    brand_id: Optional[str] = None
    
    # Core scoring dimensions
    brand_alignment: CritiqueScore
    visual_quality: CritiqueScore
    message_clarity: CritiqueScore
    safety_ethics: CritiqueScore
    
    # Overall assessment
    overall_score: float = Field(ge=0.0, le=1.0)
    overall_level: ScoreLevel
    ready_to_deploy: bool
    
    # Detailed analysis
    detected_elements: Dict[str, Any] = {}
    improvements_needed: List[str] = []
    approval_status: str = "pending"  # pending, approved, rejected
    
    created_at: datetime = Field(default_factory=datetime.now)


class GenerateAdRequest(BaseModel):
    """Request to generate an ad"""
    brand_id: str
    product_name: str
    product_description: str
    tagline: Optional[str] = None
    style: str = "modern"  # modern, minimal, bold, elegant
    duration: int = Field(default=10, ge=5, le=15, description="Duration in seconds for video")
    media_type: str = "image"  # image or video


class CritiqueRequest(BaseModel):
    """Request to critique an ad"""
    brand_id: Optional[str] = None
    ad_description: Optional[str] = None
    check_dimensions: List[str] = ["brand", "quality", "safety", "clarity"]


class ImproveAdRequest(BaseModel):
    """Request to improve an ad based on critique"""
    critique_id: str
    improvement_iterations: int = Field(default=1, ge=1, le=3)


class ColorAnalysis(BaseModel):
    """Color analysis results"""
    dominant_colors: List[str]
    color_palette: List[str]
    brand_color_match: float = Field(ge=0.0, le=1.0)
    color_harmony: float = Field(ge=0.0, le=1.0)


class VisualAnalysis(BaseModel):
    """Visual quality analysis results"""
    sharpness: float = Field(ge=0.0, le=1.0)
    composition: float = Field(ge=0.0, le=1.0)
    has_watermark: bool
    has_artifacts: bool
    resolution: Dict[str, int]
    aspect_ratio: str
