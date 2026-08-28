"""
用户反馈路由
"""
from fastapi import APIRouter

from ..models import FeedbackRequest, FeedbackResponse
from .. import storage

router = APIRouter()


@router.post("/api/feedback", response_model=FeedbackResponse)
async def feedback(req: FeedbackRequest):
    saved = storage.save_feedback(req.model_dump())
    return FeedbackResponse(ok=True, id=saved["id"])