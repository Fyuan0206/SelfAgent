"""
高级用户画像系统测试
展示深度情绪分析、趋势预测、性格推断等功能
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from core.emotion_engine import EmotionRecognitionEngine


def test_advanced_profile():
    """测试高级用户画像系统"""
    print("=" * 70)
    print("高级用户画像系统测试")
    print("=" * 70)
    print()

    # 初始化引擎（启用高级画像）
    print("初始化系统（启用高级画像）...")
    engine = EmotionRecognitionEngine(use_advanced_profile=True)
    print("   ✓ 系统初始化成功\n")

    # 模拟一个用户的多次情绪变化
    user_id = "test_user_advanced"

    # 测试场景：一个用户在不同时间的情绪输入
    test_scenarios = [
        # 第一天：正常情绪
        {"day": 1, "text": "我今天感觉还不错，天气挺好的", "context": "日常闲聊"},
        {"day": 1, "text": "工作挺顺利的，完成了几个任务", "context": "工作"},        {"day": 1, "text": "有点累，不过还好", "context": "晚上"},

        # 第二天：轻度焦虑
        {"day": 2, "text": "明天有个重要会议，有点紧张", "context": "工作压力"},
        {"day": 2, "text": "感觉有点焦虑，睡不着", "context": "晚上"},

        # 第三天：情绪下降
        {"day": 3, "text": "会议推迟了，感到很沮丧", "context": "工作挫折"},
        {"day": 3, "text": "感觉自己什么都不想做", "context": "情绪低落"},

        # 第四天：危机状态
        {"day": 4, "text": "我想伤害自己", "context": "危机"},

        # 第五天：开始恢复
        {"day": 5, "text": "稍微好一点了", "context": "恢复"},
        {"day": 5, "text": "和朋友聊了聊，感觉舒服多了", "context": "社交支持"},

        # 第六天：基本恢复
        {"day": 6, "text": "今天感觉还行", "context": "日常"},
        {"day": 6, "text": "准备迎接新的一天", "context": "积极"},

        # 第七天：再次焦虑
        {"day": 7, "text": "又开始担心下周的工作了", "context": "工作压力"},

        # 第十天：情绪稳定
        {"day": 10, "text": "今天心情还不错", "context": "日常"},
    ]

    print("=" * 70)
    print("模拟用户情绪变化过程...")
    print("=" * 70)
    print()

    # 执行分析
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"--- 场景 {i}: 第{scenario['day']}天 - {scenario['context']} ---")

        result = engine.analyze(
            text=scenario['text'],
            user_id=user_id,
            context=scenario['context']
        )

        print(f"输入: {scenario['text']}")
        print(f"路由: {result['routing_decision']['level']}")
        print(f"风险: {result['intervention_assessment']['risk_level']}")

        # 显示主要情绪
        emotions = result['emotion_features']['emotions']
        active_emotions = {k: round(v, 2) for k, v in emotions.items() if v > 0}
        if active_emotions:
            print(f"情绪: {active_emotions}")
        print()

    # 生成详细报告
    print("=" * 70)
    print("生成高级用户画像报告...")
    print("=" * 70)
    print()

    report = engine.generate_profile_report(user_id)

    if report:
        print(report)

        # 保存报告到文件
        report_path = Path(f"profiles/{user_id}_report.txt")
        report_path.parent.mkdir(exist_ok=True)
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\n✅ 报告已保存到: {report_path}")

    else:
        print("❌ 无法生成报告（数据不足）")

    # 获取Self-Agent导出数据
    print()
    print("=" * 70)
    print("Self-Agent导出数据")
    print("=" * 70)
    print()

    profile_data = engine.get_profile(user_id)
    if profile_data and 'self_agent_export' in profile_data:
        export = profile_data['self_agent_export']

        print("性格特征:")
        personality = export.get('personality', {})
        print(f"  开放性: {personality.get('openness', 0):.2%}")
        print(f"  尽责性: {personality.get('conscientiousness', 0):.2%}")
        print(f"  外向性: {personality.get('extraversion', 0):.2%}")
        print(f"  宜人性: {personality.get('agreeableness', 0):.2%}")
        print(f"  神经质: {personality.get('neuroticism', 0):.2%}")
        print()

        print("决策风格:")
        print(f"  决策方式: {personality.get('decision_style', 'unknown')}")
        print(f"  风险容忍度: {personality.get('risk_tolerance', 0):.2%}")
        print(f"  应对风格: {personality.get('coping_style', 'unknown')}")
        print()

        print("压力反应:")
        print(f"  压力应对: {personality.get('stress_response', 'unknown')}")
        print(f"  恢复力: {personality.get('resilience_score', 0):.2%}")
        print()

        # 风险预测
        risk_pred = export.get('risk_prediction', {})
        print("风险预测:")
        print(f"  下次危机概率: {risk_pred.get('next_crisis_probability', 0):.2%}")
        if risk_pred.get('high_risk_time_windows'):
            print(f"  高风险时段: {', '.join(risk_pred['high_risk_time_windows'])}")
        if risk_pred.get('early_warning_signals'):
            print(f"  早期预警信号:")
            for signal in risk_pred['early_warning_signals']:
                print(f"    ⚠️  {signal}")
        if risk_pred.get('protective_factors'):
            print(f"  保护因素:")
            for factor in risk_pred['protective_factors']:
                print(f"    ✅ {factor}")
        print()

    print("=" * 70)
    print("测试完成")
    print("=" * 70)

    return True


def test_real_scenario():
    """测试真实场景：语音+图片综合分析"""
    print()
    print("=" * 70)
    print("真实场景测试：多模态输入的高级画像")
    print("=" * 70)
    print()

    engine = EmotionRecognitionEngine(use_advanced_profile=True)
    user_id = "test_multimodal_user"

    # 测试输入
    from core.multimodal_input_processor import MultimodalInputProcessor
    processor = MultimodalInputProcessor(engine)

    # 1. 文本输入
    print("场景1: 用户发送文本消息")
    result = processor.process_input(
        "我今天感到很沮丧，什么都不想做",
        user_id=user_id,
        context="情绪低落"
    )
    print(f"路由: {result['routing_decision']['level']}")
    print()

    # 2. 语音输入
    audio_dir = Path("audio")
    if audio_dir.exists():
        audio_files = list(audio_dir.glob("*.wav"))
        for audio_file in audio_files[:1]:
            print("场景2: 用户发送语音消息")
            result = processor.process_input(
                str(audio_file),
                user_id=user_id,
                context="语音沟通"
            )
            print(f"路由: {result['routing_decision']['level']}")
            print(f"识别文本: {result.get('transcribed_text', 'N/A')}")
            print()

    # 3. 图片输入
    image_dir = Path("image")
    if image_dir.exists():
        image_files = list(image_dir.glob("*.jpg"))
        for image_file in image_files[:1]:
            print("场景3: 用户发送图片")
            result = processor.process_input(
                str(image_file),
                user_id=user_id,
                context="图片分享"
            )
            print(f"路由: {result['routing_decision']['level']}")
            print()

    # 生成画像报告
    print("生成综合画像报告...")
    report = engine.generate_profile_report(user_id)

    if report:
        print(report[:500])  # 显示前500字符
        print("...（报告较长，已截断）")
        print()

    print("=" * 70)
    print("真实场景测试完成")
    print("=" * 70)

    return True


if __name__ == "__main__":
    try:
        # 测试高级画像功能
        success = test_advanced_profile()

        # 测试真实场景
        success = test_real_scenario() and success

        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
