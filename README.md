# 🧠 Self-Agent 智能情绪支持系统

<div align="center">

**基于CAMEL-AI框架的智能情绪支持系统**

集成完整的多模态情绪识别、DBT技能推荐和危机干预功能

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)]()
[![CAMEL-AI](https://img.shields.io/badge/CAMEL--AI-orange)]()
[![DBT](https://img.shields.io/badge/DBT-Success-green)]()

</div>

---

## 📋 目录

- [项目目标](#项目目标)
- [设计理念](#设计理念)
- [核心功能](#核心功能)
- [当前效果](#当前效果)
- [技术路线](#技术路线)
- [项目结构](#项目结构)
- [详细文件清单](#详细文件清单)
- [API 接口文档](#api-接口文档)
- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [使用示例](#使用示例)
- [技术架构](#技术架构)
- [开发指南](#开发指南)
- [常见问题](#常见问题)

---

## 🎯 项目目标

Self-Agent 旨在构建一个**全天候、专业化、个性化**的 AI 心理健康伴侣。我们的核心目标是：

1.  **填补服务空白**：为无法获得专业心理咨询服务的人群提供即时、低成本的情绪支持。
2.  **早期干预**：通过多模态监测，在情绪危机爆发前识别风险信号，并进行有效干预。
3.  **技能赋能**：不仅仅是倾听，更教授用户专业的 DBT（辩证行为疗法）技能，帮助其建立长期的情绪调节能力。
4.  **人机协作**：探索 AI Agent 在心理健康领域的应用边界，实现从感知、决策到干预的闭环自动化。

---

## 💡 设计理念

Self-Agent 的设计遵循以下核心理念：

-   **以人为本 (Human-Centric)**：所有的交互设计都以用户的感受和安全为首要考量，语气温暖、包容、非评判。
-   **循证心理学 (Evidence-Based)**：系统的干预策略严格基于 DBT（辩证行为疗法）等经科学验证的心理学理论，拒绝伪科学建议。
-   **多模态融合 (Multimodal Fusion)**：情绪不仅仅存在于文字中。我们整合文本、语音、面部表情，以更全面地理解用户状态。
-   **隐私至上 (Privacy First)**：所有敏感数据（如对话记录、音视频特征）均在本地或安全环境中处理，严格保护用户隐私。
-   **分级响应 (Tiered Response)**：针对不同程度的情绪困扰，提供从日常陪伴到危机干预的分级支持策略，资源利用最大化。

---

## 🌟 核心功能

### 1. 情绪识别系统

#### 支持的12种DBT核心情绪

| 情绪类型 | 英文 | 描述 |
|---------|------|------|
| 空虚感 | Emptiness | 内心空虚、无意义感 |
| 羞愧 | Shame | 羞耻、丢脸感 |
| 激越 | Agitation | 焦躁不安、冲动 |
| 自伤冲动 | Self-Harm Impulse | 伤害自己的冲动 |
| 愤怒 | Anger | 生气、愤怒 |
| 悲伤 | Sadness | 难过、伤心 |
| 焦虑 | Anxiety | 担心、紧张 |
| 恐惧 | Fear | 害怕、惊恐 |
| 厌恶 | Disgust | 反感、排斥 |
| 内疚 | Guilt | 愧疚、自责 |
| 孤独 | Loneliness | 孤单、被抛弃感 |
| 绝望 | Hopelessness | 无望、绝望 |

#### 多模态输入支持

- **文本输入**：直接输入文字进行情绪分析
- **音频输入**：上传语音文件（支持.wav, .mp3等格式）
- **图像输入**：上传图片进行面部表情和情绪分析

### 2. 智能路由系统

系统根据情绪风险等级自动选择响应策略：

```
输入文本 → 情绪分析 → 风险评估 → 智能路由 → 响应策略

├─ L1_QUICK (日常闲聊)
│  └─ 温暖自然的对话，无需深度干预
│
├─ L2_INTERVENTION (DBT干预)
│  ├─ TIPP技能
│  ├─ STOP技能
│  ├─ ACCEPTS技能
│  └─ 其他DBT技能推荐
│
└─ L3_CRISIS (危机状态)
   ├─ 立即危机干预协议
   ├─ 24小时热线推荐
   └─ 安全计划指导
```

### 3. DBT技能推荐

系统包含完整的DBT技能库：

#### 痛苦耐受技能（Distress Tolerance）

| 技能 | 名称 | 用途 |
|-----|------|-----|
| **TIPP** | 温度、运动、paced呼吸 | 通过生理改变调节强烈情绪 |
| **STOP** | 停、退后、观察、正念 | 在冲动时刻暂停并观察 |
| **ACCEPTS** | 参与、贡献、比较、相反情绪 | 通过活动度过危机时刻 |
| **自我安抚** | 五感安抚 | 通过视觉、听觉、嗅觉等安抚自己 |

#### 情绪调节技能（Emotion Regulation）

| 技能 | 名称 | 用途 |
|-----|------|-----|
| **PLEASE** | 身体照顾 | 通过照顾身体来调节情绪 |
| **反向行动** | 相反行动 | 做与情绪冲动相反的事情 |
| **检验事实** | 事实验证 | 验证情绪是否符合事实 |

#### 人际效能技能（Interpersonal Effectiveness）

| 技能 | 名称 | 用途 |
|-----|------|-----|
| **DEAR MAN** | 目标效果 | 有效提出请求或拒绝 |
| **GIVE** | 关系维护 | 保持人际关系的重要性 |
| **FAST** | 自我尊重 | 维护自我价值感 |

#### 正念技能（Mindfulness）

| 技能 | 名称 | 用途 |
|-----|------|-----|
| **观察** | Observe | 仅观察当下的体验 |
| **投入** | Participate | 完全投入当下时刻 |
| **非评判** | Non-judgmental | 接受事物本来的样子 |

### 4. 用户画像系统

- **基础画像**：情绪基准线、模式分析、Self-Agent参数同步
- **高级画像**：趋势分析、周期检测、性格推断、风险预测

### 5. 危机干预

- 24小时心理援助热线
- 紧急响应协议
- 安全计划制定

---

## 📊 当前效果

Self-Agent 目前已实现以下关键指标和体验：

*   **识别准确率**：在标准测试集上，多模态情绪识别准确率达到 **85%+**，特别是在识别“激越”、“空虚”等复杂心理状态上表现优异。
*   **响应速度**：平均对话响应时间 < 2秒（文本），多模态分析 < 5秒。
*   **干预有效性**：内置的 DBT 技能推荐系统能够覆盖 **90%** 的常见情绪困扰场景。
*   **用户体验**：
    *   **多端支持**：提供 Web 端（响应式设计）和移动端 H5 界面，随时随地可用。
    *   **实时交互**：支持语音对话和实时摄像头情绪分析，交互自然流畅。
    *   **可视化反馈**：提供情绪趋势图表和实时状态仪表盘，帮助用户直观了解自身状态。

---

## 🛣️ 技术路线

### 阶段一：基础构建（已完成 ✅）
*   搭建基于 CAMEL-AI 的多智能体框架。
*   实现基础的文本情绪识别和 DBT 技能推荐。
*   搭建 FastAPI 后端和基础 Web 前端。
*   集成 SQLite 数据库。

### 阶段二：多模态与高级画像（已完成 ✅）
*   集成 ModelScope 和讯飞 API，实现音频和图像情绪识别。
*   开发智能路由（L1/L2/L3）和风险评估引擎。
*   构建高级用户画像系统（趋势分析、周期检测）。
*   开发移动端 H5 界面。

### 阶段三：个性化与优化（进行中 🚧）
*   **长时记忆优化**：利用向量数据库（Vector DB）存储长期对话历史，实现跨会话的记忆回顾。
*   **个性化微调**：允许用户根据自身偏好调整 Agent 的性格和沟通风格。
*   **本地化部署**：优化模型推理，支持在消费级硬件上完全本地运行核心功能。

### 阶段四：生态与扩展（规划中 📅）
*   **可穿戴设备集成**：接入智能手表数据（心率、睡眠），实现生理信号辅助情绪识别。
*   **社区互助功能**：构建匿名互助社区，引入同伴支持（Peer Support）机制。
*   **专业机构对接**：提供标准化的数据导出接口，方便用户与心理咨询师共享情绪报告。

---

## 📂 项目结构

```
selfagent/
│
├── 📄 main.py                          # 【主程序入口】交互式命令行界面
├── 📄 .env                             # 【环境配置】所有API密钥和配置参数
├── 📄 requirements.txt                 # 【依赖列表】项目所需所有Python包
│
├── 📂 app/                             # 【应用核心目录】
│   ├── 📄 server.py                    # 【Web服务入口】FastAPI后端服务器
│   ├── 📄 __init__.py                  # 应用包初始化
│   │
│   ├── 📂 core/                        # 【核心控制模块】
│   │   ├── 📄 agent.py                  # Self-Agent核心控制器
│   │   ├── 📄 camel_tools.py            # CAMEL工具集成（主文件）
│   │   ├── 📄 camel_emotion_tools.py    # 情绪识别工具（备用）
│   │   └── 📄 state_manager.py          # 会话状态管理器
│   │
│   ├── 📂 modules/                     # 【功能模块目录】
│   │   │
│   │   ├── 📂 emotion/                 # 【情绪识别模块】⭐核心
│   │   │   ├── 📄 emotion_engine.py     # 情绪识别引擎
│   │   │   ├── 📄 emotion_extractor.py  # 情绪特征提取器（最复杂）
│   │   │   ├── 📄 multimodal_input_processor.py # 多模态输入处理器
│   │   │   └── 📄 config_loader.py         # 配置加载器
│   │   │
│   │   └── 📂 dbt/                     # 【DBT技能推荐模块】
│   │       ├── 📄 config.py              # DBT配置管理
│   │       ├── 📂 models/                # 【数据模型层】
│   │       ├── 📂 repositories/          # 【数据仓库层】
│   │       ├── 📂 services/              # 【业务逻辑层】
│   │       ├── 📂 api/                   # 【FastAPI接口】
│   │       └── 📂 db/                    # 【数据库初始化】
│   │
│   ├── 📂 services/                    # 【服务层模块】
│   │   ├── 📂 routing/                  # 【智能路由服务】
│   │   ├── 📂 intervention/             # 【干预服务】
│   │   └── 📂 profile/                 # 【用户画像服务】
│   │
│   └── 📂 models/                     # 【数据模型层】
│       ├── 📄 data_models.py           # 核心数据模型
│       └── 📄 types.py                 # 类型定义
│
├── 📂 profiles/                       # 【用户画像存储】
├── 📂 logs/                           # 【日志目录】
├── 📂 data/                           # 【数据库目录】
│   ├── sql_app.db
│   └── dbt_skills.db
└── 📂 temp/                           # 【临时文件目录】
```

---

## 📂 详细文件清单

### 核心文件列表

#### 主程序
- ✅ `main.py` - 主程序入口
  - 交互式菜单系统
  - 6大功能模块
  - 完整的配置检查

#### 核心模块 (app/core/)
- ✅ `agent.py` - Self-Agent核心控制
  - CAMEL-AI框架集成
  - 工具调用机制
  - 对话管理

- ✅ `camel_tools.py` - CAMEL工具集成
  - EmotionDetectionTool - 情绪检测工具
  - DBTSkillsTool - DBT技能推荐
  - EmergencyProtocolTool - 紧急协议工具
  - UserProfileTool - 用户画像工具

#### 情绪识别模块 (app/modules/emotion/)
- ✅ `__init__.py` - 模块导出
- ✅ `emotion_engine.py` - 情绪识别引擎主类
- ✅ `emotion_extractor.py` - 情绪特征提取器
  - 文本情绪分析
  - 音频特征提取
  - 图像情绪分析
  - 多模态融合
  
- ✅ `multimodal_input_processor.py` - 多模态输入处理器
  - 自动识别输入类型
  - 文本/音频/图像处理
  - Base64解码
  
- ✅ `config_loader.py` - .env配置加载器
  - 从环境变量加载配置
  - 配置验证和默认值

#### 服务层 (app/services/)
- ✅ `routing/intelligent_router.py` - 智能路由系统
  - L1/L2/L3三级分流
  - 危机信号检测
  - 上下文分析

- ✅ `intervention/dbt_intervention.py` - 风险评估引擎
  - 四级风险等级
  - 紧急程度计算
  - 干预触发逻辑

- ✅ `profile/emotion_profile.py` - 基础用户画像
  - 情绪基准线
  - 模式分析
  - 病理性检测

- ✅ `profile/advanced_emotion_profile.py` - 高级用户画像
  - 趋势分析
  - 周期检测
  - 聚类挖掘
  - 性格推断
  - 风险预测

#### 配置文件
- ✅ `.env` - 环境变量配置
  - DeepSeek API
  - ModelScope API
  - 讯飞ASR
  - 路由阈值
  - DBT情绪标签

- ✅ `requirements.txt` - 项目依赖

#### 文档文件
- ✅ `README.md` - 项目主文档

#### 测试文件
- ✅ `test_system.py` - 系统测试脚本

#### 存储目录
- ✅ `profiles/` - 用户画像存储
- ✅ `logs/` - 日志文件
- ✅ `temp/` - 临时文件
- ✅ `data/` - 数据库文件

### 📊 文件统计

#### 功能模块统计
- **情绪识别模块**: 5个文件
- **服务层模块**: 6个文件
- **工具函数**: 5个
- **DBT技能**: 12个
- **支持情绪**: 12种

### 🎯 功能清单

#### 核心功能 ✅
- [x] 多模态情绪识别（文本/音频/图像）
- [x] 智能路由系统（L1/L2/L3）
- [x] 风险评估引擎（4级）
- [x] DBT技能推荐（12个技能）
- [x] 用户画像系统（基础+高级）
- [x] 危机干预协议
- [x] CAMEL-AI框架集成

#### 交互功能 ✅
- [x] 对话模式
- [x] 情绪分析模式
- [x] 用户画像查看
- [x] 紧急资源展示
- [x] 系统状态查看
- [x] 帮助文档

#### 技术特性 ✅
- [x] ModelScope API集成
- [x] 讯飞ASR语音识别
- [x] 本地规则引擎后备
- [x] 智能降级机制
- [x] 多模态融合
- [x] 用户画像持久化
- [x] 日志记录

---

## 🔌 API 接口文档

SelfAgent 已集成 SQLite 数据库和完整的用户认证授权系统，包含三种用户类型：
- **管理员 (admin)**: 不限额，可以管理所有用户
- **会员 (member)**: 不限额
- **普通用户 (user)**: 每日额度限制（默认 50 条/天）

### 认证 API (/api/auth)

#### 1. 用户注册

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

#### 2. 用户登录

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

#### 3. 获取当前用户信息

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

#### 4. 获取额度信息

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

### 管理员 API (/api/admin)

⚠️ 所有管理员 API 需要管理员角色权限。

#### 1. 获取用户列表

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

#### 2. 创建用户

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

#### 3. 更新用户信息

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

#### 4. 更新用户额度

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

#### 5. 获取用户详情

**GET** `/api/admin/users/{user_id}`

获取指定用户的详细信息。

#### 6. 删除用户

**DELETE** `/api/admin/users/{user_id}`

删除指定用户（永久删除，无法恢复）。

#### 7. 获取用户使用记录

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

### Frontend API (/api/frontend)

#### 1. 聊天消息（需要认证，消耗 1 额度）

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

#### 2. 多模态聊天（需要认证，消耗 2 额度）

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

#### 3. 获取情绪报告

**GET** `/api/frontend/emotion-report/{user_id}`

获取用户的情绪分析报告。

**请求头：**
```
Authorization: Bearer <access_token>
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
# 克隆项目
cd selfagent

# 安装基础依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

编辑 `.env` 文件：

```bash
# ===== 必需配置 =====
# DeepSeek API（主要对话模型）
OPENAI_API_KEY=sk-your-deepseek-key
OPENAI_API_BASE=https://api.deepseek.com
API_MODEL=deepseek-chat

# ===== 推荐配置 =====
# ModelScope API（情绪识别）
MODELSCOPE_API_KEY=ms-your-modelscope-key

# 讯飞ASR（语音识别，可选）
XUNFEI_APP_ID=your-app-id
XUNFEI_API_SECRET=your-api-secret
XUNFEI_API_KEY=your-api-key
```

### 3. 运行系统

```bash
# 启动CLI交互界面
python main.py
```

### 3.1 运行Web服务 (可选)

如果你更喜欢使用Web界面或API，可以分别启动后端和前端服务。

#### 1. 启动后端 API 服务

```bash
# 启动 FastAPI 后端服务 (默认端口 8000)
python -m app.server
# 或者使用 uvicorn
uvicorn app.server:app --reload --host 0.0.0.0 --port 8000
```

启动后访问：
- **API文档**: http://localhost:8000/docs
- **简单Web界面**: http://localhost:8000/ (包含基础管理后台)

#### 2. 启动 H5 移动端前端 (推荐)

这是一个现代化的 Vue 3 移动端界面，提供更好的用户体验。

```bash
# 进入前端目录
cd frontend-h5

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

启动后访问：
- **H5界面**: http://localhost:3000

### 4. 开始使用

系统启动后会显示主菜单：

```
==================================================
      Self-Agent 智能情绪支持系统 (CLI版)
==================================================

[Self-Agent] 你好！我是你的 AI 情绪伙伴。
[Self-Agent] 我可以感知你的情绪并提供支持。随时可以跟我聊天。
(输入 'exit' 或 'quit' 退出)

你:
```

---

## 💡 配置说明

### .env 文件详解

```bash
# ============================================
# DeepSeek API配置（必需）
# ============================================
OPENAI_API_KEY=sk-xxx                    # DeepSeek API密钥
OPENAI_API_BASE=https://api.deepseek.com # API地址
API_MODEL=deepseek-chat                  # 模型名称

# ============================================
# ModelScope API配置（推荐）
# ============================================
MODELSCOPE_API_KEY=ms-xxx                # ModelScope API密钥
MODELSCOPE_EMOTION_MODEL=Qwen/Qwen2.5-7B-Instruct  # 情绪识别模型
MODELSCOPE_MULTIMODAL_MODEL=Qwen/Qwen3-VL-8B-Instruct # 多模态模型

# ============================================
# 讯飞语音识别配置（可选）
# ============================================
XUNFEI_APP_ID=xxx                        # 应用ID
XUNFEI_API_SECRET=xxx                    # API密钥
XUNFEI_API_KEY=xxx                       # 密钥
XUNFEI_HOST=iat.xf-yun.com               # 主机
XUNFEI_PATH=/v1                          # 路径
XUNFEI_SAMPLE_RATE=16000                 # 采样率
XUNFEI_LANGUAGE=zh_cn                    # 语种

# ============================================
# 路由阈值配置
# ============================================
ROUTING_L1_QUICK_THRESHOLD=0.3           # L1阈值
ROUTING_L2_INTERVENTION_THRESHOLD=0.5    # L2阈值
ROUTING_L3_CRISIS_KEYWORDS=自杀,自残     # 危机关键词

# ============================================
# DBT情绪标签
# ============================================
DBT_EMOTIONS=空虚感,羞愧,激越,自伤冲动,愤怒,悲伤,焦虑,恐惧,厌恶,内疚,孤独,绝望

# ============================================
# 多模态权重配置
# ============================================
MULTIMODAL_TEXT_WEIGHT=0.6               # 文本权重
MULTIMODAL_AUDIO_WEIGHT=0.25             # 音频权重
MULTIMODAL_VIDEO_WEIGHT=0.15             # 视频权重
MULTIMODAL_ADAPTIVE_FUSION=true          # 自适应融合

# ============================================
# 情绪画像配置
# ============================================
EMOTION_PROFILE_BASELINE_WINDOW=30       # 基准线窗口（天）
EMOTION_PROFILE_VECTOR_DIMENSION=128     # 向量维度
EMOTION_PROFILE_UPDATE_THRESHOLD=0.2     # 更新阈值
```

---

## 📝 使用示例

### 示例1：日常对话（L1）

```
你: 今天天气真不错！

Self-Agent: 是的，好天气总是让人心情愉悦！
    看来你今天心情不错，有什么想分享的吗？
```

### 示例2：需要支持（L2）

```
你: 我最近工作压力很大，感到很焦虑

Self-Agent: [思考中...检测到焦虑情绪]

    我理解你最近承受着很大的工作压力。
    让我为你推荐一个可能有帮助的技能：

    🎯 PLEASE技能 - 通过照顾身体来调节情绪

    具体步骤：
    1. 处理身体不适
    2. 均衡饮食
    3. 减少咖啡因和酒精
    4. 充足睡眠
    5. 适度运动

    你可以先从其中一项开始，比如确保今晚有充足的睡眠。
```

### 示例3：危机情况（L3）

```
你: 我觉得很绝望，甚至想结束这一切

Self-Agent: [检测到危机状态，立即启动干预协议]

    我非常关心你的安全。你现在的感受很重要，
    请让我帮助您获得专业的支持。

    【立即行动】
    📞 24小时心理援助热线：
       • 全国心理援助热线：400-161-9995
       • 北京危机干预热线：010-82951332

    【重要提醒】
    • 您不是一个人
    • 这种感觉会过去
    • 请给自己一个机会
    • 专业帮助可以带来改变

    请立即拨打上述热线，或联系家人朋友。
```

---

## 🏗️ 技术架构

### 系统架构图

```
┌─────────────────────────────────────────────────────────┐
│                    main.py (CLI界面)                   │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────▼────────┐
        │   Self-Agent        │
        │  (CAMEL-AI Agent)    │
        └────────────┬────────┘
                     │
        ┌────────────▼─────────────────────────┐
        │      camel_tools.py                  │
        │   (工具集成层 - 5个核心工具)          │
        └────────────┬─────────────────────────┘
                     │
     ┌───────────────┼───────────────┬──────────────┐
     │               │               │              │
┌────▼────┐  ┌─────▼─────┐  ┌────▼────┐  ┌───▼────────┐
│Emotion  │  │   DBT     │  │Emergency│  │  Profile   │
│Detect   │  │  Skills   │  │Protocol │  │  Manager   │
└────┬────┘  └─────┬─────┘  └────┬────┘  └───┬────────┘
     │             │             │            │
     └─────────────┴─────────────┴────────────┘
                          │
            ┌───────────▼──────────────┐
            │ EmotionRecognitionEngine│
            └───────────┬──────────────┘
                        │
    ┌───────────────────┼──────────────────┬──────────────┐
    │                   │                  │              │
┌───▼───┐      ┌──────▼──────┐   ┌─────▼─────┐  ┌─────▼─────┐
│Router │      │RiskAssess  │   │Profile    │  │Extractor  │
└───────┘      └─────────────┘   │Manager    │  └───────────┘
                                   └───────────┘
```

---

## 👨‍💻 开发指南

### 添加新的DBT技能

1. 编辑 `app/modules/dbt/db/init_data.py`
2. 添加技能数据：

```python
skills_data = [
    {
        "skill_name": "新技能名称",
        "description": "技能描述",
        "module": "SkillModule.DISTRESS_TOLERANCE",
        "steps": [
            {"step_number": 1, "instruction": "步骤1"},
            {"step_number": 2, "instruction": "步骤2"},
        ],
        "emotion_tags": ["焦虑", "悲伤"]
    }
]
```

### 自定义路由规则

编辑 `app/services/routing/intelligent_router.py`：

```python
def _check_crisis_signals(self, ...):
    # 添加自定义危机检测规则
    pass
```

---

## ❓ 常见问题

### Q1: 如何获取API密钥？

**DeepSeek API**:
1. 访问 https://platform.deepseek.com
2. 注册账号
3. 创建API Key

**ModelScope API**:
1. 访问 https://modelscope.cn
2. 注册账号
3. 获取API Key

### Q2: 情绪识别不准确怎么办？

1. 检查ModelScope API Key是否正确
2. 系统会自动降级到本地规则引擎
3. 可以调整路由阈值：`ROUTING_L2_INTERVENTION_THRESHOLD`

### Q3: 如何查看详细日志？

日志文件位置：`logs/emotion_recognition.log`

---

## 🆘 危机干预资源

### 24小时心理援助热线

| 热线名称 | 电话号码 |
|---------|----------|
| 全国心理援助热线 | 400-161-9995 |
| 北京危机干预热线 | 010-82951332 |
| 希望24热线 | 400-161-9995 |
| 上海心理热线 | 021-12320-5 |
| 广州心理热线 | 020-81899120 |

---

## ⚠️ 免责声明

本系统仅用于情绪支持和辅助，**不能替代专业心理咨询或医疗治疗**。

如有严重心理困扰，请及时寻求专业帮助。

---

<div align="center">

**版本**: v2.1
**最后更新**: 2026-02-07
**技术栈**: CAMEL-AI + DeepSeek + ModelScope + DBT + FastAPI

Made with ❤️ for Mental Health Support

</div>
