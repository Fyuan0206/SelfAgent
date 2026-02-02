"""
智能意图路由系统
实现L1/L2/L3三级分流路由
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np
from loguru import logger


class RouteLevel(Enum):
    """路由级别"""
    L1_QUICK = "L1_QUICK"  # 快速通路（日常闲聊）
    L2_INTERVENTION = "L2_INTERVENTION"  # 干预通路（DBT技能匹配）
    L3_CRISIS = "L3_CRISIS"  # 危机重定向（最高优先级）


@dataclass
class RouteResult:
    """路由结果"""
    level: RouteLevel
    confidence: float
    reason: str
    suggested_action: str
    requires_dbt: bool
    crisis_flag: bool


class IntelligentRouter:
    """智能意图路由器"""

    def __init__(self, config: Dict):
        self.config = config
        self.routing_config = config.get('routing', {})
        self.dbt_emotions = config.get('dbt_emotions', [])  # 添加DBT情绪列表

        # 阈值配置
        self.l1_threshold = self.routing_config.get('l1_quick_threshold', 0.3)
        self.l2_threshold = self.routing_config.get('l2_intervention_threshold', 0.7)
        self.crisis_keywords = set(self.routing_config.get('l3_crisis_keywords', []))

        # 路由历史（用于自适应优化）
        self.route_history = []

    def route(self, text: str, emotion_features: Dict,
              audio_features: Optional[Dict] = None,
              video_features: Optional[Dict] = None) -> RouteResult:
        """
        执行智能路由决策

        Args:
            text: 输入文本
            emotion_features: 情绪特征
            audio_features: 音频特征（可选）
            video_features: 视频特征（可选）

        Returns:
            RouteResult: 路由结果
        """
        # 优先级1: 检查危机信号（L3）
        crisis_result = self._check_crisis_signals(text, emotion_features, audio_features, video_features)
        if crisis_result.crisis_flag:
            logger.warning(f"触发L3危机路由: {crisis_result.reason}")
            return crisis_result

        # 优先级2: 检查是否需要DBT干预（L2）
        intervention_result = self._check_intervention_needed(emotion_features, audio_features, video_features)
        if intervention_result.level == RouteLevel.L2_INTERVENTION:
            logger.info(f"触发L2干预路由: {intervention_result.reason}")
            return intervention_result

        # 优先级3: 默认快速通路（L1）
        logger.info("触发L1快速通路")
        return RouteResult(
            level=RouteLevel.L1_QUICK,
            confidence=0.8,
            reason="日常闲聊或社交辞令",
            suggested_action="直接回复，无需深度评估",
            requires_dbt=False,
            crisis_flag=False
        )

    def _check_crisis_signals(self, text: str, emotion_features: Dict,
                              audio_features: Optional[Dict],
                              video_features: Optional[Dict]) -> RouteResult:
        """
        检查危机信号（L3级别）
        包括：关键词检测、高风险表情、极端情绪
        """
        crisis_indicators = []

        # 1. 关键词检测
        text_lower = text.lower()
        for keyword in self.crisis_keywords:
            if keyword in text_lower:
                crisis_indicators.append(f"检测到危机关键词: {keyword}")
                logger.critical(f"危机关键词触发: {keyword} in {text[:50]}...")

        # 2. 极端情绪检测
        if '自伤冲动' in emotion_features:
            self_harm_score = emotion_features['自伤冲动']
            if self_harm_score > 0.5:
                crisis_indicators.append(f"自伤冲动得分过高: {self_harm_score:.2f}")
                logger.critical(f"自伤冲动触发: {self_harm_score:.2f}")

        # 3. 绝望情绪检测（降低阈值，提高敏感度）
        if '绝望' in emotion_features:
            despair_score = emotion_features['绝望']
            if despair_score > 0.4:  # 从0.7降到0.4
                crisis_indicators.append(f"绝望情绪得分过高: {despair_score:.2f}")

        # 3.1 空虚感 + 绝望 组合 = 高危机
        emptiness = emotion_features.get('空虚感', 0.0)
        despair = emotion_features.get('绝望', 0.0)
        if emptiness > 0.3 and despair > 0.3:
            crisis_indicators.append(f"空虚感与绝望并存: {emptiness:.2f}+{despair:.2f}")

        # 3.2 自伤冲动 + 绝望 组合 = 最高危机
        self_harm = emotion_features.get('自伤冲动', 0.0)
        if self_harm > 0.3 and despair > 0.3:
            crisis_indicators.append(f"自伤冲动与绝望并存: {self_harm:.2f}+{despair:.2f}")

        # 4. 音频危机信号（颤抖、异常语速）
        if audio_features:
            # 音抖过高可能表示极度紧张或恐慌
            if audio_features.get('jitter', 0) > 50:
                crisis_indicators.append(f"音频音抖异常: {audio_features['jitter']:.2f}")

            # 语速异常（极快或极慢）
            tempo = audio_features.get('tempo', 120)
            if tempo > 180 or tempo < 60:
                crisis_indicators.append(f"语速异常: {tempo:.2f} BPM")

        # 5. 视频危机信号（异常表情）
        if video_features:
            # 对比度异常可能表示极端表情
            if video_features.get('edge_density', 0) > 0.3:
                crisis_indicators.append(f"面部表情张力过高: {video_features['edge_density']:.2f}")

        # 判定是否为危机
        if crisis_indicators:
            return RouteResult(
                level=RouteLevel.L3_CRISIS,
                confidence=1.0,
                reason="; ".join(crisis_indicators),
                suggested_action="立即启动最高优先级干预，联系紧急联系人",
                requires_dbt=True,
                crisis_flag=True
            )

        return RouteResult(
            level=RouteLevel.L1_QUICK,
            confidence=0.0,
            reason="",
            suggested_action="",
            requires_dbt=False,
            crisis_flag=False
        )

    def _check_intervention_needed(self, emotion_features: Dict,
                                    audio_features: Optional[Dict],
                                    video_features: Optional[Dict]) -> RouteResult:
        """
        检查是否需要DBT干预（L2级别）
        包括：情绪强度、复合情绪、情绪斜率
        """
        intervention_indicators = []
        intervention_score = 0.0

        # 1. 检查DBT核心复合情绪
        dbt_core_emotions = ['空虚感', '羞愧', '激越', '自伤冲动']
        for emotion in dbt_core_emotions:
            if emotion in emotion_features:
                score = emotion_features[emotion]
                if score > 0.3:
                    intervention_indicators.append(f"检测到核心情绪: {emotion} ({score:.2f})")
                    intervention_score += score * 0.3

        # 2. 检查负面情绪总分（使用配置中的DBT情绪列表）
        negative_score = sum(emotion_features.get(e, 0.0) for e in self.dbt_emotions)
        if negative_score > 0.5:
            intervention_indicators.append(f"负面情绪总分: {negative_score:.2f}")
            intervention_score += negative_score * 0.3

        # 2.1 检查多情绪组合（多个负面情绪同时出现）
        active_negative_count = sum(1 for e in self.dbt_emotions if emotion_features.get(e, 0.0) > 0.2)
        if active_negative_count >= 2:
            intervention_indicators.append(f"多情绪组合: {active_negative_count}种负面情绪")
            intervention_score += 0.3

        # 3. 检查情绪唤醒度
        arousal = max(emotion_features.values()) if emotion_features else 0.0
        if arousal > self.l2_threshold:
            intervention_indicators.append(f"情绪唤醒度过高: {arousal:.2f}")
            intervention_score += 0.3

        # 4. 音频辅助判定
        if audio_features:
            # 语速快 + 能量高 = 激越状态
            if audio_features.get('tempo', 0) > 140 and audio_features.get('energy', 0) > 0.5:
                intervention_indicators.append("音频检测到激越状态")
                intervention_score += 0.2

            # 音抖高 = 紧张/焦虑
            if audio_features.get('jitter', 0) > 30:
                intervention_indicators.append("音频检测到紧张状态")
                intervention_score += 0.15

        # 5. 视频辅助判定
        if video_features:
            # 边缘密度高 = 表情紧张
            if video_features.get('edge_density', 0) > 0.2:
                intervention_indicators.append("视频检测到表情紧张")
                intervention_score += 0.1

        # 判定是否需要干预
        logger.info(f"L2判定: score={intervention_score:.2f}, threshold={self.l2_threshold}, indicators={len(intervention_indicators)}, content={intervention_indicators}")
        if intervention_score >= self.l2_threshold or len(intervention_indicators) >= 2:
            return RouteResult(
                level=RouteLevel.L2_INTERVENTION,
                confidence=min(intervention_score, 1.0),
                reason="; ".join(intervention_indicators),
                suggested_action="激活DBT技能匹配模块",
                requires_dbt=True,
                crisis_flag=False
            )

        # 未达到干预阈值
        logger.info(f"未达到L2阈值: score={intervention_score:.2f} < {self.l2_threshold}, indicators={len(intervention_indicators)} < 2")
        return RouteResult(
            level=RouteLevel.L1_QUICK,
            confidence=0.0,
            reason="",
            suggested_action="",
            requires_dbt=False,
            crisis_flag=False
        )

    def calculate_emotion_slope(self, emotion_history: List[Dict]) -> float:
        """
        计算情绪强度斜率
        用于判断情绪是否在快速恶化
        """
        if len(emotion_history) < 2:
            return 0.0

        # 取最近5次记录
        recent = emotion_history[-5:]

        # 计算负面情绪平均值的变化趋势
        negative_emotions = ['悲伤', '焦虑', '恐惧', '绝望', '愤怒']
        scores = []
        for record in recent:
            negative_score = sum(record.get(e, 0.0) for e in negative_emotions)
            scores.append(negative_score)

        # 计算斜率（线性回归）
        if len(scores) < 2:
            return 0.0

        x = np.arange(len(scores))
        y = np.array(scores)
        slope = np.polyfit(x, y, 1)[0]

        return float(slope)

    def analyze_conversation_context(self, conversation_history: List[Dict]) -> Dict:
        """
        分析对话上下文
        识别对话模式（如：反复抱怨、自我否定等）
        """
        context_features = {
            'repetition_pattern': False,
            'escalation_pattern': False,
            'self_critical_pattern': False,
            'help_seeking_pattern': False
        }

        if len(conversation_history) < 3:
            return context_features

        recent_texts = [msg.get('text', '') for msg in conversation_history[-3:]]

        # 1. 重复模式检测（简化的关键词重复检测）
        all_words = set()
        for text in recent_texts:
            words = set(text.split())
            if all_words.intersection(words):
                context_features['repetition_pattern'] = True
            all_words.update(words)

        # 2. 升级模式检测（情绪逐渐恶化）
        if len(conversation_history) >= 5:
            slope = self.calculate_emotion_slope(conversation_history)
            if slope > 0.1:  # 负面情绪持续上升
                context_features['escalation_pattern'] = True

        # 3. 自我否定模式检测
        self_negative_words = ['不行', '没用', '失败', '糟糕', '差劲', '笨']
        for text in recent_texts:
            if any(word in text for word in self_negative_words):
                context_features['self_critical_pattern'] = True
                break

        # 4. 求助模式检测
        help_words = ['帮帮我', '不知道怎么办', '求助', '怎么办']
        for text in recent_texts:
            if any(word in text for word in help_words):
                context_features['help_seeking_pattern'] = True
                break

        return context_features
