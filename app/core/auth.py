"""
JWT 认证相关工具
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user_models import User, UserRole


# JWT 配置
SECRET_KEY = "your-secret-key-change-this-in-production"  # 应该从环境变量读取
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24小时

# HTTP Bearer 认证
security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建 JWT access token

    Args:
        data: 要编码的数据（通常包含 user_id 和 role）
        expires_delta: 过期时间增量

    Returns:
        JWT token 字符串
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    解码 JWT token

    Args:
        token: JWT token 字符串

    Returns:
        解码后的数据

    Raises:
        HTTPException: token 无效或过期
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    获取当前登录用户（依赖注入）

    Args:
        credentials: HTTP Bearer 凭据
        db: 数据库会话

    Returns:
        当前用户对象

    Raises:
        HTTPException: 认证失败
    """
    token = credentials.credentials
    payload = decode_access_token(token)

    user_id: int = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户已被禁用"
        )

    return user


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    获取当前管理员用户（依赖注入）

    Args:
        current_user: 当前用户

    Returns:
        当前管理员用户

    Raises:
        HTTPException: 用户不是管理员
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return current_user


class OptionalAuth:
    """可选认证依赖（允许未登录用户访问）"""
    async def __call__(
        self,
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(
            HTTPBearer(auto_error=False)
        ),
        db: Session = Depends(get_db)
    ) -> Optional[User]:
        if credentials is None:
            return None

        try:
            token = credentials.credentials
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: int = payload.get("sub")
            if user_id is None:
                return None

            user = db.query(User).filter(User.id == user_id).first()
            return user
        except (JWTError, Exception):
            return None


optional_auth = OptionalAuth()
