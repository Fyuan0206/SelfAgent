"""
Self-Agent CAMEL工具集成
整合情绪识别、DBT技能推荐、紧急协议等所有工具
"""

from typing import Dict, Any, Optional
from camel.toolkits import BaseToolkit
from loguru import logger

# 导入情绪识别模块
from app.modules.emotion import EmotionRecognitionEngine
from app.modules.emotion.config_loader import EmotionConfigLoader


class EmotionDetectionTool(BaseToolkit):
    """情绪检测工具"""

    def __init__(self):
        self.engine = None

    def _ensure_engine(self):
        """确保引擎已初始化"""
        if self.engine is None:
            try:
                config_loader = EmotionConfigLoader()
                self.engine = EmotionRecognitionEngine(config_loader.get_config())
                logger.info("情绪识别引擎初始化成功")
            except Exception as e:
                logger.error(f"情绪识别引擎初始化失败: {e}")
                # 创建空引擎作为后备
                self.engine = None

    def detect_emotion_and_risk(
        self,
        text: str,
        user_id: str = "default_user"
    ) -> Dict[str, Any]:
        """
        检测用户情绪和风险等级

        Args:
            text: 用户输入文本
            user_id: 用户ID

        Returns:
            包含情绪分析、路由级别、风险等级的字典
        """
        self._ensure_engine()

        if self.engine is None:
            # 后备方案：返回基础分析
            return {
                'emotions': {},
                'dominant_emotion': 'unknown',
                'arousal': 0.0,
                'route_level': 'L1_QUICK',
                'risk_level': 'LOW',
                'triggered': False,
                'crisis_flag': False,
                'recommendations': ['情绪识别引擎未初始化']
            }

        try:
            result = self.engine.analyze(
                text=text,
                user_id=user_id,
                context=""
            )

            emotions = result['emotion_features']['emotions']
            dominant_emotion = max(emotions.items(), key=lambda x: x[1])[0] if emotions else 'neutral'

            return {
                'emotions': emotions,
                'dominant_emotion': dominant_emotion,
                'arousal': result['emotion_features']['arousal'],
                'route_level': result['routing_decision']['level'],
                'risk_level': result['intervention_assessment']['risk_level'],
                'triggered': result['intervention_assessment']['triggered'],
                'crisis_flag': result['routing_decision']['crisis_flag'],
                'urgency_score': result['intervention_assessment']['urgency_score'],
                'trigger_signals': result['intervention_assessment']['trigger_signals'],
                'recommendations': result['recommendations']
            }
        except Exception as e:
            logger.error(f"情绪检测失败: {e}")
            return {
                'emotions': {},
                'dominant_emotion': 'error',
                'arousal': 0.0,
                'route_level': 'L1_QUICK',
                'risk_level': 'LOW',
                'triggered': False,
                'crisis_flag': False,
                'error': str(e)
            }

    def analyze_user_emotion(self, text: str, user_id: str = "default_user") -> Dict[str, Any]:
        """
        对用户输入进行深度情绪分析，了解其详细的情绪状态。
        当需要详细的情绪细分而不仅仅是风险等级时，请使用此工具。
        
        Args:
            text: 用户的输入文本。
            user_id: 用户的唯一ID。
            
        Returns:
            详细的情绪分数、唤醒度和主要情绪。
        """
        self._ensure_engine()
        
        if not self.engine:
            return {"error": "Emotion engine not available"}
            
        try:
            result = self.engine.analyze(text=text, user_id=user_id)
            emotions = result['emotion_features']['emotions']
            dominant = max(emotions.items(), key=lambda x: x[1])[0] if emotions else "neutral"
            
            return {
                "emotions": emotions,
                "arousal": result['emotion_features']['arousal'],
                "dominant_emotion": dominant,
                "recommendations": result['recommendations']
            }
        except Exception as e:
            return {"error": str(e)}


class DBTSkillsTool(BaseToolkit):
    """DBT技能推荐工具 - 集成版"""

    def __init__(self):
        # 延迟导入以避免循环依赖和初始化问题
        self.recommendation_engine = None
        self.skill_repository = None
        self.session_factory = None

    async def _ensure_initialized(self):
        """确保推荐引擎已初始化"""
        if self.recommendation_engine is not None:
            return

        try:
            from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
            from app.modules.dbt.models.database import Base
            from app.modules.dbt.repositories.skill_repository import SkillRepository
            from app.modules.dbt.services.recommendation_engine import RecommendationEngine
            from app.modules.dbt.config import get_settings

            settings = get_settings()
            # 使用内存数据库作为演示，实际应使用持久化数据库
            engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
            
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            self.session_factory = async_sessionmaker(engine, class_=AsyncSession)
            
            # 初始化基础数据（演示用）
            async with self.session_factory() as session:
                from app.modules.dbt.db.init_data import init_db_data
                await init_db_data(session)
                
            self.recommendation_engine = RecommendationEngine(
                repository=None # Repository will be created per request with session
            )
            logger.info("DBT推荐引擎初始化成功")
            
        except Exception as e:
            logger.error(f"DBT推荐引擎初始化失败: {e}")
            self.recommendation_engine = None

    def recommend_dbt_skills(
        self,
        emotions: Dict[str, float],
        risk_level: str = "LOW",
        dominant_emotion: str = ""
    ) -> Dict[str, Any]:
        """
        根据情绪状态推荐DBT技能
        
        Args:
            emotions: 情绪分数字典
            risk_level: 风险等级
            dominant_emotion: 主要情绪
            
        Returns:
            推荐的DBT技能列表和指导
        """
        # 由于CAMEL工具目前是同步调用，我们需要在同步上下文中运行异步代码
        import asyncio
        
        try:
            return asyncio.run(self._async_recommend(emotions, risk_level, dominant_emotion))
        except Exception as e:
            logger.error(f"DBT推荐失败: {e}")
            return {
                'recommended_skills': [],
                'primary_skill': None,
                'guidance': f"系统繁忙，建议尝试深呼吸练习。错误: {str(e)}"
            }

    async def _async_recommend(
        self,
        emotions: Dict[str, float],
        risk_level: str,
        dominant_emotion: str
    ) -> Dict[str, Any]:
        """异步执行推荐"""
        await self._ensure_initialized()
        
        if not self.session_factory:
            return {'error': 'DBT引擎未初始化'}

        from app.modules.dbt.models.schemas import (
            RecommendRequest, EmotionInput, InterventionAssessment, 
            TriggerSignals
        )
        from app.modules.dbt.models.enums import RiskLevel as DBTRiskLevel
        from app.modules.dbt.repositories.skill_repository import SkillRepository
        from app.modules.dbt.services.recommendation_engine import RecommendationEngine

        # 映射风险等级
        risk_map = {
            "LOW": DBTRiskLevel.LOW,
            "MEDIUM": DBTRiskLevel.MEDIUM,
            "HIGH": DBTRiskLevel.HIGH,
            "CRITICAL": DBTRiskLevel.CRITICAL
        }
        
        # 构建请求对象
        # 计算arousal (如果没有提供，使用最大情绪值作为估算)
        arousal = max(emotions.values()) if emotions else 0.5
        
        request = RecommendRequest(
            emotion_input=EmotionInput(
                emotions=emotions,
                arousal=arousal
            ),
            intervention_assessment=InterventionAssessment(
                triggered=risk_level != "LOW",
                risk_level=risk_map.get(risk_level, DBTRiskLevel.LOW),
                urgency_score=0.8 if risk_level == "CRITICAL" else 0.5,
                trigger_signals=TriggerSignals(),
                intervention_reason=f"Detected {dominant_emotion}"
            ),
            context=f"Primary emotion: {dominant_emotion}"
        )

        async with self.session_factory() as session:
            repo = SkillRepository(session)
            engine = RecommendationEngine(repo)
            
            result = await engine.recommend(request)
            
            # 转换为简单字典格式返回
            return {
                'recommended_skills': [
                    {
                        'name': s.skill_name,
                        'description': s.description,
                        'steps': [step.instruction for step in s.steps]
                    } for s in result.recommended_skills
                ],
                'primary_skill': result.recommended_skills[0].skill_name if result.recommended_skills else None,
                'dominant_emotion': dominant_emotion,
                'risk_level': risk_level,
                'guidance': result.recommendation_reason,
                'strategy': result.guidance_strategy.model_dump()
            }



class EmergencyProtocolTool(BaseToolkit):
    """紧急协议工具"""

    def __init__(self):
        # 紧急联系人配置
        self.emergency_contacts = {
            'national_hotline': {
                'name': '全国心理援助热线',
                'number': '400-161-9995',
                'description': '24小时免费心理援助热线'
            },
            'crisis_hotline': {
                'name': '危机干预热线',
                'number': '010-82951332',
                'description': '北京心理危机研究与干预中心'
            },
            'suicide_prevention': {
                'name': '希望24热线',
                'number': '400-161-9995',
                'description': '24小时自杀预防热线'
            }
        }

    def handle_emergency_protocol(
        self,
        crisis_type: str = "suicide",
        severity: str = "high"
    ) -> Dict[str, Any]:
        """
        触发紧急协议

        Args:
            crisis_type: 危机类型
            severity: 严重程度

        Returns:
            紧急响应和联系信息
        """
        response = {
            'alert_level': 'CRITICAL',
            'immediate_actions': [],
            'contacts': [],
            'safety_plan': [],
            'message': ''
        }

        # 立即行动
        response['immediate_actions'] = [
            '⚠️ 请立即停止任何危险行为',
            '📞 马上拨打以下热线电话',
            '👥 联系您信任的人（家人、朋友）',
            '🏥 如果情况紧急，直接前往最近的医院急诊科'
        ]

        # 联系信息
        for contact_type, contact_info in self.emergency_contacts.items():
            response['contacts'].append({
                'name': contact_info['name'],
                'number': contact_info['number'],
                'description': contact_info['description']
            })

        # 安全计划
        response['safety_plan'] = [
            '1. 环境安全：移除所有可能造成伤害的物品',
            '2. 陪伴支持：不要独处，找信任的人陪伴',
            '3. 专业帮助：尽快联系心理医生或精神科医生',
            '4. 后续跟进：预约心理咨询，持续获得支持'
        ]

        # 紧急消息
        response['message'] = self._generate_emergency_message(crisis_type)

        return response

    def _generate_emergency_message(self, crisis_type: str) -> str:
        """生成紧急响应消息"""
        base_message = """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
           🚨 紧急支持协议 🚨
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

我非常关心您的安全。您现在的感受很重要，
请让我帮助您获得专业的支持。

【立即行动】
"""

        if crisis_type == "suicide":
            base_message += """
📞 24小时心理援助热线：
   • 全国心理援助热线：400-161-9995
   • 北京危机干预热线：010-82951332
   • 希望24热线：400-161-9995

【重要提醒】
• 您不是一个人
• 这种感觉会过去
• 请给自己一个机会
• 专业帮助可以带来改变

【请立即】
1. 拨打上述热线
2. 联系家人或朋友
3. 前往最近医院急诊科

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        elif crisis_type == "self_harm":
            base_message += """
📞 请立即联系：
   • 心理援助热线：400-161-9995
   • 您的信任的人

【替代方案】
• 使用TIPP技能（握住冰块、剧烈运动）
• 切换环境：离开当前场所
• 延迟行动：等待15分钟再决定

【您值得被帮助】
请联系专业心理咨询师
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        else:
            base_message += """
请根据您的具体情况联系专业帮助。
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

        return base_message


class UserProfileTool(BaseToolkit):
    """用户画像工具"""

    def __init__(self):
        self.engine = None

    def _ensure_engine(self):
        """确保引擎已初始化"""
        if self.engine is None:
            try:
                config_loader = EmotionConfigLoader()
                self.engine = EmotionRecognitionEngine(config_loader.get_config())
            except Exception as e:
                logger.error(f"用户画像工具初始化失败: {e}")
                self.engine = None

    def get_user_profile(
        self,
        user_id: str = "default_user"
    ) -> Dict[str, Any]:
        """
        获取用户画像
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户画像数据
        """
        self._ensure_engine()
        
        if self.engine is None:
            return {
                'error': '画像引擎未初始化',
                'user_id': user_id
            }
            
        try:
            profile = self.engine.get_profile(user_id)
            if profile is None:
                return {
                    'error': '用户画像不存在',
                    'user_id': user_id,
                    'message': '请先进行情绪分析以建立画像'
                }
            
            return profile
        except ImportError as e:
            logger.error(f"Import error in get_user_profile: {e}")
            return {'error': '系统配置错误: 依赖模块加载失败'}
        except Exception as e:
            return {
                'error': str(e),
                'user_id': user_id
            }

    def get_emotion_report(
        self,
        user_id: str = "default_user"
    ) -> str:
        """
        获取用户情绪报告

        Args:
            user_id: 用户ID

        Returns:
            详细的情绪报告文本
        """
        self._ensure_engine()

        if self.engine is None:
            return "情绪识别引擎未初始化"

        try:
            report = self.engine.generate_profile_report(user_id)
            if report is None:
                return "用户画像不存在或数据不足，无法生成报告"
            return report
        except Exception as e:
            return f"生成报告失败: {str(e)}"


# 全局工具实例
_emotion_tool = None
_dbt_tool = None
_emergency_tool = None
_profile_tool = None


def get_self_agent_tools() -> list:
    """
    获取Self-Agent的所有工具

    Returns:
        工具函数列表
    """
    global _emotion_tool, _dbt_tool, _emergency_tool, _profile_tool

    if _emotion_tool is None:
        _emotion_tool = EmotionDetectionTool()
        _dbt_tool = DBTSkillsTool()
        _emergency_tool = EmergencyProtocolTool()
        _profile_tool = UserProfileTool()

    return [
        _emotion_tool.detect_emotion_and_risk,
        _emotion_tool.analyze_user_emotion, # New tool registered
        _dbt_tool.recommend_dbt_skills,
        _emergency_tool.handle_emergency_protocol,
        _profile_tool.get_user_profile,
        _profile_tool.get_emotion_report
    ]
