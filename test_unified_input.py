"""
统一的多模态输入测试
演示如何自动识别和处理不同类型的输入（文本、语音、图片）
"""

import sys
from pathlib import Path
import cv2
sys.path.insert(0, str(Path(__file__).parent))

from core.emotion_engine import EmotionRecognitionEngine
from core.multimodal_input_processor import MultimodalInputProcessor, InputType


def test_unified_multimodal_input():
    """测试统一的多模态输入处理"""
    print("=" * 60)
    print("统一多模态输入测试")
    print("=" * 60 + "\n")

    # 初始化引擎和处理器
    print("初始化系统...")
    engine = EmotionRecognitionEngine()
    processor = MultimodalInputProcessor(engine)
    print("   ✓ 系统初始化成功\n")

    # ==================== 测试1: 文本输入 ====================
    print("=" * 60)
    print("测试1: 文本输入")
    print("=" * 60 + "\n")

    text_inputs = [
        "我今天很开心，感觉一切都很好",  # 积极情绪
        "我感到很焦虑，睡不着觉",      # 焦虑情绪
        "我想伤害自己",                # 危机情况
    ]

    for i, text in enumerate(text_inputs, 1):
        print(f"--- 文本输入 {i} ---")
        result = processor.process_input(text, user_id=f"test_text_{i}")

        actual_route = result['routing_decision']['level']
        emotions = result['emotion_features']['emotions']
        active_emotions = {k: round(v, 2) for k, v in emotions.items() if v > 0}

        print(f"   输入: {text}")
        print(f"   类型: {result['input_type']}")
        print(f"   路由: {actual_route}")
        print(f"   情绪: {active_emotions if active_emotions else '无明显负面情绪'}")
        print()

    # ==================== 测试2: 语音输入 ====================
    print("=" * 60)
    print("测试2: 语音输入")
    print("=" * 60 + "\n")

    audio_dir = Path("audio")
    if audio_dir.exists():
        for audio_file in audio_dir.glob("*.wav"):
            if audio_file.name.startswith('.'):
                continue

            print(f"--- 语音输入 ---")
            result = processor.process_input(str(audio_file), user_id=f"test_audio")

            actual_route = result['routing_decision']['level']
            emotions = result['emotion_features']['emotions']
            active_emotions = {k: round(v, 2) for k, v in emotions.items() if v > 0}

            print(f"   输入: {audio_file.name}")
            print(f"   类型: {result['input_type']}")
            print(f"   识别文本: {result.get('transcribed_text', 'N/A')}")
            print(f"   路由: {actual_route}")
            print(f"   情绪: {active_emotions if active_emotions else '无明显负面情绪'}")

            # 音频特征
            audio_feats = result['emotion_features'].get('audio_features')
            if audio_feats:
                print(f"   音频特征: pitch={audio_feats.get('mean_pitch', 0):.2f}, "
                      f"energy={audio_feats.get('energy', 0):.4f}")
            print()

    # ==================== 测试3: 图片输入 ====================
    print("=" * 60)
    print("测试3: 图片输入")
    print("=" * 60 + "\n")

    image_dir = Path("image")
    if image_dir.exists():
        for image_file in image_dir.glob("*.jpg"):
            if image_file.name.startswith('.'):
                continue

            print(f"--- 图片输入 ---")
            result = processor.process_input(str(image_file), user_id=f"test_image")

            actual_route = result['routing_decision']['level']
            emotions = result['emotion_features']['emotions']
            active_emotions = {k: round(v, 2) for k, v in emotions.items() if v > 0}

            # 获取专用图像情绪
            image_emotions = processor.extractor.extract_image_emotion(str(image_file))
            active_image_emotions = {k: round(v, 2) for k, v in image_emotions.items() if v > 0}

            print(f"   输入: {image_file.name}")
            print(f"   类型: {result['input_type']}")
            print(f"   路由: {actual_route}")
            if active_image_emotions:
                print(f"   图像情绪: {active_image_emotions}")
            else:
                print(f"   情绪: 无明显负面情绪")
            print()

    # ==================== 测试4: 混合输入 ====================
    print("=" * 60)
    print("测试4: 自动类型检测")
    print("=" * 60 + "\n")

    # 测试不同类型的输入，看是否能自动识别
    test_inputs = [
        ("文本", "你好，今天天气不错"),
        ("音频文件", str(audio_dir / "男人开心大笑声_耳聆网_[声音ID：21063].wav") if audio_dir.exists() else None),
        ("图片文件", str(image_dir / "pexels-olly-3767426.jpg") if image_dir.exists() else None),
    ]

    for input_type, input_data in test_inputs:
        if input_data is None:
            continue

        print(f"--- {input_type} ---")

        # 检测类型
        detected_type = processor.detect_input_type(input_data)
        print(f"   检测类型: {detected_type.value}")

        # 处理输入
        result = processor.process_input(input_data, user_id=f"test_auto_{input_type}")

        print(f"   输入: {input_data if isinstance(input_data, str) else input_data[:50]}")
        print(f"   实际类型: {result['input_type']}")
        print(f"   路由: {result['routing_decision']['level']}")
        print()

    # ==================== 测试5: 字典格式输入 ====================
    print("=" * 60)
    print("测试5: 字典格式输入（API风格）")
    print("=" * 60 + "\n")

    # 模拟API请求格式
    api_requests = [
        {"type": "text", "content": "我感到很绝望"},
        {"type": "image", "path": str(image_dir / "pexels-olly-3767426.jpg")} if image_dir.exists() else None,
    ]

    for i, request in enumerate(api_requests, 1):
        if request is None:
            continue

        print(f"--- API请求 {i} ---")
        result = processor.process_input(request, user_id=f"test_api_{i}")

        print(f"   请求类型: {request.get('type')}")
        print(f"   路由: {result['routing_decision']['level']}")
        print(f"   情绪: {result['emotion_features']['emotions']}")
        print()

    print("=" * 60)
    print("✓ 所有测试完成")
    print("=" * 60)

    return True


def demo_usage():
    """演示使用示例"""
    print("\n" + "=" * 60)
    print("使用示例")
    print("=" * 60 + "\n")

    print("""
# 初始化系统
from core.emotion_engine import EmotionRecognitionEngine
from core.multimodal_input_processor import MultimodalInputProcessor

engine = EmotionRecognitionEngine()
processor = MultimodalInputProcessor(engine)

# 1. 处理文本输入
result = processor.process_input("我今天很开心", user_id="user123")

# 2. 处理语音文件
result = processor.process_input("audio/test.wav", user_id="user123")

# 3. 处理图片文件
result = processor.process_input("image/test.jpg", user_id="user123")

# 4. 处理Base64编码的音频
audio_base64 = "data:audio/wav;base64,UklGRiQAAABXQVZF..."
result = processor.process_input(audio_base64, user_id="user123")

# 5. 处理Base64编码的图片
image_base64 = "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
result = processor.process_input(image_base64, user_id="user123")

# 6. 处理字典格式（API风格）
request = {
    "type": "text",
    "content": "我感到很焦虑"
}
result = processor.process_input(request, user_id="user123")

# 获取结果
print(f"路由级别: {result['routing_decision']['level']}")
print(f"风险等级: {result['intervention_assessment']['risk_level']}")
print(f"情绪: {result['emotion_features']['emotions']}")
""")


if __name__ == "__main__":
    try:
        success = test_unified_multimodal_input()
        demo_usage()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
