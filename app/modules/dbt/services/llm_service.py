"""
LLM服务
使用OpenAI兼容接口生成推荐理由和处理边缘情况
"""

from typing import List, Optional
import asyncio

from openai import AsyncOpenAI
from loguru import logger

from ..config import get_settings
from ..models.schemas import RecommendRequest, RecommendedSkill


class LLMService:
    """OpenAI兼容的LLM服务"""

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ):
        settings = get_settings()

        self.base_url = base_url or settings.llm.base_url
        self.api_key = api_key or settings.llm.api_key
        self.model = model or settings.llm.model
        self.temperature = settings.llm.temperature
        self.max_tokens = settings.llm.max_tokens
        self.timeout = settings.llm.timeout

        # 创建AsyncOpenAI客户端
        self.client = AsyncOpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
            timeout=self.timeout
        )

    async def generate_recommendation_reason(
        self,
        request: RecommendRequest,
        matched_skills: List[RecommendedSkill]
    ) -> str:
        """
        生成个性化推荐理由

        Args:
            request: 推荐请求
            matched_skills: 匹配的技能列表

        Returns:
            str: 推荐理由
        """
        if not matched_skills:
            return "基于当前状态，建议尝试一些放松技巧。"

        prompt = self._build_reason_prompt(request, matched_skills)

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )

            reason = response.choices[0].message.content.strip()
            logger.debug(f"LLM生成推荐理由: {reason[:100]}...")
            return reason

        except Exception as e:
            logger.error(f"LLM调用失败: {e}")
            # 返回默认推荐理由
            return self._get_fallback_reason(request, matched_skills)

    async def handle_edge_case(
        self,
        request: RecommendRequest
    ) -> List[str]:
        """
        处理规则未覆盖的边缘情况

        当规则匹配器没有找到合适的技能时，使用LLM推荐

        Args:
            request: 推荐请求

        Returns:
            List[str]: 推荐的技能名称列表
        """
        prompt = self._build_edge_case_prompt(request)

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_edge_case_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # 边缘情况使用较低温度
                max_tokens=200
            )

            content = response.choices[0].message.content.strip()
            # 解析技能名称
            skills = self._parse_skill_names(content)
            logger.info(f"LLM边缘情况推荐: {skills}")
            return skills

        except Exception as e:
            logger.error(f"LLM边缘情况处理失败: {e}")
            # 返回默认技能
            return ["深呼吸", "正念观察"]

    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一位专业的DBT（辩证行为疗法）治疗师助手。你的任务是为用户生成温暖、共情的技能推荐理由。

要求：
1. 语言温暖、自然，像朋友在关心对方
2. 先认可用户的情绪体验
3. 简洁说明为什么推荐这个技能
4. 给予希望和支持
5. 不要使用专业术语
6. 回复长度控制在50-100字

示例风格：
"我注意到你现在感到很焦虑，这种感觉一定很不好受。TIPP技能可以帮助你快速平复这种强烈的情绪。我们可以先试着用一些简单的方法让身体放松下来，好吗？"
"""

    def _get_edge_case_system_prompt(self) -> str:
        """获取边缘情况系统提示词"""
        return """你是一位DBT专家。根据用户的情绪状态，从以下DBT技能中选择最合适的1-2个：

痛苦耐受技能：
- TIPP（改变体温、剧烈运动、渐进放松、配合呼吸）
- STOP（停下、退后、观察、有意识继续）
- ACCEPTS（活动转移、贡献、比较、情绪、推开、思考、感觉）
- 自我安抚（用五感安抚自己）
- 彻底接纳（接受不能改变的现实）

情绪调节技能：
- 检查事实（核实情绪是否符合事实）
- 相反行动（做与情绪冲动相反的行为）
- ABC PLEASE（积累正面体验、建立掌控感、照顾身体）

人际效能技能：
- DEAR MAN（描述、表达、明确、强化、保持正念、表现自信、协商）
- GIVE（温和、感兴趣、验证、轻松态度）
- FAST（公平、不过度道歉、坚持价值观、真实）

正念技能：
- 智慧心（理性与情感的平衡）
- 观察（不评判地觉察）
- 描述（用语言描述体验）
- 参与（全身心投入当前活动）

只输出技能名称，用逗号分隔，例如：TIPP, 深呼吸"""

    def _build_reason_prompt(
        self,
        request: RecommendRequest,
        matched_skills: List[RecommendedSkill]
    ) -> str:
        """构建推荐理由生成提示词"""
        # 提取主要情绪
        emotions_str = ""
        if request.emotion_input.emotions:
            top_emotions = sorted(
                request.emotion_input.emotions.items(),
                key=lambda x: x[1],
                reverse=True
            )[:3]
            emotions_str = "、".join([f"{e}({v:.0%})" for e, v in top_emotions])

        # 提取技能信息
        skills_str = "、".join([s.skill_name for s in matched_skills])

        # 情境
        context = request.context or "日常生活"

        # 风险等级
        risk_level = request.intervention_assessment.risk_level.value

        prompt = f"""用户情绪状态：
- 主要情绪：{emotions_str}
- 唤醒度：{request.emotion_input.arousal:.0%}
- 风险等级：{risk_level}
- 情境：{context}

推荐技能：{skills_str}

请为用户生成一段温暖的推荐理由，解释为什么推荐这个技能。"""

        return prompt

    def _build_edge_case_prompt(self, request: RecommendRequest) -> str:
        """构建边缘情况处理提示词"""
        emotions_str = ""
        if request.emotion_input.emotions:
            emotions_str = "、".join([
                f"{e}({v:.0%})"
                for e, v in request.emotion_input.emotions.items()
                if v > 0.2
            ])

        prompt = f"""用户当前情绪状态：
- 情绪：{emotions_str or "情绪不明显"}
- 唤醒度：{request.emotion_input.arousal:.0%}
- 情境：{request.context or "未知"}
- 风险等级：{request.intervention_assessment.risk_level.value}

请推荐1-2个最适合的DBT技能。只输出技能名称。"""

        return prompt

    def _get_fallback_reason(
        self,
        request: RecommendRequest,
        matched_skills: List[RecommendedSkill]
    ) -> str:
        """获取默认推荐理由（LLM失败时使用）"""
        if not matched_skills:
            return "让我们一起试试一些放松技巧，帮助你感觉好一些。"

        skill = matched_skills[0]

        # 根据模块生成不同的默认理由
        module_reasons = {
            "痛苦耐受": f"我理解你现在的感受可能很强烈。{skill.skill_name}可以帮助你度过这个困难时刻，让我们一起来试试。",
            "情绪调节": f"情绪有时候会让我们看不清全貌。{skill.skill_name}可以帮助你更好地理解和管理这些感受。",
            "人际效能": f"人际关系有时候确实很有挑战。{skill.skill_name}可以帮助你更有效地表达自己的需求。",
            "正念": f"让我们暂停一下，关注当下。{skill.skill_name}可以帮助你找到内心的平静。"
        }

        return module_reasons.get(
            skill.module_name,
            f"我建议我们试试{skill.skill_name}，这可能会帮助你感觉好一些。"
        )

    def _parse_skill_names(self, content: str) -> List[str]:
        """从LLM响应中解析技能名称"""
        # 移除可能的标点和空格
        content = content.strip()

        # 尝试按逗号、顿号分隔
        separators = [",", "，", "、", "\n"]
        skills = [content]

        for sep in separators:
            if sep in content:
                skills = [s.strip() for s in content.split(sep)]
                break

        # 过滤空值和过长的内容
        skills = [s for s in skills if s and len(s) < 20]

        return skills[:2]  # 最多返回2个


# ============== 测试用例 ==============
if __name__ == "__main__":
    import asyncio
    from ..models.schemas import (
        EmotionInput, TriggerSignals, InterventionAssessment, RecommendRequest,
        RecommendedSkill, SkillStep
    )
    from ..models.enums import RiskLevel

    async def test_llm_service():
        """测试LLM服务"""
        # 注意：此测试需要有效的API密钥
        service = LLMService()

        # 测试数据
        request = RecommendRequest(
            emotion_input=EmotionInput(
                emotions={"焦虑": 0.7, "悲伤": 0.3},
                arousal=0.75
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

        skill = RecommendedSkill(
            skill_id=1,
            skill_name="TIPP",
            skill_name_en="TIPP",
            module_name="痛苦耐受",
            description="快速降低情绪强度",
            steps=[],
            match_score=0.85,
            match_reason="高焦虑状态"
        )

        # 测试1: 默认推荐理由（不调用API）
        fallback_reason = service._get_fallback_reason(request, [skill])
        assert "TIPP" in fallback_reason
        print(f"✓ 测试1通过: 默认推荐理由生成成功")
        print(f"  理由: {fallback_reason}")

        # 测试2: 解析技能名称
        test_responses = [
            "TIPP, 深呼吸",
            "TIPP、深呼吸",
            "TIPP，深呼吸",
            "TIPP\n深呼吸"
        ]
        for resp in test_responses:
            skills = service._parse_skill_names(resp)
            assert "TIPP" in skills
            print(f"✓ 测试2通过: 解析 '{resp}' -> {skills}")

        # 测试3: 构建提示词
        prompt = service._build_reason_prompt(request, [skill])
        assert "焦虑" in prompt
        assert "TIPP" in prompt
        print("✓ 测试3通过: 提示词构建成功")

        # 测试4: 如果有API密钥，测试实际调用
        if service.api_key:
            try:
                print("\n尝试调用LLM API...")
                reason = await service.generate_recommendation_reason(request, [skill])
                print(f"✓ 测试4通过: LLM生成推荐理由")
                print(f"  理由: {reason}")
            except Exception as e:
                print(f"⚠ 测试4跳过: LLM调用失败 ({e})")
        else:
            print("⚠ 测试4跳过: 未配置API密钥")

        print("\n所有LLM服务测试通过！")

    asyncio.run(test_llm_service())
