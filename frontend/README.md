# Self-Agent Web Frontend

Self-Agent 智能情绪支持系统的 Web 前端界面，完全按照 `main.py` 的方式调用后端 `SelfAgent`。

## 架构说明

前端通过 FastAPI 与后端 `SelfAgent` (CAMEL-AI) 直接通信：

```
前端 (JavaScript) → FastAPI (/api/chat) → SelfAgent.process_interaction() → CAMEL-AI
```

调用流程与 `main.py` 完全一致：
1. 创建 `UserInput(user_id, text)` 对象
2. 调用 `agent.process_interaction(user_input)`
3. 获取并返回响应

## 快速开始

### 1. 确保环境配置正确

检查 `.env` 文件包含必要的配置：

```bash
# 必需配置
OPENAI_API_KEY=sk-your-deepseek-key
OPENAI_API_BASE=https://api.deepseek.com
MODEL_NAME=deepseek-chat

# 可选配置
MODELSCOPE_API_KEY=ms-your-modelscope-key
```

### 2. 启动服务器

```bash
# 安装额外依赖（如果尚未安装）
pip install fastapi uvicorn python-multipart

# 启动 Web 服务器
python -m app.server
```

服务器将在 `http://localhost:8000` 启动。

启动日志示例：
```
============================================================
Starting Self-Agent Web Server
============================================================
Initializing Self-Agent with model: deepseek-chat
Self-Agent initialized successfully
✓ Agent initialized and ready
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 3. 访问前端

在浏览器中打开：`http://localhost:8000`

## API 端点

### POST /api/chat

处理文本聊天消息（完全按照 main.py 方式）

**请求：**
```json
{
  "user_id": "user_web_123",
  "text": "我今天感觉很焦虑"
}
```

**响应：**
```json
{
  "response": "我理解你现在的感受。让我来帮助你...",
  "success": true
}
```

### POST /api/chat/multimodal

处理多媒体消息（语音/图片）

**请求：**
```http
POST /api/chat/multimodal
Content-Type: multipart/form-data

user_id: user_web_123
text: 可选描述
file: [音频或图片文件]
```

**响应：**
```json
{
  "response": "我收到了你的文件...",
  "success": true
}
```

### GET /api/health

健康检查端点

**响应：**
```json
{
  "status": "ok",
  "service": "selfagent",
  "version": "2.0.0",
  "agent_initialized": true
}
```

## 前端功能

### 核心功能

- **实时对话**：与 AI 情绪伙伴实时交流
- **情绪识别**：自动检测情绪状态
- **DBT 技能推荐**：根据情绪推荐适合的心理技能
- **多模态输入**：支持文本、语音、图片输入
- **深色模式**：自动/手动切换明暗主题

### 交互组件

- **情绪快捷标签**：一键分享常见情绪
- **呼吸练习**：4-4-4-4 呼吸节奏引导
- **危机干预**：24 小时心理援助热线
- **情绪趋势图**：可视化情绪变化

## 文件结构

```
frontend/
├── index.html          # 主界面
├── js/
│   └── app.js         # 前端逻辑（连接 /api/chat）
└── README.md          # 本文档

app/
├── server.py          # FastAPI 服务器
│   ├── /api/chat      # 聊天端点
│   ├── /api/health    # 健康检查
│   └── /              # 静态文件服务
└── core/
    └── agent.py       # SelfAgent (被 server.py 调用)
```

## 技术实现

### 后端 (server.py)

```python
# 完全按照 main.py 的方式
from app.core.agent import SelfAgent
from app.models.data_models import UserInput

# 单例模式
_agent_instance: Optional[SelfAgent] = None

def get_agent() -> SelfAgent:
    global _agent_instance
    if _agent_instance is None:
        model_name = os.getenv("MODEL_NAME", "deepseek-chat")
        _agent_instance = SelfAgent(model_type=model_name)
    return _agent_instance

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    agent = get_agent()

    # 创建 UserInput（与 main.py 一致）
    user_input = UserInput(
        user_id=request.user_id,
        text=request.text
    )

    # 调用 process_interaction（与 main.py 一致）
    response = agent.process_interaction(user_input)

    return ChatResponse(response=response, success=True)
```

### 前端 (app.js)

```javascript
// 发送消息到后端
async function sendMessageToBackend(message) {
    const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            user_id: USER_ID,
            text: message
        })
    });

    const data = await response.json();

    if (data.success) {
        addMessageToUI('assistant', data.response);
    }
}
```

## 与 main.py 的对比

| main.py (CLI) | Web Frontend |
|---------------|--------------|
| `input("你: ")` | HTML input + JavaScript |
| `UserInput(user_id, text)` | `POST /api/chat {user_id, text}` |
| `agent.process_interaction(user_input)` | Server 调用 `agent.process_interaction()` |
| `print(f"Self-Agent: {response}")` | `addMessageToUI('assistant', response)` |
| 循环交互 | 单次请求/响应 |

## 常见问题

### Q: 启动时报错 "OPENAI_API_KEY not set"

确保 `.env` 文件中有 `OPENAI_API_KEY`：

```bash
OPENAI_API_KEY=sk-your-deepseek-key
```

### Q: 前端显示 "无法连接到服务器"

确保后端服务器已启动：

```bash
python -m app.server
```

检查 `http://localhost:8000/api/health` 是否返回正常。

### Q: Agent 响应很慢

这是正常的，因为需要：
1. 发送请求到 DeepSeek API
2. CAMEL-AI 框架处理
3. 可能调用工具（情绪识别、DBT 技能等）

### Q: 如何更换模型？

修改 `.env` 文件：

```bash
MODEL_NAME=deepseek-chat  # 或其他模型
```

重启服务器即可。

### Q: 可以在没有 API key 的情况下测试吗？

可以，但 agent 会返回错误。建议先获取 DeepSeek API key：

1. 访问 https://platform.deepseek.com
2. 注册账号
3. 创建 API Key
4. 添加到 `.env` 文件

## 开发建议

### 调试

1. **查看服务器日志**：控制台输出会显示所有请求和响应
2. **浏览器开发者工具**：F12 查看 Network 请求
3. **API 健康检查**：访问 `/api/health` 确认服务状态

### 扩展功能

可以添加的新功能：
- 用户认证（登录/注册）
- 聊天历史持久化
- 情绪数据导出
- 推送通知
- 语音合成（TTS）

### 生产部署

部署前需要：
1. 修改 CORS 配置（`allow_origins`）
2. 启用 HTTPS
3. 配置反向代理（Nginx）
4. 设置环境变量管理
5. 实现速率限制

## 设计特点

### UI/UX

- **Glassmorphism**：毛玻璃效果，现代柔和
- **Indigo + Pink**：专业且温暖的配色
- **响应式**：完美适配移动端和桌面端
- **深色模式**：减轻夜间使用眼睛疲劳

### 交互设计

- **打字动画**：模拟真实对话体验
- **实时反馈**：即时显示情绪状态
- **快捷操作**：一键分享情绪
- **危机按钮**：醒目的红色脉动按钮

## 许可证

本前端界面是 Self-Agent 项目的一部分。

---

**Made with ❤️ for Mental Health Support**
