from enum import Enum

class RiskLevel(Enum):
    L1 = "L1"  # Daily emotion state, no significant risk
    L2 = "L2"  # Emotional distress, negative emotions or dysregulation
    L3 = "L3"  # Crisis state, self-harm or severe psychological risk

class EmotionType(Enum):
    ANXIETY = "Anxiety"
    SADNESS = "Sadness"
    ANGER = "Anger"
    SHAME = "Shame"
    EMPTINESS = "Emptiness"
    JOY = "Joy"
    # Add more as needed based on 12 labels mentioned

class SkillModule(Enum):
    MINDFULNESS = "Mindfulness"
    DISTRESS_TOLERANCE = "Distress Tolerance"
    EMOTION_REGULATION = "Emotion Regulation"
    INTERPERSONAL_EFFECTIVENESS = "Interpersonal Effectiveness"
