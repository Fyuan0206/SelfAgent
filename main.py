import os
import sys
import logging
from dotenv import load_dotenv
from app.core.agent import SelfAgent
from app.models.data_models import UserInput

# Load environment variables
load_dotenv()

def setup_environment():
    """Ensure necessary environment variables are set."""
    if not os.environ.get("OPENAI_API_KEY"):
        print("\n[警告] 未在环境变量或 .env 文件中找到 OPENAI_API_KEY。")
        key = input("请输入您的 OpenAI API Key: ").strip()
        if key:
            os.environ["OPENAI_API_KEY"] = key
        else:
            print("错误: 必须提供 API Key 才能运行 Agent。正在退出。")
            sys.exit(1)
            
    # Default to deepseek-chat if not set
    if not os.environ.get("MODEL_NAME"):
        os.environ["MODEL_NAME"] = "deepseek-chat"

def main():
    print("==================================================")
    print("      Self-Agent 智能情绪支持系统 (CLI版)         ")
    print("==================================================")
    
    setup_environment()
    
    model_name = os.environ['MODEL_NAME']
    print(f"\n[系统] 正在初始化 Agent (模型: {model_name})...")
    
    try:
        # Initialize the Self-Agent
        # The agent is configured with tools to detect and analyze emotions automatically
        agent = SelfAgent(model_type=model_name)
        
        print("\n[Self-Agent] 你好！我是你的 AI 情绪伙伴。")
        print("[Self-Agent] 我可以感知你的情绪并提供支持。随时可以跟我聊天。")
        print("(输入 'exit' 或 'quit' 退出)\n")
        
        user_id = "user_cli_001"
        
        while True:
            try:
                user_text = input("你: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n正在退出...")
                break
                
            if not user_text:
                continue
                
            if user_text.lower() in ['exit', 'quit', 'bye', '退出']:
                print("Self-Agent: 再见！希望你今天过得愉快。")
                break
                
            # Create input object
            user_input = UserInput(user_id=user_id, text=user_text)
            
            # Process interaction
            print("...(思考与感知中)...")
            try:
                # The agent will autonomously decide to use 'detect_emotion_and_risk' 
                # or 'analyze_user_emotion' based on the conversation context.
                response = agent.process_interaction(user_input)
                print(f"Self-Agent: {response}\n")
            except Exception as e:
                print(f"[错误] 处理消息失败: {e}")
                
    except Exception as e:
        print(f"\n[严重错误] 无法初始化 Agent: {e}")
        print("请检查您的配置 (.env) 和网络连接。")

if __name__ == "__main__":
    main()
