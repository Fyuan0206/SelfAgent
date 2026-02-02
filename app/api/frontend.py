"""
Frontend API Routes
API endpoints for the web frontend
"""

from typing import Optional, List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from loguru import logger
import json
import os
from datetime import datetime

from ..core.agent import SelfAgent
from ..models.data_models import UserInput


router = APIRouter(prefix="/api/frontend", tags=["frontend"])

# Pydantic models
class ChatMessage(BaseModel):
    user_id: str
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
    current_emotion: str
    emotion_score: float
    recent_trends: List[dict]
    recommendations: List[str]


# Initialize agent (singleton)
_agent_instance = None


def get_agent():
    """Get or create agent instance"""
    global _agent_instance
    if _agent_instance is None:
        model_name = os.getenv("MODEL_NAME", "deepseek-chat")
        _agent_instance = SelfAgent(model_type=model_name)
        logger.info("Frontend API: Agent initialized")
    return _agent_instance


# ==================== Chat API ====================

@router.post("/chat", response_model=ChatResponse)
async def chat(message: ChatMessage) -> ChatResponse:
    """
    Process chat message from frontend

    - **user_id**: User identifier
    - **text**: Message text
    - **timestamp**: Optional timestamp (defaults to now)
    """
    try:
        logger.info(f"Chat request from user={message.user_id}: {message.text[:50]}...")

        agent = get_agent()

        # Create user input
        user_input = UserInput(
            user_id=message.user_id,
            text=message.text
        )

        # Process interaction
        response_text = agent.process_interaction(user_input)

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
    user_id: str = Form(...),
    text: str = Form(default=""),
    file: UploadFile = File(...),
    file_type: str = Form(...)
) -> ChatResponse:
    """
    Process multimodal chat message (audio/image)

    - **user_id**: User identifier
    - **text**: Optional text description
    - **file**: Audio or image file
    - **file_type**: Type of file ('audio' or 'image')
    """
    try:
        logger.info(f"Multimodal chat from user={user_id}, type={file_type}, file={file.filename}")

        agent = get_agent()

        # Save file temporarily
        temp_dir = "temp"
        os.makedirs(temp_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = f"{temp_dir}/{user_id}_{timestamp}_{file.filename}"
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Create user input with file path
        user_input = UserInput(
            user_id=user_id,
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
async def get_emotion_report(user_id: str) -> EmotionReport:
    """
    Get user's emotion report and trends

    - **user_id**: User identifier
    """
    try:
        logger.info(f"Emotion report request for user={user_id}")

        agent = get_agent()

        # Get emotion profile from agent tools
        # TODO: Integrate with UserProfileTool
        # For now, return mock data

        return EmotionReport(
            user_id=user_id,
            current_emotion="平静",
            emotion_score=75.0,
            recent_trends=[
                {"date": "2025-01-20", "emotion": "平静", "score": 72},
                {"date": "2025-01-21", "emotion": "焦虑", "score": 58},
                {"date": "2025-01-22", "emotion": "平静", "score": 68},
                {"date": "2025-01-23", "emotion": "开心", "score": 82},
                {"date": "2025-01-24", "emotion": "平静", "score": 75},
            ],
            recommendations=[
                "继续保持良好的情绪状态",
                "尝试每日正念冥想",
                "保持规律的作息时间"
            ]
        )

    except Exception as e:
        logger.error(f"Emotion report error: {e}")
        raise HTTPException(status_code=500, detail=f"获取情绪报告时出错: {str(e)}")


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
