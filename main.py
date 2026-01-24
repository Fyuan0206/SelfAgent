"""
情绪识别系统 - 示例使用脚本
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from core.emotion_engine import EmotionRecognitionEngine
from loguru import logger
import json


def print_separator(char="=", length=80):
    """打印分隔线"""
    print(char * length)


def demo_basic_analysis():
    """基础情绪分析演示"""
    print_separator()
    print("演示1: 基础文本情绪分析")
    print_separator()

    # 初始化引擎
    engine = EmotionRecognitionEngine()

    # 测试用例
    test_cases = [
        {
            "text": "我今天心情挺好的，天气也不错",
            "context": "日常闲聊"
        },
        {
            "text": "我感觉很空虚，什么都提不起兴趣，不知道活着有什么意义",
            "context": "情绪低落"
        },
        {
            "text": "我想伤害自己，我无法控制这种冲动",
            "context": "危机状态"
        },
        {
            "text": "我真的很生气，凭什么这么对我",
            "context": "情绪激动"
        },
        {
            "text": "我感到很羞愧，觉得自己一无是处",
            "context": "自我否定"
        }
    ]

    user_id = "demo_user_001"

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}:")
        print(f"文本: {test_case['text']}")
        print(f"上下文: {test_case['context']}")
        print("-" * 80)

        # 执行分析
        result = engine.analyze(
            text=test_case['text'],
            user_id=user_id,
            context=test_case['context']
        )

        # 打印结果
        print(f"路由级别: {result['routing_decision']['level']}")
        print(f"风险等级: {result['intervention_assessment']['risk_level']}")
        print(f"主要情绪: ", end="")

        # 显示前3个情绪
        emotions = result['emotion_features']['emotions']
        sorted_emotions = sorted(emotions.items(), key=lambda x: -x[1])[:3]
        print(", ".join([f"{e}({s:.2f})" for e, s in sorted_emotions]))

        if result['intervention_assessment']['triggered']:
            signals = result['intervention_assessment']['trigger_signals']
            print(f"触发信号: 自伤冲动={signals.get('self_harm_impulse', 0):.2f}, "
                  f"绝望={signals.get('despair_level', 0):.2f}")

        print(f"建议: {result['recommendations'][0] if result['recommendations'] else '无'}")

        print_separator(char="-")


def demo_profile_analysis():
    """用户画像分析演示"""
    print_separator()
    print("演示2: 用户画像分析")
    print_separator()

    engine = EmotionRecognitionEngine()
    user_id = "demo_user_002"

    # 模拟多轮对话
    conversations = [
        "我今天感觉很糟糕",
        "真的很难受，想哭",
        "我觉得自己什么都做不好",
        "我想结束这一切",
        "我有时候觉得自己没用"
    ]

    print(f"\n为用户 {user_id} 模拟 {len(conversations)} 轮对话...\n")

    for i, text in enumerate(conversations, 1):
        print(f"第{i}轮: {text}")
        engine.analyze(text=text, user_id=user_id, context=f"对话{i}")

    # 获取画像
    profile_data = engine.get_profile(user_id)

    if profile_data:
        print("\n" + "=" * 80)
        print("用户画像摘要:")
        print("=" * 80)
        print(profile_data['summary'])

        print("\n" + "=" * 80)
        print("Self-Agent参数:")
        print("=" * 80)
        print(json.dumps(profile_data['self_agent_params'], indent=2, ensure_ascii=False))

        if profile_data['pathological_indicators']:
            print("\n⚠️ 潜在病理性特征:")
            for indicator in profile_data['pathological_indicators']:
                print(f"  - {indicator}")


def demo_multimodal_analysis():
    """多模态分析演示（如果有音频/视频文件）"""
    print_separator()
    print("演示3: 多模态情绪分析")
    print_separator()

    engine = EmotionRecognitionEngine()

    # 检查是否有测试文件
    audio_path = "test_data/sample_audio.wav"
    video_path = "test_data/sample_video.mp4"

    if Path(audio_path).exists() or Path(video_path).exists():
        result = engine.analyze(
            text="我感到很紧张",
            user_id="demo_user_003",
            audio_path=audio_path if Path(audio_path).exists() else None,
            video_path=video_path if Path(video_path).exists() else None,
            context="多模态测试"
        )

        print("\n多模态分析结果:")
        print(f"文本情绪: {result['emotion_features']['emotions']}")
        print(f"音频特征: {result['emotion_features']['audio_features']}")
        print(f"视频特征: {result['emotion_features']['video_features']}")
    else:
        print("未找到测试音频/视频文件")
        print("如需测试多模态功能，请将文件放在 test_data/ 目录下")


def demo_risk_assessment():
    """风险评估演示"""
    print_separator()
    print("演示4: 风险评估系统")
    print_separator()

    engine = EmotionRecognitionEngine()

    # 测试不同风险等级
    test_cases = [
        {
            "text": "我今天心情很好",
            "expected": "LOW"
        },
        {
            "text": "我感到有点焦虑和不安",
            "expected": "MEDIUM"
        },
        {
            "text": "我非常绝望，觉得活着没有意义",
            "expected": "HIGH"
        },
        {
            "text": "我想伤害自己，无法控制冲动",
            "expected": "CRITICAL"
        }
    ]

    for i, test in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}:")
        print(f"文本: {test['text']}")
        print(f"期望风险: {test['expected']}")

        result = engine.analyze(text=test['text'], user_id="demo_risk")

        risk = result['intervention_assessment']['risk_level']
        urgency = result['intervention_assessment']['urgency_score']
        signals = result['intervention_assessment']['trigger_signals']

        print(f"实际风险: {risk}")
        print(f"紧急程度: {urgency:.2f}")
        print(f"触发信号:")
        for signal, value in signals.items():
            if value > 0.1:
                print(f"  - {signal}: {value:.2f}")

        print_separator(char="-")


def interactive_mode():
    """交互式模式"""
    print_separator()
    print("交互式情绪分析模式")
    print_separator()
    print("输入文本进行实时情绪分析，输入 'quit' 退出\n")

    engine = EmotionRecognitionEngine()
    user_id = "interactive_user"

    while True:
        try:
            text = input("请输入文本: ").strip()

            if text.lower() in ['quit', 'exit', 'q']:
                print("退出交互模式")
                break

            if not text:
                continue

            # 执行分析
            result = engine.analyze(text=text, user_id=user_id)

            # 显示结果
            print("\n分析结果:")
            print(f"  路由级别: {result['routing_decision']['level']}")
            print(f"  风险等级: {result['intervention_assessment']['risk_level']}")

            emotions = result['emotion_features']['emotions']
            sorted_emotions = sorted(emotions.items(), key=lambda x: -x[1])[:3]
            print(f"  主要情绪: {', '.join([f'{e}({s:.2f})' for e, s in sorted_emotions])}")

            if result['recommendations']:
                print(f"  建议: {result['recommendations'][0]}")

            print()

        except KeyboardInterrupt:
            print("\n退出交互模式")
            break
        except Exception as e:
            print(f"错误: {e}\n")


def main():
    """主函数"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "情绪识别与DBT干预系统" + " " * 34 + "║")
    print("║" + " " * 15 + "Emotion Recognition & DBT Intervention" + " " * 22 + "║")
    print("╚" + "=" * 78 + "╝")

    print("\n请选择演示模式:")
    print("1. 基础情绪分析")
    print("2. 用户画像分析")
    print("3. 多模态分析")
    print("4. 风险评估演示")
    print("5. 交互式模式")
    print("0. 退出")

    while True:
        try:
            choice = input("\n请输入选项 (0-5): ").strip()

            if choice == '0':
                print("再见！")
                break
            elif choice == '1':
                demo_basic_analysis()
            elif choice == '2':
                demo_profile_analysis()
            elif choice == '3':
                demo_multimodal_analysis()
            elif choice == '4':
                demo_risk_assessment()
            elif choice == '5':
                interactive_mode()
            else:
                print("无效选项，请重新输入")

        except KeyboardInterrupt:
            print("\n\n再见！")
            break
        except Exception as e:
            print(f"错误: {e}")


if __name__ == "__main__":
    main()
