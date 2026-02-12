from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from .types import RiskLevel, EmotionType, SkillModule

@dataclass
class UserInput:
    user_id: str
    text: Optional[str] = None
    audio_data: Optional[bytes] = None  # Placeholder for audio
    image_data: Optional[bytes] = None  # Placeholder for image
    context_history: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class EmotionOutput:
    primary_emotions: List[EmotionType]
    arousal: float  # 0.0 to 1.0
    valence: float  # -1.0 to 1.0
    risk_level: RiskLevel
    situation_summary: str
    routing_suggestion: str

@dataclass
class DBTRecommendation:
    modules: List[SkillModule]
    specific_skills: List[str]
    rationale: str
    guidance_strategy: str
    execution_template: Dict[str, Any]

@dataclass
class AgentState:
    user_id: str
    short_term_mood: Dict[str, Any]
    long_term_profile: Dict[str, Any]
    current_risk_level: RiskLevel = RiskLevel.L1
    last_intervention: Optional[str] = None
