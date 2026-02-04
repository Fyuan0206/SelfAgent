"""
Mock Server for Frontend Testing
模拟所有 API 端点，用于前端测试，无需数据库
"""

import os
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Form, Header
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI(title="Self-Agent Mock API", description="用于前端测试的模拟 API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Mock Data ====================

MOCK_USER = {
    "id": 1,
    "email": "admin@selfagent.com",
    "username": "管理员",
    "role": "admin",
    "is_active": True,
    "is_verified": True,
    "created_at": "2024-01-01T00:00:00",
    "last_login": datetime.now().isoformat()
}

MOCK_TOKEN = "mock_jwt_token_for_testing_12345"
MOCK_ADMIN_TOKEN = "mock_admin_token_12345"
MOCK_USER_TOKEN = "mock_user_token_12345"

MOCK_USERS = [
    {"id": 1, "email": "admin@selfagent.com", "username": "管理员", "role": "admin", "is_active": True, "is_verified": True, "daily_quota": 0, "daily_used": 0, "created_at": "2024-01-01T00:00:00"},
    {"id": 2, "email": "member@example.com", "username": "会员用户", "role": "member", "is_active": True, "is_verified": True, "daily_quota": 0, "daily_used": 0, "created_at": "2024-01-10T00:00:00"},
    {"id": 3, "email": "user1@example.com", "username": "普通用户1", "role": "user", "is_active": True, "is_verified": True, "daily_quota": 50, "daily_used": 15, "created_at": "2024-01-15T00:00:00"},
    {"id": 4, "email": "user2@example.com", "username": "普通用户2", "role": "user", "is_active": False, "is_verified": False, "daily_quota": 50, "daily_used": 0, "created_at": "2024-01-20T00:00:00"},
]

MOCK_SKILLS = [
    {"id": 1, "name": "TIPP技能", "name_en": "TIPP", "module_id": 2, "module_name": "痛苦耐受", "difficulty_level": 2, "is_active": True, "description": "通过改变身体化学反应来快速降低情绪强度", "trigger_emotions": ["焦虑", "激越"], "steps": ["T - 改变温度", "I - 剧烈运动", "P - 配对放松", "P - 配对呼吸"]},
    {"id": 2, "name": "正念呼吸", "name_en": "Mindful Breathing", "module_id": 1, "module_name": "正念", "difficulty_level": 1, "is_active": True, "description": "专注于呼吸的正念练习", "trigger_emotions": ["焦虑", "压力"], "steps": ["找一个舒适的姿势", "闭上眼睛", "专注于呼吸"]},
    {"id": 3, "name": "相反行动", "name_en": "Opposite Action", "module_id": 3, "module_name": "情绪调节", "difficulty_level": 3, "is_active": False, "description": "采取与情绪相反的行动", "trigger_emotions": ["悲伤", "恐惧"], "steps": ["识别情绪", "确定相反行动", "执行行动"]},
    {"id": 4, "name": "DEAR MAN", "name_en": "DEAR MAN", "module_id": 4, "module_name": "人际效能", "difficulty_level": 2, "is_active": True, "description": "有效沟通技能", "trigger_emotions": ["愤怒", "挫败"], "steps": ["D - 描述", "E - 表达", "A - 主张", "R - 强化"]},
]

MOCK_RULES = [
    {"id": 1, "rule_name": "高焦虑触发TIPP", "priority": 90, "skill_ids": [1], "module_id": 2, "module_name": "痛苦耐受", "description": "当焦虑水平高时触发TIPP技能", "is_active": True, "conditions": {"emotion": "焦虑", "threshold": 0.7}},
    {"id": 2, "rule_name": "日常正念推荐", "priority": 50, "skill_ids": [2], "module_id": 1, "module_name": "正念", "description": "日常推荐正念呼吸", "is_active": True, "conditions": {}},
    {"id": 3, "rule_name": "悲伤情绪干预", "priority": 70, "skill_ids": [3], "module_id": 3, "module_name": "情绪调节", "description": "悲伤情绪时推荐相反行动", "is_active": False, "conditions": {"emotion": "悲伤"}},
]

MOCK_PROFILES = [
    {"user_id": "user123", "created_at": "2024-01-20T10:00:00", "updated_at": "2024-01-25T20:00:00", "total_interactions": 156, "crisis_count": 3, "intervention_count": 12, "data_quality_score": 0.85},
    {"user_id": "test_user_001", "created_at": "2024-01-15T08:00:00", "updated_at": "2024-01-24T15:00:00", "total_interactions": 89, "crisis_count": 1, "intervention_count": 5, "data_quality_score": 0.72},
]

MOCK_PROFILE_DETAIL = {
    "user_id": "user123",
    "created_at": "2024-01-20T10:00:00",
    "updated_at": "2024-01-25T20:00:00",
    "total_interactions": 156,
    "crisis_count": 3,
    "intervention_count": 12,
    "avg_recovery_time": 4.2,
    "data_quality_score": 0.85,
    "emotion_baseline": {"焦虑": 0.42, "悲伤": 0.31, "空虚感": 0.25, "愤怒": 0.15, "恐惧": 0.12},
    "emotion_trend": {"direction": "improving", "slope": -0.05},
    "personality": {"openness": 0.8, "conscientiousness": 0.6, "extraversion": 0.4, "agreeableness": 0.7, "neuroticism": 0.9},
    "risk_prediction": {"next_crisis_probability": 0.12, "high_risk_time_windows": ["evening"]},
    "snapshots": []
}

# ==================== Auth API ====================

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    email: str
    username: str
    password: str

@app.post("/api/auth/login")
async def mock_login(request: LoginRequest):
    print(f"[Mock] Login attempt: {request.email}")
    if request.email == "admin@selfagent.com" and request.password == "admin123":
        return {"access_token": MOCK_ADMIN_TOKEN, "user": MOCK_USER}
    elif request.password == "test123":
        return {"access_token": MOCK_USER_TOKEN, "user": {**MOCK_USER, "id": 3, "email": request.email, "username": request.email.split("@")[0], "role": "user"}}
    return JSONResponse(status_code=401, content={"detail": "邮箱或密码错误"})

@app.post("/api/auth/register")
async def mock_register(request: RegisterRequest):
    print(f"[Mock] Register: {request.email}, {request.username}")
    return {"access_token": MOCK_USER_TOKEN, "user": {**MOCK_USER, "id": 99, "email": request.email, "username": request.username, "role": "user"}}

@app.get("/api/auth/me")
async def mock_get_me(authorization: str = Header(None)):
    print(f"[Mock] Get current user, token: {authorization[:30] if authorization else 'None'}...")
    # Check if admin token
    if authorization and MOCK_ADMIN_TOKEN in authorization:
        return {**MOCK_USER, "quota": {"daily_quota": 0, "daily_used": 0, "remaining": 0, "is_unlimited": True}}
    else:
        # Return regular user
        return {**MOCK_USER, "id": 3, "email": "user@example.com", "username": "普通用户", "role": "user", "quota": {"daily_quota": 50, "daily_used": 10, "remaining": 40}}

@app.get("/api/auth/quota")
async def mock_get_quota():
    return {"daily_quota": 50, "daily_used": 10, "remaining": 40, "is_unlimited": False}

# ==================== Chat API ====================

class ChatRequest(BaseModel):
    user_id: str
    text: str

@app.post("/api/chat")
async def mock_chat(request: ChatRequest):
    print(f"[Mock] Chat from {request.user_id}: {request.text[:50]}...")
    return {
        "response": f"[Mock Response] 我收到了你的消息：「{request.text[:30]}...」\n\n这是一个模拟响应，用于测试前端功能。在实际运行时，这里会返回 AI 的真实回复。",
        "success": True
    }

@app.post("/api/chat/multimodal")
async def mock_multimodal_chat(
    user_id: str = Form(...),
    text: str = Form(default=""),
    file: Optional[UploadFile] = File(None)
):
    file_info = f"文件: {file.filename}" if file else "无文件"
    file_type = "unknown"
    if file:
        if file.content_type and file.content_type.startswith("image"):
            file_type = "image"
        elif file.content_type and file.content_type.startswith("audio"):
            file_type = "audio"
        elif file.filename:
            if file.filename.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                file_type = "image"
            elif file.filename.endswith(('.mp3', '.wav', '.webm', '.ogg', '.m4a')):
                file_type = "audio"

    print(f"[Mock] Multimodal chat from {user_id}, type={file_type}, {file_info}")

    # 模拟情绪分析结果
    import random
    emotions = ["平静", "焦虑", "开心", "难过", "愤怒", "疲惫"]
    detected_emotion = random.choice(emotions)
    confidence = round(50 + random.random() * 45, 1)
    arousal = round(random.random(), 2)

    return {
        "response": f"[Mock Response] 收到多模态输入。{file_info}",
        "success": True,
        "emotion": {
            "name": detected_emotion,
            "confidence": confidence,
            "arousal": arousal,
            "source": file_type  # image 或 audio
        },
        "emotion_detected": detected_emotion,
        "risk_level": "low" if detected_emotion in ["平静", "开心"] else "medium",
        "is_crisis": False
    }

@app.get("/api/health")
async def mock_health():
    return {"status": "ok", "service": "selfagent-mock", "version": "2.0.0-mock", "agent_initialized": True}

# ==================== DBT Admin API ====================

@app.get("/api/v1/admin/stats")
async def mock_stats(x_admin_key: str = Header(None)):
    print(f"[Mock] Get stats, admin key: {x_admin_key}")
    return {
        "total_modules": 4,
        "total_skills": len(MOCK_SKILLS),
        "active_skills": len([s for s in MOCK_SKILLS if s["is_active"]]),
        "total_rules": len(MOCK_RULES),
        "active_rules": len([r for r in MOCK_RULES if r["is_active"]]),
        "skills_per_module": {"正念": 1, "痛苦耐受": 1, "情绪调节": 1, "人际效能": 1}
    }

@app.get("/api/v1/admin/skills")
async def mock_list_skills(x_admin_key: str = Header(None)):
    print(f"[Mock] List skills")
    return MOCK_SKILLS

@app.get("/api/v1/admin/skills/{skill_id}")
async def mock_get_skill(skill_id: int):
    skill = next((s for s in MOCK_SKILLS if s["id"] == skill_id), None)
    if skill:
        return skill
    return JSONResponse(status_code=404, content={"detail": "技能不存在"})

@app.post("/api/v1/admin/skills")
async def mock_create_skill(x_admin_key: str = Header(None)):
    print(f"[Mock] Create skill")
    new_skill = {**MOCK_SKILLS[0], "id": len(MOCK_SKILLS) + 1, "name": "新技能"}
    return new_skill

@app.put("/api/v1/admin/skills/{skill_id}")
async def mock_update_skill(skill_id: int):
    print(f"[Mock] Update skill {skill_id}")
    skill = next((s for s in MOCK_SKILLS if s["id"] == skill_id), None)
    if skill:
        return skill
    return JSONResponse(status_code=404, content={"detail": "技能不存在"})

@app.delete("/api/v1/admin/skills/{skill_id}")
async def mock_delete_skill(skill_id: int):
    print(f"[Mock] Delete skill {skill_id}")
    return {"message": "删除成功", "skill_id": skill_id}

@app.post("/api/v1/admin/skills/{skill_id}/toggle")
async def mock_toggle_skill(skill_id: int):
    print(f"[Mock] Toggle skill {skill_id}")
    for skill in MOCK_SKILLS:
        if skill["id"] == skill_id:
            skill["is_active"] = not skill["is_active"]
            return skill
    return JSONResponse(status_code=404, content={"detail": "技能不存在"})

@app.get("/api/v1/admin/rules")
async def mock_list_rules(x_admin_key: str = Header(None)):
    print(f"[Mock] List rules")
    return MOCK_RULES

@app.get("/api/v1/admin/rules/{rule_id}")
async def mock_get_rule(rule_id: int):
    rule = next((r for r in MOCK_RULES if r["id"] == rule_id), None)
    if rule:
        return rule
    return JSONResponse(status_code=404, content={"detail": "规则不存在"})

@app.post("/api/v1/admin/rules")
async def mock_create_rule(x_admin_key: str = Header(None)):
    print(f"[Mock] Create rule")
    return {**MOCK_RULES[0], "id": len(MOCK_RULES) + 1, "rule_name": "新规则"}

@app.put("/api/v1/admin/rules/{rule_id}")
async def mock_update_rule(rule_id: int):
    print(f"[Mock] Update rule {rule_id}")
    rule = next((r for r in MOCK_RULES if r["id"] == rule_id), None)
    if rule:
        return rule
    return JSONResponse(status_code=404, content={"detail": "规则不存在"})

@app.delete("/api/v1/admin/rules/{rule_id}")
async def mock_delete_rule(rule_id: int):
    print(f"[Mock] Delete rule {rule_id}")
    return {"message": "删除成功", "rule_id": rule_id}

@app.post("/api/v1/admin/rules/{rule_id}/toggle")
async def mock_toggle_rule(rule_id: int):
    print(f"[Mock] Toggle rule {rule_id}")
    for rule in MOCK_RULES:
        if rule["id"] == rule_id:
            rule["is_active"] = not rule["is_active"]
            return rule
    return JSONResponse(status_code=404, content={"detail": "规则不存在"})

# ==================== Profile API ====================

@app.get("/api/v1/admin/profiles")
async def mock_list_profiles(authorization: str = Header(None)):
    print(f"[Mock] List profiles")
    return MOCK_PROFILES

@app.get("/api/v1/admin/profiles/{user_id}")
async def mock_get_profile(user_id: str):
    print(f"[Mock] Get profile: {user_id}")
    return {**MOCK_PROFILE_DETAIL, "user_id": user_id}

@app.get("/api/v1/admin/dashboard")
async def mock_dashboard():
    return {
        "total_profiles": len(MOCK_PROFILES),
        "total_interactions": sum(p["total_interactions"] for p in MOCK_PROFILES),
        "total_crisis": sum(p["crisis_count"] for p in MOCK_PROFILES),
        "total_interventions": sum(p["intervention_count"] for p in MOCK_PROFILES),
        "avg_data_quality": 0.78
    }

# ==================== User Admin API ====================

class UserCreateRequest(BaseModel):
    email: str
    username: str
    password: str
    role: str = "user"
    daily_quota: int = 50
    is_active: bool = True

class UserUpdateRequest(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    daily_quota: Optional[int] = None
    is_active: Optional[bool] = None

@app.get("/api/admin/users")
async def mock_list_users(authorization: str = Header(None)):
    print(f"[Mock] List users")
    return MOCK_USERS

@app.post("/api/admin/users")
async def mock_create_user(request: UserCreateRequest, authorization: str = Header(None)):
    print(f"[Mock] Create user: {request.email}")
    new_user = {
        "id": len(MOCK_USERS) + 1,
        "email": request.email,
        "username": request.username,
        "role": request.role,
        "is_active": request.is_active,
        "is_verified": False,
        "daily_quota": request.daily_quota,
        "daily_used": 0,
        "created_at": datetime.now().isoformat()
    }
    return new_user

@app.get("/api/admin/users/{user_id}")
async def mock_get_user(user_id: int):
    user = next((u for u in MOCK_USERS if u["id"] == user_id), None)
    if user:
        return user
    return JSONResponse(status_code=404, content={"detail": "用户不存在"})

@app.put("/api/admin/users/{user_id}")
async def mock_update_user(user_id: int, request: UserUpdateRequest):
    print(f"[Mock] Update user {user_id}")
    user = next((u for u in MOCK_USERS if u["id"] == user_id), None)
    if user:
        updated = {**user}
        if request.email is not None:
            updated["email"] = request.email
        if request.username is not None:
            updated["username"] = request.username
        if request.role is not None:
            updated["role"] = request.role
        if request.daily_quota is not None:
            updated["daily_quota"] = request.daily_quota
        if request.is_active is not None:
            updated["is_active"] = request.is_active
        return updated
    return JSONResponse(status_code=404, content={"detail": "用户不存在"})

@app.delete("/api/admin/users/{user_id}")
async def mock_delete_user(user_id: int):
    print(f"[Mock] Delete user {user_id}")
    user = next((u for u in MOCK_USERS if u["id"] == user_id), None)
    if user:
        return {"message": "删除成功", "user_id": user_id}
    return JSONResponse(status_code=404, content={"detail": "用户不存在"})

@app.put("/api/admin/users/{user_id}/quota")
async def mock_update_quota(user_id: int):
    print(f"[Mock] Update quota for user {user_id}")
    return {"user_id": user_id, "daily_quota": 100, "message": "额度更新成功"}

# ==================== Frontend Static Files ====================

frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")

if os.path.exists(frontend_dir):
    js_dir = os.path.join(frontend_dir, "js")
    if os.path.exists(js_dir):
        app.mount("/js", StaticFiles(directory=js_dir), name="js")

    @app.get("/")
    @app.get("/index.html")
    async def read_root():
        return FileResponse(os.path.join(frontend_dir, "index.html"))

    @app.get("/login")
    @app.get("/login.html")
    async def read_login():
        return FileResponse(os.path.join(frontend_dir, "login.html"))

    @app.get("/admin")
    @app.get("/admin.html")
    async def read_admin():
        return FileResponse(os.path.join(frontend_dir, "admin.html"))

    print(f"[OK] Frontend directory: {frontend_dir}")

# ==================== Main ====================

if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("Starting Self-Agent MOCK Server")
    print("=" * 60)
    print("This is a mock server for frontend testing.")
    print("No database required!")
    print("")
    print("Test accounts:")
    print("  Admin: admin@selfagent.com / admin123")
    print("  User:  any@email.com / test123")
    print("")
    print("URLs:")
    print("  http://localhost:8000/        - Chat page")
    print("  http://localhost:8000/login   - Login page")
    print("  http://localhost:8000/admin   - Admin panel")
    print("=" * 60)

    uvicorn.run(app, host="0.0.0.0", port=8000)
