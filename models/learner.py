from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import uuid

class Activity(BaseModel):
    timestamp: str
    activity_type: str
    duration: float
    score: Optional[float] = None

class LearnerProfile(BaseModel):
    """Enhanced learner profile with complete learning data"""
    learning_style_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    primary_interest_areas: List[str] = Field(default_factory=list)
    skill_levels: Dict[str, str] = Field(default_factory=dict)  # subject: level
    accessibility_needs: List[str] = Field(default_factory=list)
    study_schedule: Dict[str, Any] = Field(default_factory=dict)
    motivation_factors: List[str] = Field(default_factory=list)
    learning_pace_preference: str = Field(default="mixed")  # slow, normal, fast
    engagement_history: Dict[str, Any] = Field(default_factory=dict)

class LearningMetrics(BaseModel):
    """Complete learning history and metrics"""
    total_study_time: float = Field(default=0.0)  # in hours
    average_session_length: float = Field(default=0.0)  # in minutes
    completion_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    knowledge_retention_score: float = Field(default=0.0, ge=0.0, le=1.0)
    skill_progression: List[Dict[str, Any]] = Field(default_factory=list)
    learning_velocity_trend: str = Field(default="stable")  # accelerating, stable, decelerating
    preferred_study_times: List[str] = Field(default_factory=list)
    difficulty_adjustment_count: int = Field(default=0)

class Learner(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    age: int
    gender: str
    learning_style: str
    preferences: List[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    activities: List[Activity] = Field(default_factory=list)
    activity_count: int = 0
    profile: LearnerProfile = Field(default_factory=LearnerProfile)
    learning_metrics: LearningMetrics = Field(default_factory=LearningMetrics)
    meta: Dict[str, Any] = Field(default_factory=dict)

    # [OK] Automatically convert string to list if needed
    @field_validator("preferences", mode="before")
    def ensure_list(cls, v):
        if isinstance(v, str):
            return [v]
        if not isinstance(v, list):
            raise TypeError("Preferences must be a list or string")
        return v

    def log_activity(self, activity_type: str, duration: float, score: Optional[float] = None):
        activity = Activity(
            timestamp=datetime.utcnow().isoformat(),
            activity_type=activity_type,
            duration=duration,
            score=score
        )
        self.activities.append(activity)
        self.activity_count += 1

    def to_dict(self) -> Dict[str, Any]:
        data = self.model_dump()
        data["_id"] = data["id"]  # for MongoDB compatibility
        data["created_at"] = data["created_at"].isoformat()
        return data
