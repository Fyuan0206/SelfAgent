"""
管理员API路由
提供规则和技能的增删改查接口，需要管理员权限
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from ..db.session import get_db
from ..config import get_settings
from ..models.schemas import (
    RuleCreate, RuleUpdate, RuleInfo,
    SkillCreate, SkillUpdate, SkillDetail,
    AdminStats
)
from ..repositories.skill_repository import SkillRepository


router = APIRouter()

# 获取配置
settings = get_settings()

# 管理员密钥（实际生产环境应使用更安全的认证方式）
ADMIN_API_KEY = "dbt-admin-secret-key"  # 可通过环境变量配置


# ==================== 认证依赖 ====================

async def verify_admin(x_admin_key: str = Header(..., description="管理员API密钥")):
    """验证管理员权限"""
    # 从环境变量获取密钥，如果没有则使用默认值
    import os
    expected_key = os.getenv("DBT_ADMIN_API_KEY", ADMIN_API_KEY)

    if x_admin_key != expected_key:
        logger.warning(f"管理员认证失败: 无效的API密钥")
        raise HTTPException(
            status_code=403,
            detail="无效的管理员密钥"
        )
    return True


async def get_repository(session: AsyncSession = Depends(get_db)) -> SkillRepository:
    """获取技能仓库实例"""
    return SkillRepository(session)


# ==================== 规则管理API ====================

@router.get(
    "/rules",
    response_model=List[RuleInfo],
    summary="获取所有规则",
    description="获取所有匹配规则列表（包括未启用的）"
)
async def list_rules(
    active_only: bool = False,
    repository: SkillRepository = Depends(get_repository),
    _: bool = Depends(verify_admin)
) -> List[RuleInfo]:
    """获取所有规则"""
    try:
        rules = await repository.get_all_rules(active_only=active_only)
        result = []
        for rule in rules:
            module_name = None
            if rule.module_id:
                module = await repository.get_module_by_id(rule.module_id)
                module_name = module.name if module else None

            result.append(RuleInfo(
                id=rule.id,
                rule_name=rule.rule_name,
                priority=rule.priority,
                conditions=rule.conditions,
                skill_ids=rule.skill_ids or [],
                module_id=rule.module_id,
                module_name=module_name,
                description=rule.description,
                is_active=rule.is_active
            ))
        return result
    except Exception as e:
        logger.error(f"获取规则列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"服务错误: {str(e)}")


@router.get(
    "/rules/{rule_id}",
    response_model=RuleInfo,
    summary="获取规则详情",
    description="根据ID获取规则详情"
)
async def get_rule(
    rule_id: int,
    repository: SkillRepository = Depends(get_repository),
    _: bool = Depends(verify_admin)
) -> RuleInfo:
    """获取规则详情"""
    try:
        rule = await repository.get_rule_by_id(rule_id)
        if not rule:
            raise HTTPException(status_code=404, detail="规则不存在")

        module_name = None
        if rule.module_id:
            module = await repository.get_module_by_id(rule.module_id)
            module_name = module.name if module else None

        return RuleInfo(
            id=rule.id,
            rule_name=rule.rule_name,
            priority=rule.priority,
            conditions=rule.conditions,
            skill_ids=rule.skill_ids or [],
            module_id=rule.module_id,
            module_name=module_name,
            description=rule.description,
            is_active=rule.is_active
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取规则详情失败: {e}")
        raise HTTPException(status_code=500, detail=f"服务错误: {str(e)}")


@router.post(
    "/rules",
    response_model=RuleInfo,
    summary="创建规则",
    description="创建新的匹配规则"
)
async def create_rule(
    rule_data: RuleCreate,
    repository: SkillRepository = Depends(get_repository),
    _: bool = Depends(verify_admin)
) -> RuleInfo:
    """创建新规则"""
    try:
        # 检查规则名称是否已存在
        existing = await repository.get_rule_by_name(rule_data.rule_name)
        if existing:
            raise HTTPException(status_code=400, detail="规则名称已存在")

        # 验证技能ID是否存在
        for skill_id in rule_data.skill_ids:
            skill = await repository.get_skill_by_id(skill_id)
            if not skill:
                raise HTTPException(status_code=400, detail=f"技能ID {skill_id} 不存在")

        # 验证模块ID是否存在
        if rule_data.module_id:
            module = await repository.get_module_by_id(rule_data.module_id)
            if not module:
                raise HTTPException(status_code=400, detail="模块ID不存在")

        # 创建规则
        rule = await repository.create_rule(
            rule_name=rule_data.rule_name,
            priority=rule_data.priority,
            conditions=rule_data.conditions.model_dump(exclude_none=True),
            skill_ids=rule_data.skill_ids,
            module_id=rule_data.module_id,
            description=rule_data.description,
            is_active=rule_data.is_active
        )

        logger.info(f"创建规则成功: {rule.rule_name} (ID: {rule.id})")

        module_name = None
        if rule.module_id:
            module = await repository.get_module_by_id(rule.module_id)
            module_name = module.name if module else None

        return RuleInfo(
            id=rule.id,
            rule_name=rule.rule_name,
            priority=rule.priority,
            conditions=rule.conditions,
            skill_ids=rule.skill_ids or [],
            module_id=rule.module_id,
            module_name=module_name,
            description=rule.description,
            is_active=rule.is_active
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建规则失败: {e}")
        raise HTTPException(status_code=500, detail=f"服务错误: {str(e)}")


@router.put(
    "/rules/{rule_id}",
    response_model=RuleInfo,
    summary="更新规则",
    description="更新指定规则"
)
async def update_rule(
    rule_id: int,
    rule_data: RuleUpdate,
    repository: SkillRepository = Depends(get_repository),
    _: bool = Depends(verify_admin)
) -> RuleInfo:
    """更新规则"""
    try:
        # 检查规则是否存在
        existing = await repository.get_rule_by_id(rule_id)
        if not existing:
            raise HTTPException(status_code=404, detail="规则不存在")

        # 如果更新规则名称，检查是否重复
        if rule_data.rule_name and rule_data.rule_name != existing.rule_name:
            name_conflict = await repository.get_rule_by_name(rule_data.rule_name)
            if name_conflict:
                raise HTTPException(status_code=400, detail="规则名称已存在")

        # 验证技能ID
        if rule_data.skill_ids:
            for skill_id in rule_data.skill_ids:
                skill = await repository.get_skill_by_id(skill_id)
                if not skill:
                    raise HTTPException(status_code=400, detail=f"技能ID {skill_id} 不存在")

        # 构建更新数据
        update_data = rule_data.model_dump(exclude_none=True)
        if "conditions" in update_data and update_data["conditions"]:
            update_data["conditions"] = rule_data.conditions.model_dump(exclude_none=True)

        # 更新规则
        rule = await repository.update_rule(rule_id, **update_data)

        logger.info(f"更新规则成功: {rule.rule_name} (ID: {rule.id})")

        module_name = None
        if rule.module_id:
            module = await repository.get_module_by_id(rule.module_id)
            module_name = module.name if module else None

        return RuleInfo(
            id=rule.id,
            rule_name=rule.rule_name,
            priority=rule.priority,
            conditions=rule.conditions,
            skill_ids=rule.skill_ids or [],
            module_id=rule.module_id,
            module_name=module_name,
            description=rule.description,
            is_active=rule.is_active
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新规则失败: {e}")
        raise HTTPException(status_code=500, detail=f"服务错误: {str(e)}")


@router.delete(
    "/rules/{rule_id}",
    summary="删除规则",
    description="删除指定规则"
)
async def delete_rule(
    rule_id: int,
    repository: SkillRepository = Depends(get_repository),
    _: bool = Depends(verify_admin)
):
    """删除规则"""
    try:
        success = await repository.delete_rule(rule_id)
        if not success:
            raise HTTPException(status_code=404, detail="规则不存在")

        logger.info(f"删除规则成功: ID={rule_id}")
        return {"message": "删除成功", "rule_id": rule_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除规则失败: {e}")
        raise HTTPException(status_code=500, detail=f"服务错误: {str(e)}")


@router.post(
    "/rules/{rule_id}/toggle",
    response_model=RuleInfo,
    summary="切换规则状态",
    description="启用/禁用规则"
)
async def toggle_rule(
    rule_id: int,
    repository: SkillRepository = Depends(get_repository),
    _: bool = Depends(verify_admin)
) -> RuleInfo:
    """切换规则启用状态"""
    try:
        rule = await repository.toggle_rule_active(rule_id)
        if not rule:
            raise HTTPException(status_code=404, detail="规则不存在")

        status = "启用" if rule.is_active else "禁用"
        logger.info(f"切换规则状态: {rule.rule_name} -> {status}")

        module_name = None
        if rule.module_id:
            module = await repository.get_module_by_id(rule.module_id)
            module_name = module.name if module else None

        return RuleInfo(
            id=rule.id,
            rule_name=rule.rule_name,
            priority=rule.priority,
            conditions=rule.conditions,
            skill_ids=rule.skill_ids or [],
            module_id=rule.module_id,
            module_name=module_name,
            description=rule.description,
            is_active=rule.is_active
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"切换规则状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"服务错误: {str(e)}")


# ==================== 技能管理API ====================

@router.get(
    "/skills",
    response_model=List[SkillDetail],
    summary="获取所有技能详情",
    description="获取所有技能的完整信息（包括未启用的）"
)
async def list_skills_admin(
    active_only: bool = False,
    repository: SkillRepository = Depends(get_repository),
    _: bool = Depends(verify_admin)
) -> List[SkillDetail]:
    """获取所有技能（管理员视角）"""
    try:
        skills = await repository.get_all_skills(active_only=active_only)
        return [
            SkillDetail(
                id=s.id,
                module_id=s.module_id,
                module_name=s.module.name if s.module else "",
                name=s.name,
                name_en=s.name_en,
                description=s.description,
                steps=s.steps,
                trigger_emotions=s.trigger_emotions,
                contraindications=s.contraindications,
                difficulty_level=s.difficulty_level or 1,
                is_active=s.is_active
            )
            for s in skills
        ]
    except Exception as e:
        logger.error(f"获取技能列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"服务错误: {str(e)}")


@router.get(
    "/skills/{skill_id}",
    response_model=SkillDetail,
    summary="获取技能详情",
    description="获取单个技能的完整信息"
)
async def get_skill_admin(
    skill_id: int,
    repository: SkillRepository = Depends(get_repository),
    _: bool = Depends(verify_admin)
) -> SkillDetail:
    """获取技能详情（管理员视角）"""
    try:
        skill = await repository.get_skill_by_id(skill_id)
        if not skill:
            raise HTTPException(status_code=404, detail="技能不存在")

        return SkillDetail(
            id=skill.id,
            module_id=skill.module_id,
            module_name=skill.module.name if skill.module else "",
            name=skill.name,
            name_en=skill.name_en,
            description=skill.description,
            steps=skill.steps,
            trigger_emotions=skill.trigger_emotions,
            contraindications=skill.contraindications,
            difficulty_level=skill.difficulty_level or 1,
            is_active=skill.is_active
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取技能详情失败: {e}")
        raise HTTPException(status_code=500, detail=f"服务错误: {str(e)}")


@router.post(
    "/skills",
    response_model=SkillDetail,
    summary="创建技能",
    description="创建新的DBT技能"
)
async def create_skill(
    skill_data: SkillCreate,
    repository: SkillRepository = Depends(get_repository),
    _: bool = Depends(verify_admin)
) -> SkillDetail:
    """创建新技能"""
    try:
        # 验证模块ID
        module = await repository.get_module_by_id(skill_data.module_id)
        if not module:
            raise HTTPException(status_code=400, detail="模块ID不存在")

        # 检查技能名称是否已存在
        existing = await repository.get_skill_by_name(skill_data.name)
        if existing:
            raise HTTPException(status_code=400, detail="技能名称已存在")

        # 创建技能
        skill = await repository.create_skill(
            module_id=skill_data.module_id,
            name=skill_data.name,
            name_en=skill_data.name_en,
            description=skill_data.description,
            steps=skill_data.steps,
            trigger_emotions=skill_data.trigger_emotions,
            contraindications=skill_data.contraindications,
            difficulty_level=skill_data.difficulty_level,
            is_active=skill_data.is_active
        )

        # 重新加载以获取模块信息
        skill = await repository.get_skill_by_id(skill.id)

        logger.info(f"创建技能成功: {skill.name} (ID: {skill.id})")

        return SkillDetail(
            id=skill.id,
            module_id=skill.module_id,
            module_name=skill.module.name if skill.module else "",
            name=skill.name,
            name_en=skill.name_en,
            description=skill.description,
            steps=skill.steps,
            trigger_emotions=skill.trigger_emotions,
            contraindications=skill.contraindications,
            difficulty_level=skill.difficulty_level or 1,
            is_active=skill.is_active
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建技能失败: {e}")
        raise HTTPException(status_code=500, detail=f"服务错误: {str(e)}")


@router.put(
    "/skills/{skill_id}",
    response_model=SkillDetail,
    summary="更新技能",
    description="更新指定技能"
)
async def update_skill(
    skill_id: int,
    skill_data: SkillUpdate,
    repository: SkillRepository = Depends(get_repository),
    _: bool = Depends(verify_admin)
) -> SkillDetail:
    """更新技能"""
    try:
        # 检查技能是否存在
        existing = await repository.get_skill_by_id(skill_id)
        if not existing:
            raise HTTPException(status_code=404, detail="技能不存在")

        # 如果更新名称，检查是否重复
        if skill_data.name and skill_data.name != existing.name:
            name_conflict = await repository.get_skill_by_name(skill_data.name)
            if name_conflict:
                raise HTTPException(status_code=400, detail="技能名称已存在")

        # 如果更新模块ID，验证是否存在
        if skill_data.module_id:
            module = await repository.get_module_by_id(skill_data.module_id)
            if not module:
                raise HTTPException(status_code=400, detail="模块ID不存在")

        # 更新技能
        update_data = skill_data.model_dump(exclude_none=True)
        skill = await repository.update_skill(skill_id, **update_data)

        # 重新加载以获取模块信息
        skill = await repository.get_skill_by_id(skill.id)

        logger.info(f"更新技能成功: {skill.name} (ID: {skill.id})")

        return SkillDetail(
            id=skill.id,
            module_id=skill.module_id,
            module_name=skill.module.name if skill.module else "",
            name=skill.name,
            name_en=skill.name_en,
            description=skill.description,
            steps=skill.steps,
            trigger_emotions=skill.trigger_emotions,
            contraindications=skill.contraindications,
            difficulty_level=skill.difficulty_level or 1,
            is_active=skill.is_active
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新技能失败: {e}")
        raise HTTPException(status_code=500, detail=f"服务错误: {str(e)}")


@router.delete(
    "/skills/{skill_id}",
    summary="删除技能",
    description="删除指定技能（会影响关联的规则）"
)
async def delete_skill(
    skill_id: int,
    repository: SkillRepository = Depends(get_repository),
    _: bool = Depends(verify_admin)
):
    """删除技能"""
    try:
        success = await repository.delete_skill(skill_id)
        if not success:
            raise HTTPException(status_code=404, detail="技能不存在")

        logger.info(f"删除技能成功: ID={skill_id}")
        return {"message": "删除成功", "skill_id": skill_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除技能失败: {e}")
        raise HTTPException(status_code=500, detail=f"服务错误: {str(e)}")


@router.post(
    "/skills/{skill_id}/toggle",
    response_model=SkillDetail,
    summary="切换技能状态",
    description="启用/禁用技能"
)
async def toggle_skill(
    skill_id: int,
    repository: SkillRepository = Depends(get_repository),
    _: bool = Depends(verify_admin)
) -> SkillDetail:
    """切换技能启用状态"""
    try:
        skill = await repository.toggle_skill_active(skill_id)
        if not skill:
            raise HTTPException(status_code=404, detail="技能不存在")

        # 重新加载以获取模块信息
        skill = await repository.get_skill_by_id(skill.id)

        status = "启用" if skill.is_active else "禁用"
        logger.info(f"切换技能状态: {skill.name} -> {status}")

        return SkillDetail(
            id=skill.id,
            module_id=skill.module_id,
            module_name=skill.module.name if skill.module else "",
            name=skill.name,
            name_en=skill.name_en,
            description=skill.description,
            steps=skill.steps,
            trigger_emotions=skill.trigger_emotions,
            contraindications=skill.contraindications,
            difficulty_level=skill.difficulty_level or 1,
            is_active=skill.is_active
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"切换技能状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"服务错误: {str(e)}")


# ==================== 统计API ====================

@router.get(
    "/stats",
    response_model=AdminStats,
    summary="获取统计信息",
    description="获取系统统计信息"
)
async def get_stats(
    repository: SkillRepository = Depends(get_repository),
    _: bool = Depends(verify_admin)
) -> AdminStats:
    """获取统计信息"""
    try:
        modules = await repository.get_all_modules()
        all_skills = await repository.get_all_skills(active_only=False)
        active_skills = await repository.get_all_skills(active_only=True)
        all_rules = await repository.get_all_rules(active_only=False)
        active_rules = await repository.get_all_rules(active_only=True)
        skills_per_module = await repository.get_module_skill_counts()

        return AdminStats(
            total_modules=len(modules),
            total_skills=len(all_skills),
            active_skills=len(active_skills),
            total_rules=len(all_rules),
            active_rules=len(active_rules),
            skills_per_module=skills_per_module
        )
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"服务错误: {str(e)}")


# ============== 测试用例 ==============
if __name__ == "__main__":
    print("管理员API路由定义完成")
    print("端点列表（需要 X-Admin-Key 头）:")
    print("\n规则管理:")
    print("  GET    /api/v1/admin/rules           - 获取所有规则")
    print("  GET    /api/v1/admin/rules/{id}      - 获取规则详情")
    print("  POST   /api/v1/admin/rules           - 创建规则")
    print("  PUT    /api/v1/admin/rules/{id}      - 更新规则")
    print("  DELETE /api/v1/admin/rules/{id}      - 删除规则")
    print("  POST   /api/v1/admin/rules/{id}/toggle - 切换规则状态")
    print("\n技能管理:")
    print("  GET    /api/v1/admin/skills          - 获取所有技能")
    print("  GET    /api/v1/admin/skills/{id}     - 获取技能详情")
    print("  POST   /api/v1/admin/skills          - 创建技能")
    print("  PUT    /api/v1/admin/skills/{id}     - 更新技能")
    print("  DELETE /api/v1/admin/skills/{id}     - 删除技能")
    print("  POST   /api/v1/admin/skills/{id}/toggle - 切换技能状态")
    print("\n统计:")
    print("  GET    /api/v1/admin/stats           - 获取统计信息")
