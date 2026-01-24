"""
情绪画像积累与Self-Agent深度同步模块
"""

import json
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from loguru import logger


@dataclass
class EmotionSnapshot:
    """情绪快照"""
    timestamp: float
    date: str
    emotions: Dict[str, float]
    arousal: float
    route_level: str
    risk_level: str
    context: str
    multimodal_vector: List[float]


@dataclass
class EmotionProfile:
    """用户情绪画像"""
    user_id: str
    created_at: str
    updated_at: str

    # 情绪基准线（日常情绪中位数）
    baseline_emotions: Dict[str, float]

    # 情绪快照历史
    snapshots: List[EmotionSnapshot]

    # 情绪模式特征
    emotion_patterns: Dict[str, any]

    # Self-Agent性格参数
    self_agent_params: Dict[str, any]

    # 统计信息
    total_interactions: int
    crisis_count: int
    intervention_count: int


class EmotionProfileManager:
    """情绪画像管理器"""

    def __init__(self, config: Dict, storage_dir: str = "profiles"):
        self.config = config
        self.profile_config = config.get('emotion_profile', {})
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)

        # 配置参数
        self.baseline_window = self.profile_config.get('baseline_window', 30)
        self.vector_dimension = self.profile_config.get('vector_dimension', 128)
        self.update_threshold = self.profile_config.get('update_threshold', 0.2)

    def create_profile(self, user_id: str) -> EmotionProfile:
        """创建新用户画像"""
        now = datetime.now().isoformat()

        profile = EmotionProfile(
            user_id=user_id,
            created_at=now,
            updated_at=now,
            baseline_emotions={},
            snapshots=[],
            emotion_patterns=self._init_emotion_patterns(),
            self_agent_params=self._init_self_agent_params(),
            total_interactions=0,
            crisis_count=0,
            intervention_count=0
        )

        self._save_profile(profile)
        logger.info(f"创建用户画像: {user_id}")
        return profile

    def load_profile(self, user_id: str) -> Optional[EmotionProfile]:
        """加载用户画像"""
        profile_path = self.storage_dir / f"{user_id}.json"

        if not profile_path.exists():
            logger.warning(f"用户画像不存在: {user_id}")
            return None

        try:
            with open(profile_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 重建EmotionSnapshot对象
            snapshots = [EmotionSnapshot(**s) for s in data['snapshots']]

            profile = EmotionProfile(
                user_id=data['user_id'],
                created_at=data['created_at'],
                updated_at=data['updated_at'],
                baseline_emotions=data['baseline_emotions'],
                snapshots=snapshots,
                emotion_patterns=data['emotion_patterns'],
                self_agent_params=data['self_agent_params'],
                total_interactions=data['total_interactions'],
                crisis_count=data['crisis_count'],
                intervention_count=data['intervention_count']
            )

            logger.info(f"加载用户画像: {user_id}")
            return profile

        except Exception as e:
            logger.error(f"加载画像失败: {e}")
            return None

    def update_profile(self, profile: EmotionProfile,
                      emotion_snapshot: EmotionSnapshot,
                      route_level: str,
                      risk_level: str):
        """
        更新用户画像
        包括：基准线更新、模式分析、Self-Agent参数优化
        """
        # 1. 添加快照
        profile.snapshots.append(emotion_snapshot)
        profile.total_interactions += 1

        # 2. 更新危机和干预计数
        if route_level == "L3_CRISIS":
            profile.crisis_count += 1
        if route_level in ["L2_INTERVENTION", "L3_CRISIS"]:
            profile.intervention_count += 1

        # 3. 更新情绪基准线
        profile.baseline_emotions = self._calculate_baseline(profile.snapshots)

        # 4. 分析情绪模式
        profile.emotion_patterns = self._analyze_emotion_patterns(profile)

        # 5. 更新Self-Agent性格参数
        profile.self_agent_params = self._update_self_agent_params(profile, emotion_snapshot)

        # 6. 更新时间戳
        profile.updated_at = datetime.now().isoformat()

        # 7. 保存
        self._save_profile(profile)

        logger.info(f"更新用户画像: {profile.user_id}")

    def _init_emotion_patterns(self) -> Dict[str, any]:
        """初始化情绪模式特征"""
        return {
            'typical_response': None,  # 典型情绪反应模式（愤怒/退缩）
            'triggers': [],  # 已知触发因素
            'coping_mechanisms': [],  # 有效的应对方式
            'time_patterns': {},  # 时间规律（如：早上更容易抑郁）
            'intensity_distribution': {},  # 强度分布
            'stability_score': 1.0,  # 情绪稳定性（0-1）
        }

    def _init_self_agent_params(self) -> Dict[str, any]:
        """初始化Self-Agent性格参数"""
        return {
            'personality_traits': {
                'neuroticism': 0.5,  # 神经质（情绪稳定性）
                'extraversion': 0.5,  # 外向性
                'openness': 0.5,  # 开放性
                'agreeableness': 0.5,  # 宜人性
                'conscientiousness': 0.5  # 尽责性
            },
            'response_style': {
                'under_pressure': 'calm',  # 压力下的反应风格
                'conflict_approach': 'avoidant',  # 冲突应对方式
                'decision_making': 'deliberate'  # 决策风格
            },
            'emotional_habits': {
                'frustration_response': 'withdrawal',  # 挫折反应（愤怒/退缩）
                'stress_coping': 'internalization',  # 压力应对
                'emotional_awareness': 0.5  # 情绪觉察能力
            },
            'voice_and_expression': {
                'typical_pitch': 1.0,  # 典型音调
                'speech_rate': 1.0,  # 语速
                'expression_intensity': 0.5  # 表情强度
            }
        }

    def _calculate_baseline(self, snapshots: List[EmotionSnapshot]) -> Dict[str, float]:
        """
        计算情绪基准线
        使用最近N天的中位数
        """
        if not snapshots:
            return {}

        # 筛选最近N天的快照
        cutoff_time = datetime.now().timestamp() - (self.baseline_window * 24 * 3600)
        recent_snapshots = [s for s in snapshots if s.timestamp >= cutoff_time]

        if not recent_snapshots:
            # 如果窗口内没有数据，使用所有数据
            recent_snapshots = snapshots

        # 计算各情绪的中位数
        baseline = {}
        emotion_names = set()
        for snapshot in recent_snapshots:
            emotion_names.update(snapshot.emotions.keys())

        for emotion in emotion_names:
            scores = [s.emotions.get(emotion, 0.0) for s in recent_snapshots]
            baseline[emotion] = float(np.median(scores)) if scores else 0.0

        return baseline

    def _analyze_emotion_patterns(self, profile: EmotionProfile) -> Dict[str, any]:
        """
        分析情绪模式
        识别用户的情绪反应习惯
        """
        patterns = profile.emotion_patterns.copy()
        snapshots = profile.snapshots

        if len(snapshots) < 5:
            return patterns  # 数据不足，保持原样

        # 1. 分析典型反应模式（挫折后倾向于愤怒还是退缩）
        high_arousal_snapshots = [s for s in snapshots if s.arousal > 0.6]
        if high_arousal_snapshots:
            anger_score = np.mean([s.emotions.get('愤怒', 0.0) for s in high_arousal_snapshots])
            sadness_score = np.mean([s.emotions.get('悲伤', 0.0) for s in high_arousal_snapshots])

            if anger_score > sadness_score:
                patterns['typical_response'] = 'anger'
            elif sadness_score > anger_score:
                patterns['typical_response'] = 'withdrawal'
            else:
                patterns['typical_response'] = 'mixed'

        # 2. 识别常见触发因素（通过上下文分析）
        context_emotions = {}
        for s in snapshots:
            if s.context not in context_emotions:
                context_emotions[s.context] = []
            context_emotions[s.context].append(max(s.emotions.values()))

        # 找出通常引发高强度情绪的上下文
        trigger_candidates = []
        for context, scores in context_emotions.items():
            avg_score = np.mean(scores)
            if avg_score > 0.6:
                trigger_candidates.append((context, avg_score))

        patterns['triggers'] = [ctx for ctx, _ in sorted(trigger_candidates, key=lambda x: -x[1])[:5]]

        # 3. 计算情绪稳定性
        if len(snapshots) >= 10:
            recent = snapshots[-10:]
            arousal_values = [s.arousal for s in recent]
            patterns['stability_score'] = 1.0 - (np.std(arousal_values) / (np.mean(arousal_values) + 0.1))
            patterns['stability_score'] = max(0.0, min(1.0, patterns['stability_score']))

        # 4. 强度分布
        all_emotions = {}
        for s in snapshots:
            for emotion, score in s.emotions.items():
                if emotion not in all_emotions:
                    all_emotions[emotion] = []
                all_emotions[emotion].append(score)

        for emotion, scores in all_emotions.items():
            patterns['intensity_distribution'][emotion] = {
                'mean': float(np.mean(scores)),
                'std': float(np.std(scores)),
                'max': float(np.max(scores))
            }

        return patterns

    def _update_self_agent_params(self, profile: EmotionProfile,
                                   latest_snapshot: EmotionSnapshot) -> Dict[str, any]:
        """
        更新Self-Agent性格参数
        使其更贴近"另一个自己"
        """
        params = profile.self_agent_params.copy()
        patterns = profile.emotion_patterns

        # 1. 根据典型反应更新情绪习惯
        if patterns.get('typical_response') == 'anger':
            params['emotional_habits']['frustration_response'] = 'anger'
        elif patterns.get('typical_response') == 'withdrawal':
            params['emotional_habits']['frustration_response'] = 'withdrawal'

        # 2. 更新神经质水平（基于情绪稳定性）
        stability = patterns.get('stability_score', 0.5)
        params['personality_traits']['neuroticism'] = 1.0 - stability

        # 3. 更新情绪觉察能力（基于情绪多样性）
        emotion_diversity = len(set(latest_snapshot.emotions.keys()))
        params['emotional_habits']['emotional_awareness'] = min(1.0, emotion_diversity / 10.0)

        # 4. 更新语音和表达特征（如果有音频/视频特征）
        # 这里简化处理，实际应从multimodal_vector中提取
        if latest_snapshot.multimodal_vector:
            # 向量的前64维是情绪，后64维包含音视频特征
            audio_features = latest_snapshot.multimodal_vector[64:96]
            if np.mean(audio_features) > 0:
                # 简化的映射逻辑
                params['voice_and_expression']['typical_pitch'] = float(np.mean(audio_features[:8]))
                params['voice_and_expression']['speech_rate'] = float(np.mean(audio_features[8:16]))
                params['voice_and_expression']['expression_intensity'] = float(np.mean(audio_features[16:24]))

        # 5. 更新压力应对风格（基于历史干预成功率）
        if profile.total_interactions > 10:
            intervention_ratio = profile.intervention_count / profile.total_interactions
            if intervention_ratio > 0.5:
                params['response_style']['under_pressure'] = 'seeking_support'
            else:
                params['response_style']['under_pressure'] = 'self_reliant'

        return params

    def detect_pathological_features(self, profile: EmotionProfile) -> List[str]:
        """
        区分"临时情绪波动"与"病理性特征"
        """
        pathological_indicators = []

        if len(profile.snapshots) < 10:
            return pathological_indicators  # 数据不足

        # 1. 长期高情绪强度
        recent_arousal = [s.arousal for s in profile.snapshots[-10:]]
        if np.mean(recent_arousal) > 0.7:
            pathological_indicators.append("持续性高情绪唤醒")

        # 2. 情绪极度不稳定
        if profile.emotion_patterns.get('stability_score', 1.0) < 0.3:
            pathological_indicators.append("情绪极度不稳定")

        # 3. 频繁危机状态
        if profile.crisis_count >= 5:
            pathological_indicators.append(f"频繁危机状态({profile.crisis_count}次)")

        # 4. 空虚感持续高水平
        emptiness_scores = [s.emotions.get('空虚感', 0.0) for s in profile.snapshots[-20:]]
        if np.mean(emptiness_scores) > 0.6:
            pathological_indicators.append("持续性空虚感")

        # 5. 自伤冲动反复出现
        self_harm_count = sum(1 for s in profile.snapshots[-20:] if s.emotions.get('自伤冲动', 0.0) > 0.3)
        if self_harm_count >= 3:
            pathological_indicators.append(f"反复自伤冲动({self_harm_count}次)")

        return pathological_indicators

    def get_profile_summary(self, profile: EmotionProfile) -> str:
        """生成画像摘要"""
        summary_parts = [
            f"# 用户情绪画像摘要\n",
            f"**用户ID**: {profile.user_id}",
            f"**创建时间**: {profile.created_at}",
            f"**最后更新**: {profile.updated_at}\n",
            f"**统计信息**:",
            f"- 总互动次数: {profile.total_interactions}",
            f"- 危机次数: {profile.crisis_count}",
            f"- 干预次数: {profile.intervention_count}\n",
            f"**情绪基准线**:"
        ]

        for emotion, score in profile.baseline_emotions.items():
            if score > 0.1:
                summary_parts.append(f"- {emotion}: {score:.2f}")

        summary_parts.append(f"\n**典型反应模式**: {profile.emotion_patterns.get('typical_response', '未知')}")
        summary_parts.append(f"**情绪稳定性**: {profile.emotion_patterns.get('stability_score', 0.5):.2f}")

        # 病理性特征检测
        pathological = self.detect_pathological_features(profile)
        if pathological:
            summary_parts.append(f"\n⚠️ **潜在病理性特征**:")
            for indicator in pathological:
                summary_parts.append(f"- {indicator}")

        return "\n".join(summary_parts)

    def export_for_self_agent(self, profile: EmotionProfile) -> Dict:
        """
        导出画像数据供Self-Agent使用
        返回性格参数和情绪模式
        """
        return {
            'user_id': profile.user_id,
            'personality_traits': profile.self_agent_params['personality_traits'],
            'response_style': profile.self_agent_params['response_style'],
            'emotional_habits': profile.self_agent_params['emotional_habits'],
            'voice_and_expression': profile.self_agent_params['voice_and_expression'],
            'typical_response': profile.emotion_patterns.get('typical_response'),
            'stability_score': profile.emotion_patterns.get('stability_score'),
            'known_triggers': profile.emotion_patterns.get('triggers', [])[:5],
            'baseline_emotions': profile.baseline_emotions
        }

    def _save_profile(self, profile: EmotionProfile):
        """保存画像到文件"""
        profile_path = self.storage_dir / f"{profile.user_id}.json"

        # 转换为可序列化的格式
        data = {
            'user_id': profile.user_id,
            'created_at': profile.created_at,
            'updated_at': profile.updated_at,
            'baseline_emotions': profile.baseline_emotions,
            'snapshots': [asdict(s) for s in profile.snapshots],
            'emotion_patterns': profile.emotion_patterns,
            'self_agent_params': profile.self_agent_params,
            'total_interactions': profile.total_interactions,
            'crisis_count': profile.crisis_count,
            'intervention_count': profile.intervention_count
        }

        with open(profile_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.debug(f"保存画像: {profile.user_id}")
