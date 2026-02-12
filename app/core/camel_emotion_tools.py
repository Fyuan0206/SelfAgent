"""
CAMEL情绪识别工具集成
将情绪识别功能封装为CAMEL工具
"""

from typing import Dict, Any, Optional
from camel.agents import ChatAgent
from camel.messages import BaseMessage
# from camel.toolkits import BaseTool # Removed: BaseTool does not exist in this version of CAMEL

from app.modules.emotion import EmotionRecognitionEngine
from loguru import logger


class EmotionRecognitionTool: # Removed inheritance from BaseTool
    """情绪识别工具 - CAMEL集成"""

    def __init__(self, config: Optional[Dict] = None):
        """
        初始化情绪识别工具

        Args:
            config: 配置字典，如果为None则从.env加载
        """
        self.config = config
        self.engine = None
        self._initialized = False

    def _ensure_initialized(self):
        """确保引擎已初始化"""
        if not self._initialized:
            logger.info("初始化情绪识别引擎...")
            self.engine = EmotionRecognitionEngine(self.config)
            self._initialized = True

    def detect_emotion(
        self,
        text: str,
        user_id: str = "default_user",
        context: str = ""
    ) -> Dict[str, Any]:
        """
        检测文本情绪

        Args:
            text: 输入文本
            user_id: 用户ID
            context: 对话上下文

        Returns:
            包含情绪分析结果的字典
        """
        self._ensure_initialized()

        result = self.engine.analyze(
            text=text,
            user_id=user_id,
            context=context
        )

        return {
            'user_id': result['user_id'],
            'emotions': result['emotion_features']['emotions'],
            'arousal': result['emotion_features']['arousal'],
            'route_level': result['routing_decision']['level'],
            'risk_level': result['intervention_assessment']['risk_level'],
            'requires_intervention': result['intervention_assessment']['triggered'],
            'recommendations': result['recommendations']
        }

    def analyze_audio_emotion(
        self,
        audio_path: str,
        user_id: str = "default_user",
        context: str = ""
    ) -> Dict[str, Any]:
        """
        分析音频情绪

        Args:
            audio_path: 音频文件路径
            user_id: 用户ID
            context: 对话上下文

        Returns:
            包含情绪分析结果的字典
        """
        self._ensure_initialized()

        result = self.engine.analyze(
            text="",  # 文本将通过ASR自动填充
            user_id=user_id,
            audio_path=audio_path,
            context=context
        )

        return {
            'user_id': result['user_id'],
            'emotions': result['emotion_features']['emotions'],
            'arousal': result['emotion_features']['arousal'],
            'route_level': result['routing_decision']['level'],
            'risk_level': result['intervention_assessment']['risk_level'],
            'requires_intervention': result['intervention_assessment']['triggered'],
            'recommendations': result['recommendations']
        }

    def analyze_image_emotion(
        self,
        image_path: str,
        user_id: str = "default_user",
        context: str = ""
    ) -> Dict[str, Any]:
        """
        分析图像情绪

        Args:
            image_path: 图像文件路径
            user_id: 用户ID
            context: 对话上下文

        Returns:
            包含情绪分析结果的字典
        """
        self._ensure_initialized()

        import cv2
        frame = cv2.imread(image_path)

        result = self.engine.analyze(
            text="[图像输入]",
            user_id=user_id,
            video_data=frame,
            context=context
        )

        return {
            'user_id': result['user_id'],
            'emotions': result['emotion_features']['emotions'],
            'arousal': result['emotion_features']['arousal'],
            'route_level': result['routing_decision']['level'],
            'risk_level': result['intervention_assessment']['risk_level'],
            'requires_intervention': result['intervention_assessment']['triggered'],
            'recommendations': result['recommendations']
        }

    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """
        获取用户画像

        Args:
            user_id: 用户ID

        Returns:
            用户画像数据
        """
        self._ensure_initialized()

        profile = self.engine.get_profile(user_id)
        if profile is None:
            return {'error': '用户画像不存在'}

        return profile

    def get_emotion_summary(self, user_id: str) -> str:
        """
        获取用户情绪摘要

        Args:
            user_id: 用户ID

        Returns:
            情绪摘要文本
        """
        self._ensure_initialized()

        report = self.engine.generate_profile_report(user_id)
        if report is None:
            return "用户画像不存在或数据不足"

        return report


def get_emotion_tools() -> list:
    """
    获取情绪识别工具列表
    用于CAMEL Agent的工具注册

    Returns:
        工具函数列表
    """
    tool = EmotionRecognitionTool()

    return [
        tool.detect_emotion,
        tool.analyze_audio_emotion,
        tool.analyze_image_emotion,
        tool.get_user_profile,
        tool.get_emotion_summary
    ]


# 便捷函数
def create_emotion_agent(
    system_message: str,
    config: Optional[Dict] = None
) -> ChatAgent:
    """
    创建具有情绪识别能力的CAMEL Agent

    Args:
        system_message: 系统消息
        config: 配置字典

    Returns:
        配置好的ChatAgent实例
    """
    # 获取情绪识别工具
    emotion_tools = get_emotion_tools()

    # 创建Agent
    agent = ChatAgent(
        system_message=BaseMessage.make_user_message(
            role_name="Emotion Assistant",
            content=system_message
        ),
        tools=emotion_tools
    )

    return agent
