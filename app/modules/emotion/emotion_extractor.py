"""
情绪特征提取器
使用ModelScope远程API进行文本、语音、图像的多维情绪特征提取
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import requests
import librosa
import cv2
import base64
import json
import re
import hashlib
import hmac
import time
import websocket
import urllib.parse
from datetime import datetime
from loguru import logger

# 语音识别库
try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False
    logger.warning("speech_recognition未安装，语音识别功能将使用API方式")

# 音频处理库
try:
    import wave
    import struct
    WAVE_AVAILABLE = True
except ImportError:
    WAVE_AVAILABLE = False


@dataclass
class EmotionFeatures:
    """情绪特征数据类"""
    text_emotion: Dict[str, float]  # 文本情绪分布
    text_arousal: float  # 文本唤醒度
    audio_features: Optional[Dict[str, float]]  # 语音特征
    video_features: Optional[Dict[str, float]]  # 视频特征
    multimodal_vector: np.ndarray  # 多模态融合向量
    confidence: float  # 置信度


class EmotionExtractor:
    """情绪特征提取器 - 使用ModelScope远程API"""

    def __init__(self, config: Dict):
        self.config = config
        self.dbt_emotions = config.get('dbt_emotions', [])
        self.multimodal_config = config.get('multimodal', {})

        # ModelScope API配置
        self.api_key = config.get('modelscope', {}).get('api_key')
        self.api_base = "https://api-inference.modelscope.cn/v1"

        # 初始化远程模型调用
        try:
            self._init_remote_models()
        except Exception as e:
            logger.error(f"远程模型初始化失败: {e}")
            raise

    def _init_remote_models(self):
        """初始化ModelScope远程API调用"""
        logger.info("初始化ModelScope远程API...")

        # 检查API密钥
        if not self.api_key:
            logger.warning("未配置ModelScope API密钥，将使用本地规则引擎")

        # 远程模型信息
        self.models = {
            'emotion': self.config.get('modelscope', {}).get('emotion_model'),
            'multimodal': self.config.get('modelscope', {}).get('multimodal_model'),
            'asr': self.config.get('modelscope', {}).get('asr_model', 'Qwen/Qwen2-Audio-7B-Instruct')
        }

        # 初始化语音识别器
        if SR_AVAILABLE:
            self.recognizer = sr.Recognizer()
        else:
            self.recognizer = None

        # 讯飞ASR配置
        self.xunfei_config = self.config.get('xunfei_asr', {})
        if self.xunfei_config.get('app_id'):
            logger.info("讯飞ASR配置已加载")

        logger.info("ModelScope远程API配置完成")

    def transcribe_audio(self, audio_path: str, method: str = 'xunfei') -> Optional[str]:
        """
        语音识别：将音频转换为文本

        Args:
            audio_path: 音频文件路径
            method: 识别方法
                - 'xunfei': 使用讯飞大模型ASR（默认，推荐）
                - 'api': 使用ModelScope API
                - 'local': 使用本地识别库

        Returns:
            识别出的文本，失败返回None
        """
        logger.info(f"开始语音识别: {audio_path}, 方法: {method}")

        # 方法1: 使用讯飞ASR（推荐）
        if method == 'xunfei' and self.xunfei_config.get('app_id'):
            try:
                text = self._asr_via_xunfei(audio_path)
                if text:
                    logger.info(f"讯飞ASR识别成功: {text[:50]}...")
                    return text
            except Exception as e:
                logger.warning(f"讯飞ASR识别失败: {e}")

        # 方法2: 使用ModelScope API进行语音识别
        if method == 'api' and self.api_key:
            try:
                text = self._asr_via_api(audio_path)
                if text:
                    logger.info(f"ModelScope API识别成功: {text[:50]}...")
                    return text
            except Exception as e:
                logger.warning(f"ModelScope API识别失败: {e}")

        # 方法3: 使用本地语音识别库（备用）
        if SR_AVAILABLE and self.recognizer:
            try:
                text = self._asr_via_local(audio_path)
                if text:
                    logger.info(f"本地语音识别成功: {text[:50]}...")
                    return text
            except Exception as e:
                logger.warning(f"本地语音识别失败: {e}")

        logger.error("语音识别失败：所有方法均失败")
        return None

    def _asr_via_xunfei(self, audio_path: str) -> Optional[str]:
        """使用讯飞大模型ASR进行语音识别"""
        if not self.xunfei_config.get('app_id'):
            logger.warning("讯飞ASR未配置")
            return None

        try:
            # 生成鉴权URL
            auth_url = self._create_xunfei_auth_url()
            if not auth_url:
                return None

            # 读取并转换音频为PCM格式
            pcm_data = self._convert_audio_to_pcm(audio_path)
            if not pcm_data:
                return None

            # 建立WebSocket连接并进行识别
            result = self._xunfei_websocket_asr(auth_url, pcm_data)
            return result

        except Exception as e:
            logger.error(f"讯飞ASR调用异常: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _create_xunfei_auth_url(self) -> Optional[str]:
        """生成讯飞ASR鉴权URL"""
        try:
            host = self.xunfei_config.get('host', 'iat.xf-yun.com')
            path = self.xunfei_config.get('path', '/v1')
            api_key = self.xunfei_config.get('api_key')
            api_secret = self.xunfei_config.get('api_secret')

            # 生成RFC1123格式时间
            date = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')

            # 生成签名原文字符串
            signature_origin = f"host: {host}\ndate: {date}\nGET {path} HTTP/1.1"

            # 使用hmac-sha256加密
            signature_sha = hmac.new(
                api_secret.encode('utf-8'),
                signature_origin.encode('utf-8'),
                digestmod=hashlib.sha256
            ).digest()

            # 进行base64编码
            signature = base64.b64encode(signature_sha).decode(encoding='utf-8')

            # 生成authorization原文字符串
            authorization_origin = (
                f'api_key="{api_key}", '
                f'algorithm="hmac-sha256", '
                f'headers="host date request-line", '
                f'signature="{signature}"'
            )

            # 进行base64编码
            authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')

            # URL编码参数
            authorization_encoded = urllib.parse.quote(authorization)
            date_encoded = urllib.parse.quote(date)

            # 拼接最终URL
            auth_url = f"wss://{host}{path}?authorization={authorization_encoded}&date={date_encoded}&host={host}"
            logger.info(f"讯飞ASR鉴权URL生成成功")
            logger.debug(f"Date: {date}")
            return auth_url

        except Exception as e:
            logger.error(f"生成讯飞鉴权URL失败: {e}")
            return None

    def _convert_audio_to_pcm(self, audio_path: str) -> Optional[bytes]:
        """将音频转换为PCM格式（16k, 16bit, 单声道）"""
        try:
            # 使用librosa加载音频并转换
            y, sr = librosa.load(audio_path, sr=16000, mono=True)

            # 转换为16bit PCM
            # 归一化到[-1, 1]范围后转换为16bit整数
            y_int16 = (y * 32767).astype(np.int16)

            # 转换为bytes
            pcm_data = y_int16.tobytes()

            logger.info(f"音频转换成功: {len(pcm_data)} bytes")
            return pcm_data

        except Exception as e:
            logger.error(f"音频转换失败: {e}")
            return None

    def _xunfei_websocket_asr(self, auth_url: str, pcm_data: bytes) -> Optional[str]:
        """通过WebSocket连接讯飞ASR服务"""
        try:
            # WebSocket结果收集
            result_text = []

            def on_message(ws, message):
                """处理收到的消息"""
                try:
                    data = json.loads(message)
                    header = data.get('header', {})

                    # 检查状态码
                    code = header.get('code')
                    if code != 0:
                        logger.error(f"讯飞ASR返回错误: {header.get('message')}")
                        return

                    # 获取payload中的text字段
                    payload = data.get('payload', {})
                    result = payload.get('result', {})

                    if result:
                        text_base64 = result.get('text', '')
                        if text_base64:
                            # 解码base64
                            text_json = base64.b64decode(text_base64).decode('utf-8')
                            text_data = json.loads(text_json)

                            # 解析识别结果
                            if 'ws' in text_data:
                                for ws_item in text_data['ws']:
                                    for cw_item in ws_item.get('cw', []):
                                        word = cw_item.get('w', '')
                                        if word:
                                            result_text.append(word)

                                        # 检查是否是最后一帧
                    if header.get('status') == 2:
                        logger.info("讯飞ASR识别完成")

                except Exception as e:
                    logger.error(f"解析讯飞ASR消息失败: {e}")

            def on_error(ws, error):
                """处理错误"""
                logger.error(f"讯飞ASR WebSocket错误: {error}")

            def on_close(ws, close_status_code, close_msg):
                """连接关闭"""
                logger.debug(f"讯飞ASR WebSocket连接关闭: {close_status_code}")

            def on_open(ws):
                """连接建立后发送音频数据"""
                try:
                    # 配置参数
                    app_id = self.xunfei_config.get('app_id')
                    sample_rate = self.xunfei_config.get('sample_rate', 16000)

                    # 构建首帧数据
                    first_frame = {
                        "header": {
                            "app_id": app_id,
                            "status": 0
                        },
                        "parameter": {
                            "iat": {
                                "domain": self.xunfei_config.get('domain', 'slm'),
                                "language": self.xunfei_config.get('language', 'zh_cn'),
                                "accent": self.xunfei_config.get('accent', 'mandarin'),
                                "eos": self.xunfei_config.get('eos', 6000),
                                "result": {
                                    "encoding": "utf8",
                                    "compress": "raw",
                                    "format": "json"
                                }
                            }
                        },
                        "payload": {
                            "audio": {
                                "encoding": "raw",
                                "sample_rate": sample_rate,
                                "channels": 1,
                                "bit_depth": 16,
                                "seq": 1,
                                "status": 0,
                                "audio": base64.b64encode(pcm_data[:1280]).decode('utf-8') if len(pcm_data) >= 1280 else base64.b64encode(pcm_data).decode('utf-8')
                            }
                        }
                    }

                    # 发送首帧
                    ws.send(json.dumps(first_frame))

                    # 分帧发送剩余音频数据
                    frame_size = 1280  # 每帧大小
                    seq = 2
                    offset = frame_size if len(pcm_data) >= frame_size else len(pcm_data)

                    while offset < len(pcm_data):
                        chunk = pcm_data[offset:offset + frame_size]
                        is_last = (offset + frame_size >= len(pcm_data))

                        frame = {
                            "header": {
                                "app_id": app_id,
                                "status": 2 if is_last else 1
                            },
                            "payload": {
                                "audio": {
                                    "encoding": "raw",
                                    "sample_rate": sample_rate,
                                    "channels": 1,
                                    "bit_depth": 16,
                                    "seq": seq,
                                    "status": 2 if is_last else 1,
                                    "audio": base64.b64encode(chunk).decode('utf-8') if chunk else ""
                                }
                            }
                        }

                        ws.send(json.dumps(frame))
                        seq += 1
                        offset += frame_size

                        # 发送间隔
                        time.sleep(0.04)

                    logger.info(f"讯飞ASR音频数据发送完成，共发送{seq}帧")

                except Exception as e:
                    logger.error(f"发送讯飞ASR数据失败: {e}")
                    import traceback
                    traceback.print_exc()

            # 创建WebSocket连接
            ws = websocket.WebSocketApp(
                auth_url,
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )

            # 运行WebSocket（设置超时）
            ws.run_forever()

            # 拼接识别结果
            final_text = ''.join(result_text)
            if final_text:
                logger.info(f"讯飞ASR识别结果: {final_text}")
                return final_text
            else:
                logger.warning("讯飞ASR未返回识别结果")
                return None

        except Exception as e:
            logger.error(f"讯飞ASR WebSocket通信异常: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _asr_via_api(self, audio_path: str) -> Optional[str]:
        """使用ModelScope API进行语音识别"""
        if not self.api_key:
            return None

        try:
            # 读取音频文件并编码为base64
            import wave
            import contextlib

            # 检查音频文件格式
            with contextlib.closing(wave.open(audio_path, 'rb')) as f:
                frames = f.getnframes()
                rate = f.getframerate()
                duration = frames / float(rate)
                logger.info(f"音频时长: {duration:.2f}秒, 采样率: {rate}Hz")

            # 读取音频数据为base64
            with open(audio_path, 'rb') as f:
                audio_data = f.read()
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')

            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }

            # 使用Qwen2-Audio模型的提示词
            prompt = """请将音频中的语音内容转换为文字。只返回识别出的文字内容，不要添加任何解释或标点符号的额外说明。"""

            data = {
                'model': self.models['asr'],
                'messages': [
                    {
                        'role': 'user',
                        'content': [
                            {'type': 'text', 'text': prompt},
                            {'type': 'audio_url', 'audio_url': {'url': f"data:audio/wav;base64,{audio_base64}"}}
                        ]
                    }
                ],
                'temperature': 0.0
            }

            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                if 'choices' in result and len(result['choices']) > 0:
                    content = result['choices'][0].get('message', {}).get('content', '')
                    logger.info(f"ASR API返回内容: {content}")
                    # 清理返回的文本
                    text = content.strip()
                    # 移除可能的引号或多余的标记
                    text = re.sub(r'^["\']|["\']$', '', text)
                    return text if text else None
            else:
                logger.warning(f"ASR API错误: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"ASR API调用异常: {e}")
            return None

    def _asr_via_local(self, audio_path: str) -> Optional[str]:
        """使用本地语音识别库进行识别（备用方案）"""
        if not SR_AVAILABLE:
            return None

        try:
            with sr.AudioFile(audio_path) as source:
                # 降噪处理
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio_data = self.recognizer.record(source)

                # 尝试使用Google Speech Recognition（需要网络）
                try:
                    text = self.recognizer.recognize_google(audio_data, language='zh-CN')
                    return text
                except sr.UnknownValueError:
                    logger.warning("Google语音识别无法理解音频")
                    return None
                except sr.RequestError:
                    logger.warning("Google语音识别服务不可用")
                    return None

        except Exception as e:
            logger.error(f"本地语音识别异常: {e}")
            return None

    def extract_image_emotion(self, image_path: str) -> Dict[str, float]:
        """
        从图像中提取情绪特征（纯图像输入，无需文本）

        Args:
            image_path: 图像文件路径

        Returns:
            DBT情绪分数字典
        """
        logger.info(f"开始分析图像情绪: {image_path}")

        # 读取图像
        try:
            frame = cv2.imread(image_path)
            if frame is None:
                logger.error(f"无法读取图像: {image_path}")
                return {emotion: 0.0 for emotion in self.dbt_emotions}

            # 编码为base64
            _, buffer = cv2.imencode('.jpg', frame)
            img_base64 = base64.b64encode(buffer).decode('utf-8')

            # 调用多模态API
            if self.api_key:
                api_result = self._call_multimodal_api_for_image(img_base64)
                if api_result:
                    emotion_scores = self._parse_api_result(api_result, text="[IMAGE_ANALYSIS]")
                    if emotion_scores:
                        logger.info(f"图像情绪分析成功: {emotion_scores}")
                        return emotion_scores

            # 降级到基于CV特征的规则分析
            logger.info("使用CV特征进行图像情绪分析")
            return self._cv_based_emotion_analysis(frame)

        except Exception as e:
            logger.error(f"图像情绪分析失败: {e}")
            return {emotion: 0.0 for emotion in self.dbt_emotions}

    def _call_multimodal_api_for_image(self, image_base64: str) -> Optional[Dict]:
        """调用ModelScope多模态API进行图像情绪分析"""
        if not self.api_key:
            return None

        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }

            dbt_emotions_str = "、".join(self.dbt_emotions)
            prompt = f"""你是一个专业的面部表情和肢体语言情绪分析专家。请仔细观察图片中人物的情绪状态。

基于DBT（辩证行为疗法）的12种核心情绪：{dbt_emotions_str}

**重要分析指引：**

1. **哭泣/流泪识别**：如果人物在哭泣、流泪、眼眶湿润、有泪痕，必须给出高悲伤分数(≥0.7)，同时给予较高的绝望(≥0.4)和孤独(≥0.3)分数

2. **面部表情细节**：
   - 眉毛：紧皱、下垂→焦虑/悲伤/绝望
   - 眼睛：红肿、湿润、泪痕→悲伤/绝望
   - 嘴巴：嘴角下垂、颤抖→悲伤/绝望

3. **肢体语言**：
   - 蜷缩姿态、抱头→绝望/悲伤
   - 委靡、低垂的头→绝望/空虚感

4. **整体氛围**：
   - 暗沉、压抑的环境→绝望/悲伤/孤独
   - 孤独、隔离的感觉→孤独/绝望

**打分规则：**
- 如果明显在哭泣：悲伤≥0.7，绝望≥0.4，孤独≥0.3
- 如果表情痛苦：悲伤≥0.6，焦虑≥0.4
- 如果情绪低落：绝望≥0.5，空虚感≥0.4
- 如果微笑/开心：所有负面情绪为0

请只输出JSON格式的情绪分数，不要添加任何其他说明：
{{
    "空虚感": 0.0,
    "羞愧": 0.0,
    "激越": 0.0,
    "自伤冲动": 0.0,
    "愤怒": 0.0,
    "悲伤": 0.0,
    "焦虑": 0.0,
    "恐惧": 0.0,
    "厌恶": 0.0,
    "内疚": 0.0,
    "孤独": 0.0,
    "绝望": 0.0
}}"""

            data = {
                'model': self.models.get('multimodal'),
                'messages': [
                    {
                        'role': 'user',
                        'content': [
                            {'type': 'text', 'text': prompt},
                            {'type': 'image_url', 'image_url': {'url': f"data:image/jpeg;base64,{image_base64}"}}
                        ]
                    }
                ],
                'temperature': 0.0,
                'max_tokens': 500
            }

            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                logger.info("多模态图像分析API调用成功")
                return result
            else:
                logger.warning(f"多模态API错误: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"多模态API调用失败: {e}")
            return None

    def _cv_based_emotion_analysis(self, frame: np.ndarray) -> Dict[str, float]:
        """基于计算机视觉特征的图像情绪分析（备用方案）"""
        scores = {emotion: 0.0 for emotion in self.dbt_emotions}

        try:
            # 转换为灰度图
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # 提取特征
            brightness = float(np.mean(gray))
            contrast = float(np.std(gray))

            # HSV分析
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            hue_mean = float(np.mean(hsv[:, :, 0]))
            saturation_mean = float(np.mean(hsv[:, :, 1]))

            # 简单规则推断情绪
            # 低亮度 + 低饱和度 → 可能是悲伤/空虚
            if brightness < 100 and saturation_mean < 80:
                scores['悲伤'] = 0.5
                scores['空虚感'] = 0.4

            # 高对比度 → 可能是激越/愤怒
            if contrast > 80:
                scores['激越'] = 0.4
                scores['愤怒'] = 0.3

            # 归一化
            total = sum(scores.values()) or 1.0
            scores = {k: v / total for k, v in scores.items()}

            logger.info(f"CV特征分析结果: {scores}")
            return scores

        except Exception as e:
            logger.error(f"CV特征分析失败: {e}")
            return scores

    def _call_modelscope_api(self, text: str, model_type: str = 'emotion') -> Optional[Dict]:
        """调用ModelScope远程API（使用OpenAI兼容接口）"""
        if not self.api_key:
            logger.warning("未配置API密钥，跳过远程调用")
            return None

        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }

            # 构建提示词
            dbt_emotions_str = "、".join(self.dbt_emotions)

            # 检测是否包含危机关键词
            crisis_keywords = ["自杀", "自残", "死掉", "不想活", "结束生命", "杀死自己"]
            is_crisis = any(kw in text for kw in crisis_keywords)

            if is_crisis:
                # 危机情况的特殊提示词
                prompt = f"""紧急情况分析！

文本明确提到自杀或自伤，这是最高级别的危机情况。

请按照以下规则赋值：
- 自伤冲动：0.9-1.0（文本明确提到自伤/自杀）
- 绝望：0.8-1.0（自杀意念通常伴随强烈绝望）
- 其他情绪：根据文本内容适当赋值

文本：{text}

返回JSON格式，自杀相关表述自伤冲动必须≥0.9。"""
            else:
                # 常规提示词
                prompt = f"""你是一个DBT情绪分析专家。分析文本的12种DBT核心情绪：{dbt_emotions_str}

要求：
1. 只识别明确的负面情绪表达
2. 积极内容、日常闲聊、礼貌用语 → 所有情绪为0
3. 输出JSON格式，分数范围0-1

文本：{text}"""

            # 构建请求数据（使用chat completions接口）
            data = {
                'model': self.models.get('emotion'),
                'messages': [
                    {'role': 'system', 'content': '你是一个专业的情绪分析助手，专注于DBT（辩证行为疗法）核心情绪识别。'},
                    {'role': 'user', 'content': prompt}
                ],
                'temperature': 0.3,
                'max_tokens': 500
            }

            # 发送请求到chat completions端点
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                logger.info(f"ModelScope API调用成功: {model_type}")
                return result
            else:
                logger.warning(f"ModelScope API返回错误: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"ModelScope API调用失败: {e}")
            return None

    def extract_text_emotion(self, text: str) -> Dict[str, float]:
        """
        深层文本情绪分析
        使用ModelScope远程API识别DBT核心的复合情绪
        """
        if not text or not text.strip():
            return {"neutral": 1.0}

        # 优先尝试远程API
        try:
            api_result = self._call_modelscope_api(text, 'emotion')
            if api_result:
                # 解析API返回结果
                emotion_scores = self._parse_api_result(api_result, text)
                if emotion_scores:
                    return emotion_scores
        except Exception as e:
            logger.warning(f"远程API调用失败，使用本地规则引擎: {e}")

        # 降级到本地规则引擎
        logger.info("使用本地规则引擎进行情绪分析")
        emotion_scores = self._rule_based_emotion_analysis(text)
        return emotion_scores

    def _parse_api_result(self, api_result: Dict, text: str = "") -> Dict[str, float]:
        """解析ModelScope chat completions API返回结果"""
        try:
            # 从chat completions响应中提取内容
            if 'choices' not in api_result or len(api_result['choices']) == 0:
                logger.warning("API响应中没有choices")
                return None

            content = api_result['choices'][0].get('message', {}).get('content', '')
            if not content:
                logger.warning("API响应中没有content")
                return None

            # 解析JSON内容
            import json
            import re

            # 尝试直接解析
            try:
                emotion_data = json.loads(content)
            except json.JSONDecodeError:
                # 如果直接解析失败，尝试提取JSON部分
                json_match = re.search(r'\{[^}]+\}', content)
                if json_match:
                    emotion_data = json.loads(json_match.group())
                else:
                    logger.warning(f"无法从响应中提取JSON: {content}")
                    return None

            # 映射到DBT情绪标签
            dbt_scores = {emotion: 0.0 for emotion in self.dbt_emotions}

            # 从API返回的数据中提取情绪分数
            for emotion, score in emotion_data.items():
                if emotion in self.dbt_emotions:
                    dbt_scores[emotion] = float(score)

            # 智能后处理：修正明显的误判
            dbt_scores = self._apply_common_sense_correction(dbt_scores, text)

            # 危机情况修正：如果文本包含危机关键词，强制修正分数
            crisis_keywords = ["自杀", "自残", "死掉", "不想活", "结束生命", "杀死自己"]
            if any(kw in text for kw in crisis_keywords):
                logger.warning(f"检测到危机关键词，应用危机修正规则")
                # 自伤冲动和绝望应该很高
                dbt_scores['自伤冲动'] = max(dbt_scores['自伤冲动'], 0.95)
                dbt_scores['绝望'] = max(dbt_scores['绝望'], 0.85)
                logger.info(f"危机修正后的情绪分数: {dbt_scores}")
                # 危机情况直接返回，不归一化
                logger.info(f"成功解析API结果（危机情况），情绪分数: {dbt_scores}")
                return dbt_scores

            # 归一化（非危机情况）
            total = sum(dbt_scores.values()) or 1.0
            if total > 0:
                dbt_scores = {k: v / total for k, v in dbt_scores.items()}

            logger.info(f"成功解析API结果，情绪分数: {dbt_scores}")
            return dbt_scores

        except Exception as e:
            logger.error(f"解析API结果失败: {e}")
            return None

    def _map_to_dbt_emotions(self, model_output: Dict) -> Dict[str, float]:
        """将模型输出映射到DBT情绪标签"""
        dbt_scores = {emotion: 0.0 for emotion in self.dbt_emotions}

        # 这里需要根据实际模型输出进行映射
        # 示例映射逻辑
        if isinstance(model_output, dict):
            for key, value in model_output.items():
                for dbt_emotion in self.dbt_emotions:
                    if dbt_emotion in key or key in dbt_emotion:
                        dbt_scores[dbt_emotion] = max(dbt_scores[dbt_emotion], float(value))

        # 归一化
        total = sum(dbt_scores.values()) or 1.0
        return {k: v / total for k, v in dbt_scores.items()}

    def _apply_common_sense_correction(self, dbt_scores: Dict[str, float], text: str) -> Dict[str, float]:
        """
        智能后处理：修正AI的明显误判
        在保留AI灵活性的同时，用常识规则兜底
        """
        text_lower = text.lower()

        # 1. 积极情绪词汇 - 如果出现这些，负面情绪应该很低
        positive_keywords = [
            "开心", "快乐", "高兴", "愉快", "幸福", "满足", "不错", "很好", "太好了",
            "喜欢", "爱", "享受", "舒服", "轻松", "顺利", "成功", "棒", "赞"
        ]

        # 2. 日常问候/礼貌用语
        greeting_keywords = [
            "你好", "您好", "早上好", "晚上好", "晚安", "再见", "谢谢", "感谢",
            "天气", "好吗", "怎么样", "最近", "在吗", "在不在"
        ]

        # 3. 中性/闲聊词汇
        neutral_keywords = [
            "今天", "明天", "昨天", "吃", "喝", "玩", "去", "来", "买",
            "看看", "说说", "聊聊", "问问", "知道", "明白", "了解"
        ]

        # 统计积极/中性词汇出现次数
        positive_count = sum(1 for kw in positive_keywords if kw in text_lower)
        greeting_count = sum(1 for kw in greeting_keywords if kw in text_lower)
        neutral_count = sum(1 for kw in neutral_keywords if kw in text_lower)

        # 计算当前负面情绪总分
        negative_total = sum(dbt_scores.values())

        # 判断：如果是明显积极/中性的文本，但AI给了高负面分，则修正
        is_likely_positive = (positive_count >= 1) or (greeting_count >= 1)
        is_likely_neutral = (neutral_count >= 2) and (negative_total > 0.3)

        if is_likely_positive or is_likely_neutral:
            # 进一步检查：是否有明确的负面情绪关键词
            clear_negative_keywords = [
                "焦虑", "空虚", "绝望", "难过", "痛苦", "抑郁", "悲伤", "恐惧",
                "愤怒", "讨厌", "烦躁", "不安", "紧张", "担心", "害怕", "孤独",
                "失眠", "睡不着", "低落", "压抑", "崩溃", "累", "疲惫"
            ]
            has_clear_negative = any(kw in text_lower for kw in clear_negative_keywords)

            # 如果没有明确的负面关键词，清零所有情绪
            if not has_clear_negative:
                logger.info(f"检测到积极/中性文本（积极:{positive_count}, 问候:{greeting_count}, 中性:{neutral_count}），清零负面情绪")
                dbt_scores = {emotion: 0.0 for emotion in dbt_scores}

        return dbt_scores

    def _rule_based_emotion_analysis(self, text: str) -> Dict[str, float]:
        """基于规则的情绪分析（备用方案）"""
        scores = {emotion: 0.0 for emotion in self.dbt_emotions}

        # DBT核心情绪关键词映射
        emotion_keywords = {
            "空虚感": ["空虚", "空洞", "没什么", "无所谓", "麻木"],
            "羞愧": ["羞愧", "羞耻", "丢脸", "没面子", "不值得"],
            "激越": ["激动", "烦躁", "坐立不安", "急躁", "冲动"],
            "自伤冲动": ["想伤害自己", "想自残", "想割", "想痛", "惩罚自己"],
            "愤怒": ["生气", "愤怒", "恼火", "恨", "不公平"],
            "悲伤": ["难过", "伤心", "痛苦", "想哭", "抑郁"],
            "焦虑": ["担心", "焦虑", "害怕", "紧张", "不安"],
            "恐惧": ["恐惧", "害怕", "惊恐", "吓死", "恐慌"],
            "厌恶": ["厌恶", "恶心", "讨厌", "反感", "排斥"],
            "内疚": ["内疚", "对不起", "愧疚", "抱歉", "都是我的错"],
            "孤独": ["孤独", "孤单", "没人", "被抛弃", "一个人"],
            "绝望": ["绝望", "没希望", "无望", "活不下去", "没有意义"]
        }

        text_lower = text.lower()
        for emotion, keywords in emotion_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    scores[emotion] += 1.0

        # 归一化
        total = sum(scores.values()) or 1.0
        return {k: v / total for k, v in scores.items()}

    def extract_audio_features(self, audio_path: Optional[str] = None,
                               audio_data: Optional[np.ndarray] = None,
                               sample_rate: int = 16000) -> Optional[Dict[str, float]]:
        """
        提取语音声学特征
        包括：音调、颤抖、语速等
        """
        if audio_path is None and audio_data is None:
            return None

        try:
            # 加载音频
            if audio_path:
                y, sr = librosa.load(audio_path, sr=sample_rate)
            else:
                y, sr = audio_data, sample_rate

            features = {}

            # 1. 音调特征 (基频F0)
            pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
            pitch_values = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    pitch_values.append(pitch)

            if pitch_values:
                features['mean_pitch'] = float(np.mean(pitch_values))
                features['std_pitch'] = float(np.std(pitch_values))
                features['pitch_range'] = float(np.max(pitch_values) - np.min(pitch_values))

            # 2. 颤抖特征（音抖）
            if len(pitch_values) > 1:
                pitch_diff = np.abs(np.diff(pitch_values))
                features['jitter'] = float(np.mean(pitch_diff))
                features['shimmer'] = float(np.std(pitch_diff))

            # 3. 语速特征
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            features['tempo'] = float(tempo)

            # 4. 能量特征
            features['energy'] = float(np.mean(librosa.feature.rms(y=y)))

            # 5. 零交叉率（紧张度指标）
            features['zero_crossing_rate'] = float(np.mean(librosa.feature.zero_crossing_rate(y)))

            # 6. MFCC特征（语音情感）
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            features['mfcc_mean'] = float(np.mean(mfccs))
            features['mfcc_std'] = float(np.std(mfccs))

            return features

        except Exception as e:
            logger.error(f"音频特征提取失败: {e}")
            return None

    def _call_multimodal_api(self, image_base64: str) -> Optional[Dict]:
        """调用ModelScope多模态API"""
        if not self.api_key:
            return None

        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }

            dbt_emotions_str = "、".join(self.dbt_emotions)
            prompt = f"""你是一个专业的面部表情和肢体语言情绪分析专家。请仔细观察图片中人物的情绪状态。

基于DBT（辩证行为疗法）的12种核心情绪：{dbt_emotions_str}

**重要分析指引：**

1. **哭泣/流泪识别**：如果人物在哭泣、流泪、眼眶湿润、有泪痕，必须给出高悲伤分数(≥0.7)，同时给予较高的绝望(≥0.4)和孤独(≥0.3)分数

2. **面部表情细节**：
   - 眉毛：紧皱、下垂→焦虑/悲伤/绝望
   - 眼睛：红肿、湿润、泪痕→悲伤/绝望
   - 嘴巴：嘴角下垂、颤抖→悲伤/绝望

3. **肢体语言**：
   - 蜷缩姿态、抱头→绝望/悲伤
   - 委靡、低垂的头→绝望/空虚感

4. **整体氛围**：
   - 暗沉、压抑的环境→绝望/悲伤/孤独
   - 孤独、隔离的感觉→孤独/绝望

**打分规则：**
- 如果明显在哭泣：悲伤≥0.7，绝望≥0.4，孤独≥0.3
- 如果表情痛苦：悲伤≥0.6，焦虑≥0.4
- 如果情绪低落：绝望≥0.5，空虚感≥0.4
- 如果微笑/开心：所有负面情绪为0

请只输出JSON格式的情绪分数，不要添加任何其他说明：
{{
    "空虚感": 0.0,
    "羞愧": 0.0,
    "激越": 0.0,
    "自伤冲动": 0.0,
    "愤怒": 0.0,
    "悲伤": 0.0,
    "焦虑": 0.0,
    "恐惧": 0.0,
    "厌恶": 0.0,
    "内疚": 0.0,
    "孤独": 0.0,
    "绝望": 0.0
}}"""

            data = {
                'model': self.models.get('multimodal'),
                'messages': [
                    {
                        'role': 'user',
                        'content': [
                            {'type': 'text', 'text': prompt},
                            {'type': 'image_url', 'image_url': {'url': f"data:image/jpeg;base64,{image_base64}"}}
                        ]
                    }
                ],
                'temperature': 0.0,
                'max_tokens': 500
            }

            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                logger.info("ModelScope多模态API调用成功")
                return result
            else:
                logger.warning(f"多模态API错误: {response.text}")
                return None

        except Exception as e:
            logger.error(f"多模态API调用失败: {e}")
            return None

    def extract_video_features(self, video_path: Optional[str] = None,
                               frame: Optional[np.ndarray] = None) -> Optional[Dict[str, float]]:
        """
        提取视频/图像特征
        结合计算机视觉特征(CV)和语义情绪特征(Multimodal LLM)
        """
        if video_path is None and frame is None:
            return None

        try:
            if video_path:
                cap = cv2.VideoCapture(video_path)
                ret, frame = cap.read()
                cap.release()
                if not ret:
                    return None

            features = {}

            # --- 1. 基础CV特征 ---
            # 转换为灰度图
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            features['brightness'] = float(np.mean(gray))
            features['contrast'] = float(np.std(gray))

            edges = cv2.Canny(gray, 50, 150)
            features['edge_density'] = float(np.sum(edges > 0) / edges.size)

            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            features['hue_mean'] = float(np.mean(hsv[:, :, 0]))
            features['saturation_mean'] = float(np.mean(hsv[:, :, 1]))
            features['value_mean'] = float(np.mean(hsv[:, :, 2]))

            # --- 1.5 CV特征的DBT情绪推断（后备规则）---
            # 检测暗沉、压抑的图像特征
            brightness = features['brightness']
            saturation = features['saturation_mean']
            value = features['value_mean']

            # 暗沉色调 + 低饱和度 → 可能是悲伤/绝望/孤独
            if brightness < 100 and saturation < 80:
                cv_sadness_boost = 0.3  # 额外的悲伤分数
                features['悲伤'] = max(features.get('悲伤', 0), cv_sadness_boost)
                features['绝望'] = max(features.get('绝望', 0), cv_sadness_boost * 0.7)
                features['孤独'] = max(features.get('孤独', 0), cv_sadness_boost * 0.5)
                logger.info(f"CV特征检测到暗沉图像，提升悲伤相关情绪分数: brightness={brightness:.2f}, saturation={saturation:.2f}")

            # --- 2. 语义情绪特征 (Qwen3-VL) ---
            try:
                # 图像编码为Base64
                _, buffer = cv2.imencode('.jpg', frame)
                img_base64 = base64.b64encode(buffer).decode('utf-8')

                # 调用多模态API
                api_result = self._call_multimodal_api(img_base64)

                if api_result:
                    semantic_emotions = self._parse_api_result(api_result, text="[IMAGE_ANALYSIS]")
                    if semantic_emotions:
                        logger.info(f"图像语义情绪分析结果: {semantic_emotions}")
                        # 将语义情绪合并到特征中，与CV特征取最大值
                        for emo, score in semantic_emotions.items():
                            current = features.get(emo, 0)
                            features[emo] = max(current, score)

                        # 如果语义分析检测到悲伤，但分数偏低，进行提升
                        if semantic_emotions.get('悲伤', 0) > 0.2 and semantic_emotions.get('悲伤', 0) < 0.5:
                            # 检查是否有其他负面情绪支持
                            negative_total = sum(semantic_emotions.get(e, 0) for e in ['绝望', '孤独', '焦虑', '恐惧'])
                            if negative_total > 0.3:
                                # 提升悲伤分数到至少0.6
                                features['悲伤'] = max(features.get('悲伤', 0), 0.6)
                                features['绝望'] = max(features.get('绝望', 0), 0.4)
                                features['孤独'] = max(features.get('孤独', 0), 0.3)
                                logger.info(f"检测到复合负面情绪，提升悲伤分数至≥0.6")
            except Exception as e:
                logger.warning(f"语义情绪分析失败，仅使用CV特征: {e}")

            return features

        except Exception as e:
            logger.error(f"视频特征提取失败: {e}")
            return None

    def multimodal_fusion(self, text_emotion: Dict[str, float],
                          audio_features: Optional[Dict[str, float]] = None,
                          video_features: Optional[Dict[str, float]] = None) -> np.ndarray:
        """
        多模态自适应融合策略
        当文本语义模糊时自动加大音视频权重
        """
        # 获取权重
        text_weight = self.multimodal_config.get('text_weight', 0.6)
        audio_weight = self.multimodal_config.get('audio_weight', 0.25)
        video_weight = self.multimodal_config.get('video_weight', 0.15)

        # 自适应权重调整
        if self.multimodal_config.get('adaptive_fusion', True):
            # 计算文本情绪的确定性（熵的倒数）
            text_probs = np.array(list(text_emotion.values()))
            text_entropy = -np.sum(text_probs * np.log(text_probs + 1e-10))
            certainty = 1.0 / (text_entropy + 1.0)

            # 文本越不确定，音视频权重越高
            if certainty < 0.5:
                weight_transfer = (0.5 - certainty) * 0.3
                text_weight -= weight_transfer
                if audio_features is not None:
                    audio_weight += weight_transfer * 0.6
                if video_features is not None:
                    video_weight += weight_transfer * 0.4

        # 归一化权重
        total_weight = text_weight + audio_weight + video_weight
        text_weight /= total_weight
        audio_weight /= total_weight
        video_weight /= total_weight

        # 构建融合向量
        vector_dim = 128
        fused_vector = np.zeros(vector_dim)

        # 文本向量（前64维）
        text_vec = np.zeros(64)
        for i, (emotion, score) in enumerate(text_emotion.items()):
            if i < 64:
                text_vec[i] = score
        fused_vector[:64] += text_vec * text_weight

        # 音频向量（中间32维）
        if audio_features:
            audio_vec = np.array(list(audio_features.values()))[:32]
            if len(audio_vec) < 32:
                audio_vec = np.pad(audio_vec, (0, 32 - len(audio_vec)))
            fused_vector[64:96] += audio_vec * audio_weight
        else:
            fused_vector[64:96] += np.zeros(32) * audio_weight

        # 视频向量（后32维）
        if video_features:
            video_vec = np.array(list(video_features.values()))[:32]
            if len(video_vec) < 32:
                video_vec = np.pad(video_vec, (0, 32 - len(video_vec)))
            fused_vector[96:128] += video_vec * video_weight
        else:
            fused_vector[96:128] += np.zeros(32) * video_weight

        return fused_vector

    def extract(self, text: str,
                audio_path: Optional[str] = None,
                audio_data: Optional[Dict] = None,
                video_path: Optional[str] = None,
                frame: Optional[np.ndarray] = None) -> EmotionFeatures:
        """
        完整的情绪特征提取流程
        """
        # 1. 提取文本情绪
        text_emotion = self.extract_text_emotion(text)

        # 2. 计算唤醒度（最大情绪得分的强度）
        text_arousal = max(text_emotion.values()) if text_emotion else 0.0

        # 3. 提取音频特征
        if audio_data:
            audio_features = self.extract_audio_features(
                audio_data=np.array(audio_data.get('data')),
                sample_rate=audio_data.get('sample_rate', 16000)
            )
        else:
            audio_features = self.extract_audio_features(audio_path)

        # 4. 提取视频特征
        video_features = self.extract_video_features(video_path, frame)

        # 5. 多模态融合
        multimodal_vector = self.multimodal_fusion(
            text_emotion, audio_features, video_features
        )

        # 6. 计算置信度
        confidence = self._calculate_confidence(
            text_emotion, audio_features, video_features
        )

        return EmotionFeatures(
            text_emotion=text_emotion,
            text_arousal=text_arousal,
            audio_features=audio_features,
            video_features=video_features,
            multimodal_vector=multimodal_vector,
            confidence=confidence
        )

    def _calculate_confidence(self, text_emotion: Dict,
                              audio_features: Optional[Dict],
                              video_features: Optional[Dict]) -> float:
        """计算整体置信度"""
        confidence = 0.5

        # 文本情绪确定性
        if text_emotion:
            max_score = max(text_emotion.values())
            confidence += max_score * 0.3

        # 音频和视频存在性加成
        if audio_features:
            confidence += 0.1
        if video_features:
            confidence += 0.1

        return min(confidence, 1.0)
