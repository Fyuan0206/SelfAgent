"""
测试讯飞ASR单独功能
"""

import sys
from pathlib import Path
import yaml
from loguru import logger

project_root = str(Path(__file__).parent)
sys.path.insert(0, project_root)

from core.emotion_extractor import EmotionExtractor

# 配置日志
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | {name}:{function}:{line} - {message}",
    level="DEBUG"
)

def test_xunfei_asr():
    print("=" * 60)
    print("讯飞ASR单独测试")
    print("=" * 60)

    # 加载配置
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # 初始化提取器
    print("\n1. 初始化提取器...")
    extractor = EmotionExtractor(config)

    # 检查配置
    xf_config = config.get('xunfei_asr', {})
    print(f"\n2. 讯飞配置:")
    print(f"   APPID: {xf_config.get('app_id')}")
    print(f"   API Key: {xf_config.get('api_key')[:10]}...")
    print(f"   API Secret: {xf_config.get('api_secret')[:10]}...")

    # 生成鉴权URL
    print(f"\n3. 生成鉴权URL...")
    auth_url = extractor._create_xunfei_auth_url()
    if auth_url:
        print(f"   ✓ URL生成成功")
        print(f"   URL长度: {len(auth_url)} 字符")
    else:
        print(f"   ✗ URL生成失败")
        return

    # 查找测试音频
    audio_dir = Path("audio")
    if not audio_dir.exists():
        print(f"\n   ✗ audio文件夹不存在")
        return

    audio_files = list(audio_dir.glob("*.wav"))
    if not audio_files:
        print(f"\n   ✗ 没有找到音频文件")
        return

    audio_path = str(audio_files[0])
    print(f"\n4. 测试音频: {audio_files[0].name}")

    # 转换音频
    print(f"\n5. 转换音频为PCM...")
    pcm_data = extractor._convert_audio_to_pcm(audio_path)
    if pcm_data:
        print(f"   ✓ 转换成功: {len(pcm_data)} bytes")
    else:
        print(f"   ✗ 转换失败")
        return

    # 进行ASR
    print(f"\n6. 开始讯飞ASR识别...")
    print(f"   连接到讯飞服务器...")
    result = extractor._xunfei_websocket_asr(auth_url, pcm_data)

    if result:
        print(f"\n   ✓ 识别成功!")
        print(f"   识别结果: {result}")
    else:
        print(f"\n   ✗ 识别失败")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_xunfei_asr()
