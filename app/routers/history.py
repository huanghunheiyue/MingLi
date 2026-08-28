"""
历史记录路由
"""
from fastapi import APIRouter, HTTPException

from .. import storage

router = APIRouter()


@router.get("/api/history")
async def list_history(limit: int = 20):
    items = storage.list_history(limit=limit)
    return {"items": items, "total": len(items)}


@router.get("/api/history/{hid}")
async def get_history(hid: str):
    item = storage.get_history(hid)
    if not item:
        raise HTTPException(404, "记录不存在")
    return item