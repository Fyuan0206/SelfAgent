"""
数据库会话管理
提供异步数据库连接和会话管理
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from ..config import get_settings
from ..models.database import Base


settings = get_settings()

# 异步引擎（用于FastAPI）
engine = create_async_engine(
    settings.database.url,
    echo=settings.database.echo,
    future=True
)

# 异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# 同步引擎（用于初始化和测试）
sync_url = settings.database.url.replace("+aiosqlite", "").replace("+asyncpg", "+psycopg2")
sync_engine = create_engine(sync_url, echo=settings.database.echo)
SessionLocal = sessionmaker(bind=sync_engine)


async def init_db():
    """初始化数据库表"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def init_db_sync():
    """同步初始化数据库表"""
    Base.metadata.create_all(sync_engine)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI依赖注入：获取数据库会话"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@asynccontextmanager
async def get_db_context() -> AsyncGenerator[AsyncSession, None]:
    """异步上下文管理器：获取数据库会话"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# ============== 测试用例 ==============
if __name__ == "__main__":
    import asyncio

    async def test_session():
        """测试数据库会话"""
        # 测试1: 初始化数据库
        await init_db()
        print("✓ 测试1通过: 数据库初始化成功")

        # 测试2: 获取异步会话
        async with get_db_context() as session:
            assert session is not None
            print("✓ 测试2通过: 异步会话获取成功")

        # 测试3: 同步会话
        sync_session = SessionLocal()
        try:
            assert sync_session is not None
            print("✓ 测试3通过: 同步会话获取成功")
        finally:
            sync_session.close()

        print("\n所有会话测试通过！")

    asyncio.run(test_session())
