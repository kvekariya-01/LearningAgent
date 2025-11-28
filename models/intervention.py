from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import uuid

class Intervention(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    learner_id: str
    intervention_type: str  # e.g., 'motivational_message', 'difficulty_adjustment'
    message: str
    triggered_by: str  # e.g., 'low_score', 'high_improvement'
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = self.model_dump()
        data["_id"] = data["id"]
        # Keep timestamp as datetime object for MongoDB BSON compatibility
        return data