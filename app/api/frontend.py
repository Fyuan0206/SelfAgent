"""
Frontend API Routes
API endpoints for the web frontend
"""

from typing import Optional, List, Dict
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pydantic import BaseModel
from loguru import logger
import json
import os
from datetime import datetime

from ..core.agent import SelfAgent
from ..models.data_models import UserInput
from ..models.user_models import ChatMessage as DBChatMessage
from ..core.database import get_db
from ..core.quota_middleware import check_chat_quota, check_multimodal_quota
from ..core.auth import get_current_user, User
from ..core.memory_manager import MemoryManager
from ..services.profile.emotion_profile import EmotionProfileManager


router = APIRouter(prefix="/api/frontend", tags=["frontend"])

# Pydantic models
class ChatMessage(BaseModel):
    text: str
    timestamp: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    emotion_detected: Optional[str] = None
    risk_level: Optional[str] = None
    dbt_skills: Optional[List[str]] = None
    is_crisis: bool = False


class EmotionReport(BaseModel):
    user_id: str
    current_emotion: Optional[str]
    emotion_score: float
    recent_trends: List[dict]
    recommendations: List[str]

class HistoryPayload(BaseModel):
    messages: List[Dict]


# Initialize agent (singleton)
_agent_instance = None
_memory_manager = MemoryManager(persist_path="./data/chroma_db")
_profile_manager = EmotionProfileManager(config={})  # Initialize profile manager
_conversation_buffers: Dict[str, List[Dict]] = {}


def get_agent():
    """Get or create agent instance"""
    global _agent_instance
    if _agent_instance is None:
        model_name = os.getenv("MODEL_NAME", "deepseek-chat")
        _agent_instance = SelfAgent(model_type=model_name)
        logger.info("Frontend API: Agent initialized")
    return _agent_instance


class HistoryMessage(BaseModel):
    id: int
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("/history", response_model=List[HistoryMessage])
async def get_history(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get chat history for current user
    """
    messages = db.query(DBChatMessage)\
        .filter(DBChatMessage.user_id == current_user.id)\
        .order_by(desc(DBChatMessage.created_at))\
        .limit(limit)\
        .offset(offset)\
        .all()
    
    # Reverse to show oldest first in frontend (or keep desc and let frontend handle)
    # Usually chat history API returns latest N messages. 
    # Frontend usually prepends them.
    return messages


# ==================== Chat API ====================

@router.post("/chat", response_model=ChatResponse)
async def chat(
    message: ChatMessage,
    current_user: User = Depends(check_chat_quota),
    db: Session = Depends(get_db)
) -> ChatResponse:
    """
    Process chat message from frontend
    需要认证，消耗 1 额度

    - **text**: Message text
    - **timestamp**: Optional timestamp (defaults to now)
    """
    try:
        logger.info(f"Chat request from user={current_user.id}: {message.text[:50]}...")

        # Save User Message to DB
        user_msg = DBChatMessage(
            user_id=current_user.id,
            role="user",
            content=message.text
        )
        db.add(user_msg)
        db.commit()

        agent = get_agent()

        # Create user input
        user_input = UserInput(
            user_id=str(current_user.id),
            text=message.text
        )

        # Process interaction
        response_text = agent.process_interaction(user_input)

        # Save Assistant Message to DB
        ai_msg = DBChatMessage(
            user_id=current_user.id,
            role="assistant",
            content=response_text
        )
        db.add(ai_msg)
        db.commit()

        buf_key = str(current_user.id)
        buf = _conversation_buffers.get(buf_key, [])
        buf.append({"role": "user", "content": message.text, "ts": datetime.now().isoformat()})
        buf.append({"role": "assistant", "content": response_text, "ts": datetime.now().isoformat()})
        _conversation_buffers[buf_key] = buf
        if len(buf) >= 12:
            summary = await _memory_manager.compress_and_archive(buf_key, buf, agent_instance=agent)
            _conversation_buffers[buf_key] = buf[-2:]

        # TODO: Extract emotion and risk level from agent context
        # For now, returning basic response
        return ChatResponse(
            response=response_text,
            emotion_detected=None,
            risk_level=None,
            dbt_skills=None,
            is_crisis=False
        )

    except Exception as e:
        logger.error(f"Chat processing error: {e}")
        raise HTTPException(status_code=500, detail=f"处理聊天消息时出错: {str(e)}")


@router.post("/chat/multimodal")
async def chat_multimodal(
    text: str = Form(default=""),
    file: UploadFile = File(...),
    file_type: str = Form(...),
    current_user: User = Depends(check_multimodal_quota)
) -> ChatResponse:
    """
    Process multimodal chat message (audio/image)
    需要认证，消耗 2 额度

    - **text**: Optional text description
    - **file**: Audio or image file
    - **file_type**: Type of file ('audio' or 'image')
    """
    try:
        logger.info(f"Multimodal chat from user={current_user.id}, type={file_type}, file={file.filename}")

        agent = get_agent()

        # Save file temporarily
        temp_dir = "temp"
        os.makedirs(temp_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = f"{temp_dir}/{current_user.id}_{timestamp}_{file.filename}"
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Create user input with file path
        user_input = UserInput(
            user_id=str(current_user.id),
            text=text or f"发送了一个{file_type}文件"
        )
        # Add file info to metadata
        user_input.metadata = {
            "file_path": file_path,
            "file_type": file_type,
            "original_filename": file.filename
        }

        # Process interaction
        response_text = agent.process_interaction(user_input)

        buf_key = str(current_user.id)
        buf = _conversation_buffers.get(buf_key, [])
        buf.append({"role": "user", "content": user_input.text, "ts": datetime.now().isoformat()})
        buf.append({"role": "assistant", "content": response_text, "ts": datetime.now().isoformat()})
        _conversation_buffers[buf_key] = buf
        if len(buf) >= 12:
            summary = await _memory_manager.compress_and_archive(buf_key, buf, agent_instance=agent)
            _conversation_buffers[buf_key] = buf[-2:]

        # Clean up temp file
        try:
            os.remove(file_path)
        except:
            pass

        return ChatResponse(
            response=response_text,
            emotion_detected=None,
            risk_level=None,
            dbt_skills=None,
            is_crisis=False
        )

    except Exception as e:
        logger.error(f"Multimodal chat error: {e}")
        raise HTTPException(status_code=500, detail=f"处理多媒体消息时出错: {str(e)}")


# ==================== Emotion Report API ====================

@router.get("/emotion-report/{user_id}", response_model=EmotionReport)
async def get_emotion_report(
    user_id: str,
    current_user: User = Depends(get_current_user)
) -> EmotionReport:
    """
    Get user's emotion report and trends
    需要认证
    """
    try:
        # 验证用户只能查看自己的报告（管理员除外）
        if current_user.role.value != "admin" and str(current_user.id) != user_id:
            raise HTTPException(status_code=403, detail="无权访问其他用户的报告")

        logger.info(f"Emotion report request for user={user_id}")

        # 加载用户画像
        profile = _profile_manager.load_profile(user_id)
        
        # 如果没有画像或快照，返回空数据
        if not profile or not profile.snapshots:
            return EmotionReport(
                user_id=user_id,
                current_emotion=None,
                emotion_score=0.0,
                recent_trends=[],
                recommendations=[]
            )

        # 获取最新情绪
        latest = profile.snapshots[-1]
        # 找出得分最高的情绪
        current_emotion = max(latest.emotions.items(), key=lambda x: x[1])[0] if latest.emotions else "未知"
        
        # 构建最近趋势（取最后 5 次）
        recent_trends = []
        for s in profile.snapshots[-5:]:
            top_emotion = max(s.emotions.items(), key=lambda x: x[1])[0] if s.emotions else "未知"
            # 将 timestamp 转换为 readable format
            dt = datetime.fromtimestamp(s.timestamp)
            date_str = dt.strftime("%Y-%m-%d %H:%M")
            
            recent_trends.append({
                "date": date_str,
                "emotion": top_emotion,
                "score": int(latest.arousal * 100)  # 使用唤醒度作为分数示例
            })
            
        # 生成简单建议
        recommendations = ["继续保持觉察"]
        if latest.risk_level != "LOW":
            recommendations.append("注意情绪波动，必要时寻求帮助")

        return EmotionReport(
            user_id=user_id,
            current_emotion=current_emotion,
            emotion_score=latest.arousal * 100,
            recent_trends=recent_trends,
            recommendations=recommendations
        )

    except Exception as e:
        logger.error(f"Emotion report error: {e}")
        # 出错时也返回空数据，避免前端崩溃
        return EmotionReport(
            user_id=user_id,
            current_emotion=None,
            emotion_score=0.0,
            recent_trends=[],
            recommendations=[]
        )


# ==================== Crisis Resources API ====================

@router.get("/crisis-resources")
async def get_crisis_resources():
    """Get crisis intervention resources"""
    return {
        "hotlines": [
            {
                "name": "全国心理援助热线",
                "phone": "400-161-9995",
                "available": "24小时"
            },
            {
                "name": "北京危机干预热线",
                "phone": "010-82951332",
                "available": "24小时"
            },
            {
                "name": "希望24热线",
                "phone": "400-161-9995",
                "available": "24小时"
            },
            {
                "name": "上海心理热线",
                "phone": "021-12320-5",
                "available": "24小时"
            },
            {
                "name": "广州心理热线",
                "phone": "020-81899120",
                "available": "24小时"
            }
        ],
        "reminders": [
            "您不是一个人",
            "这种感觉会过去",
            "请给自己一个机会",
            "专业帮助可以带来改变"
        ]
    }


# ==================== DBT Skills API (Frontend Wrapper) ====================

@router.get("/skills")
async def get_dbt_skills():
    """Get all DBT skills for frontend display"""
    # This would call the DBT module API
    # For now, return mock data
    return {
        "modules": [
            {
                "name": "痛苦耐受",
                "name_en": "Distress Tolerance",
                "skills": ["TIPP", "STOP", "ACCEPTS", "自我安抚"]
            },
            {
                "name": "情绪调节",
                "name_en": "Emotion Regulation",
                "skills": ["PLEASE", "反向行动", "检验事实"]
            },
            {
                "name": "人际效能",
                "name_en": "Interpersonal Effectiveness",
                "skills": ["DEAR MAN", "GIVE", "FAST"]
            },
            {
                "name": "正念",
                "name_en": "Mindfulness",
                "skills": ["观察", "投入", "非评判"]
            }
        ]
    }


# ==================== Health Check ====================

@router.get("/health")
async def health_check():
    """Frontend API health check"""
    return {
        "status": "ok",
        "service": "selfagent-frontend-api",
        "version": "1.0.0",
        "agent_initialized": _agent_instance is not None
    }

@router.post("/memory/compress")
async def compress_memory(
    payload: HistoryPayload,
    current_user: User = Depends(get_current_user)
):
    try:
        agent = get_agent()
        user_id = str(current_user.id)
        summary = await _memory_manager.compress_and_archive(user_id, payload.messages, agent_instance=agent)
        return {"summary": summary or ""}
    except Exception as e:
        logger.error(f"Compress memory error: {e}")
        raise HTTPException(status_code=500, detail="摘要压缩失败")
