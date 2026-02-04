"""
管理员 API
包含：用户管理、额度分配、用户列表查询
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from loguru import logger

from app.core.database import get_db
from app.core.auth import get_current_admin, User as UserModel
from app.models.user_models import User, UserQuota, UserRole, get_password_hash
from app.models.user_schemas import (
    UserCreateByAdmin, UserUpdate, UserQuotaUpdate,
    UserDetailResponse, UserListResponse, UsageRecordResponse
)
from app.services.quota_service import QuotaService


router = APIRouter(prefix="/api/admin", tags=["管理员"])


# ============== 用户列表查询 ==============

@router.get("/users", response_model=UserListResponse)
async def get_users(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    role: Optional[UserRole] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None
):
    """
    获取用户列表（仅管理员）

    - **page**: 页码（从 1 开始）
    - **page_size**: 每页数量（最大 100）
    - **role**: 按角色筛选
    - **is_active**: 按状态筛选
    - **search**: 搜索邮箱或用户名
    """
    query = db.query(User)

    # 筛选条件
    if role:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    if search:
        query = query.filter(
            (User.email.ilike(f"%{search}%")) | (User.username.ilike(f"%{search}%"))
        )

    # 计算总数
    total = query.count()

    # 分页
    offset = (page - 1) * page_size
    users = query.offset(offset).limit(page_size).all()

    # 构建响应
    user_details = []
    for user in users:
        quota = QuotaService.check_and_reset_daily_quota(db, user)
        user_details.append(UserDetailResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            role=user.role,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at,
            last_login=user.last_login,
            quota=quota
        ))

    return UserListResponse(
        total=total,
        page=page,
        page_size=page_size,
        users=user_details
    )


# ============== 创建用户 ==============

@router.post("/users", response_model=UserDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreateByAdmin,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    管理员创建新用户

    - **email**: 邮箱地址
    - **username**: 用户名
    - **password**: 密码
    - **role**: 角色（admin/member/user）
    - **daily_quota**: 每日额度（-1 表示无限）
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
        role=user_data.role,
        is_active=True,
        is_verified=True  # 管理员创建的用户自动验证
    )
    db.add(new_user)
    db.flush()

    # 创建额度记录
    user_quota = UserQuota(
        user_id=new_user.id,
        daily_quota=user_data.daily_quota,
        daily_used=0
    )
    db.add(user_quota)

    db.commit()
    db.refresh(new_user)

    quota = QuotaService.check_and_reset_daily_quota(db, new_user)

    logger.info(f"Admin {current_admin.id} created user {new_user.id}")

    return UserDetailResponse(
        id=new_user.id,
        email=new_user.email,
        username=new_user.username,
        role=new_user.role,
        is_active=new_user.is_active,
        is_verified=new_user.is_verified,
        created_at=new_user.created_at,
        last_login=new_user.last_login,
        quota=quota
    )


# ============== 更新用户信息 ==============

@router.put("/users/{user_id}", response_model=UserDetailResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    更新用户信息（仅管理员）

    - **user_id**: 用户 ID
    - **username**: 新用户名（可选）
    - **role**: 新角色（可选）
    - **is_active**: 是否激活（可选）
    - **is_verified**: 是否验证（可选）
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 更新字段
    if user_data.username is not None:
        user.username = user_data.username
    if user_data.role is not None:
        user.role = user_data.role
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    if user_data.is_verified is not None:
        user.is_verified = user_data.is_verified

    db.commit()
    db.refresh(user)

    quota = QuotaService.check_and_reset_daily_quota(db, user)

    logger.info(f"Admin {current_admin.id} updated user {user_id}")

    return UserDetailResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        role=user.role,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at,
        last_login=user.last_login,
        quota=quota
    )


# ============== 更新用户额度 ==============

@router.put("/users/{user_id}/quota", response_model=UserQuotaResponse)
async def update_user_quota(
    user_id: int,
    quota_data: UserQuotaUpdate,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    更新用户额度（仅管理员）

    - **user_id**: 用户 ID
    - **daily_quota**: 新的每日额度（-1 表示无限）
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    quota = db.query(UserQuota).filter(UserQuota.user_id == user_id).first()
    if not quota:
        # 创建新的额度记录
        quota = UserQuota(
            user_id=user_id,
            daily_quota=quota_data.daily_quota,
            daily_used=0
        )
        db.add(quota)
    else:
        quota.daily_quota = quota_data.daily_quota

    db.commit()
    db.refresh(quota)

    logger.info(f"Admin {current_admin.id} updated quota for user {user_id}: {quota_data.daily_quota}")

    return UserQuotaResponse.model_validate(quota)


# ============== 获取用户详情 ==============

@router.get("/users/{user_id}", response_model=UserDetailResponse)
async def get_user_detail(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    获取用户详细信息（仅管理员）
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    quota = QuotaService.check_and_reset_daily_quota(db, user)

    return UserDetailResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        role=user.role,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at,
        last_login=user.last_login,
        quota=quota
    )


# ============== 删除用户 ==============

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    删除用户（仅管理员）

    注意：这将永久删除用户及其所有数据
    """
    if user_id == current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己的账户"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    db.delete(user)
    db.commit()

    logger.info(f"Admin {current_admin.id} deleted user {user_id}")

    return None


# ============== 获取用户使用记录 ==============

@router.get("/users/{user_id}/usage", response_model=list[UsageRecordResponse])
async def get_user_usage_records(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=200)
):
    """
    获取用户的使用记录（仅管理员）

    - **user_id**: 用户 ID
    - **limit**: 返回记录数量（最大 200）
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    from app.models.user_models import UsageRecord

    records = db.query(UsageRecord)\
        .filter(UsageRecord.user_id == user_id)\
        .order_by(UsageRecord.created_at.desc())\
        .limit(limit)\
        .all()

    return [UsageRecordResponse.model_validate(r) for r in records]
