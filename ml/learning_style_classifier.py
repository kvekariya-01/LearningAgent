"""
Learning Style Classifier for Visual/Auditory/Kinesthetic learning style detection
Uses behavioral patterns and engagement data to classify learning preferences
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import os
from datetime import datetime, timedelta
from utils.crud_operations import read_learner, get_engagement_metrics

class LearningStyleClassifier:
    """ML model to classify learning styles based on behavioral patterns"""
    
    def __init__(self):
        self.classifier = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
        self.style_mapping = {
            0: "Visual",
            1: "Auditory", 
            2: "Kinesthetic",
            3: "Reading/Writing"
        }
        self.feature_names = [
            "video_completion_rate",
            "audio_content_preference", 
            "hands_on_activity_rate",
            "reading_completion_rate",
            "interactive_content_engagement",
            "visual_content_time_spent",
            "discussion_participation",
            "project_completion_rate",
            "quiz_performance_on_interactive",
            "average_session_length",
            "content_revisit_rate"
        ]
        
    def extract_learning_features(self, learner_id: str) -> Optional[Dict[str, float]]:
        """Extract behavioral features from learner data for classification"""
        try:
            learner = read_learner(learner_id)
            if not learner:
                return None
                
            activities = learner.get("activities", [])
            engagements = get_engagement_metrics(learner_id)
            
            if not activities and not engagements:
                return self._get_default_features()
            
            # Initialize feature counters
            features = {
                "video_completion_rate": 0.0,
                "audio_content_preference": 0.0,
                "hands_on_activity_rate": 0.0,
                "reading_completion_rate": 0.0,
                "interactive_content_engagement": 0.0,
                "visual_content_time_spent": 0.0,
                "discussion_participation": 0.0,
                "project_completion_rate": 0.0,
                "quiz_performance_on_interactive": 0.0,
                "average_session_length": 0.0,
                "content_revisit_rate": 0.0
            }
            
            # Analyze activities
            total_activities = len(activities)
            if total_activities == 0:
                return self._get_default_features()
            
            video_activities = [a for a in activities if "video" in a.get("activity_type", "").lower()]
            reading_activities = [a for a in activities if any(keyword in a.get("activity_type", "").lower() 
                              for keyword in ["reading", "article", "text"])]
            interactive_activities = [a for a in activities if any(keyword in a.get("activity_type", "").lower() 
                                   for keyword in ["interactive", "project", "assignment"])]
            discussion_activities = [a for a in activities if "discussion" in a.get("activity_type", "").lower()]
            
            # Calculate feature rates
            features["video_completion_rate"] = len(video_activities) / total_activities
            features["reading_completion_rate"] = len(reading_activities) / total_activities
            features["hands_on_activity_rate"] = len(interactive_activities) / total_activities
            features["discussion_participation"] = len(discussion_activities) / total_activities
            
            # Calculate average session length
            durations = [a.get("duration", 0) for a in activities if a.get("duration")]
            features["average_session_length"] = np.mean(durations) if durations else 0.0
            
            # Analyze engagement patterns
            if engagements:
                completion_rates = []
                for engagement in engagements[-10:]:  # Last 10 engagements
                    metrics = engagement.get("metrics", {})
                    completion_rates.append(metrics.get("completion_percentage", 0.0))
                
                features["interactive_content_engagement"] = np.mean(completion_rates) if completion_rates else 0.0
                
                # Calculate revisit rate (engagements with same content)
                content_interactions = {}
                for engagement in engagements:
                    content_id = engagement.get("engagement_id", "")
                    content_interactions[content_id] = content_interactions.get(content_id, 0) + 1
                
                revisited_content = sum(1 for count in content_interactions.values() if count > 1)
                features["content_revisit_rate"] = revisited_content / len(content_interactions) if content_interactions else 0.0
            
            # Calculate performance-based features
            scores = [a.get("score", 0) for a in activities if a.get("score")]
            if scores:
                avg_score = np.mean(scores)
                # Visual learners tend to perform well on video content
                video_scores = [a.get("score", 0) for a in video_activities if a.get("score")]
                features["visual_content_time_spent"] = np.mean(video_scores) / 100.0 if video_scores else avg_score / 100.0
                
                # Interactive learners perform well on hands-on activities
                interactive_scores = [a.get("score", 0) for a in interactive_activities if a.get("score")]
                features["quiz_performance_on_interactive"] = np.mean(interactive_scores) / 100.0 if interactive_scores else avg_score / 100.0
                
                # Project completion rate
                project_activities = [a for a in activities if "project" in a.get("activity_type", "").lower()]
                features["project_completion_rate"] = len(project_activities) / total_activities
            
            return features
            
        except Exception as e:
            print(f"Error extracting learning features: {e}")
            return self._get_default_features()
    
    def _get_default_features(self) -> Dict[str, float]:
        """Return default features for new learners"""
        return {
            "video_completion_rate": 0.25,
            "audio_content_preference": 0.25,
            "hands_on_activity_rate": 0.25,
            "reading_completion_rate": 0.25,
            "interactive_content_engagement": 0.5,
            "visual_content_time_spent": 0.5,
            "discussion_participation": 0.2,
            "project_completion_rate": 0.3,
            "quiz_performance_on_interactive": 0.6,
            "average_session_length": 30.0,
            "content_revisit_rate": 0.3
        }
    
    def classify_learning_style(self, learner_id: str) -> Tuple[str, float]:
        """Classify learner's learning style with confidence score"""
        try:
            features = self.extract_learning_features(learner_id)
            if not features:
                return "Mixed", 0.5
            
            if not self.is_trained:
                # Use rule-based classification if model not trained
                return self._rule_based_classification(features)
            
            # Use trained ML model
            feature_vector = np.array([[features[name] for name in self.feature_names]])
            feature_vector_scaled = self.scaler.transform(feature_vector)
            
            prediction = self.classifier.predict(feature_vector_scaled)[0]
            probabilities = self.classifier.predict_proba(feature_vector_scaled)[0]
            confidence = np.max(probabilities)
            
            return self.style_mapping[prediction], confidence
            
        except Exception as e:
            print(f"Error in learning style classification: {e}")
            return "Mixed", 0.5
    
    def _rule_based_classification(self, features: Dict[str, float]) -> Tuple[str, float]:
        """Rule-based classification as fallback"""
        visual_score = features["video_completion_rate"] * 0.4 + features["visual_content_time_spent"] * 0.3
        auditory_score = features["discussion_participation"] * 0.5 + features["audio_content_preference"] * 0.3
        kinesthetic_score = features["hands_on_activity_rate"] * 0.4 + features["project_completion_rate"] * 0.3
        reading_score = features["reading_completion_rate"] * 0.5
        
        scores = {
            "Visual": visual_score,
            "Auditory": auditory_score, 
            "Kinesthetic": kinesthetic_score,
            "Reading/Writing": reading_score
        }
        
        best_style = max(scores, key=scores.get)
        confidence = scores[best_style]
        
        return best_style, min(confidence, 1.0)
    
    def train_classifier(self, training_data: List[Tuple[Dict[str, float], str]]):
        """Train the classifier with labeled data"""
        try:
            if len(training_data) < 10:
                print("Insufficient training data for ML model. Using rule-based classification.")
                return
            
            X = []
            y = []
            
            for features, style in training_data:
                feature_vector = [features.get(name, 0.0) for name in self.feature_names]
                X.append(feature_vector)
                y.append(list(self.style_mapping.values()).index(style))
            
            X = np.array(X)
            y = np.array(y)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            self.classifier.fit(X_train_scaled, y_train)
            
            # Evaluate
            train_score = self.classifier.score(X_train_scaled, y_train)
            test_score = self.classifier.score(X_test_scaled, y_test)
            
            print(f"Learning Style Classifier trained - Train Accuracy: {train_score:.3f}, Test Accuracy: {test_score:.3f}")
            
            self.is_trained = True
            
            # Save model
            self.save_model()
            
        except Exception as e:
            print(f"Error training classifier: {e}")
    
    def save_model(self, filepath: str = "ml/learning_style_model.pkl"):
        """Save trained model to file"""
        try:
            model_data = {
                'classifier': self.classifier,
                'scaler': self.scaler,
                'is_trained': self.is_trained,
                'style_mapping': self.style_mapping,
                'feature_names': self.feature_names
            }
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            joblib.dump(model_data, filepath)
            print(f"Learning Style Classifier saved to {filepath}")
        except Exception as e:
            print(f"Error saving model: {e}")
    
    def load_model(self, filepath: str = "ml/learning_style_model.pkl"):
        """Load trained model from file"""
        try:
            if os.path.exists(filepath):
                model_data = joblib.load(filepath)
                self.classifier = model_data['classifier']
                self.scaler = model_data['scaler']
                self.is_trained = model_data['is_trained']
                self.style_mapping = model_data['style_mapping']
                self.feature_names = model_data['feature_names']
                print(f"Learning Style Classifier loaded from {filepath}")
            else:
                print("Model file not found. Using rule-based classification.")
        except Exception as e:
            print(f"Error loading model: {e}")

# Global classifier instance
learning_style_classifier = LearningStyleClassifier()

def classify_learner_style(learner_id: str) -> Dict[str, any]:
    """Main function to classify a learner's style"""
    try:
        style, confidence = learning_style_classifier.classify_learning_style(learner_id)
        features = learning_style_classifier.extract_learning_features(learner_id)
        
        return {
            "learner_id": learner_id,
            "learning_style": style,
            "confidence": round(confidence, 3),
            "features": features,
            "classification_method": "ml_model" if learning_style_classifier.is_trained else "rule_based",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "learner_id": learner_id,
            "learning_style": "Mixed",
            "confidence": 0.5,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    # Test the classifier
    classifier = LearningStyleClassifier()
    
    # Sample training data (in real implementation, this would come from labeled datasets)
    sample_training_data = [
        (classifier._get_default_features(), "Visual"),
        ({"video_completion_rate": 0.8, "reading_completion_rate": 0.2, "hands_on_activity_rate": 0.3, "discussion_participation": 0.1}, "Visual"),
        ({"video_completion_rate": 0.3, "reading_completion_rate": 0.8, "hands_on_activity_rate": 0.2, "discussion_participation": 0.4}, "Reading/Writing"),
        ({"video_completion_rate": 0.2, "reading_completion_rate": 0.3, "hands_on_activity_rate": 0.8, "discussion_participation": 0.6}, "Kinesthetic"),
        ({"video_completion_rate": 0.4, "reading_completion_rate": 0.4, "hands_on_activity_rate": 0.3, "discussion_participation": 0.8}, "Auditory"),
    ]
    
    # Train the model
    classifier.train_classifier(sample_training_data)
    
    # Test classification
    test_result = classify_learner_style("test-learner-123")
    print(f"Test Classification Result: {test_result}")