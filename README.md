# 情绪识别系统 (Emotion Recognition System)

一个基于DBT（辩证行为疗法）的多模态情绪识别与智能干预系统。支持文本、语音、图片三种输入方式，通过AI模型进行情绪分析，并根据风险等级自动路由到不同的干预策略。

## 目录

- [系统概述](#系统概述)
- [核心功能](#核心功能)
- [系统架构](#系统架构)
- [快速开始](#快速开始)
- [安装部署](#安装部署)
- [配置说明](#配置说明)
- [API使用](#api使用)
- [测试指南](#测试指南)
- [开发指南](#开发指南)
- [故障排查](#故障排查)
- [技术栈](#技术栈)
- [许可证](#许可证)

---

## 系统概述

本项目是一个智能情绪识别与干预系统，能够：

- **多模态输入**：自动识别并处理文本、语音、图片三种输入类型
- **DBT情绪分析**：基于辩证行为疗法的12种核心情绪进行精准识别
- **三级智能路由**：根据情绪风险自动路由到L1/L2/L3不同干预级别
- **实时风险评估**：结合用户画像和历史数据进行动态风险评估
- **讯飞语音识别**：集成讯飞大模型ASR，支持中文及202种方言识别

### 应用场景

- 心理健康辅助评估
- 情绪状态实时监测
- 危机干预智能路由
- 多模态人机交互
- 情感计算研究

---

## 核心功能

### 1. 多模态输入处理

| 输入类型 | 支持格式 | 处理方式 |
|---------|---------|---------|
| **文本** | 纯文本字符串 | ModelScope文本情绪分析 |
| **语音** | wav, mp3, m4a, aac | 讯飞ASR识别 → 文本情绪分析 |
| **图片** | jpg, png, gif, bmp | ModelScope多模态图像情绪分析 + CV特征辅助 |
| **视频** | mp4, avi, mov, mkv | 提取首帧 → 图像情绪分析 |

### 2. DBT 12种核心情绪

空虚感、羞愧、激越、自伤冲动、愤怒、悲伤、焦虑、恐惧、厌恶、内疚、孤独、绝望

### 3. 三级智能路由

| 级别 | 名称 | 触发条件 | 处理策略 |
|-----|------|---------|---------|
| **L1** | 快速通路 | 正常/积极情绪 | 基础响应 |
| **L2** | 干预路由 | 轻度负面情绪 | 心理支持干预 |
| **L3** | 危机路由 | 自伤/自杀风险 | 紧急危机干预 |

### 4. 情绪融合机制

- **图像情绪融合**：纯图像输入时，图像情绪自动融合到文本情绪
- **CV特征辅助**：基于色彩、亮度等视觉特征的情绪推断
- **多模态融合**：文本、语音、视觉特征的自适应权重融合

---

## 系统架构

```
emotion/
├── core/                          # 核心模块
│   ├── emotion_engine.py          # 情绪识别引擎（主入口）
│   ├── emotion_extractor.py       # 情绪特征提取器
│   ├── multimodal_input_processor.py  # 多模态输入处理器
│   ├── intelligent_router.py      # 智能路由系统
│   ├── risk_engine.py             # 风险评估引擎
│   └── emotion_profile.py         # 用户画像管理
├── api/                           # API接口（如果需要）
├── tests/                         # 测试文件
├── config.yaml                    # 配置文件
├── requirements.txt               # 依赖列表
└── README.md                      # 本文档
```

### 核心流程图

```
用户输入 → 多模态输入处理器 → 类型检测 → 特征提取
                ↓
    [文本] → 文本情绪分析 → 情绪特征
    [语音] → 讯飞ASR → 文本 → 文本情绪分析 → 情绪特征
    [图片] → 图像情绪分析 → 情绪特征 → 融合到text_emotion
                ↓
        智能路由系统 (L1/L2/L3)
                ↓
        风险评估引擎
                ↓
        用户画像更新
                ↓
        返回分析结果
```

---

## 快速开始

### 最小示例

```python
from core.emotion_engine import EmotionRecognitionEngine
from core.multimodal_input_processor import MultimodalInputProcessor

# 1. 初始化系统
engine = EmotionRecognitionEngine()
processor = MultimodalInputProcessor(engine)

# 2. 处理不同类型的输入（自动识别！）
result = processor.process_input("我今天很开心", user_id="user123")

# 3. 获取分析结果
print(f"路由级别: {result['routing_decision']['level']}")  # L1_QUICK
print(f"风险等级: {result['intervention_assessment']['risk_level']}")  # LOW
print(f"情绪: {result['emotion_features']['emotions']}")
```

### 输出示例

```json
{
  "routing_decision": {
    "level": "L1_QUICK",
    "reason": "未检测到明显负面情绪",
    "suggested_action": "正常对话"
  },
  "emotion_features": {
    "emotions": {
      "空虚感": 0.0,
      "羞愧": 0.0,
      "悲伤": 0.0,
      "焦虑": 0.0,
      "绝望": 0.0
    },
    "arousal": 0.3,
    "confidence": 0.85
  },
  "intervention_assessment": {
    "triggered": false,
    "risk_level": "LOW",
    "urgency_score": 0.1
  }
}
```

---

## 安装部署

### 环境要求

- Python >= 3.8
- pip >= 21.0

### 安装步骤

```bash
# 1. 克隆项目
git clone <repository_url>
cd emotion

# 2. 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 配置API密钥
# 编辑 config.yaml，填入你的API密钥

# 5. 运行测试
python test_basic.py
```

### 依赖说明

| 依赖包 | 版本 | 用途 |
|-------|------|------|
| modelscope | >=1.0.0 | ModelScope API调用 |
| torch | >=2.0.0 | 深度学习框架 |
| transformers | >=4.30.0 | NLP模型 |
| librosa | >=0.10.0 | 音频处理 |
| opencv-python | >=4.8.0 | 图像处理 |
| websocket-client | >=1.0.0 | WebSocket通信（讯飞ASR） |
| loguru | >=0.7.0 | 日志记录 |
| pyyaml | >=6.0 | 配置文件解析 |

---

## 配置说明

### config.yaml 完整配置

```yaml
# DBT 12种核心情绪
dbt_emotions:
  - 空虚感
  - 羞愧
  - 激越
  - 自伤冲动
  - 愤怒
  - 悲伤
  - 焦虑
  - 恐惧
  - 厌恶
  - 内疚
  - 孤独
  - 绝望

# ModelScope API配置
modelscope:
  api_key: "ms-your-api-key"  # 替换为你的API密钥
  emotion_model: "Qwen/Qwen2.5-7B-Instruct"
  multimodal_model: "Qwen/Qwen3-VL-8B-Instruct"

# 讯飞语音识别配置
xunfei_asr:
  app_id: "your_app_id"          # 讯飞应用ID
  api_key: "your_api_key"        # 讯飞API Key
  api_secret: "your_api_secret"  # 讯飞API Secret
  host: "iat.xf-yun.com"
  path: "/v1"
  sample_rate: 16000
  channels: 1
  bit_depth: 16
  domain: "slm"         # 大模型领域
  language: "zh_cn"     # 中文
  accent: "mandarin"    # 普通话
  eos: 6000            # 静音超时(毫秒)

# 多模态融合权重
multimodal:
  text_weight: 0.6      # 文本权重
  audio_weight: 0.25    # 语音权重
  video_weight: 0.15    # 视频权重

# 路由阈值配置
routing:
  l2:
    emotion_threshold: 0.5       # 情绪阈值
    min_indicators: 2            # 最少指标数
    arousal_threshold: 0.6       # 唤醒度阈值

  l3:
    crisis_keywords:             # 危机关键词
      - 自杀
      - 自残
      - 伤害自己
      - 不想活
      - 结束生命
    emotion_thresholds:         # 危机情绪阈值
      自伤冲动: 0.8
      绝望: 0.7

# 风险评估配置
risk_assessment:
  emotion_slope_window: 5        # 情绪斜率窗口
  high_urgency_threshold: 0.7    # 高紧急度阈值
  medium_urgency_threshold: 0.4  # 中紧急度阈值

# 日志配置
logging:
  level: "INFO"                  # 日志级别
  format: "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | {name}:{function}:{line} - {message}"
```

### 获取API密钥

#### ModelScope API密钥

1. 访问 [ModelScope开放平台](https://modelscope.cn/)
2. 注册/登录账号
3. 进入个人中心 → API密钥
4. 创建新的API密钥

#### 讯飞ASR密钥

1. 访问 [讯飞开放平台](https://www.xfyun.cn/)
2. 注册/登录账号
3. 控制台 → 创建应用 → 语音听写（流式版）
4. 获取 APPID、APIKey、APISecret

---

## API使用

### MultimodalInputProcessor 统一接口

这是推荐的统一处理接口，自动识别输入类型。

#### 初始化

```python
from core.emotion_engine import EmotionRecognitionEngine
from core.multimodal_input_processor import MultimodalInputProcessor

engine = EmotionRecognitionEngine()
processor = MultimodalInputProcessor(engine)
```

#### process_input() 方法

```python
result = processor.process_input(
    input_data,      # 输入数据（自动识别类型）
    user_id="user123",
    context=""        # 可选：对话上下文
)
```

#### 支持的输入格式

##### 1. 文本输入

```python
result = processor.process_input("我今天很开心", user_id="user123")
```

##### 2. 语音文件

```python
result = processor.process_input("audio/test.wav", user_id="user123")
```

##### 3. 图片文件

```python
result = processor.process_input("image/test.jpg", user_id="user123")
```

##### 4. Base64编码

```python
# 音频Base64
audio_base64 = "data:audio/wav;base64,UklGRiQAAABXQVZF..."
result = processor.process_input(audio_base64, user_id="user123")

# 图片Base64
image_base64 = "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
result = processor.process_input(image_base64, user_id="user123")
```

##### 5. 字典格式（API风格）

```python
request = {
    "type": "text",               # text/audio/image/video
    "content": "我感到很焦虑",     # 内容
    "path": "optional_path"       # 可选：文件路径
}
result = processor.process_input(request, user_id="user123")
```

### EmotionRecognitionEngine 核心引擎

#### analyze() 方法

```python
result = engine.analyze(
    text="用户输入的文本",
    user_id="user123",
    audio_path="audio/test.wav",      # 可选：音频文件路径
    audio_data=None,                  # 可选：音频numpy数组
    video_path=None,                  # 可选：视频文件路径
    video_data=None,                  # 可选：视频帧(numpy数组)
    context=""                        # 可选：对话上下文
)
```

#### get_profile() 方法

```python
profile = engine.get_profile("user123")
print(profile['self_agent_params']['user_id'])
print(profile['emotion_history'])
```

### 返回结果格式

```python
{
    # 路由决策
    'routing_decision': {
        'level': 'L2_INTERVENTION',      # L1_QUICK, L2_INTERVENTION, L3_CRISIS
        'reason': '负面情绪总分: 1.22; 多情绪组合: 3种负面情绪',
        'suggested_action': '建议进行心理干预'
    },

    # 情绪特征
    'emotion_features': {
        'emotions': {
            '空虚感': 0.0,
            '羞愧': 0.0,
            '悲伤': 0.6,
            '焦虑': 0.4,
            # ... 其他12种DBT情绪
        },
        'text_arousal': 0.72,
        'audio_features': {          # 如果有语音输入
            'pitch_mean': 760.58,
            'pitch_std': 157.43,
            'energy': 0.2829,
            'spectral_centroid': 2341.27
        },
        'video_features': {          # 如果有图像输入
            'brightness': 98.5,
            'contrast': 67.3,
            '悲伤': 0.6,
            '绝望': 0.4
        }
    },

    # 干预评估
    'intervention_assessment': {
        'triggered': True,
        'risk_level': 'MEDIUM',       # LOW, MEDIUM, HIGH, CRITICAL
        'urgency_score': 0.67,
        'trigger_signals': [
            '负面情绪总分: 1.22',
            '多情绪组合: 3种负面情绪'
        ]
    },

    # 输入类型
    'input_type': 'text',            # text, audio, image, video

    # 其他字段
    'transcribed_text': '...',      # 如果是语音输入，包含识别的文本
    'audio_path': '...',            # 音频文件路径
    'image_path': '...',            # 图片文件路径
}
```

---

## 测试指南

### 运行所有测试

```bash
# 基础功能测试
python test_basic.py

# 多模态测试（语音+图片）
python test_multimodal_basic.py

# 统一输入测试
python test_unified_input.py

# 讯飞ASR单独测试
python test_xunfei_asr.py
```

### 测试文件说明

| 测试文件 | 说明 | 预期结果 |
|---------|------|---------|
| `test_basic.py` | 基础文本情绪分析 | 所有测试通过 |
| `test_multimodal_basic.py` | 语音和图片情绪识别 | 输出格式对齐，哭泣图片→L2 |
| `test_unified_input.py` | 统一多模态输入接口 | 自动识别类型 |
| `test_xunfei_asr.py` | 讯飞ASR单独测试 | 成功识别语音 |

### 预期输出示例

```
============================================================
多模态情绪识别测试（语音 & 图像）
============================================================

   ✓ [语音-开心大笑]
      输入: 男人开心大笑声_耳聆网_[声音ID：21063].wav
      识别文本: 哈哈哈哈。
      路由: L1_QUICK (期望: L1_QUICK)
      情绪: 无明显负面情绪

   ✓ [图像-悲伤痛苦]
      输入: pexels-olly-3767426.jpg
      路由: L2_INTERVENTION (期望: L2_INTERVENTION)
      图像情绪: {'悲伤': 0.39, '焦虑': 0.22, '孤独': 0.17, '绝望': 0.22}
```

---

## 开发指南

### 添加新的情绪类型

1. 编辑 `config.yaml`，在 `dbt_emotions` 列表中添加新情绪
2. 更新路由规则（`core/intelligent_router.py`）
3. 重新训练或更新提示词

### 自定义路由规则

编辑 `core/intelligent_router.py`：

```python
def route(self, text: str, emotion_features: Dict, ...):
    # 添加自定义路由逻辑
    if emotion_features.get('自定义情绪') > 0.8:
        return RoutingDecision(level='L3_CRISIS', ...)
```

### 添加新的输入类型支持

1. 在 `InputType` 枚举中添加新类型
2. 在 `detect_input_type()` 中添加检测逻辑
3. 实现对应的处理方法（如 `_process_xxx()`）

### 日志级别调整

```python
from loguru import logger

# 设置全局日志级别
logger.remove()
logger.add(sys.stdout, level="DEBUG")  # 或 INFO, WARNING, ERROR
```

---

## 故障排查

### 常见问题

#### 1. 讯飞ASR连接失败

**错误信息**: `讯飞ASR WebSocket错误: Handshake status 401`

**解决方案**:
- 检查 `config.yaml` 中的讯飞API密钥是否正确
- 确认API密钥未过期
- 检查网络连接

#### 2. ModelScope API调用失败

**错误信息**: `ModelScope API错误: 401`

**解决方案**:
- 检查 `modelscope.api_key` 是否正确
- 确认API密钥有足够配额
- 访问 [ModelScope控制台](https://modelscope.cn/my/myaccesstoken) 查看状态

#### 3. 音频文件格式不支持

**错误信息**: `无法处理音频输入`

**解决方案**:
- 确保音频格式为 wav/mp3/m4a
- 使用ffmpeg转换格式：
  ```bash
  ffmpeg -i input.mp3 -acodec pcm_s16le -ar 16000 -ac 1 output.wav
  ```

#### 4. 图像情绪识别不准确

**可能原因**:
- 图像质量低
- 光线暗淡
- 表情不明显

**解决方案**:
- 已内置CV特征辅助检测
- 系统会自动提升复合负面情绪的分数
- 如需更高准确率，可考虑使用更大参数的多模态模型

#### 5. 依赖安装失败

**错误信息**: `error: Microsoft Visual C++ 14.0 is required`

**解决方案**:
```bash
# 使用预编译的wheel包
pip install --only-binary :all: librosa
pip install --only-binary :all: opencv-python
```

### 调试模式

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# 或在代码中设置
from loguru import logger
logger.add(sys.stdout, level="DEBUG")
```

---

## 技术栈

### 核心技术

- **NLP**: ModelScope, Qwen2.5, Qwen3-VL
- **语音识别**: 讯飞大模型ASR
- **计算机视觉**: OpenCV, Librosa
- **深度学习**: PyTorch, Transformers
- **WebSocket**: websocket-client

### 算法与模型

- **情绪分析**: DBT辩证行为疗法框架
- **多模态融合**: 自适应权重融合算法
- **风险评估**: 动态情绪斜率计算
- **智能路由**: 基于规则的决策树 + 阈值判断

### 性能优化

- 并行API调用
- 音频分帧处理
- 图像缓存机制
- 用户画像增量更新

---

## 许可证

本项目仅供学习和研究使用。使用相关API时请遵守：

- [ModelScope服务条款](https://modelscope.cn/)
- [讯飞开放平台服务条款](https://www.xfyun.cn/)

---

## 联系方式

- 项目地址: [GitHub Repository]
- 问题反馈: [Issues]
- 技术讨论: [Discussions]

---

## 更新日志

### v1.0.0 (2025-01-24)

**新增功能**:
- ✨ 统一多模态输入处理器（自动识别文本/语音/图片）
- ✨ 讯飞大模型ASR集成（支持中文+202种方言）
- ✨ 图像情绪识别（多模态API + CV特征辅助）
- ✨ 图像情绪融合机制
- ✨ DBT 12种核心情绪支持
- ✨ 三级智能路由（L1/L2/L3）

**优化**:
- 🎯 提升哭泣图片识别准确率（悲伤≥0.6 → L2）
- 🎯 优化提示词，增强危机情绪检测
- 🎯 添加CV特征后备规则

**测试**:
- ✅ 所有基础功能测试通过
- ✅ 多模态输入测试通过
- ✅ 语音识别测试通过（讯飞ASR）
- ✅ 图像情绪识别测试通过

---

## 致谢

感谢以下开源项目和平台的支持：

- [ModelScope](https://modelscope.cn/) - 开源模型社区
- [讯飞开放平台](https://www.xfyun.cn/) - 语音识别服务
- [Qwen](https://qwenlm.github.io/) - 通义千问大模型
