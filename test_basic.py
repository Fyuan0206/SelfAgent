"""
快速测试脚本
验证系统基础功能
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.emotion_engine import EmotionRecognitionEngine
import numpy as np
import math


def test_basic_functionality():
    """测试基础功能"""
    print("开始测试系统基础功能...\n")

    try:
        # 初始化引擎
        print("1. 初始化引擎...")
        engine = EmotionRecognitionEngine()
        print("   ✓ 引擎初始化成功\n")

        # 测试文本分析
        print("2. 测试文本情绪分析...")
        test_text = "我感到很空虚和绝望，不知道该怎么办"
        result = engine.analyze(text=test_text, user_id="test_user")
        print(f"   输入: {test_text}")
        print(f"   路由级别: {result['routing_decision']['level']}")
        print(f"   风险等级: {result['intervention_assessment']['risk_level']}")
        # 按分数降序排列，过滤掉0分的情绪，取前3个
        sorted_emotions = sorted(
            [(emo, score) for emo, score in result['emotion_features']['emotions'].items() if score > 0],
            key=lambda x: x[1],
            reverse=True
        )[:3]
        if sorted_emotions:
            print(f"   主要情绪: {[emo for emo, score in sorted_emotions]} (分数: {[f'{score:.2f}' for emo, score in sorted_emotions]})")
        else:
            print(f"   主要情绪: 未检测到明显情绪")
        print("   ✓ 文本分析成功\n")

        # 测试画像创建
        print("3. 测试用户画像...")
        profile = engine.get_profile("test_user")
        if profile:
            print(f"   用户ID: {profile['self_agent_params']['user_id']}")
            print(f"   画像已创建")
        print("   ✓ 画像功能正常\n")

        # 测试风险评估
        print("4. 测试风险评估...")
        risk_result = engine.risk_engine.evaluate_risk(
            emotion_features=result['emotion_features']['emotions'],
            emotion_slope=0.1
        )
        print(f"   风险等级: {risk_result.risk_level.value}")
        print(f"   紧急程度: {risk_result.urgency_score:.2f}")
        print(f"   触发信号数: {len(risk_result.trigger_signals)}")
        print("   ✓ 风险评估正常\n")

        # 测试路由系统
        print("5. 测试三级路由系统...")

        # 基础路由测试
        test_cases = [
            ("你好，今天天气不错", "L1_QUICK"),
            ("我感到很焦虑，睡不着觉", "L2_INTERVENTION"),
            ("我想自杀，不想活了", "L3_CRISIS")
        ]

        all_passed = True
        for text, expected_route in test_cases:
            result = engine.analyze(text=text, user_id="test_user")
            actual_route = result['routing_decision']['level']
            status = "✓" if actual_route == expected_route else "✗"
            print(f"   {status} '{text}' -> {actual_route} (期望: {expected_route})")
            if actual_route != expected_route:
                all_passed = False

        if all_passed:
            print("   ✓ 路由系统测试通过\n")
        else:
            print("   ⚠ 部分路由测试未通过，可能需要调整阈值\n")

        # 扩展测试用例
        print("=" * 50)
        print("6. 扩展测试用例（验证灵活性）...")
        print("=" * 50 + "\n")

        extended_tests = [
            # 积极情绪（应该是L1）
            ("我今天很开心，感觉一切都很好", "L1_QUICK", "积极情绪"),
            ("谢谢你的帮助，非常感谢", "L1_QUICK", "礼貌用语"),
            ("工作很顺利，项目成功了", "L1_QUICK", "成功表达"),

            # 中性/日常（应该是L1）
            ("你在吗？我想问个问题", "L1_QUICK", "日常询问"),
            ("今天吃什么比较好？", "L1_QUICK", "日常闲聊"),
            ("最近怎么样，还好吗", "L1_QUICK", "问候"),

            # 各种负面情绪（应该是L2）
            ("我感到很空虚，什么都不想做", "L2_INTERVENTION", "空虚感"),
            ("我好孤独，感觉没人理解我", "L2_INTERVENTION", "孤独"),
            ("我很内疚，觉得都是我的错", "L2_INTERVENTION", "内疚"),
            ("我很愤怒，太不公平了", "L2_INTERVENTION", "愤怒"),
            ("我感到很羞愧，不想见人", "L2_INTERVENTION", "羞愧"),
            ("我很烦躁，坐立不安", "L2_INTERVENTION", "激越"),
            ("我好难过，想哭", "L2_INTERVENTION", "悲伤"),
            ("我很恐惧，害怕面对", "L2_INTERVENTION", "恐惧"),

            # 复杂情绪（应该是L2）
            ("我既焦虑又难过，不知道该怎么办", "L2_INTERVENTION", "复合情绪"),
            ("最近总是失眠，心情很低落", "L2_INTERVENTION", "抑郁倾向"),

            # 危机情况（应该是L3）
            ("我想要结束自己的生命", "L3_CRISIS", "自杀意念"),
            ("我不知道活着还有什么意义", "L3_CRISIS", "深层绝望"),
            ("我想伤害自己", "L3_CRISIS", "自伤冲动"),
        ]

        extended_passed = 0
        extended_total = len(extended_tests)

        for text, expected_route, category in extended_tests:
            result = engine.analyze(text=text, user_id="test_user_extended")
            actual_route = result['routing_decision']['level']

            # 显示情绪（只显示>0的）
            emotions = result['emotion_features']['emotions']
            active_emotions = {k: round(v, 2) for k, v in emotions.items() if v > 0}

            status = "✓" if actual_route == expected_route else "✗"
            if actual_route == expected_route:
                extended_passed += 1

            print(f"   {status} [{category}]")
            print(f"      输入: {text}")
            print(f"      路由: {actual_route} (期望: {expected_route})")
            print(f"      情绪: {active_emotions if active_emotions else '无明显负面情绪'}")
            print()

        # 统计结果
        print("=" * 50)
        print(f"扩展测试结果: {extended_passed}/{extended_total} 通过")
        if extended_passed == extended_total:
            print("✓ 所有扩展测试通过！")
        else:
            print(f"⚠ {extended_total - extended_passed} 个测试未通过")
        print("=" * 50)

        # 多模态测试
        print("\n" + "=" * 50)
        print("7. 测试多模态输入 (语音 & 图像)...")
        print("=" * 50 + "\n")

        # 生成合成音频数据 (正弦波)
        sample_rate = 16000
        duration = 3  # 秒
        t = np.linspace(0, duration, int(sample_rate * duration))
        # 合成一个简单的440Hz音调
        audio_wave = 0.5 * np.sin(2 * np.pi * 440 * t)
        
        # 生成合成图像数据 (随机噪声)
        # 480x640 RGB图像
        video_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

        print("   正在分析多模态数据...")
        multimodal_result = engine.analyze(
            text="我感觉很不好", 
            user_id="test_multimodal",
            audio_data={'data': audio_wave, 'sample_rate': sample_rate},
            video_data=video_frame
        )

        audio_feats = multimodal_result['emotion_features'].get('audio_features')
        video_feats = multimodal_result['emotion_features'].get('video_features')
        
        if audio_feats:
            print(f"   ✓ 音频特征提取成功: {list(audio_feats.keys())}")
        else:
            print("   ✗ 音频特征提取失败")

        if video_feats:
            print(f"   ✓ 视频特征提取成功: {list(video_feats.keys())}")
        else:
            print("   ✗ 视频特征提取失败")
            
        if audio_feats and video_feats:
             print("   ✓ 多模态测试通过\n")

        print("=" * 50)
        print("✓ 所有基础功能测试完成！")
        print("=" * 50)

        return True

    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_basic_functionality()
    sys.exit(0 if success else 1)
