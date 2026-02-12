"""
DBT技能数据初始化
初始化DBT四大模块、具体技能和匹配规则
"""

from loguru import logger

from ..models.database import Base, DBTModule, DBTSkill, SkillMatchingRule
from .session import AsyncSessionLocal, sync_engine, SessionLocal


# ==================== DBT模块数据 ====================
DBT_MODULES = [
    {
        "name": "正念",
        "name_en": "mindfulness",
        "description": "培养当下觉察能力，不评判地观察内心体验。正念是DBT的核心，贯穿所有其他技能。",
        "priority": 1
    },
    {
        "name": "痛苦耐受",
        "name_en": "distress_tolerance",
        "description": "在危机时刻接受现实、度过难关而不使情况恶化。帮助处理强烈情绪和冲动。",
        "priority": 2
    },
    {
        "name": "情绪调节",
        "name_en": "emotion_regulation",
        "description": "理解和管理情绪，减少情绪脆弱性。学会识别、理解和改变不想要的情绪。",
        "priority": 3
    },
    {
        "name": "人际效能",
        "name_en": "interpersonal_effectiveness",
        "description": "在维护关系和自尊的同时有效地表达需求。提高人际沟通和冲突解决能力。",
        "priority": 4
    }
]


# ==================== DBT技能数据 ====================
DBT_SKILLS = [
    # ========== 痛苦耐受技能 ==========
    {
        "module_name_en": "distress_tolerance",
        "name": "TIPP",
        "name_en": "TIPP",
        "description": "通过改变身体化学状态快速降低情绪强度。TIPP代表Temperature（温度）、Intense Exercise（剧烈运动）、Paced Breathing（配合呼吸）、Paired Muscle Relaxation（渐进式肌肉放松）。",
        "trigger_emotions": ["焦虑", "激越", "恐惧", "愤怒", "恐慌"],
        "difficulty_level": 1,
        "steps": [
            {
                "step_number": 1,
                "instruction": "Temperature - 用冷水敷脸或握冰块",
                "goal": "激活潜水反射，降低心率和唤醒度",
                "prompt_hint": "你可以试着用冷水轻轻拍一下脸，或者握一块冰，感受一下凉意"
            },
            {
                "step_number": 2,
                "instruction": "Intense Exercise - 进行短暂剧烈运动",
                "goal": "消耗肾上腺素，释放紧张感",
                "prompt_hint": "可以原地跳跃、快走或做几个深蹲，大约1-2分钟"
            },
            {
                "step_number": 3,
                "instruction": "Paced Breathing - 缓慢深呼吸",
                "goal": "激活副交感神经，让身体放松",
                "prompt_hint": "吸气4秒，屏住4秒，呼气6秒，试着让呼气比吸气长"
            },
            {
                "step_number": 4,
                "instruction": "Paired Muscle Relaxation - 渐进式放松",
                "goal": "释放身体紧张，达到整体放松",
                "prompt_hint": "从脚趾开始，紧绷5秒然后放松，逐渐向上到全身"
            }
        ]
    },
    {
        "module_name_en": "distress_tolerance",
        "name": "STOP",
        "name_en": "STOP",
        "description": "在冲动行为之前暂停并思考。STOP代表Stop（停下）、Take a step back（退后一步）、Observe（观察）、Proceed mindfully（有意识地继续）。",
        "trigger_emotions": ["冲动", "愤怒", "激越"],
        "difficulty_level": 1,
        "steps": [
            {
                "step_number": 1,
                "instruction": "Stop - 立即停下你正在做的事",
                "goal": "打断自动化反应",
                "prompt_hint": "不管在做什么，先完全停下来"
            },
            {
                "step_number": 2,
                "instruction": "Take a step back - 退后一步",
                "goal": "创造心理和物理上的空间",
                "prompt_hint": "从当前情境中退出来，可以深呼吸几次"
            },
            {
                "step_number": 3,
                "instruction": "Observe - 观察正在发生什么",
                "goal": "客观了解情况",
                "prompt_hint": "注意你的想法、感受和周围环境，不要评判"
            },
            {
                "step_number": 4,
                "instruction": "Proceed mindfully - 有意识地继续",
                "goal": "做出明智的选择",
                "prompt_hint": "问自己：什么行动最符合我的目标和价值观？"
            }
        ]
    },
    {
        "module_name_en": "distress_tolerance",
        "name": "ACCEPTS",
        "name_en": "ACCEPTS",
        "description": "通过转移注意力度过危机时刻。包括Activities（活动）、Contributing（贡献）、Comparisons（比较）、Emotions（情绪）、Pushing away（推开）、Thoughts（思考）、Sensations（感觉）。",
        "trigger_emotions": ["悲伤", "空虚感", "孤独", "无聊"],
        "difficulty_level": 2,
        "steps": [
            {
                "step_number": 1,
                "instruction": "选择一种转移注意力的方式",
                "goal": "暂时从痛苦中抽离",
                "prompt_hint": "你可以选择：做活动、帮助他人、想想更困难的时候、看喜剧、暂时推开问题、数数或专注某种感觉"
            },
            {
                "step_number": 2,
                "instruction": "全身心投入所选择的活动",
                "goal": "让注意力完全转移",
                "prompt_hint": "尝试至少15-20分钟，给自己时间"
            }
        ]
    },
    {
        "module_name_en": "distress_tolerance",
        "name": "自我安抚",
        "name_en": "Self-Soothe",
        "description": "用五感（视觉、听觉、嗅觉、味觉、触觉）来安抚自己，创造平静和舒适的体验。",
        "trigger_emotions": ["悲伤", "孤独", "空虚感", "焦虑"],
        "difficulty_level": 1,
        "steps": [
            {
                "step_number": 1,
                "instruction": "选择一种或多种感官来安抚自己",
                "goal": "通过感官体验带来舒适",
                "prompt_hint": "视觉：看美丽的图片；听觉：听舒缓音乐；嗅觉：闻喜欢的香味；味觉：品尝喜欢的食物；触觉：抚摸柔软的东西"
            },
            {
                "step_number": 2,
                "instruction": "完全专注于这个感官体验",
                "goal": "让身心得到抚慰",
                "prompt_hint": "慢慢来，细细感受，告诉自己这是在照顾自己"
            }
        ]
    },
    {
        "module_name_en": "distress_tolerance",
        "name": "彻底接纳",
        "name_en": "Radical Acceptance",
        "description": "全然接受不能改变的现实。这不是赞同或放弃，而是停止与现实抗争，减少痛苦。",
        "trigger_emotions": ["绝望", "羞愧", "悲伤", "内疚"],
        "difficulty_level": 3,
        "steps": [
            {
                "step_number": 1,
                "instruction": "承认现实就是现实",
                "goal": "停止否认或抗争",
                "prompt_hint": "对自己说：'这就是现在的情况'"
            },
            {
                "step_number": 2,
                "instruction": "允许自己对现实有感受",
                "goal": "接受伴随的情绪",
                "prompt_hint": "感到难过、愤怒或害怕都是正常的"
            },
            {
                "step_number": 3,
                "instruction": "思考接受后可以做什么",
                "goal": "从接受中找到前进的路",
                "prompt_hint": "问自己：既然这是事实，我现在可以做什么？"
            }
        ]
    },

    # ========== 情绪调节技能 ==========
    {
        "module_name_en": "emotion_regulation",
        "name": "检查事实",
        "name_en": "Check the Facts",
        "description": "检查情绪是否与事实相符，区分想法和事实，减少由错误解读引发的强烈情绪。",
        "trigger_emotions": ["焦虑", "恐惧", "愤怒", "嫉妒"],
        "difficulty_level": 2,
        "steps": [
            {
                "step_number": 1,
                "instruction": "描述引发情绪的事件",
                "goal": "明确触发点",
                "prompt_hint": "只描述事实，像摄像机一样记录发生了什么"
            },
            {
                "step_number": 2,
                "instruction": "识别你对事件的解读",
                "goal": "区分事实和想法",
                "prompt_hint": "你对这件事的想法或假设是什么？"
            },
            {
                "step_number": 3,
                "instruction": "检验解读是否符合证据",
                "goal": "用证据检验想法",
                "prompt_hint": "有什么证据支持或反对你的想法？"
            },
            {
                "step_number": 4,
                "instruction": "考虑其他可能的解释",
                "goal": "拓宽视角",
                "prompt_hint": "还有什么其他可能的解释？"
            }
        ]
    },
    {
        "module_name_en": "emotion_regulation",
        "name": "相反行动",
        "name_en": "Opposite Action",
        "description": "当情绪不符合事实或不利于你的目标时，做与情绪冲动相反的行为来改变情绪。",
        "trigger_emotions": ["悲伤", "羞愧", "内疚", "恐惧", "愤怒"],
        "difficulty_level": 2,
        "steps": [
            {
                "step_number": 1,
                "instruction": "识别当前的情绪和冲动",
                "goal": "明确要对抗什么",
                "prompt_hint": "你现在感受到什么情绪？它让你想做什么？"
            },
            {
                "step_number": 2,
                "instruction": "判断这个情绪是否符合事实或有用",
                "goal": "决定是否使用相反行动",
                "prompt_hint": "这个情绪在当前情况下合理吗？按冲动行动会帮助你吗？"
            },
            {
                "step_number": 3,
                "instruction": "做与冲动相反的行为",
                "goal": "通过行为改变情绪",
                "prompt_hint": "悲伤想退缩→接触他人；恐惧想逃避→面对；愤怒想攻击→温和回应"
            }
        ]
    },
    {
        "module_name_en": "emotion_regulation",
        "name": "ABC PLEASE",
        "name_en": "ABC PLEASE",
        "description": "通过积累正面体验、建立掌控感和照顾身体来减少情绪脆弱性。",
        "trigger_emotions": ["情绪不稳定", "抑郁", "焦虑"],
        "difficulty_level": 2,
        "steps": [
            {
                "step_number": 1,
                "instruction": "Accumulate - 积累正面体验",
                "goal": "增加积极情绪的机会",
                "prompt_hint": "今天做一件让你开心的小事"
            },
            {
                "step_number": 2,
                "instruction": "Build - 建立掌控感",
                "goal": "增强自我效能",
                "prompt_hint": "完成一个小任务，体验成就感"
            },
            {
                "step_number": 3,
                "instruction": "Cope - 提前准备应对策略",
                "goal": "为困难做好准备",
                "prompt_hint": "想想可能遇到的挑战，准备好应对方法"
            },
            {
                "step_number": 4,
                "instruction": "PLEASE - 照顾身体健康",
                "goal": "减少身体对情绪的负面影响",
                "prompt_hint": "注意：药物、饮食平衡、避免药物滥用、睡眠、运动"
            }
        ]
    },

    # ========== 人际效能技能 ==========
    {
        "module_name_en": "interpersonal_effectiveness",
        "name": "DEAR MAN",
        "name_en": "DEAR MAN",
        "description": "有效请求他人或拒绝请求的技能。代表Describe（描述）、Express（表达）、Assert（明确）、Reinforce（强化）、Mindful（正念）、Appear confident（表现自信）、Negotiate（协商）。",
        "trigger_emotions": ["愤怒", "委屈", "人际困扰"],
        "difficulty_level": 2,
        "steps": [
            {
                "step_number": 1,
                "instruction": "Describe - 描述情况，只说事实",
                "goal": "让对方了解情况",
                "prompt_hint": "用'我注意到...'开头，不加评判"
            },
            {
                "step_number": 2,
                "instruction": "Express - 表达你的感受和想法",
                "goal": "让对方理解你的体验",
                "prompt_hint": "用'我感到...'或'我认为...'"
            },
            {
                "step_number": 3,
                "instruction": "Assert - 明确地请求或说不",
                "goal": "清楚表达你想要什么",
                "prompt_hint": "直接说出你的需求或拒绝"
            },
            {
                "step_number": 4,
                "instruction": "Reinforce - 说明好处",
                "goal": "增加对方配合的动力",
                "prompt_hint": "解释这样做对双方都有什么好处"
            },
            {
                "step_number": 5,
                "instruction": "保持Mindful、Appear confident、Negotiate",
                "goal": "有效沟通",
                "prompt_hint": "保持专注、表现自信、愿意协商"
            }
        ]
    },
    {
        "module_name_en": "interpersonal_effectiveness",
        "name": "GIVE",
        "name_en": "GIVE",
        "description": "维护人际关系的技能。代表Gentle（温和）、Interested（感兴趣）、Validate（验证）、Easy manner（轻松态度）。",
        "trigger_emotions": ["人际困扰", "愤怒", "委屈"],
        "difficulty_level": 1,
        "steps": [
            {
                "step_number": 1,
                "instruction": "Gentle - 保持温和，不攻击",
                "goal": "避免伤害关系",
                "prompt_hint": "不威胁、不评判、不攻击"
            },
            {
                "step_number": 2,
                "instruction": "Interested - 表现出对对方的兴趣",
                "goal": "让对方感到被重视",
                "prompt_hint": "认真倾听，问问题，保持眼神接触"
            },
            {
                "step_number": 3,
                "instruction": "Validate - 认可对方的感受",
                "goal": "让对方感到被理解",
                "prompt_hint": "承认对方的感受是可以理解的"
            },
            {
                "step_number": 4,
                "instruction": "Easy manner - 保持轻松态度",
                "goal": "减少紧张感",
                "prompt_hint": "适当微笑，使用幽默（如果合适）"
            }
        ]
    },
    {
        "module_name_en": "interpersonal_effectiveness",
        "name": "FAST",
        "name_en": "FAST",
        "description": "维护自尊的技能。代表Fair（公平）、no Apologies（不过度道歉）、Stick to values（坚持价值观）、Truthful（真实）。",
        "trigger_emotions": ["羞愧", "内疚", "自我怀疑"],
        "difficulty_level": 2,
        "steps": [
            {
                "step_number": 1,
                "instruction": "Fair - 对自己和他人都要公平",
                "goal": "平衡双方需求",
                "prompt_hint": "你的需求和他人的需求同样重要"
            },
            {
                "step_number": 2,
                "instruction": "no Apologies - 不过度道歉",
                "goal": "维护自尊",
                "prompt_hint": "不为合理的请求或拒绝道歉"
            },
            {
                "step_number": 3,
                "instruction": "Stick to values - 坚持你的价值观",
                "goal": "保持自我一致",
                "prompt_hint": "不为了取悦他人而放弃重要原则"
            },
            {
                "step_number": 4,
                "instruction": "Truthful - 诚实",
                "goal": "维护诚信",
                "prompt_hint": "不撒谎、不夸张、不假装无助"
            }
        ]
    },

    # ========== 正念技能 ==========
    {
        "module_name_en": "mindfulness",
        "name": "智慧心",
        "name_en": "Wise Mind",
        "description": "在理性思维（理性心）和情感思维（情绪心）之间找到平衡，进入直觉的智慧状态。",
        "trigger_emotions": ["情绪混乱", "困惑", "犹豫不决"],
        "difficulty_level": 2,
        "steps": [
            {
                "step_number": 1,
                "instruction": "识别你当前是在理性心还是情绪心",
                "goal": "了解当前状态",
                "prompt_hint": "理性心只看逻辑，情绪心只看感受"
            },
            {
                "step_number": 2,
                "instruction": "寻找两者的交汇点",
                "goal": "进入智慧心",
                "prompt_hint": "问自己：理性和感受都认同的是什么？"
            },
            {
                "step_number": 3,
                "instruction": "从智慧心的角度做决定",
                "goal": "做出平衡的选择",
                "prompt_hint": "相信你内在的直觉和智慧"
            }
        ]
    },
    {
        "module_name_en": "mindfulness",
        "name": "观察",
        "name_en": "Observe",
        "description": "不评判地觉察当下体验，包括内在（想法、感受、冲动）和外在（环境、他人）。",
        "trigger_emotions": ["焦虑", "注意力分散", "情绪混乱"],
        "difficulty_level": 1,
        "steps": [
            {
                "step_number": 1,
                "instruction": "将注意力带到当下",
                "goal": "回到此时此刻",
                "prompt_hint": "注意你现在看到、听到、感觉到什么"
            },
            {
                "step_number": 2,
                "instruction": "像旁观者一样观察你的内心",
                "goal": "不卷入地觉察",
                "prompt_hint": "注意你的想法和感受，像看云飘过"
            },
            {
                "step_number": 3,
                "instruction": "不评判，只是注意",
                "goal": "保持开放接纳",
                "prompt_hint": "不说好坏对错，只是觉察'这个存在'"
            }
        ]
    },
    {
        "module_name_en": "mindfulness",
        "name": "描述",
        "name_en": "Describe",
        "description": "用语言描述观察到的内容，帮助将体验从自动反应中分离出来。",
        "trigger_emotions": ["情绪混乱", "困惑"],
        "difficulty_level": 1,
        "steps": [
            {
                "step_number": 1,
                "instruction": "用语言描述你观察到的",
                "goal": "将体验概念化",
                "prompt_hint": "比如：'我注意到我的心跳很快'"
            },
            {
                "step_number": 2,
                "instruction": "区分观察和评判",
                "goal": "保持客观",
                "prompt_hint": "'我感到焦虑'是描述，'我不应该焦虑'是评判"
            }
        ]
    },
    {
        "module_name_en": "mindfulness",
        "name": "参与",
        "name_en": "Participate",
        "description": "全身心投入当前活动，完全融入体验而不自我意识过强。",
        "trigger_emotions": ["回避", "退缩", "麻木"],
        "difficulty_level": 2,
        "steps": [
            {
                "step_number": 1,
                "instruction": "选择一个活动全身心投入",
                "goal": "练习完全参与",
                "prompt_hint": "可以是任何事：走路、洗碗、对话"
            },
            {
                "step_number": 2,
                "instruction": "放下自我意识，融入活动",
                "goal": "体验心流状态",
                "prompt_hint": "不担心表现，不过度分析，只是做"
            }
        ]
    }
]


# ==================== 匹配规则数据 ====================
MATCHING_RULES = [
    # 高唤醒焦虑规则
    {
        "rule_name": "high_arousal_anxiety",
        "priority": 100,
        "module_name_en": "distress_tolerance",
        "skill_names": ["TIPP"],
        "conditions": {
            "emotion_conditions": [
                {"emotion": "焦虑", "operator": ">=", "value": 0.5}
            ],
            "trigger_signals": [
                {"signal": "agitation_level", "operator": ">=", "value": 0.4}
            ],
            "arousal": {"operator": ">=", "value": 0.6}
        },
        "description": "高唤醒焦虑状态推荐TIPP技能快速降低情绪强度"
    },
    # 冲动控制规则
    {
        "rule_name": "impulse_control",
        "priority": 95,
        "module_name_en": "distress_tolerance",
        "skill_names": ["STOP", "TIPP"],
        "conditions": {
            "trigger_signals": [
                {"signal": "self_harm_impulse", "operator": ">=", "value": 0.3}
            ]
        },
        "description": "存在自伤冲动时推荐STOP和TIPP"
    },
    # 绝望情绪规则
    {
        "rule_name": "despair_crisis",
        "priority": 90,
        "module_name_en": "distress_tolerance",
        "skill_names": ["彻底接纳", "TIPP"],
        "conditions": {
            "trigger_signals": [
                {"signal": "despair_level", "operator": ">=", "value": 0.5}
            ],
            "emotion_conditions": [
                {"emotion": "绝望", "operator": ">=", "value": 0.4}
            ]
        },
        "description": "绝望情绪推荐彻底接纳和TIPP"
    },
    # 羞愧情绪规则
    {
        "rule_name": "shame_spiral",
        "priority": 85,
        "module_name_en": "distress_tolerance",
        "skill_names": ["彻底接纳", "自我安抚"],
        "conditions": {
            "trigger_signals": [
                {"signal": "shame_level", "operator": ">=", "value": 0.5}
            ],
            "emotion_conditions": [
                {"emotion": "羞愧", "operator": ">=", "value": 0.4}
            ]
        },
        "description": "强烈羞愧感推荐彻底接纳和自我安抚"
    },
    # 情绪快速恶化规则
    {
        "rule_name": "emotional_volatility",
        "priority": 80,
        "module_name_en": "emotion_regulation",
        "skill_names": ["检查事实"],
        "conditions": {
            "trigger_signals": [
                {"signal": "emotion_slope", "operator": ">=", "value": 0.2}
            ]
        },
        "description": "情绪快速恶化时推荐检查事实"
    },
    # 人际冲突规则
    {
        "rule_name": "interpersonal_conflict",
        "priority": 75,
        "module_name_en": "interpersonal_effectiveness",
        "skill_names": ["DEAR MAN", "GIVE"],
        "conditions": {
            "context_contains": ["人际", "关系", "朋友", "同学", "家人", "老师"],
            "emotion_conditions": [
                {"emotion": "愤怒", "operator": ">=", "value": 0.3}
            ]
        },
        "description": "人际冲突情境推荐DEAR MAN和GIVE"
    },
    # 悲伤退缩规则
    {
        "rule_name": "sadness_withdrawal",
        "priority": 70,
        "module_name_en": "emotion_regulation",
        "skill_names": ["相反行动", "ABC PLEASE"],
        "conditions": {
            "emotion_conditions": [
                {"emotion": "悲伤", "operator": ">=", "value": 0.5}
            ]
        },
        "description": "悲伤情绪推荐相反行动"
    },
    # 空虚无聊规则
    {
        "rule_name": "emptiness_boredom",
        "priority": 65,
        "module_name_en": "distress_tolerance",
        "skill_names": ["ACCEPTS", "自我安抚"],
        "conditions": {
            "trigger_signals": [
                {"signal": "emptiness_level", "operator": ">=", "value": 0.4}
            ]
        },
        "description": "空虚感推荐ACCEPTS和自我安抚"
    },
    # 焦虑恐惧规则
    {
        "rule_name": "anxiety_fear",
        "priority": 60,
        "module_name_en": "emotion_regulation",
        "skill_names": ["检查事实", "相反行动"],
        "conditions": {
            "emotion_conditions": [
                {"emotion": "焦虑", "operator": ">=", "value": 0.4},
                {"emotion": "恐惧", "operator": ">=", "value": 0.3}
            ]
        },
        "description": "焦虑恐惧推荐检查事实"
    },
    # 内疚规则
    {
        "rule_name": "guilt_management",
        "priority": 55,
        "module_name_en": "interpersonal_effectiveness",
        "skill_names": ["FAST", "相反行动"],
        "conditions": {
            "emotion_conditions": [
                {"emotion": "内疚", "operator": ">=", "value": 0.4}
            ]
        },
        "description": "内疚情绪推荐FAST维护自尊"
    },
    # 情绪混乱规则
    {
        "rule_name": "emotional_confusion",
        "priority": 50,
        "module_name_en": "mindfulness",
        "skill_names": ["观察", "描述"],
        "conditions": {
            "emotion_conditions": [
                {"emotion": "困惑", "operator": ">=", "value": 0.3}
            ]
        },
        "description": "情绪混乱时推荐正念技能"
    },
    # 低唤醒默认规则
    {
        "rule_name": "low_arousal_default",
        "priority": 10,
        "module_name_en": "mindfulness",
        "skill_names": ["观察", "智慧心"],
        "conditions": {
            "arousal": {"operator": "<", "value": 0.4}
        },
        "description": "低唤醒状态推荐正念练习"
    }
]


async def init_database():
    """异步初始化数据库数据"""
    async with AsyncSessionLocal() as session:
        # 检查是否已初始化
        from sqlalchemy import select
        result = await session.execute(select(DBTModule))
        existing = result.scalars().first()

        if existing:
            logger.info("数据库已初始化，跳过")
            return

        logger.info("开始初始化DBT数据...")

        # 创建模块
        modules = {}
        for mod_data in DBT_MODULES:
            module = DBTModule(**mod_data)
            session.add(module)
            await session.flush()
            modules[mod_data["name_en"]] = module

        # 创建技能
        skills = {}
        for skill_data in DBT_SKILLS:
            module_name_en = skill_data.pop("module_name_en")
            module = modules.get(module_name_en)
            if module:
                skill = DBTSkill(module_id=module.id, **skill_data)
                session.add(skill)
                await session.flush()
                skills[skill_data["name"]] = skill

        # 创建规则
        for rule_data in MATCHING_RULES:
            module_name_en = rule_data.pop("module_name_en")
            skill_names = rule_data.pop("skill_names")

            module = modules.get(module_name_en)
            skill_ids = [skills[name].id for name in skill_names if name in skills]

            rule = SkillMatchingRule(
                module_id=module.id if module else None,
                skill_ids=skill_ids,
                **rule_data
            )
            session.add(rule)

        await session.commit()
        logger.info(f"初始化完成: {len(modules)}个模块, {len(skills)}个技能, {len(MATCHING_RULES)}条规则")


def init_database_sync():
    """同步初始化数据库数据"""
    session = SessionLocal()
    try:
        # 检查是否已初始化
        existing = session.query(DBTModule).first()
        if existing:
            logger.info("数据库已初始化，跳过")
            return

        logger.info("开始初始化DBT数据...")

        # 创建模块
        modules = {}
        for mod_data in DBT_MODULES:
            module = DBTModule(**mod_data)
            session.add(module)
            session.flush()
            modules[mod_data["name_en"]] = module

        # 创建技能
        skills = {}
        for skill_data in DBT_SKILLS.copy():
            data = skill_data.copy()
            module_name_en = data.pop("module_name_en")
            module = modules.get(module_name_en)
            if module:
                skill = DBTSkill(module_id=module.id, **data)
                session.add(skill)
                session.flush()
                skills[data["name"]] = skill

        # 创建规则
        for rule_data in MATCHING_RULES:
            data = rule_data.copy()
            module_name_en = data.pop("module_name_en")
            skill_names = data.pop("skill_names")

            module = modules.get(module_name_en)
            skill_ids = [skills[name].id for name in skill_names if name in skills]

            rule = SkillMatchingRule(
                module_id=module.id if module else None,
                skill_ids=skill_ids,
                **data
            )
            session.add(rule)

        session.commit()
        logger.info(f"初始化完成: {len(modules)}个模块, {len(skills)}个技能, {len(MATCHING_RULES)}条规则")

    finally:
        session.close()


# ============== 测试用例 ==============
if __name__ == "__main__":
    import asyncio

    async def test_init_data():
        """测试数据初始化"""
        # 创建内存数据库测试
        from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
        from ..models.database import Base

        engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        # 临时替换会话工厂
        global AsyncSessionLocal
        AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

        # 测试初始化
        await init_database()

        # 验证数据
        from sqlalchemy.ext.asyncio import AsyncSession
        async with AsyncSessionLocal() as session:
            modules = (await session.execute(select(DBTModule))).scalars().all()
            skills = (await session.execute(select(DBTSkill))).scalars().all()
            rules = (await session.execute(select(SkillMatchingRule))).scalars().all()

            assert len(modules) == 4, f"应有4个模块，实际{len(modules)}个"
            print(f"✓ 测试1通过: 创建了{len(modules)}个DBT模块")

            assert len(skills) >= 15, f"应有至少15个技能，实际{len(skills)}个"
            print(f"✓ 测试2通过: 创建了{len(skills)}个技能")

            assert len(rules) >= 10, f"应有至少10条规则，实际{len(rules)}条"
            print(f"✓ 测试3通过: 创建了{len(rules)}条匹配规则")

            # 检查TIPP技能
            tipp = next((s for s in skills if s.name == "TIPP"), None)
            assert tipp is not None
            assert len(tipp.steps) == 4
            print("✓ 测试4通过: TIPP技能数据正确")

            # 检查模块关联
            mindfulness = next((m for m in modules if m.name_en == "mindfulness"), None)
            assert mindfulness is not None
            print("✓ 测试5通过: 模块数据正确")

        await engine.dispose()
        print("\n所有数据初始化测试通过！")

    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy import select
    asyncio.run(test_init_data())
