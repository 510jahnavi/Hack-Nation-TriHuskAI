"""
Refinement Agent - Generates improved ad prompts based on critique feedback
"""
import google.generativeai as genai
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class RefinementAgent:
    """
    Takes critique feedback and generates improved prompts for ad regeneration.
    Uses AI to translate critique scores and feedback into actionable improvements.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
        else:
            self.model = None
            logger.warning("Refinement Agent initialized without Gemini API key - using fallback mode")
    
    def generate_improved_prompt(
        self,
        original_prompt: str,
        critique_result: Dict[str, Any],
        description: Dict[str, Any],
        brand_kit: Optional[Dict[str, Any]] = None,
        iteration: int = 1
    ) -> Dict[str, Any]:
        """
        Generate an improved ad generation prompt based on critique feedback
        
        Args:
            original_prompt: The original user prompt
            critique_result: The critique scores and feedback
            description: The descriptor agent's analysis
            brand_kit: Optional brand kit information
            iteration: Current iteration number
            
        Returns:
            Dictionary with improved prompt and refinement strategy
        """
        if not self.model:
            return self._fallback_refinement(original_prompt, critique_result)
        
        try:
            # Create refinement prompt
            refinement_prompt = self._create_refinement_prompt(
                original_prompt,
                critique_result,
                description,
                brand_kit,
                iteration
            )
            
            # Generate improved prompt
            response = self.model.generate_content(refinement_prompt)
            
            # Parse response
            result = self._parse_refinement(response.text, original_prompt)
            
            logger.info(f"Generated refinement for iteration {iteration}")
            return result
            
        except Exception as e:
            logger.error(f"Error generating refinement: {str(e)}")
            return self._fallback_refinement(original_prompt, critique_result)
    
    def _create_refinement_prompt(
        self,
        original_prompt: str,
        critique_result: Dict[str, Any],
        description: Dict[str, Any],
        brand_kit: Optional[Dict[str, Any]],
        iteration: int
    ) -> str:
        """Create detailed prompt for generating refinement"""
        
        # Extract critique scores
        scores = critique_result.get("scores", {})
        feedback = critique_result.get("detailed_feedback", {})
        issues = critique_result.get("issues", [])
        
        # Build brand context
        brand_context = ""
        if brand_kit:
            brand_context = f"""
**Brand Guidelines:**
- Brand Name: {brand_kit.get('brand_name', 'Unknown')}
- Primary Colors: {', '.join(brand_kit.get('primary_colors', []))}
- Brand Voice: {brand_kit.get('brand_voice', 'Unknown')}
- Target Audience: {brand_kit.get('target_audience', 'Unknown')}
"""
        
        return f"""You are an expert Ad Refinement Specialist. Your job is to improve ad generation prompts based on critique feedback.

**Current Iteration:** {iteration}

**Original Prompt:**
{original_prompt}

**Critique Scores:**
- Brand Alignment: {scores.get('brand_alignment', 0):.2f}/1.0
- Visual Quality: {scores.get('visual_quality', 0):.2f}/1.0
- Message Clarity: {scores.get('message_clarity', 0):.2f}/1.0
- Safety Score: {scores.get('safety', 0):.2f}/1.0
- Overall Score: {critique_result.get('overall_score', 0):.2f}/1.0

**Identified Issues:**
{chr(10).join(f"- {issue}" for issue in issues) if issues else "None"}

**Detailed Feedback:**
{chr(10).join(f"- {category}: {fb}" for category, fb in feedback.items()) if feedback else "No detailed feedback"}

**Current Ad Description:**
{self._format_description(description)}

{brand_context}

**Your Task:**
Based on the critique, generate an IMPROVED prompt that will create a better ad. Focus on addressing the lowest-scoring areas.

**Refinement Strategy:**
1. If brand_alignment is low: Add specific brand colors, logo placement, brand voice keywords
2. If visual_quality is low: Add composition keywords (rule of thirds, sharp focus, professional lighting)
3. If message_clarity is low: Make product/CTA more explicit, simplify messaging
4. If safety is low: Remove potentially problematic elements, add safety keywords

**Output Format (JSON only):**
{{
  "improved_prompt": "Your improved detailed prompt here",
  "changes_made": ["change 1", "change 2", ...],
  "focus_areas": ["area 1", "area 2", ...],
  "expected_improvements": {{
    "brand_alignment": "what should improve",
    "visual_quality": "what should improve",
    "message_clarity": "what should improve"
  }},
  "iteration_strategy": "brief explanation of this iteration's focus"
}}

Return ONLY the JSON object."""
    
    def _format_description(self, description: Dict[str, Any]) -> str:
        """Format description for prompt"""
        if description.get("source") == "fallback":
            return "Limited description available (API key required for detailed analysis)"
        
        lines = []
        if "visual_elements" in description:
            ve = description["visual_elements"]
            lines.append(f"Colors: {', '.join(ve.get('colors', []))}")
            lines.append(f"Style: {ve.get('style', 'unknown')}")
            lines.append(f"Quality: {ve.get('quality', 'unknown')}")
        
        if "text_content" in description:
            tc = description["text_content"]
            if tc.get("headline"):
                lines.append(f"Headline: {tc['headline']}")
            if tc.get("cta"):
                lines.append(f"CTA: {tc['cta']}")
        
        return "\n".join(lines) if lines else "No detailed description available"
    
    def _parse_refinement(self, response_text: str, original_prompt: str) -> Dict[str, Any]:
        """Parse refinement response"""
        import json
        
        try:
            # Remove markdown code blocks
            clean_text = response_text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.startswith("```"):
                clean_text = clean_text[3:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            
            refinement = json.loads(clean_text.strip())
            
            # Add metadata
            refinement["source"] = "gemini_refinement"
            refinement["original_prompt"] = original_prompt
            
            return refinement
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse refinement JSON: {e}")
            # Extract improved prompt from text
            return {
                "source": "gemini_refinement_raw",
                "improved_prompt": response_text,
                "changes_made": ["Unable to parse structured changes"],
                "focus_areas": ["general_improvement"],
                "original_prompt": original_prompt,
                "parsing_error": str(e)
            }
    
    def _fallback_refinement(
        self,
        original_prompt: str,
        critique_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fallback refinement using rule-based improvements"""
        
        scores = critique_result.get("scores", {})
        issues = critique_result.get("issues", [])
        
        improvements = []
        improved_prompt = original_prompt
        
        # Add improvements based on low scores
        if scores.get("brand_alignment", 1.0) < 0.7:
            improvements.append("professional branding")
            improved_prompt += ", with clear brand colors and logo placement"
        
        if scores.get("visual_quality", 1.0) < 0.7:
            improvements.append("high visual quality")
            improved_prompt += ", sharp focus, professional photography, rule of thirds composition"
        
        if scores.get("message_clarity", 1.0) < 0.7:
            improvements.append("clear messaging")
            improved_prompt += ", with bold clear text and obvious call-to-action"
        
        if scores.get("safety", 1.0) < 0.9:
            improvements.append("safe content")
            improved_prompt += ", safe for all audiences, no controversial elements"
        
        return {
            "source": "fallback_rules",
            "improved_prompt": improved_prompt,
            "changes_made": improvements,
            "focus_areas": [k for k, v in scores.items() if v < 0.7],
            "expected_improvements": {
                "note": "Rule-based refinement - API key required for AI-powered improvements"
            },
            "iteration_strategy": "Adding safety and quality keywords to original prompt",
            "original_prompt": original_prompt
        }
