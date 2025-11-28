"""
Difficulty Matching Algorithm and Adaptive Recommendation Engine
Matches content difficulty to learner ability and provides personalized recommendations
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
from utils.crud_operations import read_learner, read_contents, read_engagements

class DifficultyMatchingAlgorithm:
    """Algorithm to match content difficulty to learner ability"""
    
    def __init__(self):
        self.difficulty_levels = {
            1: {"name": "Beginner", "description": "Basic concepts, no prior knowledge required"},
            2: {"name": "Novice", "description": "Fundamental knowledge, simple applications"},
            3: {"name": "Elementary", "description": "Basic skills with some complexity"},
            4: {"name": "Intermediate", "description": "Moderate complexity, some experience needed"},
            5: {"name": "Upper Intermediate", "description": "Good understanding, moderate challenges"},
            6: {"name": "Advanced", "description": "Complex concepts, substantial experience"},
            7: {"name": "Expert", "description": "Highly complex, expert knowledge required"},
            8: {"name": "Master", "description": "Advanced specialization, deep expertise"},
            9: {"name": "Professional", "description": "Industry-level proficiency"},
            10: {"name": "Authority", "description": "Research-level or cutting-edge content"}
        }
        
        self.skill_difficulty_mapping = {
            "python": {"beginner": 2, "intermediate": 4, "advanced": 7},
            "data_science": {"beginner": 4, "intermediate": 6, "advanced": 8},
            "web_development": {"beginner": 3, "intermediate": 5, "advanced": 7},
            "mathematics": {"beginner": 3, "intermediate": 6, "advanced": 9},
            "machine_learning": {"beginner": 6, "intermediate": 8, "advanced": 10},
            "language": {"beginner": 2, "intermediate": 4, "advanced": 7}
        }
    
    def assess_learner_ability(self, learner_id: str) -> Dict[str, any]:
        """Assess learner's current ability level across different domains"""
        try:
            learner_data = read_learner(learner_id)
            if not learner_data:
                return {"error": "Learner not found"}
            
            activities = learner_data.get("activities", [])
            if not activities:
                return self._get_default_ability_assessment(learner_id)
            
            # Analyze performance by domain
            domain_performance = self._analyze_domain_performance(activities)
            
            # Calculate ability levels
            ability_assessment = {}
            for domain, performance in domain_performance.items():
                ability_level = self._calculate_ability_level(performance)
                ability_assessment[domain] = ability_level
            
            # Calculate overall ability
            overall_ability = self._calculate_overall_ability(ability_assessment)
            
            return {
                "learner_id": learner_id,
                "domain_abilities": ability_assessment,
                "overall_ability": overall_ability,
                "assessment_timestamp": datetime.now().isoformat(),
                "confidence_score": self._calculate_assessment_confidence(activities)
            }
            
        except Exception as e:
            return {"error": f"Ability assessment failed: {str(e)}"}
    
    def match_content_difficulty(self, learner_id: str, content_list: List[Dict]) -> List[Dict]:
        """Match content difficulty to learner ability"""
        try:
            ability_assessment = self.assess_learner_ability(learner_id)
            if "error" in ability_assessment:
                return []
            
            overall_ability = ability_assessment["overall_ability"]["level"]
            domain_abilities = ability_assessment["domain_abilities"]
            
            matched_content = []
            
            for content in content_list:
                # Extract content difficulty and domain
                content_difficulty = self._extract_content_difficulty(content)
                content_domain = self._extract_content_domain(content)
                
                if not content_difficulty or not content_domain:
                    continue
                
                # Calculate match score
                match_score = self._calculate_difficulty_match_score(
                    overall_ability, domain_abilities, content_difficulty, content_domain, content
                )
                
                # Determine if content is appropriate
                difficulty_gap = abs(content_difficulty - overall_ability["numeric_level"])
                
                if difficulty_gap <= 2:  # Within 2 levels is considered appropriate
                    matched_content.append({
                        "content_id": content.get("id", content.get("_id", "")),
                        "title": content.get("title", ""),
                        "difficulty_level": content_difficulty,
                        "difficulty_name": self.difficulty_levels[content_difficulty]["name"],
                        "match_score": round(match_score, 3),
                        "difficulty_gap": difficulty_gap,
                        "recommendation_reason": self._generate_match_reason(difficulty_gap, match_score),
                        "estimated_completion_time": content.get("metadata", {}).get("estimated_completion_time", 60)
                    })
            
            # Sort by match score (highest first)
            matched_content.sort(key=lambda x: x["match_score"], reverse=True)
            
            return matched_content
            
        except Exception as e:
            print(f"Error in difficulty matching: {e}")
            return []
    
    def _analyze_domain_performance(self, activities: List[Dict]) -> Dict[str, List[Dict]]:
        """Analyze performance by learning domain"""
        domain_performance = {}
        
        for activity in activities:
            domain = self._extract_domain_from_activity(activity)
            if domain:
                if domain not in domain_performance:
                    domain_performance[domain] = []
                
                domain_performance[domain].append({
                    "score": activity.get("score", 0),
                    "duration": activity.get("duration", 0),
                    "activity_type": activity.get("activity_type", ""),
                    "timestamp": activity.get("timestamp", "")
                })
        
        return domain_performance
    
    def _calculate_ability_level(self, domain_activities: List[Dict]) -> Dict[str, any]:
        """Calculate ability level for a specific domain"""
        if not domain_activities:
            return {
                "level": "beginner",
                "numeric_level": 2,
                "confidence": 0.3,
                "evidence": "No data available"
            }
        
        scores = [a["score"] for a in domain_activities if a["score"] is not None]
        
        if not scores:
            return {
                "level": "beginner",
                "numeric_level": 2,
                "confidence": 0.3,
                "evidence": "No scores available"
            }
        
        # Calculate average score and trend
        avg_score = np.mean(scores)
        
        # Determine ability level based on average score
        if avg_score >= 90:
            level = "expert"
            numeric_level = 9
        elif avg_score >= 80:
            level = "advanced"
            numeric_level = 7
        elif avg_score >= 70:
            level = "intermediate"
            numeric_level = 5
        elif avg_score >= 60:
            level = "novice"
            numeric_level = 3
        else:
            level = "beginner"
            numeric_level = 2
        
        # Calculate confidence based on activity count and consistency
        activity_count = len(domain_activities)
        if activity_count >= 10:
            confidence = 0.9
        elif activity_count >= 5:
            confidence = 0.7
        elif activity_count >= 3:
            confidence = 0.5
        else:
            confidence = 0.3
        
        # Adjust confidence based on score consistency
        if len(scores) > 1:
            score_variance = np.var(scores)
            if score_variance < 100:  # Low variance = high confidence
                confidence += 0.1
            elif score_variance > 400:  # High variance = lower confidence
                confidence -= 0.1
        
        confidence = max(0.1, min(0.95, confidence))
        
        return {
            "level": level,
            "numeric_level": numeric_level,
            "confidence": round(confidence, 3),
            "average_score": round(avg_score, 2),
            "activity_count": activity_count,
            "score_range": [min(scores), max(scores)]
        }
    
    def _calculate_overall_ability(self, domain_abilities: Dict) -> Dict[str, any]:
        """Calculate overall ability across all domains"""
        if not domain_abilities:
            return {
                "level": "beginner",
                "numeric_level": 2,
                "confidence": 0.3
            }
        
        # Calculate weighted average numeric level
        total_weight = 0
        weighted_level = 0
        total_confidence = 0
        
        for domain, ability in domain_abilities.items():
            weight = ability["confidence"]
            weighted_level += ability["numeric_level"] * weight
            total_weight += weight
            total_confidence += ability["confidence"]
        
        if total_weight > 0:
            overall_numeric_level = weighted_level / total_weight
            avg_confidence = total_confidence / len(domain_abilities)
        else:
            overall_numeric_level = 2
            avg_confidence = 0.3
        
        # Determine overall level
        overall_level = self._numeric_to_level(overall_numeric_level)
        
        return {
            "level": overall_level,
            "numeric_level": round(overall_numeric_level, 1),
            "confidence": round(avg_confidence, 3),
            "domains_assessed": len(domain_abilities)
        }
    
    def _numeric_to_level(self, numeric_level: float) -> str:
        """Convert numeric level to level name"""
        if numeric_level >= 9:
            return "expert"
        elif numeric_level >= 7:
            return "advanced"
        elif numeric_level >= 5:
            return "intermediate"
        elif numeric_level >= 3:
            return "novice"
        else:
            return "beginner"
    
    def _extract_domain_from_activity(self, activity: Dict) -> Optional[str]:
        """Extract learning domain from activity"""
        activity_type = activity.get("activity_type", "").lower()
        
        domain_mapping = {
            "programming": ["python", "code", "programming", "algorithm"],
            "data_science": ["data", "analytics", "statistics", "machine_learning"],
            "web_development": ["web", "html", "css", "javascript"],
            "mathematics": ["math", "algebra", "calculus"],
            "language": ["english", "writing", "communication"],
            "design": ["design", "ux", "ui", "graphics"]
        }
        
        for domain, keywords in domain_mapping.items():
            if any(keyword in activity_type for keyword in keywords):
                return domain
        
        return "general"
    
    def _extract_content_difficulty(self, content: Dict) -> Optional[int]:
        """Extract difficulty level from content"""
        # Try to get numeric difficulty from metadata
        metadata = content.get("metadata", {})
        if isinstance(metadata, dict):
            difficulty_score = metadata.get("difficulty_score")
            if difficulty_score and 1 <= difficulty_score <= 10:
                return difficulty_score
        
        # Fall back to text-based difficulty
        difficulty_text = content.get("difficulty_level", "").lower()
        
        difficulty_mapping = {
            "beginner": 2,
            "novice": 3,
            "elementary": 4,
            "intermediate": 5,
            "upper intermediate": 6,
            "advanced": 7,
            "expert": 8,
            "master": 9,
            "professional": 10
        }
        
        return difficulty_mapping.get(difficulty_text, 5)  # Default to intermediate
    
    def _extract_content_domain(self, content: Dict) -> Optional[str]:
        """Extract domain from content"""
        # Extract from course_id or title
        course_id = content.get("course_id", "").lower()
        title = content.get("title", "").lower()
        content_type = content.get("content_type", "").lower()
        
        # Combine all text for analysis
        text_to_analyze = f"{course_id} {title} {content_type}"
        
        domain_mapping = {
            "programming": ["python", "code", "programming", "software"],
            "data_science": ["data", "analytics", "statistics", "machine_learning", "ai"],
            "web_development": ["web", "html", "css", "javascript", "frontend", "react"],
            "mathematics": ["math", "algebra", "calculus", "statistics"],
            "language": ["english", "writing", "communication", "language"],
            "design": ["design", "ux", "ui", "graphics", "visual"]
        }
        
        for domain, keywords in domain_mapping.items():
            if any(keyword in text_to_analyze for keyword in keywords):
                return domain
        
        return "general"
    
    def _calculate_difficulty_match_score(self, overall_ability: Dict, domain_abilities: Dict, 
                                        content_difficulty: int, content_domain: str, content: Dict) -> float:
        """Calculate how well content difficulty matches learner ability"""
        
        # Base score from overall ability match
        overall_numeric = overall_ability["numeric_level"]
        difficulty_gap = abs(content_difficulty - overall_numeric)
        
        # Base score (higher score for better match)
        if difficulty_gap == 0:
            base_score = 1.0
        elif difficulty_gap == 1:
            base_score = 0.9
        elif difficulty_gap == 2:
            base_score = 0.7
        else:
            base_score = max(0.1, 0.5 - (difficulty_gap * 0.15))
        
        # Adjust for domain-specific ability
        if content_domain in domain_abilities:
            domain_ability = domain_abilities[content_domain]["numeric_level"]
            domain_gap = abs(content_difficulty - domain_ability)
            domain_bonus = max(0, 0.2 - (domain_gap * 0.05))
            base_score += domain_bonus
        
        # Adjust for content quality indicators
        metadata = content.get("metadata", {})
        estimated_time = metadata.get("estimated_completion_time", 60)
        
        # Bonus for appropriate duration (45-120 minutes)
        if 45 <= estimated_time <= 120:
            base_score += 0.1
        elif estimated_time > 180:  # Penalty for very long content
            base_score -= 0.1
        
        return max(0.0, min(1.0, base_score))
    
    def _generate_match_reason(self, difficulty_gap: int, match_score: float) -> str:
        """Generate reason for difficulty match recommendation"""
        if difficulty_gap == 0:
            return f"Perfect difficulty match for your current level"
        elif difficulty_gap == 1:
            return f"Excellent match - slightly challenging content"
        elif difficulty_gap == 2:
            return f"Good match - appropriately challenging for growth"
        else:
            if difficulty_gap > 2 and match_score > 0.5:
                return f"Challenging content - may require additional effort"
            else:
                return f"May be too {'easy' if difficulty_gap > 2 else 'difficult'} for current level"
    
    def _calculate_assessment_confidence(self, activities: List[Dict]) -> float:
        """Calculate confidence in ability assessment"""
        if not activities:
            return 0.3
        
        # More activities = higher confidence
        activity_count = len(activities)
        if activity_count >= 20:
            confidence = 0.9
        elif activity_count >= 10:
            confidence = 0.8
        elif activity_count >= 5:
            confidence = 0.6
        else:
            confidence = 0.4
        
        # Consider recency of activities
        recent_activities = 0
        cutoff_date = datetime.now() - timedelta(days=30)
        
        for activity in activities:
            try:
                activity_date = datetime.fromisoformat(activity.get("timestamp", "").replace('Z', '+00:00'))
                if activity_date >= cutoff_date:
                    recent_activities += 1
            except (ValueError, TypeError):
                continue
        
        # Boost confidence if recent activities exist
        if recent_activities > 0:
            confidence += 0.1
        
        return max(0.1, min(0.95, confidence))
    
    def _get_default_ability_assessment(self, learner_id: str) -> Dict[str, any]:
        """Default ability assessment for new learners"""
        return {
            "learner_id": learner_id,
            "domain_abilities": {},
            "overall_ability": {
                "level": "beginner",
                "numeric_level": 2,
                "confidence": 0.3
            },
            "assessment_timestamp": datetime.now().isoformat(),
            "confidence_score": 0.3,
            "note": "New learner - ability assessment pending activity completion"
        }


class AdaptiveRecommendationEngine:
    """Engine for generating adaptive learning recommendations"""
    
    def __init__(self):
        self.difficulty_matcher = DifficultyMatchingAlgorithm()
        
        self.recommendation_weights = {
            "difficulty_match": 0.3,
            "learning_style_match": 0.25,
            "interest_match": 0.2,
            "progression_value": 0.15,
            "engagement_potential": 0.1
        }
    
    def generate_adaptive_recommendations(self, learner_id: str, num_recommendations: int = 5) -> Dict[str, any]:
        """Generate comprehensive adaptive recommendations"""
        try:
            learner_data = read_learner(learner_id)
            if not learner_data:
                return {"error": "Learner not found"}
            
            # Get all available content
            all_content = read_contents()
            if not all_content:
                return {"error": "No content available for recommendations"}
            
            # Generate recommendations based on multiple factors
            recommendations = []
            
            for content in all_content:
                recommendation_score = self._calculate_adaptive_score(learner_data, content)
                
                if recommendation_score["total_score"] > 0.3:  # Minimum threshold
                    recommendations.append({
                        "content": content,
                        "score_breakdown": recommendation_score,
                        "total_score": recommendation_score["total_score"]
                    })
            
            # Sort by total score
            recommendations.sort(key=lambda x: x["total_score"], reverse=True)
            
            # Select top recommendations
            top_recommendations = recommendations[:num_recommendations]
            
            # Generate learning path suggestions
            learning_path = self._generate_learning_path(learner_data, top_recommendations)
            
            return {
                "learner_id": learner_id,
                "recommendations": top_recommendations,
                "learning_path": learning_path,
                "recommendation_timestamp": datetime.now().isoformat(),
                "total_content_evaluated": len(all_content),
                "recommendations_selected": len(top_recommendations)
            }
            
        except Exception as e:
            return {"error": f"Adaptive recommendation generation failed: {str(e)}"}
    
    def _calculate_adaptive_score(self, learner_data: Dict, content: Dict) -> Dict[str, float]:
        """Calculate comprehensive adaptive score for content"""
        
        # Difficulty match score
        difficulty_scores = self.difficulty_matcher.match_content_difficulty(
            learner_data["id"], [content]
        )
        difficulty_score = difficulty_scores[0]["match_score"] if difficulty_scores else 0.5
        
        # Learning style match score
        learning_style_score = self._calculate_learning_style_match(learner_data, content)
        
        # Interest/preference match score
        interest_score = self._calculate_interest_match(learner_data, content)
        
        # Progression value score
        progression_score = self._calculate_progression_value(learner_data, content)
        
        # Engagement potential score
        engagement_score = self._calculate_engagement_potential(learner_data, content)
        
        # Calculate weighted total score
        total_score = (
            difficulty_score * self.recommendation_weights["difficulty_match"] +
            learning_style_score * self.recommendation_weights["learning_style_match"] +
            interest_score * self.recommendation_weights["interest_match"] +
            progression_score * self.recommendation_weights["progression_value"] +
            engagement_score * self.recommendation_weights["engagement_potential"]
        )
        
        return {
            "difficulty_match": difficulty_score,
            "learning_style_match": learning_style_score,
            "interest_match": interest_score,
            "progression_value": progression_score,
            "engagement_potential": engagement_score,
            "total_score": round(total_score, 3)
        }
    
    def _calculate_learning_style_match(self, learner_data: Dict, content: Dict) -> float:
        """Calculate how well content matches learner's learning style"""
        learner_style = learner_data.get("learning_style", "Mixed")
        content_type = content.get("content_type", "").lower()
        
        # Learning style preferences
        style_content_mapping = {
            "Visual": ["video", "infographic", "diagram", "chart"],
            "Auditory": ["audio", "podcast", "discussion", "lecture"],
            "Kinesthetic": ["interactive", "simulation", "hands_on", "project"],
            "Reading/Writing": ["article", "text", "documentation", "written"],
            "Mixed": ["video", "article", "interactive"]  # Broad preferences
        }
        
        preferred_content_types = style_content_mapping.get(learner_style, style_content_mapping["Mixed"])
        
        # Check if content type matches preferences
        for preferred_type in preferred_content_types:
            if preferred_type in content_type:
                return 1.0
        
        # Partial match
        if any(keyword in content_type for keyword in ["educational", "learning", "tutorial"]):
            return 0.6
        
        return 0.3  # Default low score
    
    def _calculate_interest_match(self, learner_data: Dict, content: Dict) -> float:
        """Calculate how well content matches learner interests"""
        learner_preferences = learner_data.get("preferences", [])
        if not learner_preferences:
            return 0.5
        
        # Extract content topics
        content_title = content.get("title", "").lower()
        content_description = content.get("description", "").lower()
        content_tags = [tag.lower() for tag in content.get("tags", [])]
        content_course_id = content.get("course_id", "").lower()
        
        # Combine all content text
        content_text = f"{content_title} {content_description} {content_course_id} {' '.join(content_tags)}"
        
        # Calculate interest match
        match_score = 0.0
        for preference in learner_preferences:
            preference_lower = preference.lower()
            if preference_lower in content_text:
                match_score += 1.0
        
        # Normalize score
        if len(learner_preferences) > 0:
            match_score = match_score / len(learner_preferences)
        
        return min(1.0, match_score)
    
    def _calculate_progression_value(self, learner_data: Dict, content: Dict) -> float:
        """Calculate how valuable content is for learner's progression"""
        learner_activities = learner_data.get("activities", [])
        
        if not learner_activities:
            return 0.8  # High value for new learners
        
        # Check if content covers new topics
        content_topics = self._extract_content_topics(content)
        completed_topics = set()
        
        for activity in learner_activities:
            activity_type = activity.get("activity_type", "").lower()
            # Extract completed topics from activities
            for topic in content_topics:
                if topic.lower() in activity_type:
                    completed_topics.add(topic.lower())
        
        # Calculate novelty score
        new_topics = len(content_topics) - len(completed_topics.intersection(set([t.lower() for t in content_topics])))
        total_topics = len(content_topics) if content_topics else 1
        
        novelty_score = new_topics / total_topics
        
        # Consider content difficulty for progression
        difficulty_score = self.difficulty_matcher._extract_content_difficulty(content)
        learner_ability = self.difficulty_matcher._calculate_overall_ability({})
        
        # Optimal progression: content slightly above current ability
        difficulty_gap = difficulty_score - learner_ability["numeric_level"]
        if 0.5 <= difficulty_gap <= 2.0:  # Slightly challenging
            progression_bonus = 0.3
        elif difficulty_gap <= 0:  # Too easy
            progression_bonus = 0.1
        else:  # Too hard
            progression_bonus = 0.0
        
        return min(1.0, novelty_score + progression_bonus)
    
    def _calculate_engagement_potential(self, learner_data: Dict, content: Dict) -> float:
        """Calculate potential for learner engagement with content"""
        content_type = content.get("content_type", "").lower()
        
        # Engagement factors by content type
        engagement_factors = {
            "interactive": 0.9,
            "video": 0.8,
            "quiz": 0.7,
            "assignment": 0.7,
            "article": 0.6,
            "text": 0.5,
            "audio": 0.6,
            "simulation": 0.9
        }
        
        base_engagement = 0.5
        for content_key, engagement_value in engagement_factors.items():
            if content_key in content_type:
                base_engagement = max(base_engagement, engagement_value)
        
        # Adjust based on content length
        estimated_time = content.get("metadata", {}).get("estimated_completion_time", 60)
        
        # Optimal engagement: 30-90 minutes
        if 30 <= estimated_time <= 90:
            base_engagement += 0.1
        elif estimated_time > 120:  # Penalty for very long content
            base_engagement -= 0.1
        
        return max(0.1, min(1.0, base_engagement))
    
    def _extract_content_topics(self, content: Dict) -> List[str]:
        """Extract topics from content"""
        topics = []
        
        # From tags
        topics.extend(content.get("tags", []))
        
        # From metadata
        metadata = content.get("metadata", {})
        if isinstance(metadata, dict):
            topics.extend(metadata.get("topics", []))
        
        # From title and description (simple keyword extraction)
        title = content.get("title", "").lower()
        description = content.get("description", "").lower()
        
        # Common topic keywords
        topic_keywords = [
            "python", "programming", "data science", "machine learning", "web development",
            "mathematics", "statistics", "algorithms", "database", "networking",
            "design", "ux", "ui", "language", "writing", "communication"
        ]
        
        for keyword in topic_keywords:
            if keyword in title or keyword in description:
                topics.append(keyword)
        
        return list(set(topics))  # Remove duplicates
    
    def _generate_learning_path(self, learner_data: Dict, recommendations: List[Dict]) -> List[Dict]:
        """Generate suggested learning path from recommendations"""
        if not recommendations:
            return []
        
        # Sort recommendations by difficulty for path generation
        sorted_recommendations = sorted(recommendations, key=lambda x: x["content"].get("metadata", {}).get("difficulty_score", 5))
        
        learning_path = []
        for i, rec in enumerate(sorted_recommendations[:5]):  # Top 5 for path
            content = rec["content"]
            learning_path.append({
                "sequence": i + 1,
                "content_id": content.get("id", content.get("_id", "")),
                "title": content.get("title", ""),
                "difficulty": content.get("difficulty_level", "intermediate"),
                "estimated_time": content.get("metadata", {}).get("estimated_completion_time", 60),
                "prerequisites_met": i == 0,  # First item has no prerequisites
                "reason": rec["score_breakdown"]["total_score"]
            })
        
        return learning_path


# Global instances
difficulty_matcher = DifficultyMatchingAlgorithm()
adaptive_recommender = AdaptiveRecommendationEngine()

def match_content_difficulty(learner_id: str, content_list: List[Dict] = None) -> List[Dict]:
    """Main function to match content difficulty"""
    if content_list is None:
        content_list = read_contents()
    return difficulty_matcher.match_content_difficulty(learner_id, content_list)

def generate_adaptive_recommendations(learner_id: str, num_recommendations: int = 5) -> Dict[str, any]:
    """Main function to generate adaptive recommendations"""
    return adaptive_recommender.generate_adaptive_recommendations(learner_id, num_recommendations)

if __name__ == "__main__":
    # Test the systems
    matcher = DifficultyMatchingAlgorithm()
    recommender = AdaptiveRecommendationEngine()
    
    print("Difficulty Matching Algorithm and Adaptive Recommendation Engine initialized")
    
    # Sample test
    sample_learner = {
        "id": "test-learner",
        "learning_style": "Visual",
        "preferences": ["Python", "Data Science"],
        "activities": [
            {"activity_type": "python_quiz", "score": 75},
            {"activity_type": "data_science_video", "score": 80}
        ]
    }
    
    sample_content = {
        "id": "test-content",
        "title": "Advanced Python Programming",
        "content_type": "video",
        "difficulty_level": "intermediate",
        "metadata": {"difficulty_score": 5, "estimated_completion_time": 90}
    }
    
    difficulty_match = matcher._calculate_difficulty_match_score(
        {"numeric_level": 4.5}, {}, 5, "programming", sample_content
    )
    
    print(f"Sample Difficulty Match Score: {difficulty_match}")