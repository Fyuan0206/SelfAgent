"""
测试真实音频和图像数据
"""
import sys
import os
import cv2
from pathlib import Path

# 添加项目根目录到路径
project_root = str(Path(__file__).parent)
sys.path.insert(0, project_root)

from core.emotion_engine import EmotionRecognitionEngine

def test_real_data():
    print("开始测试真实音频和图像数据...\n")
    
    engine = EmotionRecognitionEngine()
    
    # 1. 测试音频
    audio_dir = Path("audio")
    if audio_dir.exists():
        print("=" * 50)
        print("测试音频文件:")
        for audio_file in audio_dir.glob("*"):
            if audio_file.name.startswith('.'): continue
            
            print(f"\n正在分析音频: {audio_file.name}")
            try:
                # 简单的情绪分析调用
                result = engine.analyze(
                    text="这是一个音频测试",  # 占位文本
                    user_id=f"test_audio_{audio_file.stem}",
                    audio_path=str(audio_file)
                )
                
                audio_feats = result['emotion_features'].get('audio_features')
                if audio_feats:
                    print(f"   ✓ 特征提取成功")
                    print(f"   特征概览: {list(audio_feats.keys())}")
                    # 打印一些关键特征值
                    print(f"   Pitch: {audio_feats.get('mean_pitch', 0):.2f}")
                    print(f"   Energy: {audio_feats.get('energy', 0):.2f}")
                else:
                    print("   ✗ 特征提取失败")
            except Exception as e:
                print(f"   ✗ 分析出错: {e}")
                
    # 2. 测试图像
    image_dir = Path("image")
    if image_dir.exists():
        print("\n" + "=" * 50)
        print("测试图像文件:")
        for image_file in image_dir.glob("*"):
            if image_file.name.startswith('.'): continue
            
            print(f"\n正在分析图像: {image_file.name}")
            try:
                # 读取图像
                frame = cv2.imread(str(image_file))
                if frame is None:
                    print("   ✗ 无法读取图像文件")
                    continue
                    
                result = engine.analyze(
                    text="这是一个图像测试",
                    user_id=f"test_image_{image_file.stem}",
                    video_data=frame
                )
                
                video_feats = result['emotion_features'].get('video_features')
                if video_feats:
                    print(f"   ✓ 特征提取成功")
                    print(f"   特征概览: {list(video_feats.keys())}")
                    print(f"   Brightness: {video_feats.get('brightness', 0):.2f}")
                    print(f"   Contrast: {video_feats.get('contrast', 0):.2f}")
                else:
                    print("   ✗ 特征提取失败")
            except Exception as e:
                print(f"   ✗ 分析出错: {e}")

if __name__ == "__main__":
    test_real_data()
