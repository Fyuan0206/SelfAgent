# SelfAgent PostgreSQL 用户系统 API 文档

## 概述

SelfAgent 已集成 PostgreSQL 数据库和完整的用户认证授权系统，包含三种用户类型：
- **管理员 (admin)**: 不限额，可以管理所有用户
- **会员 (member)**: 不限额
- **普通用户 (user)**: 每日额度限制（默认 50 条/天）

## 快速开始

### 1. 启动数据库

```bash
docker-compose up -d
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env` 并配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，设置必要的环境变量。

### 4. 初始化数据库

```bash
python app/core/database.py
```

### 5. 启动服务器

```bash
./start.sh
```

或手动启动：

```bash
uvicorn app.server:app --host 0.0.0.0 --port 8000 --reload
```

服务器将在 http://localhost:8000 启动

## 默认账号

系统会自动创建默认管理员账号：
- 邮箱: `admin@selfagent.com`
- 密码: `admin123`

**⚠️ 重要：生产环境请立即修改默认密码！**

## API 文档

交互式 API 文档：http://localhost:8000/docs

---

## 认证 API (/api/auth)

### 1. 用户注册

**POST** `/api/auth/register`

注册新用户（默认为普通用户角色，每日额度 50 条）。

**请求体：**
```json
{
  "email": "user@example.com",
  "username": "张三",
  "password": "password123"
}
```

**响应：**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "张三",
    "role": "user",
    "is_active": true,
    "is_verified": false,
    "created_at": "2025-01-25T10:00:00",
    "last_login": null
  }
}
```

---

### 2. 用户登录

**POST** `/api/auth/login`

使用邮箱和密码登录。

**请求体：**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**响应：**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "张三",
    "role": "user",
    "is_active": true,
    "is_verified": true,
    "created_at": "2025-01-25T10:00:00",
    "last_login": "2025-01-25T12:00:00"
  }
}
```

---

### 3. 获取当前用户信息

**GET** `/api/auth/me`

获取当前登录用户的详细信息（包含额度）。

**请求头：**
```
Authorization: Bearer <access_token>
```

**响应：**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "张三",
  "role": "user",
  "is_active": true,
  "is_verified": true,
  "created_at": "2025-01-25T10:00:00",
  "last_login": "2025-01-25T12:00:00",
  "quota": {
    "daily_quota": 50,
    "daily_used": 5,
    "remaining_quota": 45,
    "quota_date": "2025-01-25"
  }
}
```

---

### 4. 获取额度信息

**GET** `/api/auth/quota`

获取当前用户的额度详情。

**请求头：**
```
Authorization: Bearer <access_token>
```

**响应：**
```json
{
  "daily_quota": 50,
  "daily_used": 5,
  "remaining_quota": 45,
  "has_quota": true,
  "quota_date": "2025-01-25",
  "is_unlimited": false
}
```

---

## 管理员 API (/api/admin)

⚠️ 所有管理员 API 需要管理员角色权限。

### 1. 获取用户列表

**GET** `/api/admin/users`

获取所有用户的列表（支持分页和筛选）。

**请求头：**
```
Authorization: Bearer <admin_access_token>
```

**查询参数：**
- `page`: 页码（默认 1）
- `page_size`: 每页数量（默认 20，最大 100）
- `role`: 按角色筛选 (admin/member/user)
- `is_active`: 按状态筛选 (true/false)
- `search`: 搜索邮箱或用户名

**示例请求：**
```
GET /api/admin/users?page=1&page_size=20&role=user
```

**响应：**
```json
{
  "total": 100,
  "page": 1,
  "page_size": 20,
  "users": [
    {
      "id": 1,
      "email": "user@example.com",
      "username": "张三",
      "role": "user",
      "is_active": true,
      "is_verified": true,
      "created_at": "2025-01-25T10:00:00",
      "last_login": "2025-01-25T12:00:00",
      "quota": {
        "daily_quota": 50,
        "daily_used": 5,
        "remaining_quota": 45,
        "quota_date": "2025-01-25"
      }
    }
  ]
}
```

---

### 2. 创建用户

**POST** `/api/admin/users`

管理员创建新用户。

**请求头：**
```
Authorization: Bearer <admin_access_token>
```

**请求体：**
```json
{
  "email": "newuser@example.com",
  "username": "李四",
  "password": "password123",
  "role": "member",
  "daily_quota": -1
}
```

**role 可选值：**
- `admin`: 管理员
- `member`: 会员（无限额度）
- `user`: 普通用户

**daily_quota:**
- `-1`: 无限额度（管理员和会员）
- `>=0`: 每日额度限制（普通用户）

---

### 3. 更新用户信息

**PUT** `/api/admin/users/{user_id}`

更新用户信息。

**请求体：**
```json
{
  "username": "李四（更新）",
  "role": "member",
  "is_active": true,
  "is_verified": true
}
```

---

### 4. 更新用户额度

**PUT** `/api/admin/users/{user_id}/quota`

更新用户的每日额度。

**请求体：**
```json
{
  "daily_quota": 100
}
```

或设置为无限：

```json
{
  "daily_quota": -1
}
```

---

### 5. 获取用户详情

**GET** `/api/admin/users/{user_id}`

获取指定用户的详细信息。

---

### 6. 删除用户

**DELETE** `/api/admin/users/{user_id}`

删除指定用户（永久删除，无法恢复）。

---

### 7. 获取用户使用记录

**GET** `/api/admin/users/{user_id}/usage`

获取指定用户的使用记录。

**查询参数：**
- `limit`: 返回记录数量（默认 50，最大 200）

**响应：**
```json
[
  {
    "id": 1,
    "action_type": "chat",
    "resource_cost": 1,
    "details": "API call: chat",
    "created_at": "2025-01-25T12:00:00"
  },
  {
    "id": 2,
    "action_type": "emotion_analysis",
    "resource_cost": 1,
    "details": "API call: emotion_analysis",
    "created_at": "2025-01-25T12:01:00"
  }
]
```

---

## Frontend API (/api/frontend)

### 1. 聊天消息（需要认证，消耗 1 额度）

**POST** `/api/frontend/chat`

发送聊天消息。

**请求头：**
```
Authorization: Bearer <access_token>
```

**请求体：**
```json
{
  "text": "你好，我感到很焦虑"
}
```

**响应：**
```json
{
  "response": "你好！我理解你的感受...",
  "emotion_detected": "焦虑",
  "risk_level": "L2",
  "dbt_skills": ["TIPP", "STOP"],
  "is_crisis": false
}
```

**额度不足响应：**
```json
{
  "detail": {
    "error": "quota_exceeded",
    "message": "今日额度已用完，请明天再试或升级为会员",
    "daily_quota": 50,
    "daily_used": 50,
    "remaining_quota": 0
  }
}
```

---

### 2. 多模态聊天（需要认证，消耗 2 额度）

**POST** `/api/frontend/chat/multimodal`

发送语音或图片消息。

**请求头：**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

**表单数据：**
- `text`: 可选文本描述
- `file`: 音频或图片文件
- `file_type`: 文件类型（"audio" 或 "image"）

---

### 3. 获取情绪报告

**GET** `/api/frontend/emotion-report/{user_id}`

获取用户的情绪分析报告。

**请求头：**
```
Authorization: Bearer <access_token>
```

---

## 使用示例（Python）

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. 用户注册
response = requests.post(f"{BASE_URL}/api/auth/register", json={
    "email": "test@example.com",
    "username": "测试用户",
    "password": "password123"
})
data = response.json()
token = data["access_token"]

# 2. 发送聊天消息
headers = {"Authorization": f"Bearer {token}"}
response = requests.post(
    f"{BASE_URL}/api/frontend/chat",
    json={"text": "你好"},
    headers=headers
)
print(response.json())

# 3. 查看额度
response = requests.get(
    f"{BASE_URL}/api/auth/quota",
    headers=headers
)
print(response.json())
```

---

## 使用示例（cURL）

```bash
# 1. 用户注册
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"测试用户","password":"password123"}'

# 2. 用户登录
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# 3. 发送聊天消息（替换 YOUR_TOKEN）
curl -X POST "http://localhost:8000/api/frontend/chat" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"text":"你好"}'

# 4. 查看额度（替换 YOUR_TOKEN）
curl -X GET "http://localhost:8000/api/auth/quota" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 使用示例（管理员 API）

```bash
# 1. 管理员登录
TOKEN=$(curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@selfagent.com","password":"admin123"}' \
  | jq -r '.access_token')

# 2. 获取用户列表
curl -X GET "http://localhost:8000/api/admin/users" \
  -H "Authorization: Bearer $TOKEN"

# 3. 创建会员用户
curl -X POST "http://localhost:8000/api/admin/users" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email":"vip@example.com",
    "username":"VIP用户",
    "password":"vip123",
    "role":"member",
    "daily_quota":-1
  }'

# 4. 更新用户额度
curl -X PUT "http://localhost:8000/api/admin/users/2/quota" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"daily_quota":100}'
```

---

## 数据库表结构

### users（用户表）
- `id`: 主键
- `email`: 邮箱（唯一）
- `username`: 用户名
- `hashed_password`: 密码哈希
- `role`: 角色 (admin/member/user)
- `is_active`: 是否激活
- `is_verified`: 是否验证
- `created_at`: 创建时间
- `updated_at`: 更新时间
- `last_login`: 最后登录时间

### user_quotas（用户额度表）
- `id`: 主键
- `user_id`: 用户 ID（外键）
- `daily_quota`: 每日额度（-1 表示无限）
- `daily_used`: 今日已用额度
- `quota_date`: 额度日期
- `created_at`: 创建时间
- `updated_at`: 更新时间

### usage_records（使用记录表）
- `id`: 主键
- `user_id`: 用户 ID（外键）
- `action_type`: 操作类型
- `resource_cost`: 消耗的额度
- `details`: 详细信息
- `created_at`: 创建时间

---

## 常见问题

### 1. 额度何时重置？

每日额度在 UTC 时间 00:00 自动重置。

### 2. 如何设置无限额度？

将 `daily_quota` 设置为 `-1` 即可。

### 3. 管理员和会员有额度限制吗？

没有。管理员和会员的角色不受额度限制。

### 4. Token 有效期多久？

Access Token 有效期为 24 小时（可在环境变量中配置）。

---

## 生产环境部署建议

1. **修改默认管理员密码**
2. **使用强密钥** 更新 `.env` 中的 `SECRET_KEY`
3. **配置 HTTPS**
4. **限制 CORS 来源**
5. **定期备份数据库**
6. **监控额度使用情况**
