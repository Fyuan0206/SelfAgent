"""
高级情绪画像系统 - 深度版
提供多维度、预测性的用户情绪分析
"""

import json
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from pathlib import Path
from loguru import logger
from collections import defaultdict, Counter
from scipy import stats
from scipy.signal import find_peaks
import hashlib


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

    # 扩展字段
    input_type: str = "unknown"  # text/audio/image
    duration: Optional[float] = None  # 互动时长
    time_of_day: str = ""  # morning/afternoon/evening/night
    day_of_week: str = ""  # Monday/Tuesday...
    is_weekend: bool = False


@dataclass
class EmotionTrend:
    """情绪趋势"""
    direction: str  # rising/falling/stable/volatile
    slope: float  # 变化斜率
    confidence: float  # 置信度
    timespan_days: float  # 分析时间跨度
    change_percentage: Dict[str, float]  # 各情绪变化百分比


@dataclass
class EmotionCycle:
    """情绪周期"""
    cycle_type: str  # daily/weekly/monthly
    peak_times: List[str]  # 高峰时段
    low_times: List[str]  # 低谷时段
    strength: float  # 周期强度
    pattern: Dict[str, List[float]]  # 各情绪的周期模式


@dataclass
class EmotionCluster:
    """情绪聚类模式"""
    cluster_name: str  # 聚类名称
    emotions: Dict[str, float]  # 典型情绪组合
    frequency: int  # 出现频率
    triggers: List[str]  # 触发因素
    outcomes: List[str]  # 常见结果


@dataclass
class PersonalityProfile:
    """性格画像"""
    # 大五人格
    openness: float = 0.5
    conscientiousness: float = 0.5
    extraversion: float = 0.5
    agreeableness: float = 0.5
    neuroticism: float = 0.5

    # 决策风格
    decision_style: str = "analytical"  # analytical/intuitive/dependent/avoidant
    risk_tolerance: float = 0.5
    coping_style: str = "problem_focused"  # problem_focused/emotion_focused/avoidant

    # 社交特征
    social_orientation: str = "ambivert"  # introvert/ambivert/extravert
    expressiveness: float = 0.5
    support_seeking: float = 0.5

    # 压力反应
    stress_response: str = "active"  # active/passive/withdrawn
    resilience_score: float = 0.5

    # 情绪特征
    emotional_awareness: float = 0.5
    emotion_regulation: float = 0.5
    impulse_control: float = 0.5


@dataclass
class RiskPrediction:
    """风险预测"""
    next_crisis_probability: float  # 下次危机概率
    high_risk_time_windows: List[str]  # 高风险时段
    early_warning_signals: List[str]  # 早期预警信号
    protective_factors: List[str]  # 保护因素
    recommended_monitoring: List[str]  # 建议监控指标


@dataclass
class AdvancedEmotionProfile:
    """高级情绪画像"""
    # 基本信息
    user_id: str
    created_at: str
    updated_at: str

    # 情绪快照历史
    snapshots: List[EmotionSnapshot] = field(default_factory=list)

    # 核心分析
    emotion_baseline: Dict[str, float] = field(default_factory=dict)
    emotion_trend: EmotionTrend = None
    emotion_cycles: List[EmotionCycle] = field(default_factory=list)
    emotion_clusters: List[EmotionCluster] = field(default_factory=list)

    # 性格画像
    personality: PersonalityProfile = field(default_factory=PersonalityProfile)

    # 风险评估
    risk_prediction: RiskPrediction = None

    # 深度洞察
    triggers: Dict[str, float] = field(default_factory=dict)  # 触发因素及强度
    coping_strategies: Dict[str, float] = field(default_factory=dict)  # 应对策略及效果
    emotion_network: Dict[str, Dict[str, float]] = field(default_factory=dict)  # 情绪关联网络

    # 统计信息
    total_interactions: int = 0
    crisis_count: int = 0
    intervention_count: int = 0
    avg_recovery_time: float = 0.0  # 平均恢复时间（小时）

    # 元数据
    data_quality_score: float = 1.0  # 数据质量分数
    last_analysis_date: str = ""


class AdvancedEmotionProfileManager:
    """高级情绪画像管理器"""

    def __init__(self, config: Dict, storage_dir: str = "profiles"):
        self.config = config
        self.profile_config = config.get('emotion_profile', {})
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)

        # 配置参数
        self.baseline_window = self.profile_config.get('baseline_window', 30)
        self.trend_window = self.profile_config.get('trend_window', 7)  # 趋势分析窗口（天）
        self.min_snapshots_for_analysis = self.profile_config.get('min_snapshots', 5)

        # DBT情绪列表
        self.dbt_emotions = config.get('dbt_emotions', [])

        logger.info("高级情绪画像管理器初始化完成")

    def create_profile(self, user_id: str) -> AdvancedEmotionProfile:
        """创建新用户画像"""
        now = datetime.now().isoformat()

        profile = AdvancedEmotionProfile(
            user_id=user_id,
            created_at=now,
            updated_at=now,
            emotion_trend=EmotionTrend(
                direction="stable",
                slope=0.0,
                confidence=0.0,
                timespan_days=0.0,
                change_percentage={}
            ),
            risk_prediction=RiskPrediction(
                next_crisis_probability=0.0,
                high_risk_time_windows=[],
                early_warning_signals=[],
                protective_factors=[],
                recommended_monitoring=[]
            )
        )

        self._save_profile(profile)
        logger.info(f"创建高级用户画像: {user_id}")
        return profile

    def load_profile(self, user_id: str) -> Optional[AdvancedEmotionProfile]:
        """加载用户画像"""
        profile_path = self.storage_dir / f"{user_id}.json"

        if not profile_path.exists():
            return None

        try:
            with open(profile_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 重建嵌套对象
            snapshots = [EmotionSnapshot(**s) for s in data.get('snapshots', [])]

            trend_data = data.get('emotion_trend', {})
            emotion_trend = EmotionTrend(**trend_data) if trend_data else None

            cycles_data = data.get('emotion_cycles', [])
            emotion_cycles = [EmotionCycle(**c) for c in cycles_data]

            clusters_data = data.get('emotion_clusters', [])
            emotion_clusters = [EmotionCluster(**c) for c in clusters_data]

            personality_data = data.get('personality', {})
            personality = PersonalityProfile(**personality_data) if personality_data else PersonalityProfile()

            risk_data = data.get('risk_prediction', {})
            risk_prediction = RiskPrediction(**risk_data) if risk_data else None

            profile = AdvancedEmotionProfile(
                user_id=data['user_id'],
                created_at=data['created_at'],
                updated_at=data['updated_at'],
                snapshots=snapshots,
                emotion_baseline=data.get('emotion_baseline', {}),
                emotion_trend=emotion_trend,
                emotion_cycles=emotion_cycles,
                emotion_clusters=emotion_clusters,
                personality=personality,
                risk_prediction=risk_prediction,
                triggers=data.get('triggers', {}),
                coping_strategies=data.get('coping_strategies', {}),
                emotion_network=data.get('emotion_network', {}),
                total_interactions=data.get('total_interactions', 0),
                crisis_count=data.get('crisis_count', 0),
                intervention_count=data.get('intervention_count', 0),
                avg_recovery_time=data.get('avg_recovery_time', 0.0),
                data_quality_score=data.get('data_quality_score', 1.0),
                last_analysis_date=data.get('last_analysis_date', '')
            )

            logger.info(f"加载高级用户画像: {user_id}")
            return profile

        except Exception as e:
            logger.error(f"加载画像失败: {e}")
            return None

    def update_profile(self, profile: AdvancedEmotionProfile,
                      emotion_snapshot: EmotionSnapshot,
                      route_level: str,
                      risk_level: str):
        """
        深度更新用户画像
        包括：趋势分析、周期检测、聚类挖掘、性格推断、风险预测
        """
        # 1. 添加快照并增强元数据
        self._enrich_snapshot(emotion_snapshot)
        profile.snapshots.append(emotion_snapshot)
        profile.total_interactions += 1

        # 2. 更新统计
        if route_level == "L3_CRISIS":
            profile.crisis_count += 1
        if route_level in ["L2_INTERVENTION", "L3_CRISIS"]:
            profile.intervention_count += 1

        # 3. 计算数据质量分数
        profile.data_quality_score = self._calculate_data_quality(profile)

        # 4. 深度分析（需要足够数据）
        if len(profile.snapshots) >= self.min_snapshots_for_analysis:
            # 4.1 更新情绪基准线
            profile.emotion_baseline = self._calculate_advanced_baseline(profile.snapshots)

            # 4.2 分析情绪趋势
            profile.emotion_trend = self._analyze_trend(profile.snapshots)

            # 4.3 检测情绪周期
            profile.emotion_cycles = self._detect_cycles(profile.snapshots)

            # 4.4 挖掘情绪聚类
            profile.emotion_clusters = self._mine_emotion_clusters(profile.snapshots)

            # 4.5 构建情绪关联网络
            profile.emotion_network = self._build_emotion_network(profile.snapshots)

            # 4.6 挖掘触发因素
            profile.triggers = self._mine_triggers(profile.snapshots)

            # 4.7 评估应对策略
            profile.coping_strategies = self._evaluate_coping_strategies(profile.snapshots)

            # 4.8 推断性格特征
            profile.personality = self._infer_personality(profile)

            # 4.9 风险预测
            profile.risk_prediction = self._predict_risk(profile)

            # 4.10 计算平均恢复时间
            profile.avg_recovery_time = self._calculate_recovery_time(profile.snapshots)

        # 5. 更新时间戳
        profile.updated_at = datetime.now().isoformat()
        profile.last_analysis_date = datetime.now().isoformat()

        # 6. 保存
        self._save_profile(profile)

        logger.info(f"深度更新用户画像: {profile.user_id}")

    def _enrich_snapshot(self, snapshot: EmotionSnapshot):
        """增强快照元数据"""
        dt = datetime.fromtimestamp(snapshot.timestamp)

        # 一天中的时段
        hour = dt.hour
        if 5 <= hour < 12:
            snapshot.time_of_day = "morning"
        elif 12 <= hour < 18:
            snapshot.time_of_day = "afternoon"
        elif 18 <= hour < 22:
            snapshot.time_of_day = "evening"
        else:
            snapshot.time_of_day = "night"

        # 星期几
        snapshot.day_of_week = dt.strftime("%A")
        snapshot.is_weekend = dt.weekday() >= 5

    def _calculate_data_quality(self, profile: AdvancedEmotionProfile) -> float:
        """计算数据质量分数"""
        if not profile.snapshots:
            return 0.0

        score = 1.0

        # 1. 数据量（越多越好，上限100次）
        data_count = len(profile.snapshots)
        score *= min(1.0, data_count / 50.0)

        # 2. 数据覆盖度（最近30天的数据）
        now = datetime.now().timestamp()
        recent_30_days = [s for s in profile.snapshots if now - s.timestamp <= 30 * 24 * 3600]
        score *= min(1.0, len(recent_30_days) / 10.0)

        # 3. 多模态数据占比
        multimodal_count = sum(1 for s in profile.snapshots if s.input_type in ['audio', 'image'])
        if data_count > 0:
            score *= (0.7 + 0.3 * (multimodal_count / data_count))

        return min(1.0, max(0.0, score))

    def _calculate_advanced_baseline(self, snapshots: List[EmotionSnapshot]) -> Dict[str, float]:
        """
        计算高级情绪基准线
        使用加权平均（近期权重更高）+ 异常值过滤
        """
        if not snapshots:
            return {}

        # 筛选最近30天的快照
        now = datetime.now().timestamp()
        cutoff_time = now - (self.baseline_window * 24 * 3600)
        recent_snapshots = [s for s in snapshots if s.timestamp >= cutoff_time]

        if not recent_snapshots:
            recent_snapshots = snapshots

        # 时间加权（越近权重越高）
        timestamps = [s.timestamp for s in recent_snapshots]
        min_ts = min(timestamps)
        max_ts = max(timestamps)
        time_span = max_ts - min_ts + 1

        weights = [(s.timestamp - min_ts) / time_span for s in recent_snapshots]

        # 计算加权平均
        baseline = {}
        emotion_names = set()
        for s in recent_snapshots:
            emotion_names.update(s.emotions.keys())

        for emotion in emotion_names:
            scores = [s.emotions.get(emotion, 0.0) for s in recent_snapshots]

            # 去除异常值（使用IQR方法）
            if len(scores) >= 4:
                q1, q3 = np.percentile(scores, [25, 75])
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr

                filtered_scores = [s for s in scores if lower_bound <= s <= upper_bound]
                filtered_weights = [w for s, w in zip(scores, weights) if lower_bound <= s <= upper_bound]
            else:
                filtered_scores = scores
                filtered_weights = weights

            if sum(filtered_weights) > 0:
                baseline[emotion] = float(np.average(filtered_scores, weights=filtered_weights))
            else:
                baseline[emotion] = 0.0

        return baseline

    def _analyze_trend(self, snapshots: List[EmotionSnapshot]) -> EmotionTrend:
        """
        分析情绪趋势
        检测上升、下降、稳定、波动
        """
        if len(snapshots) < 3:
            return EmotionTrend(
                direction="stable",
                slope=0.0,
                confidence=0.0,
                timespan_days=0.0,
                change_percentage={}
            )

        # 只分析最近N天的数据
        now = datetime.now().timestamp()
        cutoff_time = now - (self.trend_window * 24 * 3600)
        recent_snapshots = sorted([s for s in snapshots if s.timestamp >= cutoff_time], key=lambda x: x.timestamp)

        if len(recent_snapshots) < 3:
            recent_snapshots = sorted(snapshots, key=lambda x: x.timestamp)[-10:]

        # 计算时间跨度
        timespan_days = (recent_snapshots[-1].timestamp - recent_snapshots[0].timestamp) / (24 * 3600)

        # 提取总体情绪强度（所有情绪的平均）
        overall_scores = []
        timestamps = []
        for s in recent_snapshots:
            overall = max(s.emotions.values()) if s.emotions else 0.0
            overall_scores.append(overall)
            timestamps.append(s.timestamp)

        # 线性回归计算趋势
        if len(timestamps) >= 2:
            timestamps_norm = [(t - timestamps[0]) / (timestamps[-1] - timestamps[0] + 1) for t in timestamps]
            slope, intercept, r_value, p_value, std_err = stats.linregress(timestamps_norm, overall_scores)

            # 判断趋势方向
            if abs(slope) < 0.05:
                direction = "stable"
            elif slope > 0:
                direction = "rising"
            else:
                direction = "falling"

            # 检测波动性
            if len(overall_scores) >= 5:
                volatility = np.std(overall_scores)
                if volatility > 0.3:
                    direction = "volatile"

            confidence = abs(r_value)

            # 计算各情绪变化百分比
            change_percentage = {}
            first_emotions = recent_snapshots[0].emotions
            last_emotions = recent_snapshots[-1].emotions

            for emotion in set(list(first_emotions.keys()) + list(last_emotions.keys())):
                first_score = first_emotions.get(emotion, 0.0)
                last_score = last_emotions.get(emotion, 0.0)
                if first_score > 0:
                    change_percentage[emotion] = ((last_score - first_score) / first_score) * 100
                else:
                    change_percentage[emotion] = 0.0

            return EmotionTrend(
                direction=direction,
                slope=float(slope),
                confidence=float(confidence),
                timespan_days=float(timespan_days),
                change_percentage=change_percentage
            )

        return EmotionTrend(
            direction="stable",
            slope=0.0,
            confidence=0.0,
            timespan_days=float(timespan_days),
            change_percentage={}
        )

    def _detect_cycles(self, snapshots: List[EmotionSnapshot]) -> List[EmotionCycle]:
        """
        检测情绪周期
        包括：日内周期、周内周期、月度周期
        """
        if len(snapshots) < 10:
            return []

        cycles = []
        now = datetime.now().timestamp()

        # 1. 日内周期分析
        daily_patterns = defaultdict(list)
        for s in snapshots:
            if now - s.timestamp <= 30 * 24 * 3600:  # 最近30天
                daily_patterns[s.time_of_day].append(max(s.emotions.values(), default=0.0))

        if len(daily_patterns) >= 3:
            times = list(daily_patterns.keys())
            avg_scores = [np.mean(daily_patterns[t]) for t in times]

            peak_idx = np.argmax(avg_scores)
            low_idx = np.argmin(avg_scores)

            cycles.append(EmotionCycle(
                cycle_type="daily",
                peak_times=[times[peak_idx]],
                low_times=[times[low_idx]],
                strength=float(np.std(avg_scores)),
                pattern={"daily": avg_scores}
            ))

        # 2. 周内周期分析
        weekday_patterns = defaultdict(list)
        for s in snapshots:
            if now - s.timestamp <= 60 * 24 * 3600:  # 最近60天
                weekday_patterns[s.day_of_week].append(max(s.emotions.values(), default=0.0))

        if len(weekday_patterns) >= 5:
            weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            avg_scores = []
            for wd in weekdays:
                scores = weekday_patterns.get(wd, [])
                avg_scores.append(np.mean(scores) if scores else 0.0)

            peak_idx = np.argmax(avg_scores)
            low_idx = np.argmin(avg_scores)

            cycles.append(EmotionCycle(
                cycle_type="weekly",
                peak_times=[weekdays[peak_idx]],
                low_times=[weekdays[low_idx]],
                strength=float(np.std(avg_scores)),
                pattern={"weekly": avg_scores}
            ))

        # 3. 工作日 vs 周末
        weekday_scores = [max(s.emotions.values(), default=0.0) for s in snapshots if not s.is_weekend]
        weekend_scores = [max(s.emotions.values(), default=0.0) for s in snapshots if s.is_weekend]

        if weekday_scores and weekend_scores:
            cycles.append(EmotionCycle(
                cycle_type="weekend_vs_weekday",
                peak_times=["weekday" if np.mean(weekday_scores) > np.mean(weekend_scores) else "weekend"],
                low_times=["weekend" if np.mean(weekday_scores) < np.mean(weekend_scores) else "weekday"],
                strength=float(abs(np.mean(weekday_scores) - np.mean(weekend_scores))),
                pattern={"weekday": [np.mean(weekday_scores)], "weekend": [np.mean(weekend_scores)]}
            ))

        return cycles

    def _mine_emotion_clusters(self, snapshots: List[EmotionSnapshot]) -> List[EmotionCluster]:
        """
        挖掘情绪聚类模式
        发现经常一起出现的情绪组合
        """
        if len(snapshots) < 5:
            return []

        # 1. 提取所有非零情绪向量
        emotion_vectors = []
        for s in snapshots:
            vector = {k: v for k, v in s.emotions.items() if v > 0.1}
            if vector:
                emotion_vectors.append((vector, s.context, s.route_level))

        if not emotion_vectors:
            return []

        # 2. 简单聚类（基于相似度）
        clusters = []
        used_indices = set()

        for i, (vector, context, route) in enumerate(emotion_vectors):
            if i in used_indices:
                continue

            # 找到相似的向量
            similar_vectors = []
            for j, (v2, c2, r2) in enumerate(emotion_vectors):
                if j <= i or j in used_indices:
                    continue

                # 计算余弦相似度
                similarity = self._cosine_similarity(vector, v2)
                if similarity > 0.7:  # 相似度阈值
                    similar_vectors.append((v2, c2, r2))
                    used_indices.add(j)

            if similar_vectors:
                # 合并情绪向量
                all_vectors = [vector] + [v for v, _, _ in similar_vectors]
                avg_emotions = {}
                for emo in set().union(*[set(v.keys()) for v in all_vectors]):
                    avg_emotions[emo] = float(np.mean([v.get(emo, 0.0) for v in all_vectors]))

                # 提取触发因素
                triggers = list(set([context for _, context, _ in similar_vectors] + [context]))

                # 提取结果
                outcomes = list(set([route for _, _, route in similar_vectors] + [route]))

                # 生成聚类名称
                top_emotions = sorted(avg_emotions.items(), key=lambda x: -x[1])[:3]
                cluster_name = "_".join([e for e, _ in top_emotions])

                clusters.append(EmotionCluster(
                    cluster_name=cluster_name,
                    emotions=avg_emotions,
                    frequency=len(all_vectors),
                    triggers=triggers[:5],
                    outcomes=outcomes
                ))

                used_indices.add(i)

        # 3. 按频率排序
        clusters.sort(key=lambda x: -x.frequency)

        return clusters[:10]  # 返回前10个聚类

    def _cosine_similarity(self, vec1: Dict, vec2: Dict) -> float:
        """计算两个向量的余弦相似度"""
        all_keys = set(vec1.keys()) | set(vec2.keys())

        dot_product = sum(vec1.get(k, 0) * vec2.get(k, 0) for k in all_keys)
        norm1 = np.sqrt(sum(v ** 2 for v in vec1.values()))
        norm2 = np.sqrt(sum(v ** 2 for v in vec2.values()))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def _build_emotion_network(self, snapshots: List[EmotionSnapshot]) -> Dict[str, Dict[str, float]]:
        """
        构建情绪关联网络
        发现哪些情绪经常一起出现
        """
        network = {}

        if len(snapshots) < 3:
            return network

        # 计算共现矩阵
        co_occurrence = defaultdict(lambda: defaultdict(int))

        for s in snapshots:
            emotions = [k for k, v in s.emotions.items() if v > 0.1]
            for e1 in emotions:
                for e2 in emotions:
                    if e1 != e2:
                        co_occurrence[e1][e2] += 1

        # 归一化并转换为关联强度
        for e1, related in co_occurrence.items():
            total = sum(related.values())
            network[e1] = {e2: count / total for e2, count in related.items()}

        # 只保留强关联（>0.3）
        network = {
            e1: {e2: s for e2, s in related.items() if s > 0.3}
            for e1, related in network.items()
        }

        return network

    def _mine_triggers(self, snapshots: List[EmotionSnapshot]) -> Dict[str, float]:
        """
        深度挖掘触发因素
        基于上下文和情绪强度
        """
        triggers = {}

        if not snapshots:
            return triggers

        # 1. 从context中提取关键词
        context_intensity = defaultdict(list)
        for s in snapshots:
            if s.context:
                intensity = max(s.emotions.values(), default=0.0)
                if intensity > 0.3:  # 只考虑高情绪强度的context
                    context_intensity[s.context].append(intensity)

        # 2. 计算平均触发强度
        for context, intensities in context_intensity.items():
            if len(intensities) >= 2:
                triggers[context] = float(np.mean(intensities))

        # 3. 排序并返回前10个
        triggers = dict(sorted(triggers.items(), key=lambda x: -x[1])[:10])

        return triggers

    def _evaluate_coping_strategies(self, snapshots: List[EmotionSnapshot]) -> Dict[str, float]:
        """
        评估应对策略效果
        通过观察情绪恢复模式
        """
        strategies = {}

        if len(snapshots) < 5:
            return strategies

        # 找出危机后的恢复序列
        for i in range(len(snapshots) - 1):
            current = snapshots[i]
            next_s = snapshots[i + 1]

            # 当前是高负面情绪，下次低了 → 有效策略
            current_negative = sum(current.emotions.get(e, 0) for e in
                                ['悲伤', '焦虑', '绝望', '空虚感', '自伤冲动'])
            next_negative = sum(next_s.emotions.get(e, 0) for e in
                             ['悲伤', '焦虑', '绝望', '空虚感', '自伤冲动'])

            if current_negative > 0.5 and next_negative < current_negative * 0.5:
                # 有效的恢复
                if current.context:
                    effectiveness = (current_negative - next_negative) / current_negative
                    strategies[current.context] = max(
                        strategies.get(current.context, 0.0),
                        effectiveness
                    )

        return strategies

    def _infer_personality(self, profile: AdvancedEmotionProfile) -> PersonalityProfile:
        """
        基于真实数据推断性格特征
        """
        snapshots = profile.snapshots
        personality = PersonalityProfile()

        if len(snapshots) < 5:
            return personality

        # 1. 神经质 - 基于情绪稳定性
        if profile.emotion_trend:
            stability = 1.0 - abs(profile.emotion_trend.slope)
            personality.neuroticism = 1.0 - stability

        # 2. 外向性 - 基于时间模式（周末vs工作日）
        weekend_scores = [max([0] + list(s.emotions.values())) for s in snapshots if s.is_weekend]
        weekday_scores = [max([0] + list(s.emotions.values())) for s in snapshots if not s.is_weekend]

        if weekend_scores and weekday_scores:
            if np.mean(weekend_scores) > np.mean(weekday_scores):
                personality.extraversion = 0.7  # 周末更活跃
            else:
                personality.extraversion = 0.3  # 工作日更活跃

        # 3. 尽责性 - 基于规律性
        if len(snapshots) >= 10:
            # 计算互动时间间隔的标准差
            intervals = []
            for i in range(1, len(snapshots)):
                interval = snapshots[i].timestamp - snapshots[i-1].timestamp
                intervals.append(interval)

            if intervals:
                regularity = 1.0 / (1.0 + np.std(intervals) / (np.mean(intervals) + 1))
                personality.conscientiousness = regularity

        # 4. 宜人性 - 基于情绪类型
        anger_scores = [s.emotions.get('愤怒', 0) for s in snapshots]
        empathy_scores = [s.emotions.get('内疚', 0) + s.emotions.get('羞愧', 0) for s in snapshots]

        if anger_scores and empathy_scores:
            avg_anger = np.mean(anger_scores)
            avg_empathy = np.mean(empathy_scores)
            personality.agreeableness = 1.0 - avg_anger + avg_empathy * 0.5
            personality.agreeableness = max(0.0, min(1.0, personality.agreeableness))

        # 5. 开放性 - 基于情绪多样性
        emotion_diversity = len(set().union(*[set(s.emotions.keys()) for s in snapshots]))
        personality.openness = min(1.0, emotion_diversity / len(self.dbt_emotions))

        # 6. 决策风格 - 基于变化模式
        if profile.emotion_clusters:
            cluster_count = len(profile.emotion_clusters)
            if cluster_count >= 5:
                personality.decision_style = "flexible"
            elif cluster_count <= 2:
                personality.decision_style = "rigid"
            else:
                personality.decision_style = "analytical"

        # 7. 压力应对 - 基于危机历史
        if profile.total_interactions > 0:
            crisis_ratio = profile.crisis_count / profile.total_interactions
            if crisis_ratio > 0.3:
                personality.stress_response = "withdrawn"
            elif crisis_ratio < 0.1:
                personality.stress_response = "active"

        # 8. 恢复力 - 基于恢复时间
        if profile.avg_recovery_time > 0:
            personality.resilience_score = 1.0 / (1.0 + profile.avg_recovery_time / 24)  # 按天归一化

        # 9. 情绪觉察 - 基于表达细腻度
        avg_emotions_per_snapshot = np.mean([len([e for e, v in s.emotions.items() if v > 0.1])
                                              for s in snapshots])
        personality.emotional_awareness = min(1.0, avg_emotions_per_snapshot / 5.0)

        # 10. 冲动控制 - 基于激越和自伤冲动
        impulsiveness_scores = [s.emotions.get('激越', 0) + s.emotions.get('自伤冲动', 0) * 2
                              for s in snapshots]
        if impulsiveness_scores:
            avg_impulsiveness = np.mean(impulsiveness_scores)
            personality.impulse_control = 1.0 - min(1.0, avg_impulsiveness)

        # 归一化到[0,1]
        for field_name, field_type in personality.__dataclass_fields__.items():
            if field_name != 'coping_style':
                value = getattr(personality, field_name)
                if isinstance(value, float):
                    setattr(personality, field_name, max(0.0, min(1.0, value)))

        return personality

    def _predict_risk(self, profile: AdvancedEmotionProfile) -> RiskPrediction:
        """
        风险预测
        预测下次危机概率和高风险时段
        """
        prediction = RiskPrediction(
            next_crisis_probability=0.0,
            high_risk_time_windows=[],
            early_warning_signals=[],
            protective_factors=[],
            recommended_monitoring=[]
        )

        if len(profile.snapshots) < 5:
            return prediction

        # 1. 计算危机概率（基于历史频率）
        if profile.total_interactions > 0:
            crisis_ratio = profile.crisis_count / profile.total_interactions
            prediction.next_crisis_probability = crisis_ratio

        # 2. 识别高风险时段
        if profile.emotion_cycles:
            for cycle in profile.emotion_cycles:
                if cycle.strength > 0.2:  # 明显的周期
                    prediction.high_risk_time_windows.append(f"{cycle.cycle_type}_{cycle.peak_times[0]}")

        # 3. 早期预警信号
        # 检查最近的趋势
        if profile.emotion_trend and profile.emotion_trend.direction == "rising":
            if profile.emotion_trend.slope > 0.1:
                prediction.early_warning_signals.append("情绪持续上升")

        # 检查高频率的负面情绪
        recent_negative_avg = np.mean([
            sum(s.emotions.get(e, 0) for e in ['悲伤', '焦虑', '绝望'])
            for s in profile.snapshots[-10:]
        ])
        if recent_negative_avg > 0.4:
            prediction.early_warning_signals.append("负面情绪持续高位")

        # 检查波动性
        if profile.emotion_trend and profile.emotion_trend.direction == "volatile":
            prediction.early_warning_signals.append("情绪极度不稳定")

        # 4. 保护因素
        if profile.coping_strategies:
            prediction.protective_factors = list(profile.coping_strategies.keys())[:5]

        if profile.personality.resilience_score > 0.7:
            prediction.protective_factors.append("高恢复力")

        if profile.intervention_count > 0 and profile.crisis_count / (profile.intervention_count + 1) < 0.5:
            prediction.protective_factors.append("干预响应良好")

        # 5. 建议监控的指标
        prediction.recommended_monitoring = [
            "整体情绪强度",
            "危机触发频率",
            "恢复时间长度"
        ]

        if profile.emotion_trend:
            prediction.recommended_monitoring.append(f"趋势方向: {profile.emotion_trend.direction}")

        return prediction

    def _calculate_recovery_time(self, snapshots: List[EmotionSnapshot]) -> float:
        """计算平均恢复时间（小时）"""
        recovery_times = []

        for i in range(len(snapshots) - 1):
            current = snapshots[i]
            next_s = snapshots[i + 1]

            # 当前是危机，下次不是
            if current.route_level == "L3_CRISIS" and next_s.route_level != "L3_CRISIS":
                recovery_hours = (next_s.timestamp - current.timestamp) / 3600
                recovery_times.append(recovery_hours)

        if recovery_times:
            return float(np.mean(recovery_times))

        return 0.0

    def generate_profile_report(self, profile: AdvancedEmotionProfile) -> str:
        """生成详细的画像报告"""
        lines = []
        lines.append("=" * 70)
        lines.append(f"高级用户情绪画像报告")
        lines.append(f"用户ID: {profile.user_id}")
        lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"数据质量分数: {profile.data_quality_score:.2%}")
        lines.append("=" * 70)
        lines.append("")

        # 1. 基本信息
        lines.append("## 📊 基本信息")
        lines.append(f"- 总互动次数: {profile.total_interactions}")
        lines.append(f"- 危机次数: {profile.crisis_count}")
        lines.append(f"- 干预次数: {profile.intervention_count}")
        lines.append(f"- 平均恢复时间: {profile.avg_recovery_time:.1f} 小时")
        lines.append("")

        # 2. 情绪基准线
        lines.append("## 🎯 情绪基准线")
        if profile.emotion_baseline:
            sorted_emotions = sorted(profile.emotion_baseline.items(), key=lambda x: -x[1])
            for emotion, score in sorted_emotions[:10]:
                if score > 0.05:
                    bar = "█" * int(score * 20)
                    lines.append(f"- {emotion}: {score:.2%} {bar}")
        else:
            lines.append("暂无数据")
        lines.append("")

        # 3. 情绪趋势
        lines.append("## 📈 情绪趋势")
        if profile.emotion_trend and profile.emotion_trend.confidence > 0.3:
            trend = profile.emotion_trend
            direction_icon = {"rising": "📈", "falling": "📉", "stable": "➡️", "volatile": "📊"}
            lines.append(f"- 趋势方向: {direction_icon.get(trend.direction, '?')} {trend.direction.upper()}")
            lines.append(f"- 变化斜率: {trend.slope:.4f}")
            lines.append(f"- 置信度: {trend.confidence:.2%}")
            lines.append(f"- 分析周期: {trend.timespan_days:.1f} 天")

            if trend.change_percentage:
                lines.append("- 情绪变化:")
                for emotion, change in sorted(trend.change_percentage.items(), key=lambda x: -abs(x[1]))[:5]:
                    icon = "📈" if change > 0 else "📉"
                    lines.append(f"  {icon} {emotion}: {change:+.1f}%")
        else:
            lines.append("数据不足，无法分析趋势")
        lines.append("")

        # 4. 情绪周期
        lines.append("## 🔄 情绪周期")
        if profile.emotion_cycles:
            for cycle in profile.emotion_cycles[:3]:
                lines.append(f"- {cycle.cycle_type.upper()} 周期:")
                lines.append(f"  高峰时段: {', '.join(cycle.peak_times)}")
                lines.append(f"  低谷时段: {', '.join(cycle.low_times)}")
                lines.append(f"  周期强度: {cycle.strength:.2%}")
        else:
            lines.append("暂无明显周期")
        lines.append("")

        # 5. 情绪聚类
        lines.append("## 🔍 情绪模式")
        if profile.emotion_clusters:
            for cluster in profile.emotion_clusters[:5]:
                lines.append(f"- {cluster.cluster_name} (出现{cluster.frequency}次)")
                top_emotions = sorted(cluster.emotions.items(), key=lambda x: -x[1])[:3]
                lines.append(f"  典型情绪: {', '.join([f'{e}:{s:.2f}' for e, s in top_emotions])}")
                if cluster.triggers:
                    lines.append(f"  触发因素: {', '.join(cluster.triggers[:3])}")
        else:
            lines.append("暂无聚类数据")
        lines.append("")

        # 6. 性格画像
        lines.append("## 👤 性格画像")
        p = profile.personality
        lines.append(f"- 开放性: {p.openness:.2%}")
        lines.append(f"- 尽责性: {p.conscientiousness:.2%}")
        lines.append(f"- 外向性: {p.extraversion:.2%}")
        lines.append(f"- 宜人性: {p.agreeableness:.2%}")
        lines.append(f"- 神经质: {p.neuroticism:.2%}")
        lines.append(f"- 决策风格: {p.decision_style}")
        lines.append(f"- 压力应对: {p.stress_response}")
        lines.append(f"- 恢复力: {p.resilience_score:.2%}")
        lines.append("")

        # 7. 风险预测
        lines.append("## ⚠️ 风险预测")
        if profile.risk_prediction:
            rp = profile.risk_prediction
            lines.append(f"- 下次危机概率: {rp.next_crisis_probability:.2%}")
            if rp.high_risk_time_windows:
                lines.append(f"- 高风险时段: {', '.join(rp.high_risk_time_windows)}")
            if rp.early_warning_signals:
                lines.append(f"- 早期预警信号:")
                for signal in rp.early_warning_signals:
                    lines.append(f"  ⚠️ {signal}")
            if rp.protective_factors:
                lines.append(f"- 保护因素:")
                for factor in rp.protective_factors:
                    lines.append(f"  ✅ {factor}")
        lines.append("")

        # 8. 应对策略
        lines.append("## 💡 有效应对策略")
        if profile.coping_strategies:
            for strategy, effectiveness in sorted(profile.coping_strategies.items(), key=lambda x: -x[1])[:5]:
                lines.append(f"- {strategy} (效果: {effectiveness:.2%})")
        else:
            lines.append("暂无足够数据")
        lines.append("")

        lines.append("=" * 70)
        lines.append(f"报告生成于: {datetime.now().isoformat()}")
        lines.append("=" * 70)

        return "\n".join(lines)

    def export_for_self_agent(self, profile: AdvancedEmotionProfile) -> Dict:
        """导出为Self-Agent可用的格式"""
        return {
            'user_id': profile.user_id,
            'personality': asdict(profile.personality),
            'emotion_baseline': profile.emotion_baseline,
            'typical_patterns': [asdict(c) for c in profile.emotion_clusters[:5]],
            'triggers': profile.triggers,
            'coping_strategies': profile.coping_strategies,
            'risk_prediction': asdict(profile.risk_prediction) if profile.risk_prediction else {},
            'emotion_network': profile.emotion_network
        }

    def _save_profile(self, profile: AdvancedEmotionProfile):
        """保存画像到文件"""
        profile_path = self.storage_dir / f"{profile.user_id}.json"

        data = {
            'user_id': profile.user_id,
            'created_at': profile.created_at,
            'updated_at': profile.updated_at,
            'snapshots': [asdict(s) for s in profile.snapshots],
            'emotion_baseline': profile.emotion_baseline,
            'emotion_trend': asdict(profile.emotion_trend) if profile.emotion_trend else None,
            'emotion_cycles': [asdict(c) for c in profile.emotion_cycles],
            'emotion_clusters': [asdict(c) for c in profile.emotion_clusters],
            'personality': asdict(profile.personality),
            'risk_prediction': asdict(profile.risk_prediction) if profile.risk_prediction else None,
            'triggers': profile.triggers,
            'coping_strategies': profile.coping_strategies,
            'emotion_network': profile.emotion_network,
            'total_interactions': profile.total_interactions,
            'crisis_count': profile.crisis_count,
            'intervention_count': profile.intervention_count,
            'avg_recovery_time': profile.avg_recovery_time,
            'data_quality_score': profile.data_quality_score,
            'last_analysis_date': profile.last_analysis_date
        }

        with open(profile_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.debug(f"保存高级画像: {profile.user_id}")
