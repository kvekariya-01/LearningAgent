from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid

class InteractionMetrics(BaseModel):
    click_count: int = 0
    scroll_depth: float = 0.0
    pause_count: int = 0
    replay_count: int = 0
    completion_percentage: float = 0.0
    attention_span: float = 0.0
    interaction_frequency: float = 0.0
    device_type: str = "unknown"
    browser_type: str = "unknown"

class EngagementPattern(BaseModel):
    learning_session_id: Optional[str] = None
    previous_engagement_time: Optional[datetime] = None
    engagement_frequency_score: float = 0.0
    consistency_score: float = 0.0
    engagement_streak: int = 0
    preferred_engagement_times: List[str] = []
    engagement_method: str = "standard"

class Engagement(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    learner_id: str
    content_id: str
    course_id: str
    engagement_type: str
    duration: Optional[float] = None
    score: Optional[float] = None
    feedback: Optional[str] = None
    interaction_metrics: InteractionMetrics = InteractionMetrics()
    engagement_pattern: EngagementPattern = EngagementPattern()
    metadata: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        data = self.model_dump()
        data["_id"] = data["id"]
        return data