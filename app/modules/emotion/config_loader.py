"""
配置加载器
从.env文件加载情绪识别系统的配置
"""

import os
from typing import Dict, List, Any
from pathlib import Path
from dotenv import load_dotenv

class EmotionConfigLoader:
    """情绪识别配置加载器"""

    def __init__(self, env_path: str = None):
        """
        初始化配置加载器

        Args:
            env_path: .env文件路径，默认为项目根目录下的.env
        """
        if env_path is None:
            # 默认使用项目根目录下的.env
            project_root = Path(__file__).parent.parent.parent.parent
            env_path = project_root / ".env"

        load_dotenv(env_path)
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """从环境变量加载配置"""
        config = {}

        # ModelScope API配置
        config['modelscope'] = {
            'api_key': os.getenv('MODELSCOPE_API_KEY', ''),
            'emotion_model': os.getenv('MODELSCOPE_EMOTION_MODEL', 'Qwen/Qwen2.5-7B-Instruct'),
            'multimodal_model': os.getenv('MODELSCOPE_MULTIMODAL_MODEL', 'Qwen/Qwen3-VL-8B-Instruct')
        }

        # 讯飞语音识别配置
        config['xunfei_asr'] = {
            'app_id': os.getenv('XUNFEI_APP_ID', ''),
            'api_secret': os.getenv('XUNFEI_API_SECRET', ''),
            'api_key': os.getenv('XUNFEI_API_KEY', ''),
            'host': os.getenv('XUNFEI_HOST', 'iat.xf-yun.com'),
            'path': os.getenv('XUNFEI_PATH', '/v1'),
            'sample_rate': int(os.getenv('XUNFEI_SAMPLE_RATE', '16000')),
            'channels': int(os.getenv('XUNFEI_CHANNELS', '1')),
            'bit_depth': int(os.getenv('XUNFEI_BIT_DEPTH', '16')),
            'format': os.getenv('XUNFEI_FORMAT', 'pcm'),
            'domain': os.getenv('XUNFEI_DOMAIN', 'slm'),
            'language': os.getenv('XUNFEI_LANGUAGE', 'zh_cn'),
            'accent': os.getenv('XUNFEI_ACCENT', 'mandarin'),
            'eos': int(os.getenv('XUNFEI_EOS', '6000'))
        }

        # 路由阈值配置
        crisis_keywords_str = os.getenv('ROUTING_L3_CRISIS_KEYWORDS', '自杀,自残,自毁,不想活,结束生命,死掉,杀死自己')
        config['routing'] = {
            'l1_quick_threshold': float(os.getenv('ROUTING_L1_QUICK_THRESHOLD', '0.3')),
            'l2_intervention_threshold': float(os.getenv('ROUTING_L2_INTERVENTION_THRESHOLD', '0.5')),
            'l3_crisis_keywords': [kw.strip() for kw in crisis_keywords_str.split(',')]
        }

        # DBT核心情绪标签
        emotions_str = os.getenv('DBT_EMOTIONS', '空虚感,羞愧,激越,自伤冲动,愤怒,悲伤,焦虑,恐惧,厌恶,内疚,孤独,绝望')
        config['dbt_emotions'] = [e.strip() for e in emotions_str.split(',')]

        # 情绪画像配置
        config['emotion_profile'] = {
            'baseline_window': int(os.getenv('EMOTION_PROFILE_BASELINE_WINDOW', '30')),
            'vector_dimension': int(os.getenv('EMOTION_PROFILE_VECTOR_DIMENSION', '128')),
            'update_threshold': float(os.getenv('EMOTION_PROFILE_UPDATE_THRESHOLD', '0.2'))
        }

        # 多模态权重配置
        adaptive_fusion = os.getenv('MULTIMODAL_ADAPTIVE_FUSION', 'true').lower() == 'true'
        config['multimodal'] = {
            'text_weight': float(os.getenv('MULTIMODAL_TEXT_WEIGHT', '0.6')),
            'audio_weight': float(os.getenv('MULTIMODAL_AUDIO_WEIGHT', '0.25')),
            'video_weight': float(os.getenv('MULTIMODAL_VIDEO_WEIGHT', '0.15')),
            'adaptive_fusion': adaptive_fusion
        }

        # 危机预警配置
        recipients_str = os.getenv('CRISIS_ALERT_RECIPIENTS', 'emergency@example.com')
        config['crisis'] = {
            'alert_recipients': [r.strip() for r in recipients_str.split(',')],
            'response_timeout': int(os.getenv('CRISIS_RESPONSE_TIMEOUT', '5000')),
            'max_priority': int(os.getenv('CRISIS_MAX_PRIORITY', '10'))
        }

        # 日志配置
        config['logging'] = {
            'level': os.getenv('LOGGING_LEVEL', 'INFO'),
            'file': os.getenv('LOGGING_FILE', 'logs/emotion_recognition.log'),
            'rotation': os.getenv('LOGGING_ROTATION', '10 MB')
        }

        # 存储配置
        config['storage_dir'] = os.getenv('STORAGE_DIR', 'profiles')
        config['temp_dir'] = os.getenv('TEMP_DIR', 'temp')
        config['logs_dir'] = os.getenv('LOGS_DIR', 'logs')

        return config

    def get_config(self) -> Dict[str, Any]:
        """获取完整配置字典"""
        return self.config

    def get(self, key: str, default=None):
        """获取配置项（支持点号分隔的路径）"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
