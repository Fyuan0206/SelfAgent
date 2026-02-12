"""
Self-Agent Web Server
FastAPI server with frontend integration - following main.py pattern
"""

import os
import sys
import asyncio
from contextlib import asynccontextmanager
from typing import Optional, List, Dict
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from loguru import logger
from datetime import datetime

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.agent import SelfAgent
from app.models.data_models import UserInput
from app.api import auth, admin, frontend
from app.api import profile_api
from app.core.database import init_db, get_db
from loguru import logger
from app.core.memory_manager import MemoryManager

# DBT 模块路由
from app.modules.dbt.api.admin_routes import router as dbt_admin_router
from app.modules.dbt.api.routes import router as dbt_public_router
from app.modules.dbt.db import session as dbt_session
from app.modules.dbt.db.init_data import init_database as init_dbt_data


# ==================== Pydantic Models ====================

class ChatRequest(BaseModel):
    user_id: str
    text: str


class ChatResponse(BaseModel):
    response: str
    success: bool


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup and cleanup on shutdown"""
    logger.info("=" * 60)
    logger.info("Starting Self-Agent Web Server")
    logger.info("=" * 60)

    # Initialize main database
    try:
        init_db()
        logger.info("✓ Database initialized")

        # Create default admin if not exists
        db = next(get_db())
        from app.core.database import create_default_admin
        create_default_admin(db)
        db.close()
        logger.info("✓ Default admin user ready (admin@selfagent.com / admin123)")
    except Exception as e:
        logger.error(f"✗ Failed to initialize database: {e}")
        logger.warning("Please check your database configuration in .env")

    # Initialize DBT database (SQLite)
    try:
        await dbt_session.init_db()
        logger.info("✓ DBT database initialized")

        # Initialize default DBT data
        await init_dbt_data()
        logger.info("✓ DBT default data ready")
    except Exception as e:
        logger.error(f"✗ Failed to initialize DBT database: {e}")
        logger.warning("DBT skill/rule management may not work properly")

    # Check environment variables
    if not os.getenv("OPENAI_API_KEY"):
        logger.warning("OPENAI_API_KEY not set! Please set it in .env file")

    # Pre-initialize agent
    try:
        get_agent()
        logger.info("✓ Agent initialized and ready")
    except Exception as e:
        logger.error(f"✗ Failed to initialize agent: {e}")
        logger.warning("Server will start, but chat functionality may not work")

    yield

    """Cleanup on shutdown"""
    logger.info("Shutting down Self-Agent server...")


# ==================== Create FastAPI App ====================

app = FastAPI(
    title="Self-Agent API",
    description="智能情绪支持系统 API",
    version="2.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== API Routes ====================

# 包含认证和管理 API
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(frontend.router)
app.include_router(profile_api.router)

# 包含 DBT 管理 API（技能、规则、统计）
app.include_router(dbt_admin_router, prefix="/api/v1/admin", tags=["DBT管理"])
# 包含 DBT 公开 API（技能列表、推荐）
app.include_router(dbt_public_router, prefix="/api/v1/dbt", tags=["DBT技能"])

# ==================== Agent Initialization ====================

# Global agent instance (following main.py pattern)
_agent_instance: Optional[SelfAgent] = None
_memory_manager = MemoryManager(persist_path="./data/chroma_db")
_conversation_buffers: Dict[str, List[Dict]] = {}


def get_agent() -> SelfAgent:
    """Get or create agent instance - exactly like main.py"""
    global _agent_instance
    if _agent_instance is None:
        model_name = os.getenv("MODEL_NAME", "deepseek-chat")
        logger.info(f"Initializing Self-Agent with model: {model_name}")
        _agent_instance = SelfAgent(model_type=model_name)
        logger.info("Self-Agent initialized successfully")
    return _agent_instance


# ==================== API Routes ====================

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest) -> ChatResponse:
    """
    Process chat message - following main.py pattern exactly

    This endpoint mimics the exact flow from main.py:
    1. Create UserInput object
    2. Call agent.process_interaction(user_input)
    3. Return the response
    """
    try:
        logger.info(f"Received message from {request.user_id}: {request.text[:50]}...")

        # Get agent instance
        agent = get_agent()

        # Create UserInput object (exactly like main.py)
        user_input = UserInput(
            user_id=request.user_id,
            text=request.text
        )

        # Process interaction (exactly like main.py)
        logger.info("Processing interaction...")
        response = agent.process_interaction(user_input)

        buf_key = request.user_id
        buf = _conversation_buffers.get(buf_key, [])
        buf.append({"role": "user", "content": request.text, "ts": datetime.now().isoformat()})
        buf.append({"role": "assistant", "content": response, "ts": datetime.now().isoformat()})
        _conversation_buffers[buf_key] = buf
        if len(buf) >= 12:
            summary = await _memory_manager.compress_and_archive(buf_key, buf, agent_instance=agent)
            _conversation_buffers[buf_key] = buf[-2:]

        logger.info(f"Agent response: {response[:100]}...")

        return ChatResponse(
            response=response,
            success=True
        )

    except Exception as e:
        logger.error(f"Error processing chat: {e}")
        return ChatResponse(
            response=f"抱歉，发生了错误：{str(e)}",
            success=False
        )


@app.post("/api/chat/multimodal")
async def chat_multimodal_endpoint(
    user_id: str = Form(...),
    text: str = Form(default=""),
    file: Optional[UploadFile] = File(None)
) -> ChatResponse:
    """
    Process multimodal chat (audio/image) - following main.py pattern
    """
    try:
        logger.info(f"Multimodal chat from {user_id}, file: {file.filename if file else 'None'}")

        agent = get_agent()

        # For now, we'll just process the text
        # TODO: Implement proper audio/image processing
        message_text = text
        if file:
            message_text = f"[发送了文件: {file.filename}] {text}"

        user_input = UserInput(
            user_id=user_id,
            text=message_text
        )

        response = agent.process_interaction(user_input)

        buf_key = user_id
        buf = _conversation_buffers.get(buf_key, [])
        buf.append({"role": "user", "content": message_text, "ts": datetime.now().isoformat()})
        buf.append({"role": "assistant", "content": response, "ts": datetime.now().isoformat()})
        _conversation_buffers[buf_key] = buf
        if len(buf) >= 12:
            summary = await _memory_manager.compress_and_archive(buf_key, buf, agent_instance=agent)
            _conversation_buffers[buf_key] = buf[-2:]

        return ChatResponse(
            response=response,
            success=True
        )

    except Exception as e:
        logger.error(f"Error processing multimodal chat: {e}")
        return ChatResponse(
            response=f"抱歉，发生了错误：{str(e)}",
            success=False
        )


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "selfagent",
        "version": "2.0.0",
        "agent_initialized": _agent_instance is not None
    }


# ==================== Frontend Static Files ====================

# 使用绝对路径确保准确性
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
frontend_dir = os.path.join(BASE_DIR, "frontend")

logger.info(f"Frontend static directory: {frontend_dir}")

if os.path.exists(frontend_dir):
    # Serve static files
    static_dir = os.path.join(frontend_dir, "static")
    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")

    # Serve js files
    js_dir = os.path.join(frontend_dir, "js")
    if os.path.exists(js_dir):
        app.mount("/js", StaticFiles(directory=js_dir), name="js")

    # Serve css files if exists
    css_dir = os.path.join(frontend_dir, "css")
    if os.path.exists(css_dir):
        app.mount("/css", StaticFiles(directory=css_dir), name="css")

    # Serve index.html at root
    @app.get("/")
    @app.get("/index.html")
    async def read_root():
        index_file = os.path.join(frontend_dir, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"message": "Self-Agent API is running. Frontend index.html not found."}

    # Serve login.html
    @app.get("/login")
    @app.get("/login.html")
    async def read_login():
        login_file = os.path.join(frontend_dir, "login.html")
        if os.path.exists(login_file):
            return FileResponse(login_file)
        return {"message": "Login page not found."}

    # Serve admin.html
    @app.get("/admin")
    @app.get("/admin.html")
    async def read_admin():
        admin_file = os.path.join(frontend_dir, "admin.html")
        if os.path.exists(admin_file):
            return FileResponse(admin_file)
        return {"message": "Admin page not found."}
else:
    logger.warning(f"Frontend directory not found: {frontend_dir}")


# ==================== Lifecycle Events (Deprecated) ====================
# Using lifespan context manager instead



# ==================== Main ====================

if __name__ == "__main__":
    import uvicorn

    logger.info("Starting Self-Agent web server...")

    uvicorn.run(
        "app.server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
