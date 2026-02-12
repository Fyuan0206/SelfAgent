"""
统一的多模态输入处理器
自动识别输入类型（文本、语音、图片）并进行相应的情绪分析
"""

import os
import base64
import mimetypes
from pathlib import Path
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum
import cv2
import numpy as np
from loguru import logger


class InputType(Enum):
    """输入类型枚举"""
    TEXT = "text"
    AUDIO = "audio"
    IMAGE = "image"
    VIDEO = "video"
    UNKNOWN = "unknown"


@dataclass
class MultimodalInput:
    """多模态输入数据类"""
    input_type: InputType
    content: Union[str, bytes, np.ndarray]
    metadata: Dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class MultimodalInputProcessor:
    """统一的多模态输入处理器"""

    def __init__(self, emotion_engine):
        """
        初始化多模态输入处理器

        Args:
            emotion_engine: EmotionRecognitionEngine实例
        """
        self.engine = emotion_engine
        self.extractor = emotion_engine.extractor

        # 支持的音频格式
        self.audio_formats = ['.wav', '.mp3', '.m4a', '.aac', '.ogg', '.flac']
        # 支持的图像格式
        self.image_formats = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        # 支持的视频格式
        self.video_formats = ['.mp4', '.avi', '.mov', '.mkv', '.flv']

        logger.info("多模态输入处理器初始化完成")

    def detect_input_type(self, input_data: Union[str, bytes, Path, Dict]) -> InputType:
        """
        自动检测输入类型

        Args:
            input_data: 输入数据，可以是：
                - str: 文本内容或文件路径
                - bytes: 文件数据
                - Path: 文件路径对象
                - Dict: 包含type和content的字典

        Returns:
            InputType枚举值
        """
        # 如果是字典，检查type字段
        if isinstance(input_data, dict):
            type_str = input_data.get('type', input_data.get('input_type', ''))
            if isinstance(type_str, str):
                type_str = type_str.lower()
                if type_str == 'text':
                    return InputType.TEXT
                elif type_str == 'audio':
                    return InputType.AUDIO
                elif type_str == 'image':
                    return InputType.IMAGE
                elif type_str == 'video':
                    return InputType.VIDEO

        # 如果是Path对象，转换为字符串
        if isinstance(input_data, Path):
            input_data = str(input_data)

        # 如果是字符串
        if isinstance(input_data, str):
            # 检查是否是文件路径
            if os.path.exists(input_data):
                _, ext = os.path.splitext(input_data)
                ext = ext.lower()

                if ext in self.audio_formats:
                    return InputType.AUDIO
                elif ext in self.image_formats:
                    return InputType.IMAGE
                elif ext in self.video_formats:
                    return InputType.VIDEO
                else:
                    return InputType.UNKNOWN

            # 检查是否是base64编码的数据
            if input_data.startswith('data:'):
                mime_type = input_data.split(':')[1].split(';')[0]
                if mime_type.startswith('audio/'):
                    return InputType.AUDIO
                elif mime_type.startswith('image/'):
                    return InputType.IMAGE
                elif mime_type.startswith('video/'):
                    return InputType.VIDEO

            # 否则当作文本处理
            return InputType.TEXT

        # 如果是bytes，检查magic number
        if isinstance(input_data, bytes):
            # 检查图片magic numbers
            if input_data.startswith(b'\xFF\xD8\xFF'):  # JPEG
                return InputType.IMAGE
            elif input_data.startswith(b'\x89PNG'):  # PNG
                return InputType.IMAGE
            elif input_data.startswith(b'GIF87a') or input_data.startswith(b'GIF89a'):  # GIF
                return InputType.IMAGE
            # 可以添加更多格式的检测...
            else:
                return InputType.UNKNOWN

        # 如果是numpy数组，当作图像/视频帧
        if isinstance(input_data, np.ndarray):
            return InputType.IMAGE

        return InputType.UNKNOWN

    def process_input(self, input_data: Union[str, bytes, Path, Dict],
                     user_id: str = "default_user",
                     context: str = "") -> Dict:
        """
        处理多模态输入并返回情绪分析结果

        Args:
            input_data: 输入数据（文本、文件路径、base64等）
            user_id: 用户ID
            context: 对话上下文

        Returns:
            完整的分析结果字典
        """
        # 检测输入类型
        input_type = self.detect_input_type(input_data)

        logger.info(f"检测到输入类型: {input_type.value}")

        # 根据类型进行处理
        if input_type == InputType.TEXT:
            return self._process_text(input_data, user_id, context)
        elif input_type == InputType.AUDIO:
            return self._process_audio(input_data, user_id, context)
        elif input_type == InputType.IMAGE:
            return self._process_image(input_data, user_id, context)
        elif input_type == InputType.VIDEO:
            return self._process_video(input_data, user_id, context)
        else:
            logger.warning(f"未知输入类型，尝试作为文本处理")
            return self._process_text(str(input_data), user_id, context)

    def _process_text(self, text: str, user_id: str, context: str) -> Dict:
        """处理文本输入"""
        # 如果text是字典格式，提取content字段
        if isinstance(text, dict):
            text = text.get('content', '')

        logger.info(f"处理文本输入: {text[:50]}...")

        result = self.engine.analyze(
            text=text,
            user_id=user_id,
            context=context
        )

        # 添加输入类型标记
        result['input_type'] = 'text'
        result['input_content'] = text

        return result

    def _process_audio(self, audio_input: Union[str, bytes, Dict], user_id: str, context: str) -> Dict:
        """处理语音输入"""
        # 1. 获取音频文件路径
        audio_path = None

        if isinstance(audio_input, str):
            if os.path.exists(audio_input):
                audio_path = audio_input
            elif audio_input.startswith('data:audio'):
                # Base64编码的音频，需要解码保存
                audio_path = self._save_base64_audio(audio_input, user_id)
        elif isinstance(audio_input, dict):
            # 字典格式，可能包含path或content
            audio_path = audio_input.get('path')
            if not audio_path and audio_input.get('content'):
                audio_path = self._save_base64_audio(audio_input['content'], user_id)
        elif isinstance(audio_input, bytes):
            # 直接的字节数据，需要保存
            audio_path = self._save_audio_bytes(audio_input, user_id)

        if not audio_path or not os.path.exists(audio_path):
            logger.error(f"无法处理音频输入")
            return self._create_error_result("audio", "无法处理音频输入")

        logger.info(f"处理音频输入: {audio_path}")

        # 2. 语音识别（使用讯飞ASR）
        transcribed_text = self.extractor.transcribe_audio(audio_path, method='xunfei')

        if not transcribed_text:
            # 如果ASR失败，尝试备用方法
            transcribed_text = self.extractor.transcribe_audio(audio_path, method='local')

        if not transcribed_text:
            logger.error(f"语音识别失败")
            return self._create_error_result("audio", "语音识别失败")

        logger.info(f"语音识别结果: {transcribed_text}")

        # 3. 使用识别的文本进行情绪分析
        result = self.engine.analyze(
            text=transcribed_text,
            user_id=user_id,
            audio_path=audio_path,
            context=context
        )

        # 添加输入类型标记
        result['input_type'] = 'audio'
        result['audio_path'] = audio_path
        result['transcribed_text'] = transcribed_text

        return result

    def _process_image(self, image_input: Union[str, bytes, np.ndarray, Dict], user_id: str, context: str) -> Dict:
        """处理图片输入"""
        # 1. 获取图像数据
        frame = None
        image_path = None

        if isinstance(image_input, str):
            if os.path.exists(image_input):
                # 文件路径
                image_path = image_input
                frame = cv2.imread(image_input)
            elif image_input.startswith('data:image'):
                # Base64编码的图像
                frame = self._decode_base64_image(image_input)
        elif isinstance(image_input, dict):
            image_path = image_input.get('path')
            if image_path and os.path.exists(image_path):
                frame = cv2.imread(image_path)
            if frame is None and image_input.get('content'):
                frame = self._decode_base64_image(image_input['content'])
        elif isinstance(image_input, bytes):
            # 直接的字节数据
            frame = self._decode_image_bytes(image_input)
        elif isinstance(image_input, np.ndarray):
            # 直接是numpy数组
            frame = image_input

        if frame is None:
            logger.error(f"无法处理图片输入")
            return self._create_error_result("image", "无法处理图片输入")

        logger.info(f"处理图片输入: {image_path or 'from memory/base64'}")

        # 2. 进行图像情绪分析
        result = self.engine.analyze(
            text="[图像输入]",  # 占位文本，会被图像情绪替换
            user_id=user_id,
            video_data=frame,
            context=context
        )

        # 添加输入类型标记
        result['input_type'] = 'image'
        if image_path:
            result['image_path'] = image_path

        return result

    def _process_video(self, video_input: Union[str, Dict], user_id: str, context: str) -> Dict:
        """处理视频输入"""
        # 视频输入当作图像处理（提取第一帧）
        video_path = None

        if isinstance(video_input, str) and os.path.exists(video_input):
            video_path = video_input
        elif isinstance(video_input, dict):
            video_path = video_input.get('path')

        if not video_path or not os.path.exists(video_path):
            logger.error(f"无法处理视频输入")
            return self._create_error_result("video", "无法处理视频输入")

        logger.info(f"处理视频输入: {video_path}")

        # 提取第一帧作为图像处理
        result = self.engine.analyze(
            text="[视频输入]",
            user_id=user_id,
            video_path=video_path,
            context=context
        )

        # 添加输入类型标记
        result['input_type'] = 'video'
        result['video_path'] = video_path

        return result

    def _save_base64_audio(self, base64_data: str, user_id: str) -> Optional[str]:
        """保存base64编码的音频到临时文件"""
        try:
            # 提取base64数据
            if ',' in base64_data:
                base64_data = base64_data.split(',')[1]

            # 解码
            audio_data = base64.b64decode(base64_data)

            # 保存到临时文件
            temp_dir = Path("temp")
            temp_dir.mkdir(exist_ok=True)

            temp_path = temp_dir / f"audio_{user_id}_{id(base64_data)}.wav"

            with open(temp_path, 'wb') as f:
                f.write(audio_data)

            return str(temp_path)
        except Exception as e:
            logger.error(f"保存base64音频失败: {e}")
            return None

    def _save_audio_bytes(self, audio_data: bytes, user_id: str) -> Optional[str]:
        """保存音频字节数据到临时文件"""
        try:
            temp_dir = Path("temp")
            temp_dir.mkdir(exist_ok=True)

            temp_path = temp_dir / f"audio_{user_id}_{id(audio_data)}.wav"

            with open(temp_path, 'wb') as f:
                f.write(audio_data)

            return str(temp_path)
        except Exception as e:
            logger.error(f"保存音频字节失败: {e}")
            return None

    def _decode_base64_image(self, base64_data: str) -> Optional[np.ndarray]:
        """解码base64编码的图像"""
        try:
            # 提取base64数据
            if ',' in base64_data:
                base64_data = base64_data.split(',')[1]

            # 解码
            img_data = base64.b64decode(base64_data)

            # 转换为numpy数组
            nparr = np.frombuffer(img_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            return frame
        except Exception as e:
            logger.error(f"解码base64图像失败: {e}")
            return None

    def _decode_image_bytes(self, img_data: bytes) -> Optional[np.ndarray]:
        """解码图像字节数据"""
        try:
            nparr = np.frombuffer(img_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return frame
        except Exception as e:
            logger.error(f"解码图像字节失败: {e}")
            return None

    def _create_error_result(self, input_type: str, error_msg: str) -> Dict:
        """创建错误结果"""
        return {
            'input_type': input_type,
            'error': error_msg,
            'routing_decision': {
                'level': 'L1_QUICK',
                'reason': f'处理失败: {error_msg}',
                'suggested_action': '请重试或使用其他输入方式'
            },
            'emotion_features': {
                'emotions': {emotion: 0.0 for emotion in self.extractor.dbt_emotions},
                'arousal': 0.0,
                'confidence': 0.0
            },
            'intervention_assessment': {
                'triggered': False,
                'risk_level': 'LOW',
                'urgency_score': 0.0
            }
        }
