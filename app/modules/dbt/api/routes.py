"""
API路由定义
定义DBT技能推荐模块的所有API端点
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from ..db.session import get_db
from ..models.schemas import (
    RecommendRequest, DBTRecommendation,
    SkillInfo, ModuleInfo, HealthResponse
)
from ..repositories.skill_repository import SkillRepository
from ..services.recommendation_engine import RecommendationEngine


router = APIRouter()


# ==================== 依赖注入 ====================

async def get_repository(session: AsyncSession = Depends(get_db)) -> SkillRepository:
    """获取技能仓库实例"""
    return SkillRepository(session)


async def get_recommendation_engine(
    repository: SkillRepository = Depends(get_repository)
) -> RecommendationEngine:
    """获取推荐引擎实例"""
    return RecommendationEngine(repository)


# ==================== 推荐API ====================

@router.post(
    "/recommend",
    response_model=DBTRecommendation,
    summary="获取DBT技能推荐",
    description="根据情绪状态和干预评估，推荐合适的DBT技能"
)
async def get_recommendation(
    request: RecommendRequest,
    engine: RecommendationEngine = Depends(get_recommendation_engine)
) -> DBTRecommendation:
    """
    获取DBT技能推荐

    - **emotion_input**: 情绪识别结果
    - **intervention_assessment**: 干预评估结果
    - **user_profile**: 用户画像（可选）
    - **agent_context**: Agent上下文（可选）
    - **context**: 情境描述（可选）
    """
    try:
        logger.info(f"收到推荐请求: risk_level={request.intervention_assessment.risk_level}")
        recommendation = await engine.recommend(request)
        logger.info(f"推荐完成: module={recommendation.recommended_module}, "
                   f"skills={[s.skill_name for s in recommendation.recommended_skills]}")
        return recommendation
    except Exception as e:
        logger.error(f"推荐失败: {e}")
        raise HTTPException(status_code=500, detail=f"推荐服务错误: {str(e)}")


# ==================== 技能API ====================

@router.get(
    "/skills",
    response_model=List[SkillInfo],
    summary="获取所有技能列表",
    description="获取所有可用的DBT技能"
)
async def get_all_skills(
    active_only: bool = True,
    repository: SkillRepository = Depends(get_repository)
) -> List[SkillInfo]:
    """获取所有技能列表"""
    try:
        skills = await repository.get_all_skills(active_only=active_only)
        return [
            SkillInfo(
                id=s.id,
                name=s.name,
                name_en=s.name_en,
                module_name=s.module.name if s.module else "",
                description=s.description or "",
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
    response_model=SkillInfo,
    summary="获取单个技能详情",
    description="根据ID获取技能详情"
)
async def get_skill_by_id(
    skill_id: int,
    repository: SkillRepository = Depends(get_repository)
) -> SkillInfo:
    """获取单个技能详情"""
    try:
        skill = await repository.get_skill_by_id(skill_id)
        if not skill:
            raise HTTPException(status_code=404, detail="技能不存在")
        return SkillInfo(
            id=skill.id,
            name=skill.name,
            name_en=skill.name_en,
            module_name=skill.module.name if skill.module else "",
            description=skill.description or "",
            difficulty_level=skill.difficulty_level or 1,
            is_active=skill.is_active
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取技能详情失败: {e}")
        raise HTTPException(status_code=500, detail=f"服务错误: {str(e)}")


# ==================== 模块API ====================

@router.get(
    "/modules",
    response_model=List[ModuleInfo],
    summary="获取DBT模块列表",
    description="获取所有DBT四大模块信息"
)
async def get_all_modules(
    repository: SkillRepository = Depends(get_repository)
) -> List[ModuleInfo]:
    """获取所有模块列表"""
    try:
        modules = await repository.get_all_modules()
        result = []
        for m in modules:
            skills = await repository.get_skills_by_module(m.id)
            result.append(ModuleInfo(
                id=m.id,
                name=m.name,
                name_en=m.name_en,
                description=m.description or "",
                skill_count=len(skills)
            ))
        return result
    except Exception as e:
        logger.error(f"获取模块列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"服务错误: {str(e)}")


# ==================== 健康检查 ====================

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="健康检查",
    description="检查服务状态"
)
async def health_check(
    repository: SkillRepository = Depends(get_repository)
) -> HealthResponse:
    """健康检查"""
    try:
        # 尝试查询数据库
        skill_count = await repository.count_skills()
        return HealthResponse(
            status="ok",
            version="0.1.0",
            database=f"connected (skills: {skill_count})"
        )
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return HealthResponse(
            status="error",
            version="0.1.0",
            database=f"error: {str(e)}"
        )


# ============== 测试用例 ==============
if __name__ == "__main__":
    print("API路由定义完成")
    print("端点列表:")
    print("  POST /api/v1/dbt/recommend    - 获取技能推荐")
    print("  GET  /api/v1/dbt/skills       - 获取所有技能")
    print("  GET  /api/v1/dbt/skills/{id}  - 获取技能详情")
    print("  GET  /api/v1/dbt/modules      - 获取模块列表")
    print("  GET  /api/v1/dbt/health       - 健康检查")
