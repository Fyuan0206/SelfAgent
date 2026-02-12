"""
额度检查中间件和依赖注入
用于保护需要消耗额度的 API 端点
"""

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from loguru import logger

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user_models import User
from app.services.quota_service import QuotaService


def require_quota(cost: int = 1, action_type: str = "default"):
    """
    额度检查依赖注入工厂函数

    Args:
        cost: 消耗的额度数量
        action_type: 操作类型（用于记录）

    Returns:
        依赖注入函数

    使用示例:
        @router.post("/chat")
        async def chat(
            message: ChatMessage,
            user: User = Depends(require_quota(cost=1, action_type="chat")),
            db: Session = Depends(get_db)
        ):
            ...
    """
    async def check_quota_dependency(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        """
        检查用户是否有足够额度

        Returns:
            用户对象

        Raises:
            HTTPException: 额度不足
        """
        # 检查额度
        if not QuotaService.has_quota(db, current_user, cost):
            logger.warning(f"User {current_user.id} has insufficient quota for {action_type}")

            # 获取额度信息
            quota_info = QuotaService.get_user_quota_info(db, current_user)

            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "quota_exceeded",
                    "message": "今日额度已用完，请明天再试或升级为会员",
                    "daily_quota": quota_info["daily_quota"],
                    "daily_used": quota_info["daily_used"],
                    "remaining_quota": quota_info["remaining_quota"]
                }
            )

        # 消耗额度
        if not QuotaService.consume_quota(
            db=db,
            user=current_user,
            action_type=action_type,
            cost=cost,
            details=f"API call: {action_type}"
        ):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="扣除额度失败，请稍后重试"
            )

        return current_user

    return check_quota_dependency


def consume_quota_after(action_type: str = "default", cost: int = 1):
    """
    在请求成功后消耗额度的依赖注入

    用于需要先处理请求再扣除额度的场景

    使用示例:
        @router.post("/chat")
        async def chat(
            message: ChatMessage,
            user: User = Depends(get_current_user),
            db: Session = Depends(get_db)
        ):
            # 处理请求...
            # 成功后扣除额度
            consume_quota_after("chat", 1)
    """
    def quota_consumer(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        """返回一个消费函数"""
        def consume():
            QuotaService.consume_quota(
                db=db,
                user=current_user,
                action_type=action_type,
                cost=cost,
                details=f"API call: {action_type}"
            )
        return consume

    return quota_consumer


# ============== 预定义的额度检查依赖 ==============

# 聊天消息（消耗 1 额度）
check_chat_quota = require_quota(cost=1, action_type="chat")

# 情绪分析（消耗 1 额度）
check_emotion_quota = require_quota(cost=1, action_type="emotion_analysis")

# 技能推荐（消耗 1 额度）
check_skill_quota = require_quota(cost=1, action_type="skill_recommend")

# 多模态处理（消耗 2 额度）
check_multimodal_quota = require_quota(cost=2, action_type="multimodal")
