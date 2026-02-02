"""
推荐引擎
整合规则匹配和LLM的推荐引擎，提供完整的DBT技能推荐功能
"""

from typing import Optional
from loguru import logger

from ..config import get_settings
from ..models.schemas import (
    RecommendRequest, DBTRecommendation, GuidanceStrategy,
    RecommendedSkill, MatchResult
)
from ..models.enums import (
    GuidanceApproach, GuidanceIntensity, GuidanceTone, RiskLevel
)
from .skill_matcher import SkillMatcher
from .llm_service import LLMService
from ..repositories.skill_repository import SkillRepository


class RecommendationEngine:
    """整合规则匹配和LLM的推荐引擎"""

    def __init__(
        self,
        repository: SkillRepository,
        skill_matcher: Optional[SkillMatcher] = None,
        llm_service: Optional[LLMService] = None
    ):
        self.repository = repository
        self.skill_matcher = skill_matcher or SkillMatcher(repository)
        self.llm_service = llm_service or LLMService()
        self.settings = get_settings()

    async def recommend(self, request: RecommendRequest) -> DBTRecommendation:
        """
        执行完整推荐流程

        1. 规则匹配获取技能
        2. 如果规则未匹配，调用LLM处理边缘情况
        3. 调用LLM生成推荐理由
        4. 确定引导策略
        5. 组装返回结果

        Args:
            request: 推荐请求

        Returns:
            DBTRecommendation: 完整推荐结果
        """
        logger.info(f"开始推荐流程，风险等级: {request.intervention_assessment.risk_level}")

        # 1. 规则匹配
        match_result = await self.skill_matcher.match(
            request,
            max_skills=self.settings.recommendation.max_skills_per_recommendation
        )
        logger.debug(f"规则匹配结果: {len(match_result.skills)} 个技能，规则: {match_result.matched_rules}")

        # 2. 边缘情况处理
        if not match_result.skills and self.settings.recommendation.enable_llm_fallback:
            logger.info("规则未匹配，尝试LLM边缘情况处理")
            match_result = await self._handle_edge_case(request)

        # 确保有推荐结果
        if not match_result.skills:
            logger.warning("未能找到匹配技能，使用默认推荐")
            match_result = await self._get_default_recommendation(request)

        # 3. 生成推荐理由
        if self.settings.recommendation.enable_llm_reason:
            reason = await self.llm_service.generate_recommendation_reason(
                request, match_result.skills
            )
        else:
            reason = self._get_simple_reason(match_result.skills)

        # 4. 确定引导策略
        strategy = self._determine_guidance_strategy(request, match_result)

        # 5. 组装结果
        recommendation = DBTRecommendation(
            recommended_module=match_result.module,
            recommended_skills=match_result.skills,
            recommendation_reason=reason,
            guidance_strategy=strategy,
            fallback_skills=match_result.fallbacks,
            metadata={
                "matched_rules": match_result.matched_rules,
                "risk_level": request.intervention_assessment.risk_level.value,
                "urgency_score": request.intervention_assessment.urgency_score
            }
        )

        logger.info(f"推荐完成: 模块={recommendation.recommended_module}, "
                   f"技能数={len(recommendation.recommended_skills)}")

        return recommendation

    async def _handle_edge_case(self, request: RecommendRequest) -> MatchResult:
        """处理边缘情况"""
        # 调用LLM获取推荐技能名称
        skill_names = await self.llm_service.handle_edge_case(request)

        if not skill_names:
            return MatchResult(module="痛苦耐受", skills=[], fallbacks=[])

        # 查找对应的技能
        skills = []
        module_name = "痛苦耐受"

        for name in skill_names:
            skill = await self.repository.get_skill_by_name(name)
            if skill:
                recommended = RecommendedSkill(
                    skill_id=skill.id,
                    skill_name=skill.name,
                    skill_name_en=skill.name_en,
                    module_name=skill.module.name if skill.module else "",
                    description=skill.description or "",
                    steps=[],
                    match_score=0.5,  # 边缘情况固定分数
                    match_reason="LLM推荐"
                )
                skills.append(recommended)
                if skill.module:
                    module_name = skill.module.name

        return MatchResult(
            module=module_name,
            skills=skills,
            fallbacks=[],
            matched_rules=["llm_edge_case"]
        )

    async def _get_default_recommendation(self, request: RecommendRequest) -> MatchResult:
        """获取默认推荐（当所有方法都失败时）"""
        # 根据风险等级选择默认技能
        risk_level = request.intervention_assessment.risk_level

        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            # 高风险优先推荐TIPP
            default_skill_name = "TIPP"
            module_name = "痛苦耐受"
        elif request.emotion_input.arousal > 0.6:
            # 高唤醒推荐深呼吸/TIPP
            default_skill_name = "TIPP"
            module_name = "痛苦耐受"
        else:
            # 其他情况推荐正念观察
            default_skill_name = "观察"
            module_name = "正念"

        # 尝试获取技能
        skill = await self.repository.get_skill_by_name(default_skill_name)

        if skill:
            recommended = RecommendedSkill(
                skill_id=skill.id,
                skill_name=skill.name,
                skill_name_en=skill.name_en,
                module_name=skill.module.name if skill.module else module_name,
                description=skill.description or "",
                steps=[],
                match_score=0.3,
                match_reason="默认推荐"
            )
            return MatchResult(
                module=module_name,
                skills=[recommended],
                fallbacks=["深呼吸", "自我安抚"],
                matched_rules=["default_fallback"]
            )

        # 如果数据库为空，返回空结果
        return MatchResult(
            module=module_name,
            skills=[],
            fallbacks=["深呼吸", "正念观察"],
            matched_rules=[]
        )

    def _determine_guidance_strategy(
        self,
        request: RecommendRequest,
        match_result: MatchResult
    ) -> GuidanceStrategy:
        """确定引导策略"""
        risk_level = request.intervention_assessment.risk_level
        urgency = request.intervention_assessment.urgency_score
        arousal = request.emotion_input.arousal

        # 确定引导方式
        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            approach = GuidanceApproach.EMPATHY_FIRST
        elif urgency > 0.7:
            approach = GuidanceApproach.SKILL_ORIENTED
        else:
            approach = GuidanceApproach.EMPATHY_FIRST

        # 确定引导强度
        if risk_level == RiskLevel.CRITICAL:
            intensity = GuidanceIntensity.CRISIS_PRIORITY
        elif risk_level == RiskLevel.HIGH or urgency > 0.6:
            intensity = GuidanceIntensity.STANDARD_TRAINING
        else:
            intensity = GuidanceIntensity.LIGHT_REMINDER

        # 确定语气
        if arousal > 0.7:
            tone = GuidanceTone.CALM  # 高唤醒时使用平静语气
        elif risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            tone = GuidanceTone.WARM  # 高风险时使用温暖语气
        else:
            tone = GuidanceTone.ENCOURAGING  # 其他情况使用鼓励语气

        # 生成关键引导点
        key_points = self._generate_key_points(request, match_result, approach)

        return GuidanceStrategy(
            approach=approach,
            intensity=intensity,
            tone=tone,
            key_points=key_points
        )

    def _generate_key_points(
        self,
        request: RecommendRequest,
        match_result: MatchResult,
        approach: GuidanceApproach
    ) -> list:
        """生成关键引导点"""
        points = []

        # 根据引导方式添加基础引导点
        if approach == GuidanceApproach.EMPATHY_FIRST:
            points.append("先认可用户的情绪体验")
            points.append("表达理解和支持")

        # 根据技能添加引导点
        if match_result.skills:
            skill = match_result.skills[0]

            # 特定技能的引导点
            skill_guidance = {
                "TIPP": ["引导用户感受身体状态", "一步一步引导TIPP技能"],
                "STOP": ["帮助用户暂停当前行动", "引导观察和思考"],
                "ACCEPTS": ["提供注意力转移的选项", "鼓励尝试不同的活动"],
                "检查事实": ["帮助用户分析情境", "区分事实和解读"],
                "彻底接纳": ["认可用户的痛苦", "引导接受不能改变的现实"],
                "观察": ["引导关注当下", "不评判地觉察"],
                "DEAR MAN": ["帮助明确需求", "练习有效表达"],
            }

            if skill.skill_name in skill_guidance:
                points.extend(skill_guidance[skill.skill_name])
            else:
                points.append(f"一步一步引导{skill.skill_name}技能")

        # 根据风险等级添加引导点
        risk_level = request.intervention_assessment.risk_level
        if risk_level == RiskLevel.CRITICAL:
            points.insert(0, "确认用户安全")
        elif risk_level == RiskLevel.HIGH:
            points.append("持续关注用户状态")

        # 限制引导点数量
        return points[:5]

    def _get_simple_reason(self, skills: list) -> str:
        """生成简单推荐理由（不使用LLM时）"""
        if not skills:
            return "建议尝试一些放松技巧来帮助你感觉好一些。"

        skill_names = "、".join([s.skill_name for s in skills])
        return f"基于当前状态，推荐使用{skill_names}技能来帮助你调节情绪。"


# ============== 测试用例 ==============
if __name__ == "__main__":
    import asyncio
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
    from ..models.database import Base, DBTModule, DBTSkill, SkillMatchingRule
    from ..models.schemas import (
        EmotionInput, TriggerSignals, InterventionAssessment, RecommendRequest
    )
    from ..models.enums import RiskLevel

    async def test_recommendation_engine():
        """测试推荐引擎"""
        # 创建内存数据库
        engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession)

        async with AsyncSessionLocal() as session:
            # 准备测试数据
            module1 = DBTModule(name="痛苦耐受", name_en="distress_tolerance")
            module2 = DBTModule(name="正念", name_en="mindfulness")
            session.add_all([module1, module2])
            await session.commit()
            await session.refresh(module1)
            await session.refresh(module2)

            skill1 = DBTSkill(
                module_id=module1.id,
                name="TIPP",
                name_en="TIPP",
                description="快速降低情绪强度",
                trigger_emotions=["焦虑", "激越"]
            )
            skill2 = DBTSkill(
                module_id=module2.id,
                name="观察",
                name_en="Observe",
                description="不评判地觉察当下体验",
                trigger_emotions=["注意力分散"]
            )
            session.add_all([skill1, skill2])
            await session.commit()
            await session.refresh(skill1)

            rule = SkillMatchingRule(
                rule_name="high_arousal_anxiety",
                priority=100,
                conditions={
                    "emotion_conditions": [
                        {"emotion": "焦虑", "operator": ">=", "value": 0.5}
                    ]
                },
                skill_ids=[skill1.id],
                module_id=module1.id
            )
            session.add(rule)
            await session.commit()

            # 创建推荐引擎
            repo = SkillRepository(session)
            engine_instance = RecommendationEngine(repo)

            # 测试1: 高焦虑状态推荐
            request = RecommendRequest(
                emotion_input=EmotionInput(
                    emotions={"焦虑": 0.7, "悲伤": 0.2},
                    arousal=0.8
                ),
                intervention_assessment=InterventionAssessment(
                    triggered=True,
                    risk_level=RiskLevel.MEDIUM,
                    urgency_score=0.6,
                    trigger_signals=TriggerSignals(agitation_level=0.5),
                    intervention_reason="焦虑(0.70)"
                ),
                context="学业压力"
            )

            recommendation = await engine_instance.recommend(request)

            assert recommendation.recommended_module == "痛苦耐受"
            assert len(recommendation.recommended_skills) > 0
            assert "TIPP" in [s.skill_name for s in recommendation.recommended_skills]
            print("✓ 测试1通过: 高焦虑状态正确推荐TIPP")

            # 测试2: 引导策略
            assert recommendation.guidance_strategy is not None
            assert recommendation.guidance_strategy.approach == GuidanceApproach.EMPATHY_FIRST
            print(f"✓ 测试2通过: 引导策略正确 (approach={recommendation.guidance_strategy.approach})")

            # 测试3: 推荐理由
            assert recommendation.recommendation_reason
            print(f"✓ 测试3通过: 推荐理由: {recommendation.recommendation_reason[:50]}...")

            # 测试4: 关键引导点
            assert len(recommendation.guidance_strategy.key_points) > 0
            print(f"✓ 测试4通过: 关键引导点: {recommendation.guidance_strategy.key_points}")

            # 测试5: 元数据
            assert "risk_level" in recommendation.metadata
            print(f"✓ 测试5通过: 元数据包含风险等级")

            # 测试6: 高风险状态
            request2 = RecommendRequest(
                emotion_input=EmotionInput(
                    emotions={"绝望": 0.8, "悲伤": 0.6},
                    arousal=0.9
                ),
                intervention_assessment=InterventionAssessment(
                    triggered=True,
                    risk_level=RiskLevel.HIGH,
                    urgency_score=0.9,
                    trigger_signals=TriggerSignals(despair_level=0.7),
                    intervention_reason="绝望(0.80)"
                )
            )

            recommendation2 = await engine_instance.recommend(request2)
            assert recommendation2.guidance_strategy.tone == GuidanceTone.WARM
            print("✓ 测试6通过: 高风险状态使用温暖语气")

            print("\n所有推荐引擎测试通过！")

        await engine.dispose()

    asyncio.run(test_recommendation_engine())
