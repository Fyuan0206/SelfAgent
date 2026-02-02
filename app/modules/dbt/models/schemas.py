"""
Pydantic模型定义
定义API输入输出的数据模型
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from .enums import (
    RiskLevel, GuidanceApproach, GuidanceIntensity, GuidanceTone, DialogueGoal
)


# ==================== 输入模型 ====================

class EmotionInput(BaseModel):
    """情绪识别结果（来自SelfAgent）"""
    emotions: Dict[str, float] = Field(
        ...,
        description="DBT 12种情绪分数，key为情绪名称，value为0-1的分数",
        examples=[{"焦虑": 0.7, "悲伤": 0.3, "愤怒": 0.1}]
    )
    arousal: float = Field(
        ...,
        ge=0.0, le=1.0,
        description="唤醒度，0-1之间"
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0, le=1.0,
        description="识别置信度"
    )


class TriggerSignals(BaseModel):
    """触发信号（来自intervention_assessment）"""
    self_harm_impulse: float = Field(default=0.0, ge=0.0, le=1.0, description="自伤冲动")
    despair_level: float = Field(default=0.0, ge=0.0, le=1.0, description="绝望程度")
    agitation_level: float = Field(default=0.0, ge=0.0, le=1.0, description="激越程度")
    emptiness_level: float = Field(default=0.0, ge=0.0, le=1.0, description="空虚感")
    shame_level: float = Field(default=0.0, ge=0.0, le=1.0, description="羞愧程度")
    emotion_slope: float = Field(default=0.0, ge=-1.0, le=1.0, description="情绪变化斜率")
    negative_total: float = Field(default=0.0, ge=0.0, le=1.0, description="负面情绪总和")


class InterventionAssessment(BaseModel):
    """干预评估结果"""
    triggered: bool = Field(..., description="是否触发干预")
    risk_level: RiskLevel = Field(..., description="风险等级")
    urgency_score: float = Field(..., ge=0.0, le=1.0, description="紧迫度分数")
    trigger_signals: TriggerSignals = Field(..., description="触发信号")
    intervention_reason: str = Field(..., description="干预原因")


class AgentContext(BaseModel):
    """SelfAgent上下文（可选）"""
    dialogue_round: int = Field(default=1, ge=1, description="对话轮次")
    dialogue_goal: DialogueGoal = Field(default=DialogueGoal.COMFORT, description="对话目标")
    last_skill_used: Optional[str] = Field(default=None, description="上次使用的技能")


class UserProfile(BaseModel):
    """用户画像（可选，来自SelfAgent）"""
    user_id: str = Field(..., description="用户ID")
    typical_response: Optional[str] = Field(
        default=None,
        description="典型响应类型: anger/withdrawal/mixed"
    )
    stability_score: float = Field(
        default=0.5,
        ge=0.0, le=1.0,
        description="稳定性分数"
    )
    known_triggers: List[str] = Field(default_factory=list, description="已知触发因素")
    skill_preferences: Dict[str, int] = Field(
        default_factory=dict,
        description="技能使用频率偏好"
    )


class RecommendRequest(BaseModel):
    """推荐请求"""
    emotion_input: EmotionInput = Field(..., description="情绪输入")
    intervention_assessment: InterventionAssessment = Field(..., description="干预评估")
    user_profile: Optional[UserProfile] = Field(default=None, description="用户画像")
    agent_context: Optional[AgentContext] = Field(default=None, description="Agent上下文")
    context: str = Field(default="", description="情境描述（学业/人际/家庭等）")


# ==================== 输出模型 ====================

class SkillStep(BaseModel):
    """技能执行步骤"""
    step_number: int = Field(..., description="步骤编号")
    instruction: str = Field(..., description="步骤指令")
    goal: str = Field(..., description="步骤目标")
    prompt_hint: Optional[str] = Field(default=None, description="引导提示")


class RecommendedSkill(BaseModel):
    """推荐的技能"""
    skill_id: int = Field(..., description="技能ID")
    skill_name: str = Field(..., description="技能名称")
    skill_name_en: str = Field(..., description="技能英文名")
    module_name: str = Field(..., description="所属模块名称")
    description: str = Field(..., description="技能描述")
    steps: List[SkillStep] = Field(default_factory=list, description="执行步骤")
    match_score: float = Field(..., ge=0.0, le=1.0, description="匹配分数")
    match_reason: str = Field(..., description="匹配原因")


class GuidanceStrategy(BaseModel):
    """引导策略"""
    approach: GuidanceApproach = Field(..., description="引导方式")
    intensity: GuidanceIntensity = Field(..., description="引导强度")
    tone: GuidanceTone = Field(..., description="引导语气")
    key_points: List[str] = Field(default_factory=list, description="关键引导点")


class DBTRecommendation(BaseModel):
    """完整推荐结果"""
    recommended_module: str = Field(..., description="推荐的DBT模块")
    recommended_skills: List[RecommendedSkill] = Field(
        ...,
        description="推荐的技能（1-2个）"
    )
    recommendation_reason: str = Field(..., description="LLM生成的推荐理由")
    guidance_strategy: GuidanceStrategy = Field(..., description="引导策略")
    fallback_skills: List[str] = Field(default_factory=list, description="备选技能")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


# ==================== 辅助模型 ====================

class SkillInfo(BaseModel):
    """技能信息（用于列表展示）"""
    id: int
    name: str
    name_en: str
    module_name: str
    description: str
    difficulty_level: int
    is_active: bool


class ModuleInfo(BaseModel):
    """模块信息"""
    id: int
    name: str
    name_en: str
    description: str
    skill_count: int = 0


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = "ok"
    version: str = "0.1.0"
    database: str = "connected"


class MatchResult(BaseModel):
    """匹配结果（内部使用）"""
    module: str
    skills: List[RecommendedSkill]
    fallbacks: List[str] = Field(default_factory=list)
    matched_rules: List[str] = Field(default_factory=list)


# ==================== 管理员模型 ====================

class RuleCondition(BaseModel):
    """规则条件"""
    emotion_conditions: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="情绪条件列表，如 [{'emotion': '焦虑', 'operator': '>=', 'value': 0.5}]"
    )
    trigger_signals: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="触发信号条件，如 [{'signal': 'agitation_level', 'operator': '>=', 'value': 0.4}]"
    )
    arousal: Optional[Dict[str, Any]] = Field(
        default=None,
        description="唤醒度条件，如 {'operator': '>=', 'value': 0.6}"
    )
    context_contains: Optional[List[str]] = Field(
        default=None,
        description="情境关键词，如 ['人际', '关系']"
    )
    risk_level: Optional[List[str]] = Field(
        default=None,
        description="风险等级条件，如 ['HIGH', 'CRITICAL']"
    )


class RuleCreate(BaseModel):
    """创建规则请求"""
    rule_name: str = Field(..., min_length=1, max_length=100, description="规则名称（唯一）")
    priority: int = Field(default=50, ge=0, le=1000, description="优先级（0-1000，越大越优先）")
    conditions: RuleCondition = Field(..., description="匹配条件")
    skill_ids: List[int] = Field(..., min_length=1, description="关联的技能ID列表")
    module_id: Optional[int] = Field(default=None, description="关联的模块ID")
    description: Optional[str] = Field(default=None, max_length=500, description="规则描述")
    is_active: bool = Field(default=True, description="是否启用")


class RuleUpdate(BaseModel):
    """更新规则请求"""
    rule_name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    priority: Optional[int] = Field(default=None, ge=0, le=1000)
    conditions: Optional[RuleCondition] = None
    skill_ids: Optional[List[int]] = Field(default=None, min_length=1)
    module_id: Optional[int] = None
    description: Optional[str] = Field(default=None, max_length=500)
    is_active: Optional[bool] = None


class RuleInfo(BaseModel):
    """规则信息"""
    id: int
    rule_name: str
    priority: int
    conditions: Dict[str, Any]
    skill_ids: List[int]
    module_id: Optional[int]
    module_name: Optional[str] = None
    description: Optional[str]
    is_active: bool


class SkillCreate(BaseModel):
    """创建技能请求"""
    module_id: int = Field(..., description="所属模块ID")
    name: str = Field(..., min_length=1, max_length=100, description="技能名称（中文）")
    name_en: str = Field(..., min_length=1, max_length=100, description="技能名称（英文）")
    description: Optional[str] = Field(default=None, description="技能描述")
    steps: Optional[List[Dict[str, Any]]] = Field(default=None, description="执行步骤")
    trigger_emotions: Optional[List[str]] = Field(default=None, description="触发情绪列表")
    contraindications: Optional[List[str]] = Field(default=None, description="禁忌情况")
    difficulty_level: int = Field(default=1, ge=1, le=3, description="难度等级 1-3")
    is_active: bool = Field(default=True, description="是否启用")


class SkillUpdate(BaseModel):
    """更新技能请求"""
    module_id: Optional[int] = None
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    name_en: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = None
    steps: Optional[List[Dict[str, Any]]] = None
    trigger_emotions: Optional[List[str]] = None
    contraindications: Optional[List[str]] = None
    difficulty_level: Optional[int] = Field(default=None, ge=1, le=3)
    is_active: Optional[bool] = None


class SkillDetail(BaseModel):
    """技能详情"""
    id: int
    module_id: int
    module_name: str
    name: str
    name_en: str
    description: Optional[str]
    steps: Optional[List[Dict[str, Any]]]
    trigger_emotions: Optional[List[str]]
    contraindications: Optional[List[str]]
    difficulty_level: int
    is_active: bool


class AdminStats(BaseModel):
    """管理统计信息"""
    total_modules: int
    total_skills: int
    active_skills: int
    total_rules: int
    active_rules: int
    skills_per_module: Dict[str, int]


# ============== 测试用例 ==============
if __name__ == "__main__":
    def test_schemas():
        """测试Pydantic模型"""
        # 测试1: EmotionInput
        emotion = EmotionInput(
            emotions={"焦虑": 0.7, "悲伤": 0.3},
            arousal=0.75
        )
        assert emotion.emotions["焦虑"] == 0.7
        print("✓ 测试1通过: EmotionInput验证成功")

        # 测试2: TriggerSignals
        signals = TriggerSignals(
            agitation_level=0.5,
            despair_level=0.2
        )
        assert signals.self_harm_impulse == 0.0  # 默认值
        print("✓ 测试2通过: TriggerSignals验证成功")

        # 测试3: InterventionAssessment
        assessment = InterventionAssessment(
            triggered=True,
            risk_level=RiskLevel.MEDIUM,
            urgency_score=0.6,
            trigger_signals=signals,
            intervention_reason="焦虑(0.70)"
        )
        assert assessment.triggered is True
        print("✓ 测试3通过: InterventionAssessment验证成功")

        # 测试4: RecommendRequest
        request = RecommendRequest(
            emotion_input=emotion,
            intervention_assessment=assessment,
            context="学业压力"
        )
        assert request.user_profile is None  # 可选字段
        print("✓ 测试4通过: RecommendRequest验证成功")

        # 测试5: RecommendedSkill
        skill = RecommendedSkill(
            skill_id=1,
            skill_name="TIPP",
            skill_name_en="TIPP",
            module_name="痛苦耐受",
            description="快速降低情绪强度",
            steps=[
                SkillStep(
                    step_number=1,
                    instruction="用冷水敷脸",
                    goal="激活潜水反射"
                )
            ],
            match_score=0.85,
            match_reason="高唤醒焦虑状态"
        )
        assert len(skill.steps) == 1
        print("✓ 测试5通过: RecommendedSkill验证成功")

        # 测试6: GuidanceStrategy
        strategy = GuidanceStrategy(
            approach=GuidanceApproach.EMPATHY_FIRST,
            intensity=GuidanceIntensity.STANDARD_TRAINING,
            tone=GuidanceTone.WARM,
            key_points=["先认可情绪", "引导身体感受"]
        )
        assert strategy.approach == GuidanceApproach.EMPATHY_FIRST
        print("✓ 测试6通过: GuidanceStrategy验证成功")

        # 测试7: DBTRecommendation
        recommendation = DBTRecommendation(
            recommended_module="痛苦耐受",
            recommended_skills=[skill],
            recommendation_reason="建议使用TIPP技能",
            guidance_strategy=strategy
        )
        assert len(recommendation.recommended_skills) == 1
        print("✓ 测试7通过: DBTRecommendation验证成功")

        # 测试8: JSON序列化
        json_str = recommendation.model_dump_json(indent=2)
        assert "TIPP" in json_str
        print("✓ 测试8通过: JSON序列化成功")

        print("\n所有Schema测试通过！")

    test_schemas()
