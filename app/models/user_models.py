"""
用户和权限相关数据库模型
包含：User（用户）、Role（角色）、UserQuota（用户额度）、UsageRecord（使用记录）
"""

from datetime import datetime, date
from typing import Optional, List
from enum import Enum

from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Date,
    ForeignKey, Numeric, Enum as SQLEnum, Index
)
from sqlalchemy.orm import relationship, DeclarativeBase
from passlib.context import CryptContext


class Base(DeclarativeBase):
    """SQLAlchemy 基类"""
    pass


class UserRole(str, Enum):
    """用户角色枚举"""
    ADMIN = "admin"      # 管理员：不限额，可管理用户
    MEMBER = "member"    # 会员：不限额
    USER = "user"        # 普通用户：有限额


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # 关联额度
    quota = relationship("UserQuota", back_populates="user", uselist=False, cascade="all, delete-orphan")
    # 关联使用记录
    usage_records = relationship("UsageRecord", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"


class UserQuota(Base):
    """用户额度表"""
    __tablename__ = "user_quotas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)

    # 每日额度
    daily_quota = Column(Integer, default=50, nullable=False)  # 普通用户默认50条/天
    daily_used = Column(Integer, default=0, nullable=False)

    # 额度重置日期
    quota_date = Column(Date, default=date.today, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 关联用户
    user = relationship("User", back_populates="quota")

    def __repr__(self):
        return f"<UserQuota(user_id={self.user_id}, daily_used={self.daily_used}/{self.daily_quota})>"

    @property
    def remaining_quota(self) -> int:
        """返回剩余额度"""
        if self.daily_quota == -1:  # -1 表示无限额度
            return -1
        return max(0, self.daily_quota - self.daily_used)

    @property
    def has_quota(self) -> bool:
        """检查是否还有额度"""
        return self.remaining_quota != 0


class UsageRecord(Base):
    """使用记录表"""
    __tablename__ = "usage_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # 使用信息
    action_type = Column(String(50), nullable=False)  # 'chat', 'emotion_analysis', 'skill_recommend' 等
    resource_cost = Column(Integer, default=1, nullable=False)  # 消耗的额度

    # 详细信息（JSON格式存储）
    details = Column(String(1000), nullable=True)  # 存储额外的详细信息

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # 关联用户
    user = relationship("User", back_populates="usage_records")

    def __repr__(self):
        return f"<UsageRecord(id={self.id}, user_id={self.user_id}, action='{self.action_type}')>"


# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)
