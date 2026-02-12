"""
枚举定义
定义DBT模块中使用的各种枚举类型
"""

from enum import Enum


class RiskLevel(str, Enum):
    """风险等级"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class DBTModuleName(str, Enum):
    """DBT四大模块"""
    MINDFULNESS = "mindfulness"  # 正念
    DISTRESS_TOLERANCE = "distress_tolerance"  # 痛苦耐受
    EMOTION_REGULATION = "emotion_regulation"  # 情绪调节
    INTERPERSONAL_EFFECTIVENESS = "interpersonal_effectiveness"  # 人际效能


class DBTModuleNameCN(str, Enum):
    """DBT四大模块（中文）"""
    MINDFULNESS = "正念"
    DISTRESS_TOLERANCE = "痛苦耐受"
    EMOTION_REGULATION = "情绪调节"
    INTERPERSONAL_EFFECTIVENESS = "人际效能"


class GuidanceApproach(str, Enum):
    """引导方式"""
    EMPATHY_FIRST = "empathy_first"  # 先共情
    SKILL_ORIENTED = "skill_oriented"  # 技能导向
    SCENARIO_PRACTICE = "scenario_practice"  # 情景练习


class GuidanceIntensity(str, Enum):
    """引导强度"""
    LIGHT_REMINDER = "light_reminder"  # 轻度提醒
    STANDARD_TRAINING = "standard_training"  # 标准训练
    CRISIS_PRIORITY = "crisis_priority"  # 危机优先


class GuidanceTone(str, Enum):
    """引导语气"""
    WARM = "warm"  # 温暖
    CALM = "calm"  # 平静
    ENCOURAGING = "encouraging"  # 鼓励


class DialogueGoal(str, Enum):
    """对话目标"""
    COMFORT = "安抚"
    TRAINING = "训练"
    REFLECTION = "反思"


class UserResponseType(str, Enum):
    """用户响应类型"""
    ANGER = "anger"  # 愤怒型
    WITHDRAWAL = "withdrawal"  # 退缩型
    MIXED = "mixed"  # 混合型


class ConditionOperator(str, Enum):
    """条件运算符"""
    GREATER_THAN = ">"
    GREATER_EQUAL = ">="
    LESS_THAN = "<"
    LESS_EQUAL = "<="
    EQUAL = "=="
    NOT_EQUAL = "!="
    IN = "in"
    NOT_IN = "not_in"
    CONTAINS = "contains"


# ============== 测试用例 ==============
if __name__ == "__main__":
    def test_enums():
        """测试枚举定义"""
        # 测试1: 风险等级
        assert RiskLevel.LOW.value == "LOW"
        assert RiskLevel.CRITICAL.value == "CRITICAL"
        print("✓ 测试1通过: RiskLevel枚举正确")

        # 测试2: DBT模块
        assert DBTModuleName.MINDFULNESS.value == "mindfulness"
        assert DBTModuleNameCN.MINDFULNESS.value == "正念"
        print("✓ 测试2通过: DBTModule枚举正确")

        # 测试3: 引导相关枚举
        assert GuidanceApproach.EMPATHY_FIRST.value == "empathy_first"
        assert GuidanceIntensity.CRISIS_PRIORITY.value == "crisis_priority"
        assert GuidanceTone.WARM.value == "warm"
        print("✓ 测试3通过: Guidance枚举正确")

        # 测试4: 条件运算符
        assert ConditionOperator.GREATER_EQUAL.value == ">="
        print("✓ 测试4通过: ConditionOperator枚举正确")

        print("\n所有枚举测试通过！")

    test_enums()
