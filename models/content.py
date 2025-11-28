from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid

class ContentMetadata(BaseModel):
    """Enhanced content metadata with topics, prerequisites, and difficulty"""
    topics: List[str] = Field(default_factory=list)  # Main topics covered
    prerequisites: List[str] = Field(default_factory=list)  # Required knowledge/skills
    learning_objectives: List[str] = Field(default_factory=list)
    estimated_completion_time: Optional[int] = None  # in minutes
    difficulty_score: int = Field(default=1, ge=1, le=10)  # Numeric difficulty 1-10
    skill_requirements: Dict[str, str] = Field(default_factory=dict)  # skill: level required
    content_sources: List[str] = Field(default_factory=list)
    accessibility_features: List[str] = Field(default_factory=list)
    assessment_criteria: List[str] = Field(default_factory=list)
    related_content: List[str] = Field(default_factory=list)  # Content IDs

class Content(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    content_type: str  # e.g., 'video', 'quiz', 'article', 'project', 'assignment'
    course_id: str
    module_id: Optional[str] = None
    difficulty_level: str  # e.g., 'beginner', 'intermediate', 'advanced'
    tags: List[str] = Field(default_factory=list)
    metadata: ContentMetadata = Field(default_factory=ContentMetadata)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        data = self.model_dump()
        data["_id"] = data["id"]
        # Keep datetime objects for MongoDB BSON compatibility
        return data