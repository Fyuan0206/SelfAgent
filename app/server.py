"""
Self-Agent Web Server
FastAPI server with frontend integration - following main.py pattern
"""

import os
import sys
import asyncio
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from loguru import logger

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.agent import SelfAgent
from app.models.data_models import UserInput


# ==================== Pydantic Models ====================

class ChatRequest(BaseModel):
    user_id: str
    text: str


class ChatResponse(BaseModel):
    response: str
    success: bool


# ==================== Create FastAPI App ====================

app = FastAPI(
    title="Self-Agent API",
    description="智能情绪支持系统 API",
    version="2.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Agent Initialization ====================

# Global agent instance (following main.py pattern)
_agent_instance: Optional[SelfAgent] = None


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

frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")

if os.path.exists(frontend_dir):
    # Serve static files
    static_dir = os.path.join(frontend_dir, "static")
    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")

    # Serve js files
    js_dir = os.path.join(frontend_dir, "js")
    if os.path.exists(js_dir):
        app.mount("/js", StaticFiles(directory=js_dir), name="js")

    # Serve index.html at root
    @app.get("/")
    async def read_root():
        index_file = os.path.join(frontend_dir, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return {"message": "Self-Agent API is running. Frontend not found."}

    logger.info(f"Frontend directory: {frontend_dir}")
else:
    logger.warning(f"Frontend directory not found: {frontend_dir}")


# ==================== Lifecycle Events ====================

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("=" * 60)
    logger.info("Starting Self-Agent Web Server")
    logger.info("=" * 60)

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


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Self-Agent server...")


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
