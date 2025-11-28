# Learning Agent Scoring & Recommendation System

## Overview

This comprehensive scoring and recommendation system calculates learner performance based on test marks and quiz marks, then provides personalized course recommendations. The system uses advanced algorithms to analyze learning patterns, identify strengths and weaknesses, and create tailored learning paths.

## Features

### 🎯 Core Scoring Features

- **Weighted Score Calculation**: Different test types have different weights (exams > assignments > tests > quizzes)
- **Recency Adjustment**: Older scores get reduced weight to reflect current performance
- **Performance Trend Analysis**: Identifies improving, stable, or declining performance patterns
- **Confidence Scoring**: Measures consistency in performance across different tests
- **Subject Analysis**: Identifies strongest and weakest subject areas

### 📊 Performance Analysis

- **Average Score Calculation**: Weighted average across all test results
- **Latest Score Tracking**: Most recent performance indicator
- **Score Trend Analysis**: Multi-period comparison to identify learning momentum
- **Strengths/Weaknesses Identification**: Subject-specific performance analysis
- **Recommendation Level Determination**: Beginner, intermediate, or advanced level assignment

### 🎓 Recommendation Engine

- **Personalized Course Matching**: Matches courses to learner's performance level
- **Difficulty Alignment**: Recommends appropriate difficulty levels based on performance
- **Subject-Based Filtering**: Considers learner's strongest subjects for recommendations
- **Confidence-Based Adjustments**: Adjusts recommendations based on performance consistency
- **Progression Planning**: Suggests next steps and learning paths

## System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Test Results  │───▶│  Scoring Engine  │───▶│ Recommendation  │
│                 │    │                  │    │   Engine        │
│ • Quizzes       │    │ • Weighted Calc  │    │                 │
│ • Tests         │    │ • Trend Analysis │    │ • Course Match  │
│ • Assignments   │    │ • Confidence     │    │ • Difficulty    │
│ • Exams         │    │ • Subject ID     │    │ • Learning Path │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Quick Start Guide

### 1. Basic Scoring Demo

Run the standalone scoring demonstration:

```bash
python scoring_recommendation_demo.py
```

This will:
- Generate sample test results for a demo learner
- Calculate performance scores and metrics
- Display detailed performance analysis
- Show personalized course recommendations
- Generate a complete learning path

### 2. API-Based Demo

Start the Flask API server first:

```bash
python flask_api.py
```

Then run the API demo:

```bash
python scoring_api_demo.py
```

This interactive demo will:
- Check API health and connectivity
- Submit multiple test results via API
- Retrieve score summaries and analytics
- Get personalized recommendations
- Generate learning paths

### 3. Direct Integration

Use the scoring system in your own applications:

```python
from ml.scoring_engine import ScoringEngine, get_learner_score_summary
from ml.score_based_recommender import ScoreBasedRecommender
from models.test_result import TestResult

# Initialize the scoring engine
scoring_engine = ScoringEngine()

# Create sample test results
test_results = [
    TestResult(
        learner_id="learner_123",
        test_id="quiz_001",
        test_type="quiz",
        course_id="python-basics",
        score=85,
        max_score=100
    )
]

# Generate score summary
score_summary = get_learner_score_summary("learner_123", test_results)

# Get recommendations
recommender = ScoreBasedRecommender()
recommendations = recommender.get_personalized_recommendations("learner_123", score_summary)
```

## API Endpoints

### Submit Test Result
```http
POST /api/scoring/test-result
Content-Type: application/json

{
    "learner_id": "learner_123",
    "test_id": "quiz_001",
    "test_type": "quiz",
    "course_id": "python-basics",
    "score": 85,
    "max_score": 100,
    "time_taken": 30,
    "attempts": 1
}
```

### Get Score Summary
```http
GET /api/scoring/learner/{learner_id}/score-summary
```

### Get Recommendations
```http
GET /api/scoring/learner/{learner_id}/recommendations
```

### Get Learning Path
```http
GET /api/scoring/learner/{learner_id}/learning-path
```

## Scoring Algorithm Details

### Weighted Score Calculation

The system uses different weights for different test types:

| Test Type | Weight | Description |
|-----------|--------|-------------|
| Exam | 0.7 | High-stakes final assessments |
| Assignment | 0.5 | Project-based evaluations |
| Test | 0.4 | Regular chapter/unit tests |
| Quiz | 0.3 | Quick knowledge checks |

### Recency Adjustment

Scores older than 30 days get reduced weight:
- 0-30 days: Full weight (100%)
- 30+ days: Reduced weight (minimum 70%)

### Performance Thresholds

| Score Range | Performance Level | Description |
|-------------|------------------|-------------|
| 90-100% | Excellent | Outstanding performance |
| 80-89% | Good | Solid understanding |
| 70-79% | Satisfactory | Adequate knowledge |
| 60-69% | Needs Improvement | Requires attention |
| <60% | Poor | Needs significant support |

### Recommendation Levels

Based on weighted scores, confidence, and trends:

| Level | Criteria | Description |
|-------|----------|-------------|
| Beginner | <70 points | New to the subject, needs foundational support |
| Intermediate | 70-84 points | Has basic knowledge, ready for more complex topics |
| Advanced | ≥85 points | Strong foundation, ready for challenging content |

## Recommendation Logic

### Match Score Components

1. **Difficulty Matching (40%)**: How well course difficulty matches learner level
2. **Performance Alignment (30%)**: Based on recent test scores
3. **Progression Score (20%)**: Considers improvement trend
4. **Subject Strength Bonus (10%)**: Leverages learner's strongest areas

### Course Selection Criteria

- **Difficulty alignment** with learner's current level
- **Subject relevance** to performance strengths
- **Progression appropriateness** based on learning momentum
- **Prerequisite satisfaction** checking

## Learning Path Generation

The system creates personalized learning paths by:

1. **Analyzing current performance** level and confidence
2. **Selecting appropriate courses** based on match scores
3. **Ordering courses logically** for progressive learning
4. **Estimating completion times** based on performance patterns
5. **Suggesting next steps** for continued development

### Learning Path Features

- **Sequential Course Ordering**: Logical progression from basic to advanced
- **Estimated Durations**: Personalized time estimates based on performance
- **Difficulty Progression**: Gradual increase in complexity
- **Skill Coverage Mapping**: Ensures comprehensive skill development
- **Outcome Expectations**: Clear learning objectives for each path

## Data Models

### TestResult Model
```python
class TestResult(BaseModel):
    id: str
    learner_id: str
    test_id: str
    test_type: str  # 'quiz', 'test', 'assignment', 'exam'
    course_id: str
    score: float
    max_score: float
    percentage: float
    time_taken: Optional[float]
    attempts: int
    passed: bool
    completed_at: datetime
    metadata: Dict[str, Any]
```

### LearnerScoreSummary Model
```python
class LearnerScoreSummary(BaseModel):
    learner_id: str
    total_tests: int
    average_score: float
    latest_score: float
    score_trend: str  # 'improving', 'declining', 'stable'
    strongest_subject: str
    weakest_subject: str
    recommendation_level: str  # 'beginner', 'intermediate', 'advanced'
    confidence_score: float
    recent_performance: List[TestResult]
```

## Configuration Options

### Scoring Engine Configuration
```python
scoring_engine = ScoringEngine()
scoring_engine.weight_config = {
    'quiz': 0.3,
    'test': 0.4,
    'assignment': 0.5,
    'exam': 0.7
}
scoring_engine.recency_decay_days = 30
```

### Recommender Configuration
```python
recommender = ScoreBasedRecommender()
recommender.difficulty_mapping = {
    'beginner': ['beginner', 'easy'],
    'intermediate': ['beginner', 'intermediate', 'medium'],
    'advanced': ['intermediate', 'advanced', 'difficult']
}
```

## Error Handling

The system includes comprehensive error handling:

- **Invalid test results**: Graceful handling of malformed data
- **Missing learner data**: Default responses for new learners
- **API timeouts**: Fallback mechanisms for service unavailability
- **Calculation errors**: Safe defaults and logging for debugging

## Performance Considerations

- **Efficient scoring**: O(n log n) for test result processing
- **Caching**: Score summaries cached for frequent access
- **Batch processing**: Support for bulk score calculations
- **Scalability**: Designed to handle thousands of learners

## Integration Examples

### Streamlit Integration
```python
import streamlit as st
from ml.scoring_engine import get_learner_score_summary

def show_score_dashboard(learner_id):
    score_summary = get_learner_score_summary(learner_id)
    
    st.metric("Average Score", f"{score_summary.average_score:.1f}%")
    st.metric("Performance Trend", score_summary.score_trend.title())
    st.metric("Recommendation Level", score_summary.recommendation_level.title())
```

### Django Integration
```python
from django.http import JsonResponse
from ml.score_based_recommender import get_score_based_recommendations

def get_recommendations(request, learner_id):
    recommendations = get_score_based_recommendations(learner_id)
    return JsonResponse(recommendations)
```

### React Integration
```javascript
// Using fetch API
const getRecommendations = async (learnerId) => {
  const response = await fetch(`/api/scoring/learner/${learnerId}/recommendations`);
  const data = await response.json();
  return data.recommendations;
};
```

## Testing

Run the test suite:

```bash
python -m pytest test_scoring_system.py -v
```

Test coverage includes:
- Score calculation accuracy
- Recommendation relevance
- API endpoint functionality
- Edge case handling
- Performance benchmarking

## Monitoring and Analytics

The system provides analytics endpoints for monitoring:

- **Learner performance trends** across the platform
- **Recommendation effectiveness** metrics
- **Course completion rates** by difficulty level
- **Learning path success rates**

## Future Enhancements

Planned features include:
- **Machine learning models** for predictive scoring
- **Social learning** recommendations
- **Real-time adaptive** difficulty adjustment
- **Collaborative filtering** for peer-based suggestions
- **Advanced analytics** dashboard for educators

## Support and Documentation

For questions, issues, or contributions:
- Check the example scripts for usage patterns
- Review the API documentation for endpoint details
- Examine the test files for implementation examples
- Refer to the configuration options for customization

## License

This scoring and recommendation system is part of the Learning Agent project and follows the same licensing terms.