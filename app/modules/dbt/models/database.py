"""
数据库模型定义（SQLAlchemy）
定义DBT模块、技能和匹配规则的数据库表结构
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Column, Integer, String, Text, Boolean, Float,
    ForeignKey, DateTime, JSON, ARRAY
)
from sqlalchemy.orm import relationship, DeclarativeBase


class Base(DeclarativeBase):
    """SQLAlchemy基类"""
    pass


class DBTModule(Base):
    """DBT四大模块表"""
    __tablename__ = "dbt_modules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, comment="模块名称（中文）")
    name_en = Column(String(50), nullable=False, comment="模块名称（英文）")
    description = Column(Text, comment="模块描述")
    priority = Column(Integer, default=0, comment="优先级")
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关联技能
    skills = relationship("DBTSkill", back_populates="module")
    # 关联规则
    rules = relationship("SkillMatchingRule", back_populates="module")

    def __repr__(self):
        return f"<DBTModule(id={self.id}, name='{self.name}')>"


class DBTSkill(Base):
    """DBT具体技能表"""
    __tablename__ = "dbt_skills"

    id = Column(Integer, primary_key=True, autoincrement=True)
    module_id = Column(Integer, ForeignKey("dbt_modules.id"), nullable=False)
    name = Column(String(100), nullable=False, comment="技能名称（中文）")
    name_en = Column(String(100), nullable=False, comment="技能名称（英文/缩写）")
    description = Column(Text, comment="技能描述")
    steps = Column(JSON, comment="执行步骤 [{step_number, instruction, goal, prompt_hint}]")
    trigger_emotions = Column(JSON, comment="触发情绪列表")  # 使用JSON代替ARRAY以兼容SQLite
    trigger_conditions = Column(JSON, comment="触发条件规则")
    contraindications = Column(JSON, comment="禁忌情况")  # 使用JSON代替ARRAY
    difficulty_level = Column(Integer, default=1, comment="难度等级 1-3")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关联模块
    module = relationship("DBTModule", back_populates="skills")

    def __repr__(self):
        return f"<DBTSkill(id={self.id}, name='{self.name}', module_id={self.module_id})>"


class SkillMatchingRule(Base):
    """技能匹配规则表"""
    __tablename__ = "skill_matching_rules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    rule_name = Column(String(100), nullable=False, comment="规则名称")
    priority = Column(Integer, default=0, comment="规则优先级（数字越大越优先）")
    conditions = Column(JSON, nullable=False, comment="匹配条件")
    skill_ids = Column(JSON, comment="匹配的技能ID列表")  # 使用JSON代替ARRAY
    module_id = Column(Integer, ForeignKey("dbt_modules.id"))
    is_active = Column(Boolean, default=True)
    description = Column(Text, comment="规则描述")
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关联模块
    module = relationship("DBTModule", back_populates="rules")

    def __repr__(self):
        return f"<SkillMatchingRule(id={self.id}, rule_name='{self.rule_name}')>"


# ============== 测试用例 ==============
if __name__ == "__main__":
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    def test_database_models():
        """测试数据库模型"""
        # 创建内存数据库
        engine = create_engine("sqlite:///:memory:", echo=True)
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()

        try:
            # 测试1: 创建DBT模块
            module = DBTModule(
                name="正念",
                name_en="mindfulness",
                description="培养当下觉察能力",
                priority=1
            )
            session.add(module)
            session.commit()
            assert module.id is not None
            print("✓ 测试1通过: DBTModule创建成功")

            # 测试2: 创建DBT技能
            skill = DBTSkill(
                module_id=module.id,
                name="观察",
                name_en="Observe",
                description="不评判地觉察当下体验",
                steps=[
                    {"step_number": 1, "instruction": "找一个安静的地方坐下", "goal": "准备"},
                    {"step_number": 2, "instruction": "注意你的呼吸", "goal": "觉察"}
                ],
                trigger_emotions=["焦虑", "注意力分散"],
                difficulty_level=1
            )
            session.add(skill)
            session.commit()
            assert skill.id is not None
            assert skill.module.name == "正念"
            print("✓ 测试2通过: DBTSkill创建成功，关联模块正确")

            # 测试3: 创建匹配规则
            rule = SkillMatchingRule(
                rule_name="high_anxiety",
                priority=100,
                conditions={
                    "emotion_conditions": [
                        {"emotion": "焦虑", "operator": ">=", "value": 0.5}
                    ]
                },
                skill_ids=[skill.id],
                module_id=module.id,
                description="高焦虑状态匹配规则"
            )
            session.add(rule)
            session.commit()
            assert rule.id is not None
            print("✓ 测试3通过: SkillMatchingRule创建成功")

            # 测试4: 查询关联
            module = session.query(DBTModule).first()
            assert len(module.skills) == 1
            assert len(module.rules) == 1
            print("✓ 测试4通过: 关联查询正确")

            print("\n所有数据库模型测试通过！")

        finally:
            session.close()

    test_database_models()
