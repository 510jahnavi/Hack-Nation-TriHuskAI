"""
Multi-Agent Workflow API - Auto-refining ad generation
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import logging

from app.core.multi_agent_orchestrator import MultiAgentOrchestrator
from app.services.brand_service import BrandService
from config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
brand_service = BrandService()


class MultiAgentRequest(BaseModel):
    """Request for multi-agent workflow"""
    prompt: str = Field(..., description="Initial ad generation prompt")
    brand_kit_id: Optional[str] = Field(None, description="Brand kit ID to use")
    aspect_ratio: str = Field("1:1", description="Image aspect ratio (1:1, 16:9, 9:16)")
    include_logo: bool = Field(True, description="Include brand logo in ad")
    max_iterations: int = Field(3, ge=1, le=10, description="Maximum refinement iterations")
    score_threshold: float = Field(0.75, ge=0.0, le=1.0, description="Target quality score")


class MultiAgentResponse(BaseModel):
    """Response from multi-agent workflow"""
    success: bool
    iterations_count: int
    iterations: list
    best_ad: Optional[Dict[str, Any]]
    final_score: float
    threshold_met: bool
    workflow_duration_seconds: float
    message: str


@router.post("/generate-and-refine", response_model=MultiAgentResponse)
async def generate_and_refine_ad(request: MultiAgentRequest):
    """
    Generate an ad and automatically refine it using multi-agent workflow
    
    Pipeline:
    1. Generate ad from prompt (Generator Agent)
    2. Describe ad components (Descriptor Agent)  
    3. Critique the ad (Critic Agent)
    4. If score < threshold, refine prompt and regenerate (Refinement Agent)
    5. Repeat until acceptable or max iterations
    
    Returns detailed iteration history and best result.
    """
    try:
        logger.info(f"Multi-agent request: prompt='{request.prompt[:50]}...', iterations={request.max_iterations}")
        
        # Load brand kit if specified
        brand_kit_data = None
        if request.brand_kit_id:
            brand_kit_data = brand_service.get_brand_kit(request.brand_kit_id)
            if not brand_kit_data:
                raise HTTPException(
                    status_code=404,
                    detail=f"Brand kit '{request.brand_kit_id}' not found"
                )
        
        # Initialize orchestrator
        orchestrator = MultiAgentOrchestrator(
            gemini_api_key=settings.gemini_api_key,
            vertex_project_id=settings.google_cloud_project,
            vertex_location=settings.vertex_ai_location,
            max_iterations=request.max_iterations,
            score_threshold=request.score_threshold
        )
        
        # Run workflow
        result = await orchestrator.generate_and_refine(
            prompt=request.prompt,
            brand_kit_id=request.brand_kit_id,
            aspect_ratio=request.aspect_ratio,
            include_logo=request.include_logo,
            brand_kit_data=brand_kit_data
        )
        
        # Build response message
        if result["threshold_met"]:
            message = f"✅ Success! Achieved {result['final_score']:.2f} score in {result['iterations_count']} iteration(s)"
        elif result["best_ad"]:
            message = f"⚠️ Best score: {result['final_score']:.2f} after {result['iterations_count']} iterations (target: {request.score_threshold})"
        else:
            message = f"❌ Failed to generate acceptable ad after {result['iterations_count']} iterations"
        
        result["message"] = message
        
        logger.info(f"Multi-agent workflow complete: {message}")
        
        return MultiAgentResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Multi-agent workflow error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Multi-agent workflow failed: {str(e)}"
        )


@router.get("/workflow-status")
async def get_workflow_info():
    """
    Get information about the multi-agent workflow capabilities
    """
    return {
        "available": True,
        "agents": [
            {
                "name": "Generator Agent",
                "description": "Generates ad images using Imagen 2 / Vertex AI",
                "status": "active"
            },
            {
                "name": "Descriptor Agent", 
                "description": "Analyzes ad components (colors, text, objects, mood)",
                "status": "active",
                "requires_api_key": True
            },
            {
                "name": "Critic Agent",
                "description": "Scores ads on brand alignment, visual quality, message clarity, safety",
                "status": "active",
                "requires_api_key": True
            },
            {
                "name": "Refinement Agent",
                "description": "Generates improved prompts based on critique feedback",
                "status": "active",
                "requires_api_key": True
            }
        ],
        "max_iterations": 10,
        "default_threshold": 0.75,
        "features": [
            "Automatic iterative refinement",
            "Detailed iteration history",
            "Best ad tracking across iterations",
            "Structured critique feedback",
            "AI-powered prompt improvement"
        ],
        "api_key_configured": bool(settings.gemini_api_key),
        "note": "Full functionality requires gemini_api_key in .env file"
    }
