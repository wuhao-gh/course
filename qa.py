import logging

from fastapi import APIRouter

router = APIRouter(prefix="/api/qa", tags=["问答管理"])
logger = logging.getLogger(__name__)

