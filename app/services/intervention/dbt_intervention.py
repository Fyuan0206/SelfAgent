"""
风险分级与干预触发模块
只负责评估风险等级和触发信号，不包含具体DBT技能（由模块2负责）
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import numpy as np
from loguru import logger


class RiskLevel(Enum):
    """风险等级"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class InterventionTrigger:
    """干预触发器"""
    triggered: bool
    risk_level: RiskLevel
    emotion_slope: float
    urgency_score: float  # 0-1，紧急程度
    intervention_reason: str
    # 移除recommended_skills，由模块2负责
    trigger_signals: Dict[str, float]  # 触发信号详情


class RiskAssessmentEngine:
    """风险评估引擎"""

    def __init__(self, config: Dict):
        self.config = config
        self.routing_config = config.get('routing', {})

        # 情绪历史（用于计算斜率）
        self.emotion_history = []
        self.max_history = 100

    def evaluate_risk(self, emotion_features: Dict,
                      emotion_slope: float = 0.0,
                      conversation_context: Optional[Dict] = None) -> InterventionTrigger:
        """
        评估风险等级和干预触发信号

        Args:
            emotion_features: 情绪特征
            emotion_slope: 情绪强度斜率
            conversation_context: 对话上下文特征

        Returns:
            InterventionTrigger: 干预触发决策（不包含具体技能推荐）
        """
        # 1. 计算风险等级
        risk_level = self._calculate_risk_level(emotion_features, emotion_slope, conversation_context)

        # 2. 计算紧急程度分数
        urgency_score = self._calculate_urgency_score(emotion_features, emotion_slope)

        # 3. 提取触发信号（供模块2使用）
        trigger_signals = self._extract_trigger_signals(emotion_features, emotion_slope)

        # 4. 判断是否触发干预
        triggered = self._should_trigger_intervention(risk_level, urgency_score)

        # 5. 生成干预原因说明
        reason = self._generate_intervention_reason(emotion_features, emotion_slope, risk_level)

        # 6. 记录情绪历史
        self._record_emotion_history(emotion_features)

        return InterventionTrigger(
            triggered=triggered,
            risk_level=risk_level,
            emotion_slope=emotion_slope,
            urgency_score=urgency_score,
            intervention_reason=reason,
            trigger_signals=trigger_signals
        )

    def _calculate_risk_level(self, emotion_features: Dict,
                              emotion_slope: float,
                              conversation_context: Optional[Dict]) -> RiskLevel:
        """计算风险等级"""
        risk_score = 0.0

        # 1. 自伤冲动（最高权重）
        self_harm = emotion_features.get('自伤冲动', 0.0)
        if self_harm > 0.7:
            risk_score += 40
        elif self_harm > 0.4:
            risk_score += 20

        # 2. 绝望情绪
        despair = emotion_features.get('绝望', 0.0)
        if despair > 0.7:
            risk_score += 30
        elif despair > 0.4:
            risk_score += 15

        # 3. 激越状态
        agitation = emotion_features.get('激越', 0.0)
        if agitation > 0.7:
            risk_score += 20
        elif agitation > 0.4:
            risk_score += 10

        # 4. 情绪斜率（恶化趋势）
        if emotion_slope > 0.3:
            risk_score += 25  # 快速恶化
        elif emotion_slope > 0.1:
            risk_score += 15  # 缓慢恶化

        # 5. 复合负面情绪
        negative_emotions = ['悲伤', '焦虑', '恐惧', '羞愧', '内疚']
        negative_total = sum(emotion_features.get(e, 0.0) for e in negative_emotions)
        if negative_total > 3.0:
            risk_score += 15
        elif negative_total > 2.0:
            risk_score += 10

        # 6. 对话上下文
        if conversation_context:
            if conversation_context.get('escalation_pattern'):
                risk_score += 10
            if conversation_context.get('self_critical_pattern'):
                risk_score += 5

        # 7. 空虚感（长期风险）
        emptiness = emotion_features.get('空虚感', 0.0)
        if emptiness > 0.6:
            risk_score += 10

        # 映射到风险等级
        if risk_score >= 70:
            return RiskLevel.CRITICAL
        elif risk_score >= 50:
            return RiskLevel.HIGH
        elif risk_score >= 30:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def _calculate_urgency_score(self, emotion_features: Dict,
                                  emotion_slope: float) -> float:
        """计算紧急程度分数（0-1）"""
        urgency = 0.0

        # 关键指标权重
        weights = {
            '自伤冲动': 0.35,
            '绝望': 0.25,
            '激越': 0.15,
            '焦虑': 0.10,
            '悲伤': 0.10,
            'slope': 0.05
        }

        # 情绪得分
        for emotion, weight in weights.items():
            if emotion == 'slope':
                # 情绪斜率的贡献
                urgency += min(emotion_slope * 2, 1.0) * weight
            else:
                urgency += emotion_features.get(emotion, 0.0) * weight

        return min(urgency, 1.0)

    def _extract_trigger_signals(self, emotion_features: Dict,
                                  emotion_slope: float) -> Dict[str, float]:
        """
        提取触发信号
        供模块2（DBT技能匹配）使用
        """
        signals = {
            'self_harm_impulse': emotion_features.get('自伤冲动', 0.0),
            'despair_level': emotion_features.get('绝望', 0.0),
            'agitation_level': emotion_features.get('激越', 0.0),
            'emptiness_level': emotion_features.get('空虚感', 0.0),
            'shame_level': emotion_features.get('羞愧', 0.0),
            'emotion_slope': emotion_slope,
            'negative_total': sum([
                emotion_features.get('悲伤', 0.0),
                emotion_features.get('焦虑', 0.0),
                emotion_features.get('恐惧', 0.0),
                emotion_features.get('愤怒', 0.0),
                emotion_features.get('内疚', 0.0)
            ])
        }
        return signals

    def _should_trigger_intervention(self, risk_level: RiskLevel,
                                      urgency_score: float) -> bool:
        """判断是否应该触发干预"""
        # 高风险以上必须干预
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            return True

        # 中等风险 + 高紧急程度
        if risk_level == RiskLevel.MEDIUM and urgency_score > 0.6:
            return True

        # 低风险一般不干预
        return False

    def _generate_intervention_reason(self, emotion_features: Dict,
                                       emotion_slope: float,
                                       risk_level: RiskLevel) -> str:
        """生成干预原因说明"""
        reasons = []

        # 找出主要情绪
        sorted_emotions = sorted(emotion_features.items(), key=lambda x: x[1], reverse=True)
        top_emotions = sorted_emotions[:3]

        for emotion, score in top_emotions:
            if score > 0.4:
                reasons.append(f"{emotion}(强度{score:.2f})")

        # 情绪斜率
        if emotion_slope > 0.2:
            reasons.append(f"情绪快速恶化(斜率{emotion_slope:.2f})")

        # 风险等级
        reasons.append(f"风险等级: {risk_level.value}")

        return "; ".join(reasons) if reasons else "未检测到明显风险因素"

    def _record_emotion_history(self, emotion_features: Dict):
        """记录情绪历史"""
        import time
        record = {
            'timestamp': time.time(),
            'emotions': emotion_features.copy()
        }
        self.emotion_history.append(record)

        # 限制历史长度
        if len(self.emotion_history) > self.max_history:
            self.emotion_history.pop(0)

    def get_emotion_baseline(self) -> Dict[str, float]:
        """计算情绪基准线（日常情绪中位数）"""
        if not self.emotion_history:
            return {}

        # 只使用最近30天数据（假设每次记录间隔约1天）
        recent = self.emotion_history[-30:]

        baseline = {}
        for emotion in self.dbt_skills['distress_tolerance']['trigger_emotions']:
            scores = [r['emotions'].get(emotion, 0.0) for r in recent]
            baseline[emotion] = float(np.median(scores)) if scores else 0.0

        return baseline

    def compare_to_baseline(self, current_emotions: Dict) -> Dict[str, float]:
        """将当前情绪与基准线对比"""
        baseline = self.get_emotion_baseline()

        deviations = {}
        for emotion, baseline_score in baseline.items():
            current_score = current_emotions.get(emotion, 0.0)
            deviations[emotion] = current_score - baseline_score

        return deviations

    def get_intervention_summary(self, trigger: InterventionTrigger) -> str:
        """生成干预摘要"""
        prompt_parts = [
            "# 风险评估结果\n",
            f"**风险等级**: {trigger.risk_level.value}",
            f"**紧急程度**: {trigger.urgency_score:.2f}/1.0",
            f"**干预触发**: {'是' if trigger.triggered else '否'}",
            f"**评估原因**: {trigger.intervention_reason}\n",
            "**触发信号详情**:"
        ]

        for signal, value in trigger.trigger_signals.items():
            if value > 0.1:  # 只显示有意义的信号
                prompt_parts.append(f"- {signal}: {value:.2f}")

        if trigger.risk_level == RiskLevel.CRITICAL:
            prompt_parts.append("\n⚠️ 警告：检测到危机状态，请立即采取行动！")

        return "\n".join(prompt_parts)
