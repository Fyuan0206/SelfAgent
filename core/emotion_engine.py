"""
情绪识别引擎主模块
整合所有子模块，提供统一接口
"""

import yaml
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

from core.emotion_extractor import EmotionExtractor, EmotionFeatures
from routing.intelligent_router import IntelligentRouter, RouteLevel
from intervention.dbt_intervention import RiskAssessmentEngine
from profile.emotion_profile import EmotionProfileManager, EmotionSnapshot
from profile.advanced_emotion_profile import AdvancedEmotionProfileManager, AdvancedEmotionProfile, EmotionSnapshot as AdvancedEmotionSnapshot
from loguru import logger


class EmotionRecognitionEngine:
    """情绪识别引擎主类"""

    def __init__(self, config_path: str = "config.yaml", use_advanced_profile: bool = True):
        # 加载配置
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        # 初始化各模块
        logger.info("初始化情绪识别引擎...")

        self.extractor = EmotionExtractor(self.config)
        self.router = IntelligentRouter(self.config)
        self.risk_engine = RiskAssessmentEngine(self.config)

        # 选择画像管理器（高级版 or 基础版）
        self.use_advanced_profile = use_advanced_profile
        if use_advanced_profile:
            self.profile_manager = AdvancedEmotionProfileManager(self.config)
            logger.info("使用高级情绪画像系统")
        else:
            self.profile_manager = EmotionProfileManager(self.config)
            logger.info("使用基础情绪画像系统")

        # 对话历史（用于上下文分析）
        self.conversation_history = {}

        logger.info("情绪识别引擎初始化完成")

    def analyze(self, text: str,
                user_id: str,
                audio_path: Optional[str] = None,
                audio_data: Optional[Dict] = None,
                video_path: Optional[str] = None,
                video_data: Optional[np.ndarray] = None,
                context: str = "") -> Dict:
        """
        完整的情绪分析流程

        Args:
            text: 输入文本
            user_id: 用户ID
            audio_path: 音频文件路径（可选）
            audio_data: 音频数据字典（可选）包含'data'和'sample_rate'
            video_path: 视频文件路径（可选）
            video_data: 视频数据帧（可选）numpy数组
            context: 对话上下文（可选）

        Returns:
            完整的分析结果字典
        """
        logger.info(f"开始分析用户 {user_id} 的情绪状态")

        # 1. 提取情绪特征
        logger.info("步骤1: 提取情绪特征")
        features = self.extractor.extract(
            text=text,
            audio_path=audio_path,
            audio_data=audio_data,
            video_path=video_path,
            frame=video_data
        )

        # 1.5 融合图像情绪到text_emotion（用于纯图像输入的情况）
        if features.video_features:
            # 检查video_features中是否包含DBT情绪
            dbt_emotions = self.extractor.dbt_emotions
            video_emotions = {k: v for k, v in features.video_features.items()
                            if k in dbt_emotions and v > 0}

            # 如果图像有明显的情绪分数，且文本是占位符或中性
            if video_emotions and sum(video_emotions.values()) > 0.3:
                if text in ["[图像输入]", "[IMAGE_INPUT]", ""] or \
                   all(v == 0 for v in features.text_emotion.values()):
                    # 将图像情绪融合到text_emotion中
                    for emotion, score in video_emotions.items():
                        features.text_emotion[emotion] = max(
                            features.text_emotion.get(emotion, 0),
                            score * 0.8  # 图像情绪权重0.8
                        )
                    logger.info(f"融合图像情绪到text_emotion: {video_emotions}")

        # 2. 智能路由
        logger.info("步骤2: 执行智能路由")
        route_result = self.router.route(
            text=text,
            emotion_features=features.text_emotion,
            audio_features=features.audio_features,
            video_features=features.video_features
        )

        # 3. 计算情绪斜率
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []

        emotion_slope = self.router.calculate_emotion_slope(
            self.conversation_history[user_id]
        )

        # 4. 分析对话上下文
        conversation_context = self.router.analyze_conversation_context(
            self.conversation_history[user_id]
        )

        # 5. 风险评估
        logger.info("步骤3: 评估风险等级")
        intervention_trigger = self.risk_engine.evaluate_risk(
            emotion_features=features.text_emotion,
            emotion_slope=emotion_slope,
            conversation_context=conversation_context
        )

        # 6. 加载或创建用户画像
        logger.info("步骤4: 更新用户画像")
        profile = self.profile_manager.load_profile(user_id)
        if profile is None:
            profile = self.profile_manager.create_profile(user_id)

        # 创建情绪快照（根据画像类型选择）
        if self.use_advanced_profile:
            # 高级快照 - 包含更多元数据
            snapshot = AdvancedEmotionSnapshot(
                timestamp=datetime.now().timestamp(),
                date=datetime.now().isoformat(),
                emotions=features.text_emotion,
                arousal=features.text_arousal,
                route_level=route_result.level.value,
                risk_level=intervention_trigger.risk_level.value,
                context=context,
                multimodal_vector=features.multimodal_vector.tolist(),
                input_type=self._detect_input_type(text, audio_path, video_data),
                time_of_day="",  # 会在profile update中填充
                day_of_week="",  # 会在profile update中填充
                is_weekend=False  # 会在profile update中填充
            )
        else:
            # 基础快照
            snapshot = EmotionSnapshot(
                timestamp=datetime.now().timestamp(),
                date=datetime.now().isoformat(),
                emotions=features.text_emotion,
                arousal=features.text_arousal,
                route_level=route_result.level.value,
                risk_level=intervention_trigger.risk_level.value,
                context=context,
                multimodal_vector=features.multimodal_vector.tolist()
            )

        # 更新画像
        self.profile_manager.update_profile(
            profile=profile,
            emotion_snapshot=snapshot,
            route_level=route_result.level.value,
            risk_level=intervention_trigger.risk_level.value
        )

        # 7. 记录对话历史
        self.conversation_history[user_id].append({
            'timestamp': datetime.now().timestamp(),
            'text': text,
            'emotions': features.text_emotion.copy()
        })

        # 限制历史长度
        if len(self.conversation_history[user_id]) > 50:
            self.conversation_history[user_id].pop(0)

        # 8. 构建返回结果
        result = {
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),

            # 情绪特征
            'emotion_features': {
                'emotions': features.text_emotion,
                'arousal': features.text_arousal,
                'confidence': features.confidence,
                'audio_features': features.audio_features,
                'video_features': features.video_features
            },

            # 路由决策
            'routing_decision': {
                'level': route_result.level.value,
                'reason': route_result.reason,
                'suggested_action': route_result.suggested_action,
                'requires_dbt': route_result.requires_dbt,
                'crisis_flag': route_result.crisis_flag
            },

            # 干预评估
            'intervention_assessment': {
                'triggered': intervention_trigger.triggered,
                'risk_level': intervention_trigger.risk_level.value,
                'urgency_score': intervention_trigger.urgency_score,
                'trigger_signals': intervention_trigger.trigger_signals,
                'intervention_reason': intervention_trigger.intervention_reason
            },

            # 上下文分析
            'context_analysis': {
                'emotion_slope': emotion_slope,
                'conversation_patterns': conversation_context
            },

            # 画像更新
            'profile_updated': True,
            'baseline_emotions': profile.emotion_baseline if self.use_advanced_profile else profile.baseline_emotions,
            'stability_score': profile.emotion_patterns.get('stability_score', 0.5) if hasattr(profile, 'emotion_patterns') else 0.5,

            # 系统建议
            'recommendations': self._generate_recommendations(
                route_result, intervention_trigger, profile
            )
        }

        logger.info(f"分析完成 - 路由级别: {route_result.level.value}, 风险等级: {intervention_trigger.risk_level.value}")

        return result

    def _generate_recommendations(self, route_result, intervention_trigger, profile) -> List[str]:
        """生成系统建议"""
        recommendations = []

        # 根据路由级别
        if route_result.level == RouteLevel.L3_CRISIS:
            recommendations.append("🚨 立即启动危机干预程序")
            recommendations.append("📞 联系紧急联系人或专业帮助")
            recommendations.append("⚠️ 不要让用户独处")
        elif route_result.level == RouteLevel.L2_INTERVENTION:
            recommendations.append("💡 建议启用DBT技能支持（模块2）")
            recommendations.append(f"📊 风险信号: {intervention_trigger.trigger_signals}")
        else:
            recommendations.append("✅ 继续日常对话支持")

        # 根据风险等级
        if intervention_trigger.risk_level.value in ['HIGH', 'CRITICAL']:
            recommendations.append("⏰ 安排后续跟进")
            recommendations.append("👥 考虑通知支持网络")

        # 根据画像特征
        typical_response = None
        if self.use_advanced_profile and hasattr(profile, 'emotion_clusters'):
            # 从聚类中推断典型反应
            if profile.emotion_clusters:
                cluster_name = profile.emotion_clusters[0].cluster_name
                if 'anger' in cluster_name.lower() or 'rage' in cluster_name.lower():
                    typical_response = 'anger'
                elif 'sad' in cluster_name.lower() or 'withdraw' in cluster_name.lower():
                    typical_response = 'withdrawal'

        if not typical_response and hasattr(profile, 'emotion_patterns'):
            typical_response = profile.emotion_patterns.get('typical_response')

        if typical_response == 'withdrawal':
            recommendations.append("🤗 用户倾向于退缩，给予温和支持")
        elif typical_response == 'anger':
            recommendations.append("😤 用户倾向于愤怒，接纳并认可感受")

        # 病理性特征警告
        if self.use_advanced_profile:
            # 高级画像有内置的风险预测
            if profile.risk_prediction and profile.risk_prediction.early_warning_signals:
                recommendations.append("⚠️ 检测到早期预警信号，建议密切关注")
        else:
            pathological = self.profile_manager.detect_pathological_features(profile)
            if pathological:
                recommendations.append("⚠️ 建议寻求专业心理咨询")

        return recommendations

    def get_profile(self, user_id: str) -> Optional[Dict]:
        """获取用户画像"""
        profile = self.profile_manager.load_profile(user_id)
        if profile is None:
            return None

        if self.use_advanced_profile:
            # 高级画像
            return {
                'raw_profile': profile,
                'report': self.profile_manager.generate_profile_report(profile),
                'self_agent_export': self.profile_manager.export_for_self_agent(profile)
            }
        else:
            # 基础画像
            return {
                'summary': self.profile_manager.get_profile_summary(profile),
                'self_agent_params': self.profile_manager.export_for_self_agent(profile),
                'pathological_indicators': self.profile_manager.detect_pathological_features(profile)
            }

    def generate_profile_report(self, user_id: str) -> Optional[str]:
        """生成详细的用户画像报告"""
        if not self.use_advanced_profile:
            logger.warning("生成详细报告需要启用高级画像系统 (use_advanced_profile=True)")
            return None

        profile = self.profile_manager.load_profile(user_id)
        if profile is None:
            logger.warning(f"用户画像不存在: {user_id}")
            return None

        return self.profile_manager.generate_profile_report(profile)

    def _detect_input_type(self, text: str, audio_path: Optional[str], video_data: Optional[np.ndarray]) -> str:
        """检测输入类型"""
        if video_data is not None:
            return "image"
        elif audio_path is not None:
            return "audio"
        elif text and text not in ["[图像输入]", "[IMAGE_INPUT]", "[视频输入]", ""]:
            return "text"
        else:
            return "unknown"

    def reset_user_history(self, user_id: str):
        """重置用户历史（测试用）"""
        if user_id in self.conversation_history:
            self.conversation_history[user_id] = []
        logger.info(f"重置用户 {user_id} 的历史记录")

    def batch_analyze(self, texts: List[str], user_id: str) -> List[Dict]:
        """批量分析（用于数据处理）"""
        results = []
        for text in texts:
            result = self.analyze(text=text, user_id=user_id)
            results.append(result)
        return results

    def get_system_stats(self) -> Dict:
        """获取系统统计信息"""
        # 统计profiles目录下的用户数
        profiles_dir = Path("profiles")
        user_count = len(list(profiles_dir.glob("*.json"))) if profiles_dir.exists() else 0

        return {
            'total_users': user_count,
            'tracked_users': len(self.conversation_history),
            'engine_type': 'risk_assessment',
            'model_status': 'remote_api' if self.extractor.api_key else 'local_rules'
        }
