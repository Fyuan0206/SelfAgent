from typing import Dict, Any, Optional
from datetime import datetime
import json
import os
from loguru import logger

class StateManager:
    """会话状态管理器"""
    
    def __init__(self, state_file: str = "session_state.json"):
        self.state_file = state_file
        self.state: Dict[str, Any] = self._load_state()
        
    def _load_state(self) -> Dict[str, Any]:
        """加载状态"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"加载状态失败: {e}")
        return self._get_default_state()
        
    def _get_default_state(self) -> Dict[str, Any]:
        """默认状态"""
        return {
            "session_id": datetime.now().strftime("%Y%m%d%H%M%S"),
            "risk_level": "LOW",
            "emotion_history": [],
            "interventions": [],
            "last_interaction": None,
            "metadata": {}
        }
        
    def save_state(self):
        """保存状态"""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存状态失败: {e}")
            
    def update_risk_level(self, level: str):
        """更新风险等级"""
        self.state["risk_level"] = level
        self.save_state()
        
    def add_emotion_record(self, emotion: str, score: float):
        """添加情绪记录"""
        self.state["emotion_history"].append({
            "timestamp": datetime.now().isoformat(),
            "emotion": emotion,
            "score": score
        })
        # 保持历史记录长度在合理范围
        if len(self.state["emotion_history"]) > 50:
            self.state["emotion_history"] = self.state["emotion_history"][-50:]
        self.save_state()
        
    def get_context(self) -> Dict[str, Any]:
        """获取当前上下文"""
        return self.state
