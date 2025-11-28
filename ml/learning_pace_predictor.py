"""
Learning Pace Calculator and Performance Prediction Model
Analyzes learning velocity and predicts future performance
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib
import os
from utils.crud_operations import read_learner, get_engagement_metrics

class LearningPaceCalculator:
    """Calculates and analyzes learning pace patterns"""
    
    def __init__(self):
        self.pace_categories = {
            "very_slow": {"range": (0, 0.5), "description": "Less than 0.5 modules per week"},
            "slow": {"range": (0.5, 1.0), "description": "0.5-1.0 modules per week"},
            "moderate": {"range": (1.0, 2.0), "description": "1.0-2.0 modules per week"},
            "fast": {"range": (2.0, 3.5), "description": "2.0-3.5 modules per week"},
            "very_fast": {"range": (3.5, float('inf')), "description": "More than 3.5 modules per week"}
        }
        
        self.pace_factors = {
            "session_frequency": 0.3,    # How often learner studies
            "session_duration": 0.25,    # How long each session is
            "completion_rate": 0.25,     # Rate of completing activities
            "engagement_quality": 0.2    # Quality of engagement
        }
    
    def calculate_learning_pace(self, learner_id: str, time_window_days: int = 30) -> Dict[str, any]:
        """Calculate detailed learning pace metrics"""
        try:
            learner_data = read_learner(learner_id)
            if not learner_data:
                return {"error": "Learner not found"}
            
            activities = learner_data.get("activities", [])
            if not activities:
                return self._get_initial_pace_assessment(learner_id)
            
            # Filter activities within time window
            cutoff_date = datetime.now() - timedelta(days=time_window_days)
            recent_activities = self._filter_activities_by_date(activities, cutoff_date)
            
            if not recent_activities:
                return self._get_insufficient_data_assessment(learner_id, time_window_days)
            
            # Calculate pace metrics
            pace_metrics = self._analyze_pace_metrics(recent_activities, time_window_days)
            
            # Calculate pace factors
            pace_factors = self._analyze_pace_factors(learner_id, recent_activities)
            
            # Determine pace category
            pace_category = self._categorize_pace(pace_metrics["velocity"])
            
            # Predict optimal pace
            optimal_pace = self._calculate_optimal_pace(pace_metrics, pace_factors)
            
            return {
                "learner_id": learner_id,
                "time_window_days": time_window_days,
                "pace_metrics": pace_metrics,
                "pace_factors": pace_factors,
                "current_pace": {
                    "category": pace_category["category"],
                    "velocity": pace_metrics["velocity"],
                    "description": pace_category["description"]
                },
                "optimal_pace": optimal_pace,
                "pace_analysis": self._analyze_pace_trend(activities),
                "calculation_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Pace calculation failed: {str(e)}"}
    
    def _filter_activities_by_date(self, activities: List[Dict], cutoff_date: datetime) -> List[Dict]:
        """Filter activities within specified date range"""
        filtered_activities = []
        
        for activity in activities:
            try:
                activity_date = datetime.fromisoformat(activity.get("timestamp", "").replace('Z', '+00:00'))
                if activity_date >= cutoff_date:
                    filtered_activities.append(activity)
            except (ValueError, TypeError):
                continue
        
        return filtered_activities
    
    def _analyze_pace_metrics(self, activities: List[Dict], time_window_days: int) -> Dict[str, any]:
        """Analyze detailed pace metrics"""
        # Count different types of completions
        module_completions = len([a for a in activities if "module" in a.get("activity_type", "").lower()])
        quiz_completions = len([a for a in activities if "quiz" in a.get("activity_type", "").lower()])
        assignment_completions = len([a for a in activities if "assignment" in a.get("activity_type", "").lower()])
        test_completions = len([a for a in activities if "test" in a.get("activity_type", "").lower()])
        
        # Calculate velocities (per week)
        weeks = time_window_days / 7
        module_velocity = module_completions / weeks if weeks > 0 else 0
        total_activity_velocity = len(activities) / weeks if weeks > 0 else 0
        
        # Calculate average session duration
        durations = [a.get("duration", 0) for a in activities if a.get("duration")]
        avg_session_duration = np.mean(durations) if durations else 0
        
        # Calculate total study time
        total_study_time = sum(durations) if durations else 0
        
        # Calculate completion rate
        total_attempts = len(activities)
        successful_completions = len([a for a in activities if a.get("score", 0) >= 60])
        completion_rate = successful_completions / total_attempts if total_attempts > 0 else 0
        
        return {
            "module_velocity": round(module_velocity, 2),
            "total_activity_velocity": round(total_activity_velocity, 2),
            "quiz_completions": quiz_completions,
            "assignment_completions": assignment_completions,
            "test_completions": test_completions,
            "avg_session_duration": round(avg_session_duration, 2),
            "total_study_time": round(total_study_time, 2),
            "completion_rate": round(completion_rate, 3),
            "total_activities": total_attempts,
            "velocity": round(module_velocity, 2)  # Primary velocity metric
        }
    
    def _analyze_pace_factors(self, learner_id: str, activities: List[Dict]) -> Dict[str, float]:
        """Analyze factors affecting learning pace"""
        
        # Session frequency factor
        if len(activities) < 2:
            session_frequency = 0.1
        else:
            # Calculate days between first and last activity
            timestamps = []
            for activity in activities:
                try:
                    ts = datetime.fromisoformat(activity.get("timestamp", "").replace('Z', '+00:00'))
                    timestamps.append(ts)
                except (ValueError, TypeError):
                    continue
            
            if len(timestamps) >= 2:
                time_span = (max(timestamps) - min(timestamps)).days
                sessions_per_week = len(activities) / (time_span / 7) if time_span > 0 else 0
                session_frequency = min(sessions_per_week / 7.0, 1.0)  # Normalize to 0-1
            else:
                session_frequency = 0.5
        
        # Session duration factor
        durations = [a.get("duration", 0) for a in activities if a.get("duration")]
        avg_duration = np.mean(durations) if durations else 0
        # Optimal session duration is 45-90 minutes
        if 45 <= avg_duration <= 90:
            session_duration = 1.0
        elif 30 <= avg_duration < 45 or 90 < avg_duration <= 120:
            session_duration = 0.7
        else:
            session_duration = 0.4
        
        # Completion rate factor
        scores = [a.get("score", 0) for a in activities if a.get("score")]
        completion_rate = len([s for s in scores if s >= 60]) / len(scores) if scores else 0
        
        # Engagement quality factor
        engagements = get_engagement_metrics(learner_id)
        if engagements:
            completion_percentages = [e.get("metrics", {}).get("completion_percentage", 0) for e in engagements]
            engagement_quality = np.mean(completion_percentages) if completion_percentages else 0.5
        else:
            engagement_quality = 0.5
        
        return {
            "session_frequency": round(session_frequency, 3),
            "session_duration": round(session_duration, 3),
            "completion_rate": round(completion_rate, 3),
            "engagement_quality": round(engagement_quality, 3)
        }
    
    def _categorize_pace(self, velocity: float) -> Dict[str, str]:
        """Categorize learning pace"""
        for category, criteria in self.pace_categories.items():
            if criteria["range"][0] <= velocity < criteria["range"][1]:
                return {
                    "category": category,
                    "description": criteria["description"]
                }
        
        return {
            "category": "very_fast",
            "description": "More than 3.5 modules per week"
        }
    
    def _calculate_optimal_pace(self, pace_metrics: Dict, pace_factors: Dict) -> Dict[str, any]:
        """Calculate optimal learning pace based on factors"""
        
        # Calculate weighted pace score
        pace_score = (
            pace_factors["session_frequency"] * self.pace_factors["session_frequency"] +
            pace_factors["session_duration"] * self.pace_factors["session_duration"] +
            pace_factors["completion_rate"] * self.pace_factors["completion_rate"] +
            pace_factors["engagement_quality"] * self.pace_factors["engagement_quality"]
        )
        
        # Optimal velocity is 2.0 modules per week for most learners
        optimal_velocity = 2.0 * pace_score
        
        # Adjust based on current performance
        current_completion_rate = pace_metrics["completion_rate"]
        if current_completion_rate < 0.6:
            optimal_velocity *= 0.8  # Reduce if struggling
        elif current_completion_rate > 0.9:
            optimal_velocity *= 1.2  # Increase if excelling
        
        return {
            "optimal_velocity": round(optimal_velocity, 2),
            "pace_score": round(pace_score, 3),
            "recommendations": self._generate_pace_recommendations(pace_factors, optimal_velocity)
        }
    
    def _generate_pace_recommendations(self, pace_factors: Dict, optimal_velocity: float) -> List[str]:
        """Generate recommendations to optimize learning pace"""
        recommendations = []
        
        if pace_factors["session_frequency"] < 0.5:
            recommendations.append("Increase study frequency to at least 3-4 sessions per week")
        
        if pace_factors["session_duration"] < 0.7:
            if pace_factors["session_duration"] < 0.4:
                recommendations.append("Extend study sessions to 45-90 minutes for better focus")
            else:
                recommendations.append("Consider slightly longer study sessions for deeper learning")
        
        if pace_factors["completion_rate"] < 0.7:
            recommendations.append("Focus on understanding concepts before moving to new material")
        
        if pace_factors["engagement_quality"] < 0.6:
            recommendations.append("Increase engagement by trying different learning methods")
        
        if optimal_velocity > 2.5:
            recommendations.append("Consider taking breaks to avoid burnout at this pace")
        elif optimal_velocity < 1.0:
            recommendations.append("Gradually increase pace with consistent daily practice")
        
        return recommendations
    
    def _analyze_pace_trend(self, activities: List[Dict]) -> Dict[str, any]:
        """Analyze pace trends over time"""
        if len(activities) < 4:
            return {"trend": "insufficient_data", "description": "Not enough data for trend analysis"}
        
        # Split activities into two halves
        mid_point = len(activities) // 2
        first_half = activities[:mid_point]
        second_half = activities[mid_point:]
        
        # Calculate velocity for each half (assuming 30-day window)
        first_velocity = len(first_half) / 0.5  # per week
        second_velocity = len(second_half) / 0.5  # per week
        
        # Determine trend
        velocity_change = second_velocity - first_velocity
        if velocity_change > 0.5:
            trend = "accelerating"
            description = "Learning pace is increasing"
        elif velocity_change < -0.5:
            trend = "decelerating"
            description = "Learning pace is slowing down"
        else:
            trend = "stable"
            description = "Learning pace is consistent"
        
        return {
            "trend": trend,
            "description": description,
            "velocity_change": round(velocity_change, 2),
            "first_half_velocity": round(first_velocity, 2),
            "second_half_velocity": round(second_velocity, 2)
        }
    
    def _get_initial_pace_assessment(self, learner_id: str) -> Dict[str, any]:
        """Initial pace assessment for new learners"""
        return {
            "learner_id": learner_id,
            "pace_metrics": {
                "velocity": 0.0,
                "total_activities": 0,
                "completion_rate": 0.0,
                "avg_session_duration": 0.0
            },
            "current_pace": {
                "category": "insufficient_data",
                "velocity": 0.0,
                "description": "No learning activity data available"
            },
            "optimal_pace": {
                "optimal_velocity": 2.0,
                "pace_score": 0.5,
                "recommendations": [
                    "Begin with consistent daily study sessions",
                    "Start with 30-45 minute sessions",
                    "Focus on completing one module per week initially"
                ]
            },
            "pace_analysis": {
                "trend": "baseline",
                "description": "Establishing initial learning pace"
            }
        }
    
    def _get_insufficient_data_assessment(self, learner_id: str, time_window_days: int) -> Dict[str, any]:
        """Assessment when insufficient data is available"""
        return {
            "learner_id": learner_id,
            "time_window_days": time_window_days,
            "pace_metrics": {
                "velocity": 0.0,
                "total_activities": 0,
                "completion_rate": 0.0,
                "avg_session_duration": 0.0
            },
            "current_pace": {
                "category": "insufficient_data",
                "velocity": 0.0,
                "description": f"Insufficient activity data in last {time_window_days} days"
            },
            "optimal_pace": {
                "optimal_velocity": 2.0,
                "pace_score": 0.5,
                "recommendations": [
                    "Complete more learning activities to establish pace",
                    "Aim for consistent study schedule",
                    "Track progress regularly"
                ]
            }
        }


class PerformancePredictionModel:
    """Predicts future learner performance based on historical data"""
    
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names = [
            "historical_avg_score",
            "recent_score_trend",
            "activity_frequency",
            "session_duration_avg",
            "completion_rate",
            "engagement_quality",
            "learning_velocity",
            "consistency_score",
            "improvement_rate",
            "time_since_last_activity"
        ]
    
    def predict_performance(self, learner_id: str, prediction_horizon: int = 7) -> Dict[str, any]:
        """Predict performance for specified number of days ahead"""
        try:
            learner_data = read_learner(learner_id)
            if not learner_data:
                return {"error": "Learner not found"}
            
            # Extract features for prediction
            features = self._extract_prediction_features(learner_data)
            if not features:
                return self._get_default_prediction(learner_id, prediction_horizon)
            
            # Make prediction
            if self.is_trained:
                prediction = self._ml_predict(features)
            else:
                prediction = self._rule_based_predict(features)
            
            # Calculate confidence
            confidence = self._calculate_prediction_confidence(features)
            
            return {
                "learner_id": learner_id,
                "prediction_horizon_days": prediction_horizon,
                "predicted_metrics": prediction,
                "confidence_score": confidence,
                "features_used": features,
                "prediction_timestamp": datetime.nowisoformat(),
                "recommendations": self._generate_prediction_recommendations(prediction, features)
            }
            
        except Exception as e:
            return {"error": f"Performance prediction failed: {str(e)}"}
    
    def _extract_prediction_features(self, learner_data: Dict) -> Optional[Dict[str, float]]:
        """Extract features for performance prediction"""
        try:
            activities = learner_data.get("activities", [])
            if not activities:
                return None
            
            # Sort activities by timestamp
            sorted_activities = sorted(activities, key=lambda x: x.get("timestamp", ""))
            
            # Historical average score
            scores = [a.get("score", 0) for a in activities if a.get("score") is not None]
            historical_avg = np.mean(scores) if scores else 50.0
            
            # Recent score trend (last 3 vs previous 3)
            recent_scores = [a.get("score", 0) for a in sorted_activities[-3:] if a.get("score") is not None]
            earlier_scores = [a.get("score", 0) for a in sorted_activities[-6:-3] if a.get("score") is not None]
            
            if recent_scores and earlier_scores:
                recent_avg = np.mean(recent_scores)
                earlier_avg = np.mean(earlier_scores)
                score_trend = (recent_avg - earlier_avg) / earlier_avg if earlier_avg > 0 else 0
            else:
                score_trend = 0.0
            
            # Activity frequency (activities per week)
            if len(sorted_activities) >= 2:
                time_span = self._calculate_time_span(sorted_activities)
                activity_frequency = len(activities) / (time_span / 7) if time_span > 0 else 0
            else:
                activity_frequency = 1.0
            
            # Session duration average
            durations = [a.get("duration", 0) for a in activities if a.get("duration")]
            session_duration_avg = np.mean(durations) if durations else 30.0
            
            # Completion rate
            completed_activities = len([a for a in activities if a.get("score", 0) >= 60])
            completion_rate = completed_activities / len(activities) if activities else 0
            
            # Engagement quality
            engagements = get_engagement_metrics(learner_data.get("id", ""))
            if engagements:
                completion_percentages = [e.get("metrics", {}).get("completion_percentage", 0) for e in engagements]
                engagement_quality = np.mean(completion_percentages) if completion_percentages else 0.5
            else:
                engagement_quality = 0.5
            
            # Learning velocity (modules per week)
            module_completions = len([a for a in activities if "module" in a.get("activity_type", "").lower()])
            if len(sorted_activities) >= 2:
                time_span_weeks = self._calculate_time_span(sorted_activities) / 7
                learning_velocity = module_completions / time_span_weeks if time_span_weeks > 0 else 0
            else:
                learning_velocity = 0.0
            
            # Consistency score (inverse of score variance)
            if len(scores) > 1:
                consistency_score = max(0, 1 - (np.std(scores) / 100))  # Normalize variance
            else:
                consistency_score = 0.5
            
            # Improvement rate
            if len(scores) >= 4:
                first_quarter = np.mean(scores[:len(scores)//4])
                last_quarter = np.mean(scores[-len(scores)//4:])
                improvement_rate = (last_quarter - first_quarter) / first_quarter if first_quarter > 0 else 0
            else:
                improvement_rate = 0.0
            
            # Time since last activity
            if sorted_activities:
                last_activity = datetime.fromisoformat(sorted_activities[-1].get("timestamp", "").replace('Z', '+00:00'))
                days_since_last = (datetime.now() - last_activity).days
            else:
                days_since_last = 7
            
            return {
                "historical_avg_score": historical_avg,
                "recent_score_trend": score_trend,
                "activity_frequency": activity_frequency,
                "session_duration_avg": session_duration_avg,
                "completion_rate": completion_rate,
                "engagement_quality": engagement_quality,
                "learning_velocity": learning_velocity,
                "consistency_score": consistency_score,
                "improvement_rate": improvement_rate,
                "time_since_last_activity": days_since_last
            }
            
        except Exception as e:
            print(f"Error extracting prediction features: {e}")
            return None
    
    def _calculate_time_span(self, activities: List[Dict]) -> float:
        """Calculate time span between first and last activity in days"""
        try:
            timestamps = [datetime.fromisoformat(a.get("timestamp", "").replace('Z', '+00:00')) for a in activities]
            return (max(timestamps) - min(timestamps)).days
        except (ValueError, TypeError):
            return 7.0  # Default to 1 week
    
    def _ml_predict(self, features: Dict[str, float]) -> Dict[str, float]:
        """Make prediction using trained ML model"""
        try:
            feature_vector = np.array([[features[name] for name in self.feature_names]])
            feature_vector_scaled = self.scaler.transform(feature_vector)
            
            prediction = self.model.predict(feature_vector_scaled)[0]
            
            # Ensure prediction is within reasonable bounds
            prediction = max(0, min(100, prediction))
            
            return {
                "predicted_avg_score": round(prediction, 2),
                "predicted_completion_rate": round(max(0, min(1, prediction / 100 + 0.1)), 3),
                "predicted_activity_count": round(max(1, prediction / 10), 0)
            }
            
        except Exception as e:
            print(f"ML prediction error: {e}")
            return self._rule_based_predict(features)
    
    def _rule_based_predict(self, features: Dict[str, float]) -> Dict[str, float]:
        """Rule-based prediction when ML model is not available"""
        # Base prediction on historical average
        base_score = features.get("historical_avg_score", 50.0)
        
        # Adjust based on trends
        score_adjustment = features.get("recent_score_trend", 0) * 20  # Scale trend impact
        activity_adjustment = min(features.get("activity_frequency", 1) / 7.0, 1.0) * 5  # Bonus for regular activity
        
        predicted_score = base_score + score_adjustment + activity_adjustment
        predicted_score = max(0, min(100, predicted_score))
        
        # Predict completion rate based on consistency and engagement
        completion_rate = (
            features.get("consistency_score", 0.5) * 0.4 +
            features.get("engagement_quality", 0.5) * 0.3 +
            features.get("completion_rate", 0.5) * 0.3
        )
        
        # Predict activity count based on frequency and velocity
        activity_count = max(1, int(features.get("activity_frequency", 1) * 7))
        
        return {
            "predicted_avg_score": round(predicted_score, 2),
            "predicted_completion_rate": round(completion_rate, 3),
            "predicted_activity_count": activity_count
        }
    
    def _calculate_prediction_confidence(self, features: Dict[str, float]) -> float:
        """Calculate confidence in the prediction"""
        # Base confidence on data availability
        base_confidence = 0.5
        
        # Increase confidence with more data
        activity_frequency = features.get("activity_frequency", 0)
        if activity_frequency > 3:  # More than 3 activities per week
            base_confidence += 0.2
        elif activity_frequency > 1:  # More than 1 activity per week
            base_confidence += 0.1
        
        # Increase confidence with consistency
        consistency = features.get("consistency_score", 0.5)
        base_confidence += consistency * 0.2
        
        # Decrease confidence for stale data
        days_since_last = features.get("time_since_last_activity", 0)
        if days_since_last > 14:  # More than 2 weeks since last activity
            base_confidence -= 0.2
        
        return max(0.1, min(0.95, base_confidence))
    
    def _generate_prediction_recommendations(self, prediction: Dict[str, float], features: Dict[str, float]) -> List[str]:
        """Generate recommendations based on prediction"""
        recommendations = []
        
        predicted_score = prediction.get("predicted_avg_score", 50)
        predicted_completion = prediction.get("predicted_completion_rate", 0.5)
        
        if predicted_score < 60:
            recommendations.append("Focus on strengthening foundational concepts")
            recommendations.append("Consider additional practice exercises")
        
        if predicted_completion < 0.6:
            recommendations.append("Improve time management and study planning")
            recommendations.append("Break larger tasks into smaller, manageable chunks")
        
        if features.get("time_since_last_activity", 0) > 7:
            recommendations.append("Resume regular study schedule")
            recommendations.append("Set small, achievable daily goals")
        
        if features.get("learning_velocity", 0) < 0.5:
            recommendations.append("Increase study frequency gradually")
            recommendations.append("Maintain consistent daily practice")
        
        return recommendations
    
    def _get_default_prediction(self, learner_id: str, horizon: int) -> Dict[str, any]:
        """Default prediction for new learners"""
        return {
            "learner_id": learner_id,
            "prediction_horizon_days": horizon,
            "predicted_metrics": {
                "predicted_avg_score": 50.0,
                "predicted_completion_rate": 0.5,
                "predicted_activity_count": horizon // 2
            },
            "confidence_score": 0.3,
            "features_used": {},
            "prediction_timestamp": datetime.now().isoformat(),
            "recommendations": [
                "Establish consistent study routine",
                "Complete initial assessments to set baseline",
                "Focus on building learning habits"
            ]
        }
    
    def train_model(self, training_data: List[Tuple[Dict[str, float], Dict[str, float]]]):
        """Train the performance prediction model"""
        try:
            if len(training_data) < 20:
                print("Insufficient training data for ML model. Using rule-based prediction.")
                return
            
            X = []
            y = []
            
            for features, target in training_data:
                feature_vector = [features.get(name, 0.0) for name in self.feature_names]
                X.append(feature_vector)
                
                # Target: predicted average score
                y.append(target.get("avg_score", 50.0))
            
            X = np.array(X)
            y = np.array(y)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            self.model.fit(X_train_scaled, y_train)
            
            # Evaluate
            train_mae = mean_absolute_error(y_train, self.model.predict(X_train_scaled))
            test_mae = mean_absolute_error(y_test, self.model.predict(X_test_scaled))
            
            print(f"Performance Prediction Model trained - Train MAE: {train_mae:.2f}, Test MAE: {test_mae:.2f}")
            
            self.is_trained = True
            
            # Save model
            self.save_model()
            
        except Exception as e:
            print(f"Error training prediction model: {e}")
    
    def save_model(self, filepath: str = "ml/performance_prediction_model.pkl"):
        """Save trained model to file"""
        try:
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'is_trained': self.is_trained,
                'feature_names': self.feature_names
            }
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            joblib.dump(model_data, filepath)
            print(f"Performance Prediction Model saved to {filepath}")
        except Exception as e:
            print(f"Error saving model: {e}")
    
    def load_model(self, filepath: str = "ml/performance_prediction_model.pkl"):
        """Load trained model from file"""
        try:
            if os.path.exists(filepath):
                model_data = joblib.load(filepath)
                self.model = model_data['model']
                self.scaler = model_data['scaler']
                self.is_trained = model_data['is_trained']
                self.feature_names = model_data['feature_names']
                print(f"Performance Prediction Model loaded from {filepath}")
            else:
                print("Model file not found. Using rule-based prediction.")
        except Exception as e:
            print(f"Error loading model: {e}")


# Global instances
learning_pace_calculator = LearningPaceCalculator()
performance_prediction_model = PerformancePredictionModel()

def calculate_learning_pace(learner_id: str, time_window_days: int = 30) -> Dict[str, any]:
    """Main function to calculate learning pace"""
    return learning_pace_calculator.calculate_learning_pace(learner_id, time_window_days)

def predict_performance(learner_id: str, prediction_horizon: int = 7) -> Dict[str, any]:
    """Main function to predict performance"""
    return performance_prediction_model.predict_performance(learner_id, prediction_horizon)

if __name__ == "__main__":
    # Test the systems
    calculator = LearningPaceCalculator()
    predictor = PerformancePredictionModel()
    
    print("Learning Pace Calculator and Performance Prediction Model initialized")
    
    # Sample test
    sample_features = {
        "historical_avg_score": 75.0,
        "recent_score_trend": 0.1,
        "activity_frequency": 3.5,
        "session_duration_avg": 60.0,
        "completion_rate": 0.8,
        "engagement_quality": 0.7,
        "learning_velocity": 1.5,
        "consistency_score": 0.6,
        "improvement_rate": 0.05,
        "time_since_last_activity": 2
    }
    
    prediction = predictor._rule_based_predict(sample_features)
    print(f"Sample Prediction: {prediction}")