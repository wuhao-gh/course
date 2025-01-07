import logging

from fastapi import APIRouter

router = APIRouter(prefix="/api/stat", tags=["统计分析"])
logger = logging.getLogger(__name__)

@router.get("")
async def get_stat():
    return {}
