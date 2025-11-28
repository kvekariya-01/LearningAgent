# Score-Based Course Recommendation System

## Overview

This document describes the comprehensive scoring and recommendation system that calculates learner performance based on test and quiz marks, then provides personalized course recommendations based on those scores.

## 🎯 Features

- **Comprehensive Scoring System**: Calculates weighted scores based on test types, recency, and performance consistency
- **Intelligent Recommendations**: Provides course recommendations based on learner performance analysis
- **Learning Path Generation**: Creates personalized learning paths based on scoring insights
- **Performance Analytics**: Tracks learner progress and provides detailed analytics
- **MongoDB Atlas Integration**: Seamlessly integrates with your existing MongoDB Atlas database

## 📊 Scoring Algorithm

### Test Type Weighting
The system uses different weights for different types of assessments:

- **Quiz**: 30% weight (lower stakes, frequent assessments)
- **Test**: 40% weight (standard assessments)
- **Assignment**: 50% weight (project-based work)
- **Exam**: 70% weight (comprehensive assessments)

### Recency Decay
Scores older than 30 days receive reduced weight to emphasize recent performance:
- Scores within 30 days: Full weight
- Scores older than 30 days: Up to 30% reduction

### Performance Metrics

1. **Weighted Average Score**: Time-adjusted, type-weighted average
2. **Score Trend**: Improving, stable, or declining based on recent vs. earlier performance
3. **Confidence Score**: Consistency measure (0-100) based on performance variation
4. **Recommendation Level**: Beginner, Intermediate, or Advanced based on overall performance

## 🏗️ System Architecture

### Data Models

#### TestResult Model
```python
class TestResult(BaseModel):
    id: str
    learner_id: str
    test_id: str
    test_type: str  # 'quiz', 'test', 'assignment', 'exam'
    course_id: str
    score: float  # Actual score achieved
    max_score: float  # Maximum possible score
    percentage: float  # Calculated percentage
    time_taken: Optional[float]  # Time in minutes
    attempts: int  # Number of attempts
    passed: bool  # Pass/fail status
    completed_at: datetime
```

#### LearnerScoreSummary Model
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
    confidence_score: float  # 0-100
    recent_performance: List[TestResult]
```

### Core Components

#### ScoringEngine (`ml/scoring_engine.py`)
- Calculates weighted scores based on test type and recency
- Analyzes score trends and performance consistency
- Determines recommendation levels based on multiple factors

#### ScoreBasedRecommender (`ml/score_based_recommender.py`)
- Generates personalized course recommendations
- Creates learning paths based on scoring analysis
- Provides detailed match scores and reasoning

## 🚀 API Endpoints

### 1. Submit Test Result
**POST** `/api/scoring/test-result`

Submit a new test or quiz result for scoring analysis.

**Request Body:**
```json
{
    "learner_id": "learner-123",
    "test_id": "quiz-python-basics",
    "test_type": "quiz",
    "course_id": "python-101",
    "score": 85,
    "max_score": 100,
    "time_taken": 25,
    "attempts": 1,
    "feedback": "Good understanding of Python basics"
}
```

**Response:**
```json
{
    "success": true,
    "test_result": {
        "id": "test-123",
        "learner_id": "learner-123",
        "percentage": 85.0,
        "passed": true,
        "completed_at": "2024-01-15T10:30:00Z"
    },
    "engagement_created": true,
    "activity_logged": true,
    "message": "Test result recorded successfully. Score: 85.0%"
}
```

### 2. Get Learner Score Summary
**GET** `/api/scoring/learner/<learner_id>/score-summary`

Get comprehensive scoring analysis for a learner.

**Response:**
```json
{
    "success": true,
    "learner_id": "learner-123",
    "score_summary": {
        "total_tests": 5,
        "average_score": 82.5,
        "latest_score": 88.0,
        "score_trend": "improving",
        "strongest_subject": "python-101",
        "weakest_subject": "data-science-intro",
        "recommendation_level": "intermediate",
        "confidence_score": 78.5,
        "recent_performance": [...]
    },
    "total_test_results": 5,
    "generated_at": "2024-01-15T10:30:00Z"
}
```

### 3. Get Score-Based Recommendations
**GET** `/api/scoring/learner/<learner_id>/recommendations`

Get personalized course recommendations based on scoring analysis.

**Response:**
```json
{
    "success": true,
    "recommendations": {
        "learner_id": "learner-123",
        "score_summary": {
            "recommendation_level": "intermediate",
            "confidence_score": 78.5
        },
        "recommendations": [
            {
                "rank": 1,
                "course_id": "python-advanced",
                "title": "Advanced Python Programming",
                "difficulty_level": "intermediate",
                "match_score": 92.5,
                "confidence": 85.3,
                "recommendation_reason": "Perfect difficulty match for intermediate level learners; Strong performance alignment",
                "estimated_completion_time": "90 minutes",
                "prerequisites_met": true,
                "next_steps": [
                    "Apply concepts through hands-on projects",
                    "Consider advancing to advanced topics soon"
                ]
            }
        ],
        "learning_path": {...},
        "generated_at": "2024-01-15T10:30:00Z"
    }
}
```

### 4. Get Learning Path
**GET** `/api/scoring/learner/<learner_id>/learning-path`

Generate a complete personalized learning path.

**Response:**
```json
{
    "success": true,
    "learner_id": "learner-123",
    "learning_path": {
        "learning_path": [
            {
                "sequence": 1,
                "course_id": "python-basics-review",
                "title": "Python Basics Review",
                "difficulty": "beginner",
                "estimated_time": "60 minutes",
                "focus_skills": ["python", "basics"],
                "prerequisites_met": true,
                "match_confidence": 95.2
            }
        ],
        "path_summary": "Personalized learning path with 3 courses covering 5 skill areas",
        "estimated_duration": "4.5 hours",
        "skill_coverage": ["python", "data-structures", "algorithms"],
        "starting_level": "intermediate",
        "expected_outcome": "Solid understanding with ability to apply concepts practically"
    },
    "current_performance": {
        "level": "intermediate",
        "confidence": 78.5,
        "trend": "improving"
    }
}
```

### 5. Performance Analytics (Admin)
**GET** `/api/scoring/analytics/performance-trends`

Get system-wide performance analytics (admin function).

## 💡 How It Works

### 1. Score Calculation Process

1. **Data Collection**: Test results are submitted via API endpoints
2. **Weight Application**: Different test types receive different weights
3. **Recency Adjustment**: Older scores are penalized
4. **Trend Analysis**: Recent vs. historical performance comparison
5. **Consistency Measurement**: Performance variation analysis
6. **Level Determination**: Beginner/Intermediate/Advanced classification

### 2. Recommendation Generation

1. **Performance Analysis**: Analyze learner's scoring summary
2. **Course Matching**: Match courses based on:
   - Difficulty level alignment
   - Performance consistency
   - Learning progression
   - Subject strengths/weaknesses
3. **Score Calculation**: Calculate detailed match scores
4. **Ranking**: Sort recommendations by match quality
5. **Explanation**: Provide reasoning for each recommendation

### 3. Learning Path Creation

1. **Sequential Ordering**: Arrange courses in logical progression
2. **Prerequisite Checking**: Ensure prerequisites are met
3. **Time Estimation**: Estimate completion times based on performance
4. **Skill Coverage**: Identify skills covered by the path
5. **Outcome Prediction**: Provide expected learning outcomes

## 🧪 Testing

### Running the Test Suite

```bash
# Start the Flask API server
python flask_api.py

# In another terminal, run the test suite
python test_scoring_system.py
```

The test script will:
1. Check API health
2. Submit sample test results
3. Generate score summaries
4. Create recommendations
5. Build learning paths
6. Display performance analytics

### Manual Testing with cURL

```bash
# Submit a test result
curl -X POST http://localhost:5000/api/scoring/test-result \
  -H "Content-Type: application/json" \
  -d '{
    "learner_id": "demo-user",
    "test_id": "python-quiz-1",
    "test_type": "quiz",
    "course_id": "python-101",
    "score": 85,
    "max_score": 100,
    "time_taken": 25
  }'

# Get score summary
curl http://localhost:5000/api/scoring/learner/demo-user/score-summary

# Get recommendations
curl http://localhost:5000/api/scoring/learner/demo-user/recommendations
```

## 🔧 Configuration

### Scoring Parameters

Modify `ScoringEngine` initialization to adjust:

```python
self.weight_config = {
    'quiz': 0.3,      # Quiz weight
    'test': 0.4,      # Test weight  
    'assignment': 0.5, # Assignment weight
    'exam': 0.7       # Exam weight
}

self.recency_decay_days = 30  # Days before score decay
```

### Recommendation Thresholds

Modify score thresholds in `ScoreBasedRecommender`:

```python
self.thresholds = {
    'excellent': 90,
    'good': 80,
    'satisfactory': 70,
    'needs_improvement': 60
}
```

## 📈 Performance Insights

### Key Metrics Tracked

1. **Academic Performance**
   - Average scores by subject
   - Score trends over time
   - Performance consistency

2. **Learning Efficiency**
   - Time taken vs. performance
   - Improvement rates
   - Confidence levels

3. **Course Effectiveness**
   - Completion rates by course
   - Score improvements after courses
   - Recommendation accuracy

### Analytics Dashboard

Access performance analytics through:
- Admin API endpoint: `/api/scoring/analytics/performance-trends`
- Real-time learner progress tracking
- Course effectiveness metrics

## 🔒 Security Considerations

1. **Input Validation**: All API inputs are validated
2. **Score Integrity**: Scores cannot be manipulated after submission
3. **Learner Privacy**: Personal data is properly secured
4. **API Rate Limiting**: Implement rate limiting for production

## 🚀 Production Deployment

### Environment Setup

1. **Database**: Ensure MongoDB Atlas is configured
2. **API Keys**: Set required environment variables
3. **Logging**: Configure appropriate logging levels
4. **Monitoring**: Set up performance monitoring

### Scaling Considerations

1. **Caching**: Cache scoring calculations
2. **Database Indexing**: Index frequently queried fields
3. **API Rate Limiting**: Implement rate limiting
4. **Load Balancing**: Use multiple API instances

## 📚 Integration Examples

### Frontend Integration

```javascript
// React component example
const getRecommendations = async (learnerId) => {
  const response = await fetch(`/api/scoring/learner/${learnerId}/recommendations`);
  const data = await response.json();
  return data.recommendations;
};

// Display recommendations
const RecommendationCard = ({ recommendation }) => (
  <div className="recommendation-card">
    <h3>{recommendation.title}</h3>
    <p>Difficulty: {recommendation.difficulty_level}</p>
    <p>Match Score: {recommendation.match_score}%</p>
    <p>Reason: {recommendation.recommendation_reason}</p>
  </div>
);
```

### Mobile App Integration

```python
# Python mobile backend example
from flask import Flask
from ml.score_based_recommender import get_score_based_recommendations

@app.route('/mobile/recommendations/<learner_id>')
def mobile_recommendations(learner_id):
    recommendations = get_score_based_recommendations(learner_id)
    return jsonify({
        'recommendations': recommendations['recommendations'][:3],  # Top 3
        'score_summary': recommendations['score_summary']
    })
```

## 🎯 Future Enhancements

1. **Advanced Analytics**: Machine learning-based performance prediction
2. **Social Learning**: Peer comparison and collaborative features
3. **Adaptive Testing**: Dynamic difficulty adjustment based on performance
4. **Real-time Coaching**: Immediate feedback and guidance
5. **Gamification**: Badges and achievements based on scoring milestones

## 🆘 Troubleshooting

### Common Issues

1. **Connection Errors**: Check MongoDB Atlas connection
2. **Import Errors**: Verify all dependencies are installed
3. **Scoring Inconsistencies**: Review test result data format
4. **Recommendation Quality**: Adjust scoring parameters

### Debug Mode

Enable debug logging by setting:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📞 Support

For issues or questions:
1. Check the test script output for debugging info
2. Review API response errors
3. Verify MongoDB Atlas connection
4. Check scoring parameter configuration

---

This scoring and recommendation system provides a robust foundation for personalized learning experiences based on objective performance metrics while maintaining MongoDB Atlas as your database backend.