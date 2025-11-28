from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid

class LearningHistory(BaseModel):
    """Complete learning history with scores, completed modules, and time tracking"""
    total_modules_completed: int = Field(default=0)
    total_time_spent: float = Field(default=0.0)  # in hours
    average_score: float = Field(default=0.0)
    best_score: float = Field(default=0.0)
    improvement_rate: float = Field(default=0.0)  # percentage improvement over time
    skill_breakdown: Dict[str, Dict[str, float]] = Field(default_factory=dict)  # skill: {score, attempts, time_spent}
    module_completion_sequence: List[str] = Field(default_factory=list)  # Order of completed modules
    learning_gaps_identified: List[str] = Field(default_factory=list)
    mastery_levels: Dict[str, str] = Field(default_factory=dict)  # skill: mastery_level

class LearningVelocity(BaseModel):
    """Detailed learning pace calculation"""
    current_velocity: float = Field(default=0.0)  # modules per week
    velocity_trend: str = Field(default="stable")  # accelerating, stable, decelerating
    peak_velocity: float = Field(default=0.0)
    average_session_length: float = Field(default=0.0)  # in minutes
    study_frequency: float = Field(default=0.0)  # sessions per week
    optimal_pace_indicator: float = Field(default=0.5)  # 0-1 scale, how close to optimal

class ProgressLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    learner_id: str
    milestone: str  # e.g., 'module_completed', 'quiz_passed', 'skill_mastered'
    engagement_score: float
    learning_velocity: LearningVelocity = Field(default_factory=LearningVelocity)
    learning_history: LearningHistory = Field(default_factory=LearningHistory)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = self.model_dump()
        data["_id"] = data["id"]
        # Keep timestamp as datetime object for MongoDB BSON compatibility
        return data