"""
情绪识别模块
提供文本、音频、图像的多模态情绪分析功能
"""

from .emotion_extractor import EmotionExtractor, EmotionFeatures
from .emotion_engine import EmotionRecognitionEngine
from .multimodal_input_processor import MultimodalInputProcessor, InputType, MultimodalInput

__all__ = [
    'EmotionExtractor',
    'EmotionFeatures',
    'EmotionRecognitionEngine',
    'MultimodalInputProcessor',
    'InputType',
    'MultimodalInput'
]
