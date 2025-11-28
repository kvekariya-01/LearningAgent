from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid

class TestResult(BaseModel):
    """Model for storing test/quiz results"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    learner_id: str
    test_id: str
    test_type: str  # 'quiz', 'test', 'assignment', 'exam'
    course_id: str
    content_id: Optional[str] = None
    score: float  # Score achieved (0-100)
    max_score: float = 100.0  # Maximum possible score
    percentage: float  # Percentage score
    time_taken: Optional[float] = None  # Time in minutes
    attempts: int = 1  # Number of attempts taken
    passed: bool  # Whether the test was passed
    completed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def __init__(self, **data):
        if 'score' in data and 'max_score' in data:
            percentage = (data['score'] / data['max_score']) * 100
            data['percentage'] = percentage
            data['passed'] = percentage >= 60  # 60% passing threshold
        super().__init__(**data)

    def to_dict(self) -> Dict[str, Any]:
        data = self.model_dump()
        data["_id"] = data["id"]
        data["completed_at"] = data["completed_at"].isoformat()
        return data

class LearnerScoreSummary(BaseModel):
    """Model for aggregated learner score summary"""
    learner_id: str
    total_tests: int
    average_score: float
    latest_score: float
    score_trend: str  # 'improving', 'declining', 'stable'
    strongest_subject: str
    weakest_subject: str
    recommendation_level: str  # 'beginner', 'intermediate', 'advanced'
    confidence_score: float  # 0-100 based on consistency
    recent_performance: List[TestResult] = Field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        data = self.model_dump()
        if 'recent_performance' in data:
            data['recent_performance'] = [
                test.to_dict() if hasattr(test, 'to_dict') else test 
                for test in data['recent_performance']
            ]
        return data