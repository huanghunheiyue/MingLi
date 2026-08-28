"""
Pydantic 数据模型
"""
from typing import Literal, Optional
from pydantic import BaseModel, Field


# ----------------------- 请求 -----------------------
class GenerateRequest(BaseModel):
    content_type: Literal["couplet", "poem", "elegiac_prose", "meme"]
    subject: str = Field(..., description="主题/人物/事件名")
    # 挽联
    relation: Optional[str] = "后人"
    occasion: Optional[str] = "纪念日"
    # 怀古诗
    poem_type: Optional[str] = "七律"
    person: Optional[str] = ""
    # 祭文
    length: Optional[int] = 500
    author_role: Optional[str] = "后人"
    # 梗文
    tone: Optional[Literal["致敬", "惋惜", "反思", "戏谑"]] = "致敬"
    meme_length: Optional[Literal["短", "中"]] = "中"

    model_config = {"json_schema_extra": {
        "example": {
            "content_type": "couplet",
            "subject": "于谦",
            "relation": "后人",
            "occasion": "纪念日",
        }
    }}


class FeedbackRequest(BaseModel):
    history_id: Optional[str] = None
    content_type: Optional[str] = None
    subject: Optional[str] = None
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = ""


# ----------------------- 响应 -----------------------
class GenerateResponse(BaseModel):
    id: str
    content_type: str
    subject: str
    title: str
    body: str
    horizontal: Optional[str] = ""  # 仅挽联
    tags: list[str] = []
    sources: list[str] = []
    note: Optional[str] = ""
    elapsed_ms: int = 0
    created_at: str


class HistoryItem(BaseModel):
    id: str
    content_type: str
    subject: str
    title: str
    body: str
    tags: list[str] = []
    created_at: str


class FeedbackResponse(BaseModel):
    ok: bool = True
    id: str


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "1.0.0"
    provider: str