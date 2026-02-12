"""
用户相关的 Pydantic 模型
用于 API 请求和响应的数据验证
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, date
from app.models.user_models import UserRole


# ============== 用户相关 Schema ==============

class UserBase(BaseModel):
    """用户基础模型"""
    email: EmailStr
    username: str


class UserCreate(UserBase):
    """用户注册请求"""
    password: str = Field(..., min_length=6, max_length=50)


class UserLogin(BaseModel):
    """用户登录请求"""
    email: EmailStr
    password: str


class UserResponse(UserBase):
    """用户响应"""
    id: int
    role: UserRole
    is_active: bool
    is_verified: bool
    is_onboarded: bool
    personality: Optional[str] = None
    emotional_profile: Optional[str] = None
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class OnboardingRequest(BaseModel):
    """用户初始化信息提交"""
    personality: str
    emotional_profile: str


class Token(BaseModel):
    """Token 响应"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ============== 额度相关 Schema ==============

class UserQuotaResponse(BaseModel):
    """用户额度响应"""
    daily_quota: int
    daily_used: int
    remaining_quota: int
    quota_date: date

    class Config:
        from_attributes = True


class UserDetailResponse(UserResponse):
    """用户详细信息响应（包含额度）"""
    quota: Optional[UserQuotaResponse] = None

    class Config:
        from_attributes = True


# ============== 管理员操作 Schema ==============

class UserUpdate(BaseModel):
    """用户更新请求（管理员）"""
    username: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None


class UserQuotaUpdate(BaseModel):
    """用户额度更新请求（管理员）"""
    daily_quota: int = Field(..., ge=-1, description="每日额度，-1 表示无限")


class UserCreateByAdmin(UserCreate):
    """管理员创建用户"""
    role: UserRole = UserRole.USER
    daily_quota: int = Field(50, ge=-1, description="每日额度，-1 表示无限")


# ============== 使用记录 Schema ==============

class UsageRecordResponse(BaseModel):
    """使用记录响应"""
    id: int
    action_type: str
    resource_cost: int
    details: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ============== 列表查询 Schema ==============

class UserListResponse(BaseModel):
    """用户列表响应"""
    total: int
    page: int
    page_size: int
    users: list[UserDetailResponse]
