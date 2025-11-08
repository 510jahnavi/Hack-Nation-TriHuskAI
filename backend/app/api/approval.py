"""
API routes for human approval/rejection workflow
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import json
import os

router = APIRouter()


class ApprovalRequest(BaseModel):
    ad_id: str
    decision: str  # "approve", "reject", "request_revision"
    feedback: Optional[str] = None
    approved_by: Optional[str] = None


class ApprovalResponse(BaseModel):
    success: bool
    ad_id: str
    status: str
    timestamp: str
    message: str


# Simple file-based storage for demo
APPROVALS_DIR = "approvals"
os.makedirs(APPROVALS_DIR, exist_ok=True)


@router.post("/approve", response_model=ApprovalResponse)
async def approve_ad(request: ApprovalRequest):
    """
    Approve an ad for deployment
    
    Workflow:
    - approve: Mark as ready for social media posting
    - reject: Mark as rejected with reason
    - request_revision: Send back to refinement with feedback
    """
    
    if request.decision not in ["approve", "reject", "request_revision"]:
        raise HTTPException(
            status_code=400,
            detail="Decision must be 'approve', 'reject', or 'request_revision'"
        )
    
    # Create approval record
    approval_data = {
        "ad_id": request.ad_id,
        "decision": request.decision,
        "feedback": request.feedback,
        "approved_by": request.approved_by or "demo_user",
        "timestamp": datetime.now().isoformat(),
        "status": _get_status(request.decision)
    }
    
    # Save to file
    approval_path = os.path.join(APPROVALS_DIR, f"{request.ad_id}.json")
    with open(approval_path, 'w') as f:
        json.dump(approval_data, f, indent=2)
    
    message = _get_message(request.decision)
    
    return ApprovalResponse(
        success=True,
        ad_id=request.ad_id,
        status=approval_data["status"],
        timestamp=approval_data["timestamp"],
        message=message
    )


@router.get("/approval-status/{ad_id}")
async def get_approval_status(ad_id: str):
    """Get the approval status of an ad"""
    
    approval_path = os.path.join(APPROVALS_DIR, f"{ad_id}.json")
    
    if not os.path.exists(approval_path):
        return {
            "ad_id": ad_id,
            "status": "pending",
            "message": "No approval decision yet"
        }
    
    with open(approval_path, 'r') as f:
        approval_data = json.load(f)
    
    return approval_data


@router.get("/approved-ads")
async def list_approved_ads():
    """List all approved ads ready for deployment"""
    
    approved_ads = []
    
    for filename in os.listdir(APPROVALS_DIR):
        if filename.endswith('.json'):
            with open(os.path.join(APPROVALS_DIR, filename), 'r') as f:
                data = json.load(f)
                if data.get('decision') == 'approve':
                    approved_ads.append(data)
    
    return {
        "total_approved": len(approved_ads),
        "approved_ads": approved_ads
    }


def _get_status(decision: str) -> str:
    """Map decision to status"""
    status_map = {
        "approve": "approved_for_deployment",
        "reject": "rejected",
        "request_revision": "needs_revision"
    }
    return status_map.get(decision, "unknown")


def _get_message(decision: str) -> str:
    """Get user-friendly message"""
    messages = {
        "approve": "✅ Ad approved and ready for deployment to social media",
        "reject": "❌ Ad rejected - will not be deployed",
        "request_revision": "🔄 Revision requested - ad sent back for improvements"
    }
    return messages.get(decision, "Decision recorded")
