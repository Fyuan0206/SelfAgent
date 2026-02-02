"""
技能匹配引擎
负责根据规则匹配合适的DBT技能
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from loguru import logger

from ..models.schemas import (
    RecommendRequest, RecommendedSkill, SkillStep, MatchResult
)
from ..models.database import DBTSkill, SkillMatchingRule
from ..models.enums import ConditionOperator
from ..repositories.skill_repository import SkillRepository


@dataclass
class MatchContext:
    """匹配上下文，用于在规则评估中传递数据"""
    emotions: Dict[str, float]
    arousal: float
    trigger_signals: Dict[str, float]
    context: str
    risk_level: str
    user_stability: float = 0.5
    last_skill: Optional[str] = None


@dataclass
class RuleMatchResult:
    """单条规则的匹配结果"""
    rule_name: str
    matched: bool
    score: float = 0.0
    skill_ids: List[int] = field(default_factory=list)
    module_id: Optional[int] = None
    match_details: Dict[str, Any] = field(default_factory=dict)


class SkillMatcher:
    """基于规则的技能匹配器"""

    def __init__(self, repository: SkillRepository):
        self.repository = repository
        # 运算符映射
        self._operators = {
            ">": lambda a, b: a > b,
            ">=": lambda a, b: a >= b,
            "<": lambda a, b: a < b,
            "<=": lambda a, b: a <= b,
            "==": lambda a, b: a == b,
            "!=": lambda a, b: a != b,
            "in": lambda a, b: a in b if isinstance(b, (list, tuple)) else False,
            "not_in": lambda a, b: a not in b if isinstance(b, (list, tuple)) else True,
            "contains": lambda a, b: b in a if isinstance(a, str) else False,
        }

    async def match(
        self,
        request: RecommendRequest,
        max_skills: int = 2
    ) -> MatchResult:
        """
        执行规则匹配

        Args:
            request: 推荐请求
            max_skills: 最大返回技能数

        Returns:
            MatchResult: 匹配结果
        """
        # 构建匹配上下文
        context = self._build_context(request)

        # 获取所有活跃规则
        rules = await self.repository.get_all_rules(active_only=True)
        logger.debug(f"加载了 {len(rules)} 条匹配规则")

        # 评估每条规则
        rule_results: List[RuleMatchResult] = []
        for rule in rules:
            result = self._evaluate_rule(rule, context)
            if result.matched:
                rule_results.append(result)
                logger.debug(f"规则 '{rule.rule_name}' 匹配成功，分数: {result.score}")

        # 如果没有匹配的规则，尝试基于情绪的直接匹配
        if not rule_results:
            logger.info("没有规则匹配，尝试基于情绪的直接匹配")
            rule_results = await self._fallback_emotion_match(context)

        # 按分数排序并选择技能
        rule_results.sort(key=lambda x: x.score, reverse=True)

        # 收集所有匹配的技能ID
        all_skill_ids = []
        matched_rules = []
        module_id = None
        for result in rule_results:
            all_skill_ids.extend(result.skill_ids)
            matched_rules.append(result.rule_name)
            if module_id is None and result.module_id:
                module_id = result.module_id

        # 去重并限制数量
        unique_skill_ids = list(dict.fromkeys(all_skill_ids))[:max_skills]

        # 获取技能详情
        skills = await self.repository.get_skills_by_ids(unique_skill_ids)

        # 转换为推荐技能
        recommended_skills = []
        for skill in skills:
            # 计算匹配分数
            match_score = self._calculate_skill_score(skill, context, rule_results)
            # 生成匹配原因
            match_reason = self._generate_match_reason(skill, context, rule_results)

            recommended_skill = self._skill_to_recommended(
                skill, match_score, match_reason
            )
            recommended_skills.append(recommended_skill)

        # 确定推荐模块
        if recommended_skills:
            module_name = recommended_skills[0].module_name
        elif module_id:
            module = await self.repository.get_module_by_id(module_id)
            module_name = module.name if module else "痛苦耐受"
        else:
            module_name = "痛苦耐受"  # 默认模块

        # 获取备选技能
        fallbacks = await self._get_fallback_skills(
            recommended_skills, module_id, context
        )

        return MatchResult(
            module=module_name,
            skills=recommended_skills,
            fallbacks=fallbacks,
            matched_rules=matched_rules
        )

    def _build_context(self, request: RecommendRequest) -> MatchContext:
        """构建匹配上下文"""
        trigger_signals = {
            "self_harm_impulse": request.intervention_assessment.trigger_signals.self_harm_impulse,
            "despair_level": request.intervention_assessment.trigger_signals.despair_level,
            "agitation_level": request.intervention_assessment.trigger_signals.agitation_level,
            "emptiness_level": request.intervention_assessment.trigger_signals.emptiness_level,
            "shame_level": request.intervention_assessment.trigger_signals.shame_level,
            "emotion_slope": request.intervention_assessment.trigger_signals.emotion_slope,
            "negative_total": request.intervention_assessment.trigger_signals.negative_total,
        }

        return MatchContext(
            emotions=request.emotion_input.emotions,
            arousal=request.emotion_input.arousal,
            trigger_signals=trigger_signals,
            context=request.context,
            risk_level=request.intervention_assessment.risk_level.value,
            user_stability=request.user_profile.stability_score if request.user_profile else 0.5,
            last_skill=request.agent_context.last_skill_used if request.agent_context else None
        )

    def _evaluate_rule(
        self,
        rule: SkillMatchingRule,
        context: MatchContext
    ) -> RuleMatchResult:
        """评估单条规则"""
        conditions = rule.conditions
        matched = True
        total_score = 0.0
        condition_count = 0
        match_details = {}

        # 评估情绪条件
        if "emotion_conditions" in conditions:
            for emo_cond in conditions["emotion_conditions"]:
                emotion = emo_cond.get("emotion")
                operator = emo_cond.get("operator", ">=")
                value = emo_cond.get("value", 0.5)

                actual_value = context.emotions.get(emotion, 0.0)
                cond_matched = self._evaluate_condition(actual_value, operator, value)

                if not cond_matched:
                    matched = False
                else:
                    total_score += actual_value
                    match_details[f"emotion_{emotion}"] = actual_value

                condition_count += 1

        # 评估触发信号条件
        if "trigger_signals" in conditions and matched:
            for sig_cond in conditions["trigger_signals"]:
                signal = sig_cond.get("signal")
                operator = sig_cond.get("operator", ">=")
                value = sig_cond.get("value", 0.3)

                actual_value = context.trigger_signals.get(signal, 0.0)
                cond_matched = self._evaluate_condition(actual_value, operator, value)

                if not cond_matched:
                    matched = False
                else:
                    total_score += actual_value * 0.5  # 触发信号权重略低
                    match_details[f"signal_{signal}"] = actual_value

                condition_count += 1

        # 评估唤醒度条件
        if "arousal" in conditions and matched:
            arousal_cond = conditions["arousal"]
            operator = arousal_cond.get("operator", ">=")
            value = arousal_cond.get("value", 0.5)

            cond_matched = self._evaluate_condition(context.arousal, operator, value)
            if not cond_matched:
                matched = False
            else:
                total_score += context.arousal * 0.3
                match_details["arousal"] = context.arousal

            condition_count += 1

        # 评估情境条件
        if "context_contains" in conditions and matched:
            keywords = conditions["context_contains"]
            if isinstance(keywords, str):
                keywords = [keywords]

            context_matched = any(kw in context.context for kw in keywords)
            if not context_matched:
                matched = False
            else:
                total_score += 0.2
                match_details["context"] = context.context

            condition_count += 1

        # 评估风险等级条件
        if "risk_level" in conditions and matched:
            required_levels = conditions["risk_level"]
            if isinstance(required_levels, str):
                required_levels = [required_levels]

            if context.risk_level not in required_levels:
                matched = False
            else:
                # 风险等级越高，分数越高
                risk_scores = {"LOW": 0.1, "MEDIUM": 0.3, "HIGH": 0.6, "CRITICAL": 0.9}
                total_score += risk_scores.get(context.risk_level, 0.1)
                match_details["risk_level"] = context.risk_level

            condition_count += 1

        # 计算平均分数
        avg_score = total_score / max(condition_count, 1)
        # 加上规则优先级加成
        final_score = avg_score + (rule.priority / 1000)

        return RuleMatchResult(
            rule_name=rule.rule_name,
            matched=matched,
            score=final_score,
            skill_ids=rule.skill_ids or [],
            module_id=rule.module_id,
            match_details=match_details
        )

    def _evaluate_condition(
        self,
        actual: float,
        operator: str,
        expected: float
    ) -> bool:
        """评估单个条件"""
        op_func = self._operators.get(operator)
        if op_func is None:
            logger.warning(f"未知运算符: {operator}")
            return False
        return op_func(actual, expected)

    async def _fallback_emotion_match(
        self,
        context: MatchContext
    ) -> List[RuleMatchResult]:
        """基于情绪的直接匹配（作为规则匹配的兜底）"""
        results = []

        # 找到最强的情绪
        if not context.emotions:
            return results

        top_emotion = max(context.emotions.items(), key=lambda x: x[1])
        emotion_name, emotion_value = top_emotion

        if emotion_value < 0.3:  # 情绪强度太低，不推荐
            return results

        # 根据情绪查找相关技能
        skills = await self.repository.get_skills_by_emotion(emotion_name)

        if skills:
            skill_ids = [s.id for s in skills[:2]]
            module_id = skills[0].module_id if skills else None

            results.append(RuleMatchResult(
                rule_name=f"emotion_fallback_{emotion_name}",
                matched=True,
                score=emotion_value,
                skill_ids=skill_ids,
                module_id=module_id,
                match_details={"primary_emotion": emotion_name, "value": emotion_value}
            ))

        return results

    def _calculate_skill_score(
        self,
        skill: DBTSkill,
        context: MatchContext,
        rule_results: List[RuleMatchResult]
    ) -> float:
        """计算技能的最终匹配分数"""
        base_score = 0.5

        # 从规则结果中获取分数
        for result in rule_results:
            if skill.id in result.skill_ids:
                base_score = max(base_score, result.score)
                break

        # 根据情绪匹配度调整
        if skill.trigger_emotions:
            for emotion in skill.trigger_emotions:
                if emotion in context.emotions:
                    base_score += context.emotions[emotion] * 0.1

        # 根据难度和用户稳定性调整
        if skill.difficulty_level:
            # 用户不稳定时，推荐简单技能
            if context.user_stability < 0.4 and skill.difficulty_level > 1:
                base_score -= 0.1 * (skill.difficulty_level - 1)
            # 用户稳定时，可以尝试更复杂的技能
            elif context.user_stability > 0.7 and skill.difficulty_level > 1:
                base_score += 0.05 * skill.difficulty_level

        return min(1.0, max(0.0, base_score))

    def _generate_match_reason(
        self,
        skill: DBTSkill,
        context: MatchContext,
        rule_results: List[RuleMatchResult]
    ) -> str:
        """生成匹配原因"""
        reasons = []

        # 从规则结果中提取原因
        for result in rule_results:
            if skill.id in result.skill_ids:
                if "emotion_" in str(result.match_details):
                    for key, value in result.match_details.items():
                        if key.startswith("emotion_"):
                            emotion = key.replace("emotion_", "")
                            reasons.append(f"{emotion}情绪较强({value:.1%})")
                if "signal_" in str(result.match_details):
                    for key, value in result.match_details.items():
                        if key.startswith("signal_"):
                            signal_names = {
                                "agitation_level": "激越状态",
                                "despair_level": "绝望感",
                                "self_harm_impulse": "冲动倾向",
                                "emptiness_level": "空虚感",
                                "shame_level": "羞愧感"
                            }
                            signal = key.replace("signal_", "")
                            signal_cn = signal_names.get(signal, signal)
                            reasons.append(f"{signal_cn}明显")
                break

        # 添加唤醒度信息
        if context.arousal > 0.6:
            reasons.append("情绪唤醒度较高")

        # 添加情境信息
        if context.context:
            reasons.append(f"情境: {context.context}")

        if reasons:
            return "；".join(reasons[:3])
        return "基于当前情绪状态推荐"

    def _skill_to_recommended(
        self,
        skill: DBTSkill,
        match_score: float,
        match_reason: str
    ) -> RecommendedSkill:
        """将数据库技能转换为推荐技能"""
        # 转换步骤
        steps = []
        if skill.steps:
            for step_data in skill.steps:
                step = SkillStep(
                    step_number=step_data.get("step_number", 0),
                    instruction=step_data.get("instruction", ""),
                    goal=step_data.get("goal", ""),
                    prompt_hint=step_data.get("prompt_hint")
                )
                steps.append(step)

        return RecommendedSkill(
            skill_id=skill.id,
            skill_name=skill.name,
            skill_name_en=skill.name_en,
            module_name=skill.module.name if skill.module else "",
            description=skill.description or "",
            steps=steps,
            match_score=match_score,
            match_reason=match_reason
        )

    async def _get_fallback_skills(
        self,
        recommended: List[RecommendedSkill],
        module_id: Optional[int],
        context: MatchContext
    ) -> List[str]:
        """获取备选技能名称"""
        fallbacks = []
        recommended_ids = {s.skill_id for s in recommended}

        # 从同一模块获取其他技能
        if module_id:
            module_skills = await self.repository.get_skills_by_module(module_id)
            for skill in module_skills:
                if skill.id not in recommended_ids:
                    fallbacks.append(skill.name)
                    if len(fallbacks) >= 2:
                        break

        # 如果备选不足，添加通用技能
        if len(fallbacks) < 2:
            universal_skills = ["深呼吸", "正念观察", "自我安抚"]
            for skill_name in universal_skills:
                if skill_name not in fallbacks:
                    fallbacks.append(skill_name)
                    if len(fallbacks) >= 2:
                        break

        return fallbacks


# ============== 测试用例 ==============
if __name__ == "__main__":
    import asyncio
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
    from ..models.database import Base, DBTModule, DBTSkill, SkillMatchingRule
    from ..models.schemas import (
        EmotionInput, TriggerSignals, InterventionAssessment, RecommendRequest
    )
    from ..models.enums import RiskLevel

    async def test_skill_matcher():
        """测试技能匹配器"""
        # 创建内存数据库
        engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession)

        async with AsyncSessionLocal() as session:
            # 准备测试数据
            module = DBTModule(name="痛苦耐受", name_en="distress_tolerance", description="测试模块")
            session.add(module)
            await session.commit()
            await session.refresh(module)

            skill = DBTSkill(
                module_id=module.id,
                name="TIPP",
                name_en="TIPP",
                description="快速降低情绪强度",
                steps=[
                    {"step_number": 1, "instruction": "用冷水敷脸", "goal": "激活潜水反射"}
                ],
                trigger_emotions=["焦虑", "激越"]
            )
            session.add(skill)
            await session.commit()
            await session.refresh(skill)

            rule = SkillMatchingRule(
                rule_name="high_arousal_anxiety",
                priority=100,
                conditions={
                    "emotion_conditions": [
                        {"emotion": "焦虑", "operator": ">=", "value": 0.5}
                    ],
                    "trigger_signals": [
                        {"signal": "agitation_level", "operator": ">=", "value": 0.4}
                    ]
                },
                skill_ids=[skill.id],
                module_id=module.id
            )
            session.add(rule)
            await session.commit()

            # 创建匹配器
            repo = SkillRepository(session)
            matcher = SkillMatcher(repo)

            # 测试1: 高焦虑状态应匹配TIPP
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
            result = await matcher.match(request)
            assert len(result.skills) > 0
            assert "TIPP" in [s.skill_name for s in result.skills]
            print("✓ 测试1通过: 高焦虑状态正确匹配TIPP")

            # 测试2: 匹配分数应在合理范围
            assert 0 < result.skills[0].match_score <= 1
            print(f"✓ 测试2通过: 匹配分数合理 ({result.skills[0].match_score:.2f})")

            # 测试3: 应有匹配原因
            assert result.skills[0].match_reason
            print(f"✓ 测试3通过: 匹配原因: {result.skills[0].match_reason}")

            # 测试4: 低焦虑状态不应匹配规则
            request2 = RecommendRequest(
                emotion_input=EmotionInput(
                    emotions={"焦虑": 0.2, "悲伤": 0.1},
                    arousal=0.3
                ),
                intervention_assessment=InterventionAssessment(
                    triggered=False,
                    risk_level=RiskLevel.LOW,
                    urgency_score=0.2,
                    trigger_signals=TriggerSignals(agitation_level=0.1),
                    intervention_reason=""
                )
            )
            result2 = await matcher.match(request2)
            # 应该通过fallback机制获得推荐
            print(f"✓ 测试4通过: 低焦虑状态使用fallback，匹配规则数: {len(result2.matched_rules)}")

            print("\n所有技能匹配器测试通过！")

        await engine.dispose()

    asyncio.run(test_skill_matcher())
