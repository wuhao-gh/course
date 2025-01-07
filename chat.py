from datetime import datetime, timezone
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, List
from sqlmodel import Session, select

from model import BaseEntity
from auth import User, get_current_user
import json

from db import get_session, engine

router = APIRouter(prefix="/api/chat", tags=["即时通讯"])

class MessageBase(BaseEntity):
    """聊天消息"""
    content: str
    from_user_id: int
    to_user_id: int
    is_read: bool

class Message(MessageBase, table=True):
    """聊天消息"""

# 存储所有活跃的 WebSocket 连接
class ConnectionManager:
    def __init__(self):
        # 使用字典存储连接，key 是用户 ID，value 是 WebSocket 连接
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: dict, user_id: int):
        # 发送私人消息给指定用户
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_json(message)

manager = ConnectionManager()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(websocket, user_id)
    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
            message = json.loads(data)

            # 保存消息到数据库
            db_message = Message(
                content=message["content"],
                from_user_id=user_id,
                to_user_id=message["to_user"],
                is_read=False
            )
            session = Session(engine)
            session.add(db_message)
            session.commit()

            # 构造响应消息
            response = {
                "id": db_message.id,
                "from_user": user_id,
                "content": message["content"],
                "to_user": message["to_user"],
            }

            # 发送给目标用户
            if message["to_user"] in manager.active_connections:
                await manager.send_personal_message(response, message["to_user"])

    except WebSocketDisconnect:
        manager.disconnect(user_id)

@router.get("/messages/{user_id}")
async def get_chat_messages(
    user_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """获取与指定用户的聊天记录"""
    # 查询双方之间的所有消息
    messages = session.exec(
        select(Message).where(
            ((Message.from_user_id == current_user.id) & (Message.to_user_id == user_id)) |
            ((Message.from_user_id == user_id) & (Message.to_user_id == current_user.id))
        ).order_by(Message.created_at.asc())
    ).all()

    # 将未读消息标记为已读
    unread_messages = [
        msg for msg in messages
        if msg.to_user_id == current_user.id and not msg.is_read
    ]
    for msg in unread_messages:
        msg.is_read = True
    if unread_messages:
        # todo
        pass
        # session.commit()

    # 转换为响应格式
    return [
        {
            "id": msg.id,
            "content": msg.content,
            "from_user": msg.from_user_id,
            "to_user": msg.to_user_id,
            "is_read": msg.is_read
        }
        for msg in messages
    ]
