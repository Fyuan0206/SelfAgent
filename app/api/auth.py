"""
用户认证和授权 API
包含：注册、登录、获取用户信息
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from loguru import logger

from app.core.database import get_db
from app.core.auth import get_current_user, create_access_token, get_current_admin
from app.models.user_models import User, UserQuota, UserRole, verify_password, get_password_hash
from app.models.user_schemas import (
    UserCreate, UserLogin, UserResponse, Token,
    UserDetailResponse, UserQuotaResponse, OnboardingRequest
)
from app.services.quota_service import QuotaService


router = APIRouter(prefix="/api/auth", tags=["认证"])


# ============== 用户初始化 (Onboarding) ==============

@router.post("/onboarding", response_model=UserResponse)
async def onboarding(
    data: OnboardingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    提交用户初始化信息 (性格、情感偏好等)
    """
    current_user.personality = data.personality
    current_user.emotional_profile = data.emotional_profile
    current_user.is_onboarded = True
    
    db.commit()
    db.refresh(current_user)
    
    return UserResponse.model_validate(current_user)


# ============== 用户注册 ==============

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    用户注册

    - **email**: 邮箱地址（唯一）
    - **username**: 用户名
    - **password**: 密码（至少6位）
    """
    # 检查邮箱是否已存在
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该邮箱已被注册"
        )

    # 创建新用户
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=get_password_hash(user_data.password),
        role=UserRole.USER,  # 默认为普通用户
        is_active=True,
        is_verified=False
    )
    db.add(new_user)
    db.flush()  # 获取用户 ID

    # 创建用户额度记录（普通用户默认 50 条/天）
    user_quota = UserQuota(
        user_id=new_user.id,
        daily_quota=50,
        daily_used=0
    )
    db.add(user_quota)

    db.commit()
    db.refresh(new_user)

    logger.info(f"New user registered: {new_user.email}")

    # 生成 token
    access_token = create_access_token(data={"sub": str(new_user.id), "role": new_user.role})

    return Token(
        access_token=access_token,
        user=UserResponse.model_validate(new_user)
    )


# ============== 用户登录 ==============

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    用户登录

    - **email**: 邮箱地址
    - **password**: 密码
    """
    # 查找用户
    user = db.query(User).filter(User.email == credentials.email).first()

    # 验证用户和密码
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误"
        )

    # 检查用户状态
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账户已被禁用"
        )

    # 更新最后登录时间
    user.last_login = datetime.utcnow()
    db.commit()

    logger.info(f"User logged in: {user.email}")

    # 生成 token
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})

    return Token(
        access_token=access_token,
        user=UserResponse.model_validate(user)
    )


# ============== 获取当前用户信息 ==============

@router.get("/me", response_model=UserDetailResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前登录用户的详细信息（包含额度）
    需要在请求头中携带 Authorization: Bearer <token>
    """
    quota = QuotaService.check_and_reset_daily_quota(db, current_user)

    return UserDetailResponse(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        role=current_user.role,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        is_onboarded=current_user.is_onboarded,  # 添加字段
        personality=current_user.personality,
        emotional_profile=current_user.emotional_profile,
        created_at=current_user.created_at,
        last_login=current_user.last_login,
        quota=UserQuotaResponse.model_validate(quota)
    )


# ============== 获取用户额度信息 ==============

@router.get("/quota", response_model=dict)
async def get_quota_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前用户的额度信息
    """
    quota_info = QuotaService.get_user_quota_info(db, current_user)
    return quota_info
