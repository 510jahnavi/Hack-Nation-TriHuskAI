"""
Multi-Agent Orchestrator - Manages the full workflow:
Generate → Describe → Critique → Refine → Final Output
"""
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import time
from datetime import datetime

from app.core.descriptor_agent import DescriptorAgent
from app.core.critique_engine import CritiqueEngine
from app.core.refinement_agent import RefinementAgent
from app.services.generation_service import GenerationService

logger = logging.getLogger(__name__)


class MultiAgentOrchestrator:
    """
    Orchestrates the multi-agent workflow for ad generation and refinement.
    
    Pipeline:
    1. Generate initial ad (Generator Agent)
    2. Describe ad components (Descriptor Agent)
    3. Critique the ad (Critic Agent)
    4. If score < threshold, refine and regenerate (Refinement Agent)
    5. Repeat until score is acceptable or max iterations reached
    """
    
    def __init__(
        self,
        gemini_api_key: Optional[str] = None,
        vertex_project_id: Optional[str] = None,
        vertex_location: Optional[str] = None,
        max_iterations: int = 3,
        score_threshold: float = 0.75
    ):
        """
        Initialize the orchestrator with all agents
        
        Args:
            gemini_api_key: Gemini API key for vision and text models
            vertex_project_id: Google Cloud project ID for Vertex AI
            vertex_location: Google Cloud location for Vertex AI
            max_iterations: Maximum refinement iterations
            score_threshold: Minimum acceptable overall score (0-1)
        """
        self.max_iterations = max_iterations
        self.score_threshold = score_threshold
        
        # Initialize agents
        self.descriptor = DescriptorAgent(api_key=gemini_api_key)
        self.critic = CritiqueEngine()  # Reads from settings internally
        self.refinement = RefinementAgent(api_key=gemini_api_key)
        self.generator = GenerationService()  # Reads from settings internally
        
        logger.info(f"Multi-Agent Orchestrator initialized (max_iter={max_iterations}, threshold={score_threshold})")
    
    async def generate_and_refine(
        self,
        prompt: str,
        brand_kit_id: Optional[str] = None,
        aspect_ratio: str = "1:1",
        include_logo: bool = True,
        brand_kit_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Run the full multi-agent pipeline
        
        Args:
            prompt: Initial user prompt for ad generation
            brand_kit_id: Brand kit identifier
            aspect_ratio: Image aspect ratio
            include_logo: Whether to include brand logo
            brand_kit_data: Optional brand kit data dictionary
            
        Returns:
            Dictionary with complete workflow results including all iterations
        """
        workflow_start = time.time()
        iterations = []
        
        logger.info(f"Starting multi-agent workflow for prompt: '{prompt[:50]}...'")
        
        current_prompt = prompt
        best_ad = None
        best_score = 0.0
        
        for iteration in range(1, self.max_iterations + 1):
            logger.info(f"=== Iteration {iteration}/{self.max_iterations} ===")
            iteration_start = time.time()
            
            iteration_result = {
                "iteration": iteration,
                "prompt": current_prompt,
                "timestamp": datetime.now().isoformat()
            }
            
            # Step 1: Generate Ad
            logger.info(f"[{iteration}] Generating ad...")
            try:
                # Create GenerateAdRequest object
                from app.models.schemas import GenerateAdRequest
                gen_request = GenerateAdRequest(
                    brand_id=brand_kit_id,
                    product_name=current_prompt.split('\n')[0] if '\n' in current_prompt else "Product",
                    product_description=current_prompt,
                    tagline="",
                    style="modern",
                    media_type="image"
                )
                
                gen_result = await self.generator.generate_ad(gen_request)
                iteration_result["generation"] = {
                    "success": gen_result.get("success", False),
                    "image_path": gen_result.get("image_path"),
                    "error": gen_result.get("error")
                }
                
                if not gen_result.get("success"):
                    logger.error(f"[{iteration}] Generation failed: {gen_result.get('error')}")
                    iteration_result["status"] = "generation_failed"
                    iterations.append(iteration_result)
                    break
                
                ad_path = gen_result["image_path"]
                
            except Exception as e:
                logger.error(f"[{iteration}] Generation error: {str(e)}")
                iteration_result["generation"] = {"success": False, "error": str(e)}
                iteration_result["status"] = "generation_error"
                iterations.append(iteration_result)
                break
            
            # Step 2: Describe Ad
            logger.info(f"[{iteration}] Describing ad components...")
            try:
                description = self.descriptor.describe_ad(ad_path)
                iteration_result["description"] = description
            except Exception as e:
                logger.error(f"[{iteration}] Description error: {str(e)}")
                iteration_result["description"] = {"error": str(e)}
            
            # Step 3: Critique Ad
            logger.info(f"[{iteration}] Critiquing ad...")
            try:
                critique = await self.critic.critique_ad(
                    image_path=ad_path,
                    brand_kit=brand_kit_data
                )
                iteration_result["critique"] = critique
                
                overall_score = critique.get("overall_score", 0.0)
                iteration_result["overall_score"] = overall_score
                
                logger.info(f"[{iteration}] Score: {overall_score:.2f} (threshold: {self.score_threshold})")
                
                # Track best ad
                if overall_score > best_score:
                    best_score = overall_score
                    best_ad = {
                        "iteration": iteration,
                        "image_path": ad_path,
                        "score": overall_score,
                        "critique": critique,
                        "description": description,
                        "prompt": current_prompt
                    }
                
            except Exception as e:
                logger.error(f"[{iteration}] Critique error: {str(e)}")
                iteration_result["critique"] = {"error": str(e)}
                overall_score = 0.0
                iteration_result["overall_score"] = overall_score
            
            # Check if we've met the threshold
            if overall_score >= self.score_threshold:
                logger.info(f"[{iteration}] ✅ Score threshold met! ({overall_score:.2f} >= {self.score_threshold})")
                iteration_result["status"] = "success"
                iteration_result["reason"] = "threshold_met"
                iterations.append(iteration_result)
                break
            
            # Step 4: Refine (if not last iteration)
            if iteration < self.max_iterations:
                logger.info(f"[{iteration}] Score below threshold, refining...")
                try:
                    refinement = self.refinement.generate_improved_prompt(
                        original_prompt=current_prompt,
                        critique_result=critique,
                        description=description,
                        brand_kit=brand_kit_data,
                        iteration=iteration
                    )
                    iteration_result["refinement"] = refinement
                    
                    # Update prompt for next iteration
                    current_prompt = refinement.get("improved_prompt", current_prompt)
                    logger.info(f"[{iteration}] Refined prompt: '{current_prompt[:50]}...'")
                    
                except Exception as e:
                    logger.error(f"[{iteration}] Refinement error: {str(e)}")
                    iteration_result["refinement"] = {"error": str(e)}
            
            iteration_result["duration_seconds"] = time.time() - iteration_start
            iteration_result["status"] = "refined" if iteration < self.max_iterations else "max_iterations"
            iterations.append(iteration_result)
        
        # Build final result
        workflow_duration = time.time() - workflow_start
        
        result = {
            "success": best_ad is not None,
            "iterations_count": len(iterations),
            "iterations": iterations,
            "best_ad": best_ad,
            "final_score": best_score,
            "threshold_met": best_score >= self.score_threshold,
            "workflow_duration_seconds": workflow_duration,
            "timestamp": datetime.now().isoformat(),
            "config": {
                "max_iterations": self.max_iterations,
                "score_threshold": self.score_threshold,
                "initial_prompt": prompt
            }
        }
        
        logger.info(f"Multi-agent workflow complete: {len(iterations)} iterations, best score: {best_score:.2f}")
        
        return result
    
    def get_iteration_summary(self, workflow_result: Dict[str, Any]) -> str:
        """Generate a human-readable summary of the workflow"""
        
        iterations = workflow_result.get("iterations", [])
        best_ad = workflow_result.get("best_ad")
        
        lines = [
            "=== Multi-Agent Workflow Summary ===",
            f"Total Iterations: {len(iterations)}",
            f"Best Score: {workflow_result.get('final_score', 0):.2f}",
            f"Threshold Met: {'Yes' if workflow_result.get('threshold_met') else 'No'}",
            f"Duration: {workflow_result.get('workflow_duration_seconds', 0):.1f}s",
            "",
            "Iteration Breakdown:"
        ]
        
        for iter_data in iterations:
            iter_num = iter_data.get("iteration", 0)
            score = iter_data.get("overall_score", 0)
            status = iter_data.get("status", "unknown")
            
            lines.append(f"  [{iter_num}] Score: {score:.2f} - Status: {status}")
            
            if iter_data.get("refinement"):
                changes = iter_data["refinement"].get("changes_made", [])
                if changes:
                    lines.append(f"      Changes: {', '.join(changes[:3])}")
        
        if best_ad:
            lines.append("")
            lines.append(f"Best Ad: Iteration {best_ad.get('iteration')} ({best_ad.get('score'):.2f})")
            lines.append(f"Path: {best_ad.get('image_path')}")
        
        return "\n".join(lines)
