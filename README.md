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

- [项目简介](#项目简介)
- [核心功能](#核心功能)
- [项目结构](#项目结构)
- [模块说明](#模块说明)
- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [使用示例](#使用示例)
- [技术架构](#技术架构)
- [开发指南](#开发指南)
- [常见问题](#常见问题)

---

## 🎯 项目简介

Self-Agent是一个基于**CAMEL-AI框架**开发的智能情绪支持系统，通过整合**多模态情绪识别**、**DBT（辩证行为疗法）技能推荐**和**危机干预协议**，为用户提供专业的心理健康支持。

### 主要特点

- ✅ **多模态情绪识别**：支持文本、音频、图像三种输入方式
- ✅ **智能路由系统**：根据风险等级自动分流（L1/L2/L3）
- ✅ **DBT技能库**：包含12个专业心理健康技能
- ✅ **用户画像系统**：长期追踪情绪模式和趋势分析
- ✅ **危机干预机制**：24小时心理援助热线和紧急协议
- ✅ **CAMEL-AI集成**：优雅的工具调用机制和对话管理

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

## 📁 项目结构

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
│   │   │   └── 功能：CAMEL-AI框架集成、对话管理、工具调度
│   │   │
│   │   ├── 📄 camel_tools.py            # CAMEL工具集成（主文件）
│   │   │   ├── EmotionDetectionTool     # 情绪检测工具
│   │   │   ├── DBTSkillsTool           # DBT技能推荐工具
│   │   │   ├── EmergencyProtocolTool    # 紧急协议工具
│   │   │   └── UserProfileTool         # 用户画像工具
│   │   │   └── 功能：将所有功能封装为CAMEL可调用工具
│   │   │
│   │   ├── 📄 camel_emotion_tools.py    # 情绪识别工具（备用）
│   │   └── 📄 state_manager.py          # 会话状态管理器
│   │       └── 功能：保存和恢复对话历史、风险等级
│   │
│   ├── 📂 modules/                     # 【功能模块目录】
│   │   │
│   │   ├── 📂 emotion/                 # 【情绪识别模块】⭐核心
│   │   │   ├── 📄 __init__.py           # 模块导出声明
│   │   │   │
│   │   │   ├── 📄 emotion_engine.py     # 情绪识别引擎
│   │   │   │   ├── EmotionRecognitionEngine类
│   │   │   │   ├── 功能：整合所有子模块，提供统一接口
│   │   │   │   └── 主要方法：
│   │   │   │       ├─ analyze()        # 完整情绪分析流程
│   │   │   │       ├─ get_profile()    # 获取用户画像
│   │   │   │       └─ generate_profile_report() # 生成详细报告
│   │   │   │
│   │   │   ├── 📄 emotion_extractor.py  # 情绪特征提取器（最复杂）
│   │   │   │   ├── EmotionExtractor类
│   │   │   │   ├── 功能：提取文本/音频/图像的情绪特征
│   │   │   │   └── 主要方法：
│   │   │   │       ├─ extract()                 # 统一提取接口
│   │   │   │       ├─ extract_text_emotion()    # 文本情绪分析
│   │   │   │       ├─ extract_audio_features()  # 音频特征提取
│   │   │   │       ├─ extract_video_features()  # 图像情绪分析
│   │   │   │       ├─ transcribe_audio()        # 语音识别（ASR）
│   │   │   │       └─ multimodal_fusion()       # 多模态融合
│   │   │   │
│   │   │   ├── 📄 multimodal_input_processor.py # 多模态输入处理器
│   │   │   │   ├── MultimodalInputProcessor类
│   │   │   │   ├── 功能：自动识别输入类型并路由处理
│   │   │   │   └── 支持类型：TEXT, AUDIO, IMAGE, VIDEO
│   │   │   │
│   │   │   └── 📄 config_loader.py         # 配置加载器
│   │   │       ├── EmotionConfigLoader类
│   │   │       └── 功能：从.env加载所有配置参数
│   │   │
│   │   └── 📂 dbt/                     # 【DBT技能推荐模块】
│   │       ├── 📄 config.py              # DBT配置管理
│   │       │   ├── Settings类
│   │       │   └── 功能：从YAML和环境变量加载配置
│   │       │
│   │       ├── 📂 models/                # 【数据模型层】
│   │       │   ├── database.py           # SQLAlchemy数据模型
│   │       │   │   ├── Skill类          # 技能实体
│   │       │   │   ├── SkillStep类      # 技能步骤
│   │       │   │   └── EmotionTag类     # 情绪标签
│   │       │   │
│   │       │   ├── schemas.py            # Pydantic请求/响应模型
│   │       │   │   ├── RecommendRequest # 推荐请求
│   │       │   │   ├── EmotionInput     # 情绪输入
│   │       │   │   └── TriggerSignals   # 触发信号
│   │       │   │
│   │       │   └── enums.py              # 枚举类型定义
│   │       │       ├── RiskLevel        # 风险等级枚举
│   │       │       ├── SkillModule      # 技能模块枚举
│   │       │       └── EmotionCategory   # 情绪类别枚举
│   │       │
│   │       ├── 📂 repositories/          # 【数据仓库层】
│   │       │   └── skill_repository.py   # 技能数据访问
│   │       │       ├── SkillRepository类
│   │       │       └── 功能：查询、匹配DBT技能
│   │       │
│   │       ├── 📂 services/              # 【业务逻辑层】
│   │       │   ├── recommendation_engine.py # 推荐引擎
│   │       │   │   ├── RecommendationEngine类
│   │       │   │   ├── 功能：根据情绪推荐最合适的DBT技能
│   │       │   │   └── 核心算法：技能匹配、LLM增强
│   │       │   │
│   │       │   ├── skill_matcher.py      # 技能匹配器
│   │       │   │   └── 功能：计算技能与情绪的匹配度
│   │       │   │
│   │       │   └── llm_service.py        # LLM增强服务
│   │       │       ├── LLMService类
│   │       │       └── 功能：使用LLM生成技能指导
│   │       │
│   │       ├── 📂 api/                   # 【FastAPI接口】
│   │       │   ├── routes.py              # 主路由
│   │       │   └── admin_routes.py        # 管理路由
│   │       │
│   │       └── 📂 db/                    # 【数据库初始化】
│   │           ├── init_data.py           # 初始化技能数据
│   │           └── session.py             # 数据库会话管理
│   │
│   ├── 📂 services/                    # 【服务层模块】
│   │   ├── 📄 __init__.py               # 服务层导出
│   │   │
│   │   ├── 📂 routing/                  # 【智能路由服务】
│   │   │   ├── 📄 __init__.py
│   │   │   └── 📄 intelligent_router.py  # 智能路由器
│   │   │       ├── IntelligentRouter类
│   │   │       ├── RouteLevel枚举（L1/L2/L3）
│   │   │       └── 功能：根据情绪特征决定路由级别
│   │   │
│   │   ├── 📂 intervention/             # 【干预服务】
│   │   │   ├── 📄 __init__.py
│   │   │   └── 📄 dbt_intervention.py     # 风险评估引擎
│   │   │       ├── RiskAssessmentEngine类
│   │   │       ├── RiskLevel枚举（LOW/MEDIUM/HIGH/CRITICAL）
│   │   │       └── 功能：评估风险等级和触发干预
│   │   │
│   │   └── 📂 profile/                 # 【用户画像服务】
│   │       ├── 📄 __init__.py
│   │       │
│   │       ├── 📄 emotion_profile.py     # 基础画像系统
│   │       │   ├── EmotionProfileManager类
│   │       │   ├── EmotionProfile数据类
│   │       │   └── 功能：情绪基准线、模式分析、Self-Agent同步
│   │       │
│   │       └── 📄 advanced_emotion_profile.py # 高级画像系统
│   │           ├── AdvancedEmotionProfileManager类
│   │           ├── EmotionTrend类（趋势）
│   │           ├── EmotionCycle类（周期）
│   │           ├── EmotionCluster类（聚类）
│   │           ├── PersonalityProfile类（性格）
│   │           ├── RiskPrediction类（风险预测）
│   │           └── 功能：深度分析、趋势预测、性格推断
│   │
│   └── 📂 models/                     # 【数据模型层】
│       ├── 📄 data_models.py           # 核心数据模型
│       │   ├── UserInput               # 用户输入
│       │   ├── EmotionOutput           # 情绪输出
│       │   ├── DBTRecommendation       # DBT推荐结果
│       │   └── AgentState              # Agent状态
│       │
│       └── 📄 types.py                 # 类型定义
│           ├── RiskLevel               # 风险等级
│           ├── EmotionType             # 情绪类型
│           └── SkillModule             # 技能模块
│
├── 📂 profiles/                       # 【用户画像存储】
│   └── *.json                          # 各用户的情绪画像数据
│
├── 📂 logs/                           # 【日志目录】
│   └── emotion_recognition.log        # 情绪识别日志
│
└── 📂 temp/                           # 【临时文件目录】
    └── （音频/图像临时处理文件）
```

---

## 🔧 模块详细说明

### 📂 core/ - 核心控制模块

#### agent.py
```python
class SelfAgent:
    """
    Self-Agent核心控制器

    职责：
    - 初始化CAMEL ChatAgent
    - 加载系统消息和工具
    - 处理用户交互
    - 管理对话历史
    """
```

#### camel_tools.py
```python
class EmotionDetectionTool:
    """情绪检测工具 - CAMEL可调用"""

    def detect_emotion_and_risk(text, user_id):
        """检测情绪和风险等级"""

    def analyze_user_emotion(text, user_id):
        """深度情绪分析"""

class DBTSkillsTool:
    """DBT技能推荐工具 - CAMEL可调用"""

    def recommend_dbt_skills(emotions, risk_level):
        """推荐DBT技能"""
        # 使用异步推荐引擎
        # 返回技能列表和指导

class EmergencyProtocolTool:
    """紧急协议工具 - CAMEL可调用"""

    def handle_emergency_protocol(crisis_type):
        """触发紧急干预"""

class UserProfileTool:
    """用户画像工具 - CAMEL可调用"""

    def get_user_profile(user_id):
        """获取用户画像"""

    def get_emotion_report(user_id):
        """生成情绪报告"""
```

### 📂 modules/emotion/ - 情绪识别模块

#### emotion_engine.py
```python
class EmotionRecognitionEngine:
    """
    情绪识别引擎主类

    功能流程：
    1. 提取情绪特征（text/audio/video）
    2. 智能路由决策（L1/L2/L3）
    3. 风险评估（LOW/MEDIUM/HIGH/CRITICAL）
    4. 更新用户画像
    5. 生成系统建议

    主要方法：
    - analyze()          # 完整分析流程
    - get_profile()      # 获取用户画像
    - generate_profile_report() # 生成详细报告
    """
```

#### emotion_extractor.py
```python
class EmotionExtractor:
    """
    情绪特征提取器

    功能：
    - 文本：ModelScope API + 本地规则
    - 音频：讯飞ASR + librosa特征提取
    - 图像：CV特征 + 多模态API
    - 多模态：自适应权重融合

    主要方法：
    - extract()                 # 统一提取接口
    - extract_text_emotion()    # 文本情绪分析
    - extract_audio_features()  # 音频特征提取
    - extract_video_features()  # 图像情绪分析
    - transcribe_audio()        # 语音识别
    - multimodal_fusion()       # 多模态融合
    """
```

### 📂 services/ - 服务层

#### routing/intelligent_router.py
```python
class IntelligentRouter:
    """
    智能路由器

    三级分流：
    - L1_QUICK：日常闲聊（阈值0.3）
    - L2_INTERVENTION：DBT干预（阈值0.5）
    - L3_CRISIS：危机状态（最高优先级）

    路由依据：
    - 危机关键词检测
    - 情绪强度分析
    - 复合情绪检测
    - 音视频辅助判定
    """
```

#### intervention/dbt_intervention.py
```python
class RiskAssessmentEngine:
    """
    风险评估引擎

    四级风险：
    - LOW：低风险
    - MEDIUM：中等风险
    - HIGH：高风险
    - CRITICAL：危急

    评估维度：
    - 自伤冲动（最高权重）
    - 绝望情绪
    - 激越状态
    - 情绪斜率
    - 复合情绪
    """
```

#### profile/ - 用户画像服务

```python
# 基础画像
class EmotionProfileManager:
    """基础画像管理器"""
    - 情绪基准线计算
    - 模式分析
    - Self-Agent参数同步
    - 病理性特征检测

# 高级画像
class AdvancedEmotionProfileManager:
    """高级画像管理器"""
    - 趋势分析（上升/下降/稳定）
    - 周期检测（日内/周内/月度）
    - 聚类挖掘（情绪模式）
    - 性格推断（大五人格）
    - 风险预测（下次危机概率）
```

### 📂 modules/dbt/ - DBT技能推荐模块

```python
# 数据模型
class Skill:
    """DBT技能实体"""
    - skill_name：技能名称
    - description：描述
    - module：所属模块
    - steps：步骤列表
    - emotion_tags：情绪标签

# 推荐引擎
class RecommendationEngine:
    """
    DBT技能推荐引擎

    推荐流程：
    1. 接收情绪输入
    2. 匹配技能标签
    3. 计算匹配分数
    4. LLM增强说明
    5. 返回推荐结果
    """
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

如果你更喜欢使用Web界面或API：

```bash
# 启动Web服务器
python app/server.py
```

启动后访问：
- **Web界面**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

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
**最后更新**: 2026-01-26
**技术栈**: CAMEL-AI + DeepSeek + ModelScope + DBT + FastAPI

Made with ❤️ for Mental Health Support

</div>
