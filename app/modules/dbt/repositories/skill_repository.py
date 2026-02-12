"""
技能数据访问层
提供对DBT技能库和匹配规则的数据访问操作
"""

from typing import List, Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.database import DBTModule, DBTSkill, SkillMatchingRule


class SkillRepository:
    """DBT技能数据仓库"""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ==================== 模块操作 ====================

    async def get_all_modules(self) -> List[DBTModule]:
        """获取所有DBT模块"""
        result = await self.session.execute(
            select(DBTModule).order_by(DBTModule.priority)
        )
        return list(result.scalars().all())

    async def get_module_by_id(self, module_id: int) -> Optional[DBTModule]:
        """根据ID获取模块"""
        result = await self.session.execute(
            select(DBTModule).where(DBTModule.id == module_id)
        )
        return result.scalar_one_or_none()

    async def get_module_by_name(self, name: str) -> Optional[DBTModule]:
        """根据名称获取模块（支持中英文）"""
        result = await self.session.execute(
            select(DBTModule).where(
                (DBTModule.name == name) | (DBTModule.name_en == name)
            )
        )
        return result.scalar_one_or_none()

    # ==================== 技能操作 ====================

    async def get_all_skills(self, active_only: bool = True) -> List[DBTSkill]:
        """获取所有技能"""
        query = select(DBTSkill).options(selectinload(DBTSkill.module))
        if active_only:
            query = query.where(DBTSkill.is_active == True)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_skill_by_id(self, skill_id: int) -> Optional[DBTSkill]:
        """根据ID获取技能"""
        result = await self.session.execute(
            select(DBTSkill)
            .options(selectinload(DBTSkill.module))
            .where(DBTSkill.id == skill_id)
        )
        return result.scalar_one_or_none()

    async def get_skills_by_ids(self, skill_ids: List[int]) -> List[DBTSkill]:
        """根据ID列表获取技能"""
        if not skill_ids:
            return []
        result = await self.session.execute(
            select(DBTSkill)
            .options(selectinload(DBTSkill.module))
            .where(DBTSkill.id.in_(skill_ids))
        )
        return list(result.scalars().all())

    async def get_skill_by_name(self, name: str) -> Optional[DBTSkill]:
        """根据名称获取技能（支持中英文）"""
        result = await self.session.execute(
            select(DBTSkill)
            .options(selectinload(DBTSkill.module))
            .where(
                (DBTSkill.name == name) | (DBTSkill.name_en == name)
            )
        )
        return result.scalar_one_or_none()

    async def get_skills_by_module(
        self,
        module_id: int,
        active_only: bool = True
    ) -> List[DBTSkill]:
        """获取指定模块的所有技能"""
        query = select(DBTSkill).where(DBTSkill.module_id == module_id)
        if active_only:
            query = query.where(DBTSkill.is_active == True)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_skills_by_emotion(self, emotion: str) -> List[DBTSkill]:
        """根据触发情绪获取技能"""
        # 注意：这里使用JSON查询，具体语法取决于数据库
        # 对于SQLite，使用JSON函数
        all_skills = await self.get_all_skills()
        return [
            skill for skill in all_skills
            if skill.trigger_emotions and emotion in skill.trigger_emotions
        ]

    # ==================== 规则操作 ====================

    async def get_all_rules(self, active_only: bool = True) -> List[SkillMatchingRule]:
        """获取所有匹配规则（按优先级排序）"""
        query = select(SkillMatchingRule).order_by(SkillMatchingRule.priority.desc())
        if active_only:
            query = query.where(SkillMatchingRule.is_active == True)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_rule_by_id(self, rule_id: int) -> Optional[SkillMatchingRule]:
        """根据ID获取规则"""
        result = await self.session.execute(
            select(SkillMatchingRule).where(SkillMatchingRule.id == rule_id)
        )
        return result.scalar_one_or_none()

    async def get_rules_by_module(
        self,
        module_id: int,
        active_only: bool = True
    ) -> List[SkillMatchingRule]:
        """获取指定模块的匹配规则"""
        query = select(SkillMatchingRule).where(
            SkillMatchingRule.module_id == module_id
        ).order_by(SkillMatchingRule.priority.desc())
        if active_only:
            query = query.where(SkillMatchingRule.is_active == True)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    # ==================== 统计操作 ====================

    async def count_skills(self, active_only: bool = True) -> int:
        """统计技能数量"""
        skills = await self.get_all_skills(active_only)
        return len(skills)

    async def count_rules(self, active_only: bool = True) -> int:
        """统计规则数量"""
        rules = await self.get_all_rules(active_only)
        return len(rules)

    async def get_module_skill_counts(self) -> dict:
        """获取每个模块的技能数量"""
        modules = await self.get_all_modules()
        counts = {}
        for module in modules:
            skills = await self.get_skills_by_module(module.id)
            counts[module.name] = len(skills)
        return counts

    # ==================== 规则CRUD操作（管理员） ====================

    async def create_rule(
        self,
        rule_name: str,
        conditions: dict,
        skill_ids: List[int],
        priority: int = 50,
        module_id: Optional[int] = None,
        description: Optional[str] = None,
        is_active: bool = True
    ) -> SkillMatchingRule:
        """创建新规则"""
        rule = SkillMatchingRule(
            rule_name=rule_name,
            priority=priority,
            conditions=conditions,
            skill_ids=skill_ids,
            module_id=module_id,
            description=description,
            is_active=is_active
        )
        self.session.add(rule)
        await self.session.commit()
        await self.session.refresh(rule)
        return rule

    async def update_rule(
        self,
        rule_id: int,
        **kwargs
    ) -> Optional[SkillMatchingRule]:
        """更新规则"""
        rule = await self.get_rule_by_id(rule_id)
        if not rule:
            return None

        for key, value in kwargs.items():
            if value is not None and hasattr(rule, key):
                setattr(rule, key, value)

        await self.session.commit()
        await self.session.refresh(rule)
        return rule

    async def delete_rule(self, rule_id: int) -> bool:
        """删除规则"""
        rule = await self.get_rule_by_id(rule_id)
        if not rule:
            return False

        await self.session.delete(rule)
        await self.session.commit()
        return True

    async def toggle_rule_active(self, rule_id: int) -> Optional[SkillMatchingRule]:
        """切换规则启用状态"""
        rule = await self.get_rule_by_id(rule_id)
        if not rule:
            return None

        rule.is_active = not rule.is_active
        await self.session.commit()
        await self.session.refresh(rule)
        return rule

    async def get_rule_by_name(self, rule_name: str) -> Optional[SkillMatchingRule]:
        """根据规则名称获取规则"""
        result = await self.session.execute(
            select(SkillMatchingRule).where(SkillMatchingRule.rule_name == rule_name)
        )
        return result.scalar_one_or_none()

    # ==================== 技能CRUD操作（管理员） ====================

    async def create_skill(
        self,
        module_id: int,
        name: str,
        name_en: str,
        description: Optional[str] = None,
        steps: Optional[List[dict]] = None,
        trigger_emotions: Optional[List[str]] = None,
        contraindications: Optional[List[str]] = None,
        difficulty_level: int = 1,
        is_active: bool = True
    ) -> DBTSkill:
        """创建新技能"""
        skill = DBTSkill(
            module_id=module_id,
            name=name,
            name_en=name_en,
            description=description,
            steps=steps,
            trigger_emotions=trigger_emotions,
            contraindications=contraindications,
            difficulty_level=difficulty_level,
            is_active=is_active
        )
        self.session.add(skill)
        await self.session.commit()
        await self.session.refresh(skill)
        return skill

    async def update_skill(
        self,
        skill_id: int,
        **kwargs
    ) -> Optional[DBTSkill]:
        """更新技能"""
        skill = await self.get_skill_by_id(skill_id)
        if not skill:
            return None

        for key, value in kwargs.items():
            if value is not None and hasattr(skill, key):
                setattr(skill, key, value)

        await self.session.commit()
        await self.session.refresh(skill)
        return skill

    async def delete_skill(self, skill_id: int) -> bool:
        """删除技能"""
        skill = await self.get_skill_by_id(skill_id)
        if not skill:
            return False

        await self.session.delete(skill)
        await self.session.commit()
        return True

    async def toggle_skill_active(self, skill_id: int) -> Optional[DBTSkill]:
        """切换技能启用状态"""
        skill = await self.get_skill_by_id(skill_id)
        if not skill:
            return None

        skill.is_active = not skill.is_active
        await self.session.commit()
        await self.session.refresh(skill)
        return skill


# ============== 测试用例 ==============
if __name__ == "__main__":
    import asyncio
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
    from ..models.database import Base

    async def test_skill_repository():
        """测试技能仓库"""
        # 创建内存数据库
        engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession)

        async with AsyncSessionLocal() as session:
            # 准备测试数据
            module = DBTModule(name="正念", name_en="mindfulness", description="测试模块")
            session.add(module)
            await session.commit()
            await session.refresh(module)

            skill = DBTSkill(
                module_id=module.id,
                name="观察",
                name_en="Observe",
                description="观察技能",
                trigger_emotions=["焦虑", "悲伤"]
            )
            session.add(skill)

            rule = SkillMatchingRule(
                rule_name="test_rule",
                priority=100,
                conditions={"test": True},
                skill_ids=[1],
                module_id=module.id
            )
            session.add(rule)
            await session.commit()

            # 创建仓库实例
            repo = SkillRepository(session)

            # 测试1: 获取所有模块
            modules = await repo.get_all_modules()
            assert len(modules) == 1
            print("✓ 测试1通过: get_all_modules")

            # 测试2: 获取模块（按ID）
            mod = await repo.get_module_by_id(module.id)
            assert mod.name == "正念"
            print("✓ 测试2通过: get_module_by_id")

            # 测试3: 获取模块（按名称）
            mod = await repo.get_module_by_name("mindfulness")
            assert mod.name == "正念"
            print("✓ 测试3通过: get_module_by_name")

            # 测试4: 获取所有技能
            skills = await repo.get_all_skills()
            assert len(skills) == 1
            print("✓ 测试4通过: get_all_skills")

            # 测试5: 根据情绪获取技能
            skills = await repo.get_skills_by_emotion("焦虑")
            assert len(skills) == 1
            print("✓ 测试5通过: get_skills_by_emotion")

            # 测试6: 获取所有规则
            rules = await repo.get_all_rules()
            assert len(rules) == 1
            print("✓ 测试6通过: get_all_rules")

            # 测试7: 统计
            count = await repo.count_skills()
            assert count == 1
            print("✓ 测试7通过: count_skills")

            print("\n所有仓库测试通过！")

        await engine.dispose()

    asyncio.run(test_skill_repository())
