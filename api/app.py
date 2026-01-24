"""
FastAPI应用
提供RESTful API接口
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
import uvicorn
from loguru import logger
import sys

# 添加项目根目录到路径
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.emotion_engine import EmotionRecognitionEngine


# Pydantic模型
class AnalyzeRequest(BaseModel):
    """情绪分析请求"""
    text: str = Field(..., description="输入文本", min_length=1)
    user_id: str = Field(..., description="用户ID")
    context: str = Field("", description="对话上下文")


class AnalyzeResponse(BaseModel):
    """情绪分析响应"""
    user_id: str
    timestamp: str
    emotion_features: Dict
    routing_decision: Dict
    intervention_assessment: Dict
    context_analysis: Dict
    recommendations: List[str]


class ProfileResponse(BaseModel):
    """用户画像响应"""
    user_id: str
    summary: str
    self_agent_params: Dict
    pathological_indicators: List[str]


# 创建FastAPI应用
app = FastAPI(
    title="Emotion Recognition API",
    description="多模态情绪识别与DBT干预系统",
    version="1.0.0"
)

# 初始化引擎
engine = None


@app.on_event("startup")
async def startup_event():
    """应用启动时初始化引擎"""
    global engine
    try:
        engine = EmotionRecognitionEngine(config_path="config.yaml")
        logger.info("引擎初始化成功")
    except Exception as e:
        logger.error(f"引擎初始化失败: {e}")
        raise


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "Emotion Recognition API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "engine_loaded": engine is not None,
        "model_type": "remote_api" if engine and engine.extractor.api_key else "local_rules"
    }


@app.post("/api/v1/analyze", response_model=AnalyzeResponse)
async def analyze_emotion(request: AnalyzeRequest):
    """
    分析文本情绪

    Args:
        request: 分析请求

    Returns:
        分析结果
    """
    if engine is None:
        raise HTTPException(status_code=503, detail="引擎未初始化")

    try:
        result = engine.analyze(
            text=request.text,
            user_id=request.user_id,
            context=request.context
        )
        return result

    except Exception as e:
        logger.error(f"分析失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/analyze/multimodal")
async def analyze_multimodal_emotion(
    text: str = Form(...),
    user_id: str = Form(...),
    context: str = Form(""),
    audio: Optional[UploadFile] = File(None),
    video: Optional[UploadFile] = File(None)
):
    """
    多模态情绪分析（支持音频和视频）

    Args:
        text: 输入文本
        user_id: 用户ID
        context: 对话上下文
        audio: 音频文件（可选）
        video: 视频文件（可选）

    Returns:
        分析结果
    """
    if engine is None:
        raise HTTPException(status_code=503, detail="引擎未初始化")

    try:
        # 保存上传的文件
        audio_path = None
        video_path = None

        if audio:
            audio_path = f"temp/audio_{user_id}_{audio.filename}"
            with open(audio_path, "wb") as f:
                f.write(await audio.read())

        if video:
            video_path = f"temp/video_{user_id}_{video.filename}"
            with open(video_path, "wb") as f:
                f.write(await video.read())

        # 执行分析
        result = engine.analyze(
            text=text,
            user_id=user_id,
            audio_path=audio_path,
            video_path=video_path,
            context=context
        )

        return result

    except Exception as e:
        logger.error(f"多模态分析失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/profile/{user_id}", response_model=ProfileResponse)
async def get_user_profile(user_id: str):
    """
    获取用户画像

    Args:
        user_id: 用户ID

    Returns:
        用户画像
    """
    if engine is None:
        raise HTTPException(status_code=503, detail="引擎未初始化")

    try:
        profile_data = engine.get_profile(user_id)

        if profile_data is None:
            raise HTTPException(status_code=404, detail="用户画像不存在")

        return ProfileResponse(
            user_id=user_id,
            summary=profile_data['summary'],
            self_agent_params=profile_data['self_agent_params'],
            pathological_indicators=profile_data['pathological_indicators']
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取画像失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/stats")
async def get_system_stats():
    """
    获取系统统计信息

    Returns:
        系统统计
    """
    if engine is None:
        raise HTTPException(status_code=503, detail="引擎未初始化")

    try:
        stats = engine.get_system_stats()
        return stats

    except Exception as e:
        logger.error(f"获取统计失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/reset/{user_id}")
async def reset_user_data(user_id: str):
    """
    重置用户数据（仅用于测试）

    Args:
        user_id: 用户ID

    Returns:
        操作结果
    """
    if engine is None:
        raise HTTPException(status_code=503, detail="引擎未初始化")

    try:
        engine.reset_user_history(user_id)
        return {"message": f"用户 {user_id} 的历史记录已重置"}

    except Exception as e:
        logger.error(f"重置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/risk/signals")
async def get_risk_signals():
    """
    获取风险信号列表（供模块2使用）

    Returns:
        风险信号说明
    """
    if engine is None:
        raise HTTPException(status_code=503, detail="引擎未初始化")

    try:
        signals = {
            "self_harm_impulse": "自伤冲动程度",
            "despair_level": "绝望情绪强度",
            "agitation_level": "激越状态强度",
            "emptiness_level": "空虚感强度",
            "shame_level": "羞愧情绪强度",
            "emotion_slope": "情绪变化斜率",
            "negative_total": "负面情绪总分"
        }
        return signals

    except Exception as e:
        logger.error(f"获取风险信号列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def main():
    """运行API服务器"""
    # 配置日志
    logger.add("logs/api.log", rotation="10 MB")

    # 运行服务器
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )


if __name__ == "__main__":
    main()
