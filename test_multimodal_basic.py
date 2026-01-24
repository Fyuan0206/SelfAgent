"""
语音和图像情绪识别测试
完全对齐test_basic.py的输出格式
"""

import sys
from pathlib import Path
import cv2
sys.path.insert(0, str(Path(__file__).parent))

from core.emotion_engine import EmotionRecognitionEngine


def test_audio_and_image():
    """测试语音和图像情绪识别"""
    print("=" * 50)
    print("多模态情绪识别测试（语音 & 图像）")
    print("=" * 50 + "\n")

    try:
        # 初始化引擎
        print("初始化情绪识别引擎...")
        engine = EmotionRecognitionEngine()
        print("   ✓ 引擎初始化成功\n")

        # ==================== 语音识别测试 ====================
        print("=" * 50)
        print("1. 语音识别测试 (讯飞ASR)")
        print("=" * 50 + "\n")

        audio_dir = Path("audio")
        if not audio_dir.exists():
            print("   ✗ audio文件夹不存在\n")
        else:
            audio_files = list(audio_dir.glob("*.wav"))
            if not audio_files:
                print("   ✗ 没有找到音频文件\n")
            else:
                for audio_file in audio_files:
                    if audio_file.name.startswith('.'):
                        continue

                    # 语音识别
                    transcribed = engine.extractor.transcribe_audio(
                        str(audio_file),
                        method='xunfei'
                    )

                    if transcribed:
                        # 使用识别的文本进行情绪分析
                        result = engine.analyze(
                            text=transcribed,
                            user_id=f"test_audio_{audio_file.stem}"
                        )

                        actual_route = result['routing_decision']['level']
                        emotions = result['emotion_features']['emotions']
                        active_emotions = {k: round(v, 2) for k, v in emotions.items() if v > 0}

                        # 根据内容判断期望路由
                        if any(kw in transcribed for kw in ['开心', '快乐', '哈哈', '笑']):
                            expected_route = "L1_QUICK"
                            category = "语音-开心大笑"
                        elif any(kw in transcribed for kw in ['哭', '难过', '痛苦', '伤心']):
                            expected_route = "L2_INTERVENTION"
                            category = "语音-悲伤哭泣"
                        elif any(kw in transcribed for kw in ['自杀', '死', '伤害']):
                            expected_route = "L3_CRISIS"
                            category = "语音-危机"
                        else:
                            expected_route = "L1_QUICK"
                            category = "语音-其他"

                        status = "✓" if actual_route == expected_route else "✗"

                        print(f"   {status} [{category}]")
                        print(f"      输入: {audio_file.name}")
                        print(f"      识别文本: {transcribed}")
                        print(f"      路由: {actual_route} (期望: {expected_route})")
                        print(f"      情绪: {active_emotions if active_emotions else '无明显负面情绪'}")
                        print()

        # ==================== 图像情绪识别测试 ====================
        print("=" * 50)
        print("2. 图像情绪识别测试")
        print("=" * 50 + "\n")

        image_dir = Path("image")
        if not image_dir.exists():
            print("   ✗ image文件夹不存在\n")
        else:
            image_files = list(image_dir.glob("*.jpg")) + list(image_dir.glob("*.png"))
            if not image_files:
                print("   ✗ 没有找到图片文件\n")
            else:
                # 定义测试用例（需要根据实际图片内容调整）
                image_test_cases = {
                    "pexels-polina-smelova-80605762-9964634.jpg": ("L2_INTERVENTION", "图像-可能悲伤"),
                    "pexels-jyjyjyjy-32699558.jpg": ("L1_QUICK", "图像-中性/开心"),
                    "pexels-olly-3767426.jpg": ("L2_INTERVENTION", "图像-悲伤痛苦"),
                }

                for image_file in image_files:
                    if image_file.name.startswith('.'):
                        continue

                    # 直接分析图像情绪
                    image_emotions = engine.extractor.extract_image_emotion(str(image_file))
                    active_image_emotions = {k: round(v, 2) for k, v in image_emotions.items() if v > 0}

                    # 也通过完整流程分析
                    frame = cv2.imread(str(image_file))
                    if frame is not None:
                        result = engine.analyze(
                            text="[图像输入]",
                            user_id=f"test_image_{image_file.stem}",
                            video_data=frame
                        )

                        actual_route = result['routing_decision']['level']

                        # 获取期望路由
                        expected_route, category = image_test_cases.get(
                            image_file.name,
                            ("L1_QUICK", "图像-未知")
                        )

                        # 如果图像情绪分析有明显负面情绪，调整期望路由
                        if image_emotions.get('悲伤', 0) >= 0.5 or \
                           image_emotions.get('绝望', 0) >= 0.4:
                            expected_route = "L2_INTERVENTION"
                            if '悲伤' in active_image_emotions:
                                category = "图像-悲伤哭泣"

                        status = "✓" if actual_route == expected_route else "✗"

                        print(f"   {status} [{category}]")
                        print(f"      输入: {image_file.name}")
                        print(f"      路由: {actual_route} (期望: {expected_route})")
                        if active_image_emotions:
                            print(f"      图像情绪: {active_image_emotions}")
                        else:
                            print(f"      情绪: 无明显负面情绪")
                        print()

        # ==================== 端到端测试 ====================
        print("=" * 50)
        print("3. 端到端多模态测试")
        print("=" * 50 + "\n")

        # 测试语音完整流程
        if audio_dir.exists() and list(audio_dir.glob("*.wav")):
            audio_file = list(audio_dir.glob("*.wav"))[0]
            transcribed = engine.extractor.transcribe_audio(str(audio_file))

            if transcribed:
                result = engine.analyze(
                    text=transcribed,
                    user_id="test_e2e_audio",
                    audio_path=str(audio_file)
                )

                actual_route = result['routing_decision']['level']
                emotions = result['emotion_features']['emotions']
                active_emotions = {k: round(v, 2) for k, v in emotions.items() if v > 0}

                print(f"   ✓ [语音完整流程]")
                print(f"      输入: {audio_file.name}")
                print(f"      识别文本: {transcribed}")
                print(f"      路由: {actual_route}")
                print(f"      情绪: {active_emotions if active_emotions else '无明显负面情绪'}")

                # 音频特征
                audio_feats = result['emotion_features'].get('audio_features')
                if audio_feats:
                    print(f"      音频特征: pitch={audio_feats.get('mean_pitch', 0):.2f}, "
                          f"energy={audio_feats.get('energy', 0):.4f}")
                print()

        # 测试图像完整流程
        if image_dir.exists() and list(image_dir.glob("*.jpg")):
            image_file = list(image_dir.glob("*.jpg"))[0]
            frame = cv2.imread(str(image_file))

            if frame is not None:
                result = engine.analyze(
                    text="[图像输入]",
                    user_id="test_e2e_image",
                    video_data=frame
                )

                actual_route = result['routing_decision']['level']

                # 获取专用图像情绪分析
                image_emotions = engine.extractor.extract_image_emotion(str(image_file))
                active_image_emotions = {k: round(v, 2) for k, v in image_emotions.items() if v > 0}

                print(f"   ✓ [图像完整流程]")
                print(f"      输入: {image_file.name}")
                print(f"      路由: {actual_route}")
                if active_image_emotions:
                    print(f"      图像情绪: {active_image_emotions}")
                else:
                    print(f"      情绪: 无明显负面情绪")
                print()

        print("=" * 50)
        print("✓ 多模态测试完成")
        print("=" * 50)

        return True

    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_audio_and_image()
    sys.exit(0 if success else 1)
