# Learning Agent API - Postman Integration Guide

## 📋 MongoDB Atlas Learning Agent API Collection

### 🚀 Quick Start

1. **Import the Collection**
   - Open Postman
   - Click "Import" button
   - Upload the `Learning_Agent_API_Postman_Collection.json` file

2. **Set Environment Variables**
   - Create a new environment called "Learning Agent Local"
   - Add variables:
     - `base_url`: `http://localhost:5000`
     - `learner_id`: (leave empty initially)

3. **Start Testing**
   - Run "Home Page" to verify API is running
   - Register a new learner to get an ID
   - Update the `learner_id` variable with the returned ID
   - Test other endpoints!

## 🔗 MongoDB Atlas Integration

The API is fully integrated with MongoDB Atlas and stores all data in the cloud database.

- **Connection**: Uses Atlas connection string from `.env` file
- **Database**: `learning_agent_db`
- **Collections**: `learners`, `contents`, `engagements`, `progress_logs`, `interventions`

## 📝 Available Endpoints

### Core Operations
- `POST /api/learner/register` - Register new learner
- `GET /api/learners` - Get all learners
- `GET /api/learner/{id}` - Get specific learner
- `PUT /api/learner/{id}` - Update learner
- `DELETE /api/learner/{id}` - Delete learner

### Activity & Progress
- `POST /api/learner/{id}/activity` - Log activity
- `GET /api/learner/{id}/activities` - Get learner activities
- `GET /api/learner/{id}/progress` - Get progress summary
- `POST /api/learner/{id}/progress/log` - Log progress milestone

### AI & Recommendations
- `GET /api/learner/{id}/recommendations` - Get recommendations
- `POST /api/predict/completion-time` - Predict completion time

### Adaptive Learning
- `POST /api/learner/{id}/adjust-difficulty` - Adjust difficulty
- `GET /api/learner/{id}/interventions` - Get interventions

### Analytics
- `GET /api/analytics/learner/{id}` - Learner analytics
- `GET /api/analytics/cohort` - Cohort comparison
- `GET /api/analytics/summary` - System analytics

## 🧪 Test Data Examples

### Register Learner
```json
{
  "name": "John Doe",
  "age": 25,
  "gender": "male",
  "learning_style": "visual",
  "preferences": ["videos", "quizzes", "discussions"]
}
```

### Log Activity
```json
{
  "activity_type": "module_completed",
  "duration": 45.5,
  "score": 85
}
```

### Adjust Difficulty
```json
{
  "recent_score": 75
}
```

### Predict Completion
```json
{
  "avg_score": 82,
  "time_spent": 120,
  "difficulty": 2
}
```

## 📊 Expected Responses

### Successful Learner Registration
```json
{
  "id": "d55d5c3b-6d14-4642-95ce-b3fd740479d5",
  "message": "Learner registered successfully"
}
```

### Activity Log Response
```json
{
  "status": "success",
  "message": "Activity logged successfully",
  "data": {
    "activities": [...],
    "difficulty_adjustment": {...},
    "interventions": [...]
  }
}
```

### Analytics Response
```json
{
  "status": "success",
  "data": {
    "learner_id": "...",
    "basic_metrics": {...},
    "performance_metrics": {...},
    "learning_velocity": 2.5,
    "activity_distribution": {...}
  }
}
```

## 🔧 Troubleshooting

1. **Connection Issues**
   - Ensure MongoDB Atlas cluster is running
   - Verify connection string in `.env` file
   - Check network connectivity

2. **API Errors**
   - Check Flask server logs in terminal
   - Verify JSON format in request body
   - Ensure all required fields are provided

3. **Variable Not Set**
   - After registering a learner, copy the ID from the response
   - Update the `learner_id` variable in Postman environment

## 🎯 MongoDB Atlas Collections

The API creates and manages the following collections:

- **learners**: Learner profiles and metadata
- **contents**: Course content and materials
- **engagements**: Learning activity records
- **progress_logs**: Milestone achievements
- **interventions**: Adaptive interventions

All collections are automatically indexed for optimal performance.