"""
数据库连接和会话管理
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
from typing import Generator
import os
from loguru import logger


# 从环境变量获取数据库 URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://selfagent:selfagent_password@localhost:5432/selfagent_db"
)

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # 检查连接有效性
    echo=False,  # 设置为 True 可查看 SQL 日志
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话（依赖注入）
    使用方式：
        db: Session = next(get_db())
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """初始化数据库表"""
    from app.models.user_models import User, UserQuota, UsageRecord
    from app.models.user_models import Base as UserBase
    from app.modules.dbt.models.database import Base as DBTBase

    logger.info("Creating database tables...")

    # 创建所有表
    UserBase.metadata.create_all(bind=engine)
    DBTBase.metadata.create_all(bind=engine)

    logger.info("Database tables created successfully")


def create_default_admin(db: Session, email: str = "admin@selfagent.com", password: str = "admin123"):
    """创建默认管理员账户"""
    from app.models.user_models import User, UserQuota, UserRole, get_password_hash

    # 检查是否已存在管理员
    existing_admin = db.query(User).filter(User.email == email).first()
    if existing_admin:
        logger.info(f"Admin user already exists: {email}")
        return existing_admin

    # 创建管理员
    admin = User(
        email=email,
        username="Admin",
        hashed_password=get_password_hash(password),
        role=UserRole.ADMIN,
        is_active=True,
        is_verified=True
    )
    db.add(admin)
    db.flush()  # 获取 admin.id

    # 创建管理员额度（无限）
    quota = UserQuota(
        user_id=admin.id,
        daily_quota=-1,  # -1 表示无限额度
        daily_used=0
    )
    db.add(quota)

    db.commit()
    logger.info(f"Default admin user created: {email} / {password}")
    return admin


if __name__ == "__main__":
    # 测试数据库连接
    logger.info("Testing database connection...")
    try:
        init_db()
        logger.info("Database connection successful!")

        # 创建测试会话
        db = next(get_db())

        # 创建默认管理员
        create_default_admin(db)

        db.close()
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        logger.info("Please ensure PostgreSQL is running:")
        logger.info("  docker-compose up -d")
