"""
用户额度管理服务
"""

from datetime import date, datetime
from typing import Optional
from sqlalchemy.orm import Session
from loguru import logger

from app.models.user_models import User, UserQuota, UsageRecord, UserRole


class QuotaService:
    """额度管理服务"""

    @staticmethod
    def check_and_reset_daily_quota(db: Session, user: User) -> UserQuota:
        """
        检查并重置每日额度

        Args:
            db: 数据库会话
            user: 用户对象

        Returns:
            用户额度对象
        """
        quota = db.query(UserQuota).filter(UserQuota.user_id == user.id).first()

        if quota is None:
            # 首次创建额度记录
            quota = UserQuota(
                user_id=user.id,
                daily_quota=50 if user.role == UserRole.USER else -1,
                daily_used=0,
                quota_date=date.today()
            )
            db.add(quota)
            db.commit()
            db.refresh(quota)
            return quota

        # 检查是否需要重置额度
        if quota.quota_date < date.today():
            logger.info(f"Resetting daily quota for user {user.id}")
            quota.daily_used = 0
            quota.quota_date = date.today()
            db.commit()
            db.refresh(quota)

        return quota

    @staticmethod
    def has_quota(db: Session, user: User, cost: int = 1) -> bool:
        """
        检查用户是否有足够额度

        Args:
            db: 数据库会话
            user: 用户对象
            cost: 需要消耗的额度

        Returns:
            是否有足够额度
        """
        # 管理员和会员无限额度
        if user.role in [UserRole.ADMIN, UserRole.MEMBER]:
            return True

        quota = QuotaService.check_and_reset_daily_quota(db, user)

        # -1 表示无限额度
        if quota.daily_quota == -1:
            return True

        return quota.daily_used + cost <= quota.daily_quota

    @staticmethod
    def consume_quota(
        db: Session,
        user: User,
        action_type: str,
        cost: int = 1,
        details: Optional[str] = None
    ) -> bool:
        """
        消耗用户额度

        Args:
            db: 数据库会话
            user: 用户对象
            action_type: 操作类型
            cost: 消耗的额度
            details: 详细信息

        Returns:
            是否成功消耗额度
        """
        # 管理员和会员不需要记录额度消耗
        if user.role in [UserRole.ADMIN, UserRole.MEMBER]:
            # 仍然记录使用记录，但不扣除额度
            usage_record = UsageRecord(
                user_id=user.id,
                action_type=action_type,
                resource_cost=0,  # 不扣除
                details=details
            )
            db.add(usage_record)
            db.commit()
            return True

        quota = QuotaService.check_and_reset_daily_quota(db, user)

        # -1 表示无限额度
        if quota.daily_quota == -1:
            usage_record = UsageRecord(
                user_id=user.id,
                action_type=action_type,
                resource_cost=0,
                details=details
            )
            db.add(usage_record)
            db.commit()
            return True

        # 检查额度是否足够
        if quota.daily_used + cost > quota.daily_quota:
            logger.warning(f"User {user.id} has insufficient quota")
            return False

        # 扣除额度
        quota.daily_used += cost

        # 记录使用
        usage_record = UsageRecord(
            user_id=user.id,
            action_type=action_type,
            resource_cost=cost,
            details=details
        )
        db.add(usage_record)

        db.commit()
        logger.info(f"User {user.id} consumed {cost} quota for {action_type}, remaining: {quota.remaining_quota}")

        return True

    @staticmethod
    def get_user_quota_info(db: Session, user: User) -> dict:
        """
        获取用户额度信息

        Args:
            db: 数据库会话
            user: 用户对象

        Returns:
            额度信息字典
        """
        quota = QuotaService.check_and_reset_daily_quota(db, user)

        return {
            "daily_quota": quota.daily_quota,
            "daily_used": quota.daily_used,
            "remaining_quota": quota.remaining_quota,
            "has_quota": quota.has_quota,
            "quota_date": quota.quota_date,
            "is_unlimited": quota.daily_quota == -1
        }
