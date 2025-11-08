from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Google Cloud
    google_cloud_project: str = ""
    google_application_credentials: Optional[str] = None
    vertex_ai_location: str = "us-central1"
    gemini_api_key: Optional[str] = None
    
    # OpenAI (Optional)
    openai_api_key: Optional[str] = None
    
    # Application
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = True
    
    # Upload Settings
    max_upload_size: int = 50000000  # 50MB
    upload_dir: str = "uploads"
    brand_kit_dir: str = "brand_kits"
    generated_ads_dir: str = "generated_ads"
    
    # Critique Thresholds
    min_brand_score: float = 0.7
    min_quality_score: float = 0.6
    min_safety_score: float = 0.9
    min_clarity_score: float = 0.7
    
    # Model Settings
    gemini_model: str = "gemini-pro-vision"
    imagen_model: str = "imagegeneration@006"
    veo_model: str = "veo-001"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
