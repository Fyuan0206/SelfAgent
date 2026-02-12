"""
FastAPI应用入口
DBT技能推荐模块主程序
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from .config import get_settings
from .api.routes import router
from .api.admin_routes import router as admin_router
from .db.session import init_db
from .db.init_data import init_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("DBT技能推荐服务启动中...")

    # 初始化数据库
    await init_db()
    logger.info("数据库表创建完成")

    # 初始化DBT技能数据
    await init_database()
    logger.info("DBT技能数据初始化完成")

    yield

    # 关闭时执行
    logger.info("DBT技能推荐服务关闭")


# 获取配置
settings = get_settings()

# 创建FastAPI应用
app = FastAPI(
    title="DBT技能推荐模块",
    description="""
DBT（辩证行为疗法）技能推荐服务

## 功能
- 根据情绪状态和干预评估推荐合适的DBT技能
- 支持规则匹配和LLM辅助推荐
- 提供个性化推荐理由和引导策略

## 模块
- 正念（Mindfulness）
- 痛苦耐受（Distress Tolerance）
- 情绪调节（Emotion Regulation）
- 人际效能（Interpersonal Effectiveness）
    """,
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router, prefix="/api/v1/dbt", tags=["DBT推荐"])
app.include_router(admin_router, prefix="/api/v1/admin", tags=["管理员"])


@app.get("/", tags=["Root"])
async def root():
    """根路径"""
    return {
        "name": "DBT技能推荐模块",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/api/v1/dbt/health"
    }


# ============== 测试用例 ==============
if __name__ == "__main__":
    import uvicorn

    logger.info(f"启动服务: {settings.server.host}:{settings.server.port}")

    uvicorn.run(
        "app.main:app",
        host=settings.server.host,
        port=settings.server.port,
        reload=settings.server.debug,
        log_level=settings.server.log_level.lower()
    )
