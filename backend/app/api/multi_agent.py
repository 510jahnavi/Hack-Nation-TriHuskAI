"""
Multi-Agent Workflow API - Auto-refining ad generation
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import logging
import os
import uuid

from app.core.multi_agent_orchestrator import MultiAgentOrchestrator
from app.services.brand_service import BrandService
from app.core.descriptor_agent import DescriptorAgent
from app.core.critique_engine import CritiqueEngine
from config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
brand_service = BrandService()
descriptor_agent = DescriptorAgent()
critique_engine = CritiqueEngine()


class MultiAgentRequest(BaseModel):
    """Request for multi-agent workflow"""
    prompt: str = Field(..., description="Initial ad generation prompt")
    brand_kit_id: Optional[str] = Field(None, description="Brand kit ID to use")
    aspect_ratio: str = Field("1:1", description="Image aspect ratio (1:1, 16:9, 9:16)")
    media_type: str = Field("image", description="Media type: 'image' or 'video'")
    duration: int = Field(10, ge=5, le=15, description="Video duration in seconds (if video)")
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
            brand_kit_data = await brand_service.get_brand_kit(request.brand_kit_id)
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
            media_type=request.media_type,
            duration=request.duration,
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


@router.post("/critique-uploaded-ad")
async def critique_uploaded_ad(
    file: UploadFile = File(..., description="Ad image or video to critique"),
    brand_kit_id: Optional[str] = Form(None, description="Brand kit ID for alignment checking")
):
    """
    Critique a user-uploaded ad clip (image or video)
    
    Workflow:
    1. User uploads ad file + provides brand kit
    2. Descriptor Agent analyzes the ad (colors, text, objects, mood)
    3. Critique Agent evaluates across 4 dimensions
    
    Returns detailed critique with scores and recommendations.
    """
    try:
        logger.info(f"Critique uploaded ad: {file.filename}, brand_kit: {brand_kit_id}")
        
        # Validate file type
        if not (file.content_type.startswith('image/') or file.content_type.startswith('video/')):
            raise HTTPException(status_code=400, detail="File must be an image or video")
        
        # Save uploaded file
        file_ext = os.path.splitext(file.filename)[1]
        file_id = str(uuid.uuid4())
        file_path = os.path.join(settings.upload_dir, f"{file_id}{file_ext}")
        
        os.makedirs(settings.upload_dir, exist_ok=True)
        
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        logger.info(f"Saved uploaded file to: {file_path}")
        
        # Load brand kit if provided
        brand_kit = None
        if brand_kit_id:
            brand_kit = await brand_service.get_brand_kit(brand_kit_id)
            if not brand_kit:
                raise HTTPException(status_code=404, detail=f"Brand kit '{brand_kit_id}' not found")
            logger.info(f"Loaded brand kit: {brand_kit.brand_name}")
        
        # Step 1: Descriptor Agent - Analyze ad components
        logger.info("Step 1: Running Descriptor Agent...")
        description = descriptor_agent.describe_ad(file_path)
        logger.info(f"Description summary: {description.get('summary', '')[:100]}...")
        
        # Step 2: Critique Agent - Evaluate the ad
        logger.info("Step 2: Running Critique Agent...")
        critique = await critique_engine.critique_ad(
            image_path=file_path,
            brand_kit=brand_kit,
            ad_description=description.get("summary")
        )
        
        logger.info(f"Critique complete - Overall score: {critique.overall_score:.2f}")
        
        # Build response
        return {
            "success": True,
            "file_path": file_path,
            "filename": file.filename,
            "brand_kit": {
                "id": brand_kit.brand_id if brand_kit else None,
                "name": brand_kit.brand_name if brand_kit else None,
                "colors": brand_kit.primary_colors if brand_kit else None
            } if brand_kit else None,
            "description": description,
            "critique": {
                "brand_alignment_score": critique.brand_alignment.score,
                "visual_quality_score": critique.visual_quality.score,
                "message_clarity_score": critique.message_clarity.score,
                "safety_score": critique.safety_ethics.score,
                "overall_score": critique.overall_score,
                "brand_alignment": {
                    "score": critique.brand_alignment.score,
                    "level": critique.brand_alignment.level,
                    "feedback": critique.brand_alignment.feedback,
                    "issues": critique.brand_alignment.issues,
                    "suggestions": critique.brand_alignment.suggestions
                },
                "visual_quality": {
                    "score": critique.visual_quality.score,
                    "level": critique.visual_quality.level,
                    "feedback": critique.visual_quality.feedback,
                    "issues": critique.visual_quality.issues,
                    "suggestions": critique.visual_quality.suggestions
                },
                "message_clarity": {
                    "score": critique.message_clarity.score,
                    "level": critique.message_clarity.level,
                    "feedback": critique.message_clarity.feedback,
                    "issues": critique.message_clarity.issues,
                    "suggestions": critique.message_clarity.suggestions
                },
                "safety_ethics": {
                    "score": critique.safety_ethics.score,
                    "level": critique.safety_ethics.level,
                    "feedback": critique.safety_ethics.feedback,
                    "issues": critique.safety_ethics.issues,
                    "suggestions": critique.safety_ethics.suggestions
                },
                "needs_manual_review": critique.needs_manual_review if hasattr(critique, 'needs_manual_review') else False,
                "confidence_scores": critique.confidence_scores if hasattr(critique, 'confidence_scores') else {}
            },
            "workflow": {
                "step_1": "Descriptor Agent - Analyzed ad components",
                "step_2": "Critique Agent - Evaluated quality and alignment"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error critiquing uploaded ad: {str(e)}", exc_info=True)
        # Clean up file on error
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Critique failed: {str(e)}")
