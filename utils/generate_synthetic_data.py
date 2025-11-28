import json
import os
import sys
import numpy as np
from faker import Faker
from datetime import datetime, timedelta, timezone
from pymongo import MongoClient, InsertOne
from pymongo.errors import PyMongoError

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.learner import Learner
from models.content import Content
from models.engagement import Engagement

fake = Faker()

def generate_learners(num_learners=1000):
    """Generate synthetic learner data"""
    learners = []

    learning_styles = ['visual', 'auditory', 'kinesthetic', 'reading/writing']
    genders = ['male', 'female', 'non-binary', 'prefer_not_to_say']
    preference_options = ['videos', 'quizzes', 'discussions', 'projects', 'readings']

    for _ in range(num_learners):
        # Generate age with realistic distribution (18-65, skewed younger)
        age = int(np.random.beta(2, 5) * 47 + 18)

        # Generate preferences (1-5 preferences per learner)
        num_prefs = np.random.randint(1, 6)
        preferences = np.random.choice(preference_options, num_prefs, replace=False).tolist()

        learner = Learner(
            name=fake.name(),
            age=age,
            gender=np.random.choice(genders, p=[0.45, 0.45, 0.05, 0.05]),
            learning_style=np.random.choice(learning_styles),
            preferences=preferences
        )
        learners.append(learner)

    return learners

def generate_courses(num_courses=200):
    """Generate synthetic course content data"""
    courses = []

    content_types = ['video', 'quiz', 'article', 'interactive', 'assignment']
    difficulty_levels = ['beginner', 'intermediate', 'advanced']
    course_names = [
        'Introduction to Python', 'Data Science Fundamentals', 'Machine Learning Basics',
        'Web Development', 'Database Design', 'Algorithm Design', 'Statistics for Data Science',
        'Deep Learning', 'Computer Vision', 'Natural Language Processing', 'DevOps',
        'Cloud Computing', 'Cybersecurity', 'Mobile App Development', 'Game Development'
    ]

    for i in range(num_courses):
        course_id = f"course_{i+1:03d}"

        # Generate modules within courses
        num_modules = np.random.randint(3, 12)
        for module_num in range(1, num_modules + 1):
            module_id = f"{course_id}_module_{module_num}"

            # Generate content items per module
            num_content_items = np.random.randint(2, 8)
            for content_num in range(1, num_content_items + 1):
                content = Content(
                    title=f"{fake.sentence(nb_words=6)[:-1]}",
                    description=fake.paragraph(nb_sentences=2),
                    content_type=np.random.choice(content_types),
                    course_id=course_id,
                    module_id=module_id,
                    difficulty_level=np.random.choice(difficulty_levels, p=[0.5, 0.3, 0.2]),
                    tags=np.random.choice(['programming', 'math', 'theory', 'practice', 'project'],
                                        np.random.randint(1, 4), replace=False).tolist(),
                    metadata={
                        'estimated_duration': np.random.randint(5, 120),  # minutes
                        'prerequisites': np.random.choice(['none', 'basic', 'intermediate'], p=[0.3, 0.5, 0.2])
                    }
                )
                courses.append(content)

    return courses

def generate_engagements(learners, courses, num_engagements=50000):
    """Generate synthetic engagement history data"""
    engagements = []

    engagement_types = ['view', 'complete', 'quiz_attempt', 'feedback', 'bookmark']

    for _ in range(num_engagements):
        learner = np.random.choice(learners)
        content = np.random.choice(courses)

        # Generate timestamp within last 6 months
        days_ago = np.random.randint(0, 180)
        timestamp = datetime.now(timezone.utc) - timedelta(days=days_ago, hours=np.random.randint(0, 24))

        engagement_type = np.random.choice(engagement_types, p=[0.4, 0.3, 0.15, 0.1, 0.05])

        # Generate duration based on content type
        if engagement_type in ['view', 'complete']:
            duration = np.random.exponential(30)  # average 30 minutes
        elif engagement_type == 'quiz_attempt':
            duration = np.random.exponential(15)  # average 15 minutes
        else:
            duration = np.random.exponential(5)   # average 5 minutes

        # Generate score for quiz attempts
        score = None
        if engagement_type == 'quiz_attempt':
            score = np.random.beta(2, 2) * 100  # scores between 0-100, centered around 50

        engagement = Engagement(
            learner_id=learner.id,
            content_id=content.id,
            course_id=content.course_id,
            engagement_type=engagement_type,
            duration=round(duration, 2),
            score=round(score, 2) if score else None,
            feedback=fake.sentence() if np.random.random() < 0.1 else None,  # 10% have feedback
            metadata={
                'device_type': np.random.choice(['desktop', 'mobile', 'tablet'], p=[0.6, 0.3, 0.1]),
                'completion_rate': np.random.uniform(0, 1) if engagement_type == 'view' else None
            },
            timestamp=timestamp
        )
        engagements.append(engagement)

    return engagements

def save_to_json(data, filename, data_dir='data'):
    """Save data to JSON file"""
    os.makedirs(data_dir, exist_ok=True)
    filepath = os.path.join(data_dir, filename)

    # Convert models to dict
    json_data = [item.to_dict() for item in data]

    with open(filepath, 'w') as f:
        json.dump(json_data, f, indent=2, default=str)

    print(f"Saved {len(data)} records to {filepath}")
    return filepath

def bulk_insert_to_mongodb(data, collection_name):
    """Bulk insert data into MongoDB"""
    try:
        client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
        db = client["learning_agent_db"]
        collection = db[collection_name]

        # Convert models to dict and prepare bulk operations
        operations = [InsertOne(item.to_dict()) for item in data]

        if operations:
            result = collection.bulk_write(operations)
            print(f"Inserted {result.inserted_count} documents into {collection_name}")
            return result.inserted_count
        else:
            print(f"No data to insert into {collection_name}")
            return 0

    except PyMongoError as e:
        print(f"⚠ MongoDB bulk insert error for {collection_name}: {e}")
        return 0

def main():
    """Generate all synthetic data"""
    print("Generating synthetic data...")

    # Generate data
    print("Generating learners...")
    learners = generate_learners(1000)

    print("Generating courses...")
    courses = generate_courses(200)

    print("Generating engagements...")
    engagements = generate_engagements(learners, courses, 50000)

    # Save to JSON
    print("Saving to JSON files...")
    save_to_json(learners, 'learners.json')
    save_to_json(courses, 'courses.json')
    save_to_json(engagements, 'engagements.json')

    # Bulk insert to MongoDB
    print("Inserting to MongoDB...")
    bulk_insert_to_mongodb(learners, 'learners')
    bulk_insert_to_mongodb(courses, 'contents')
    bulk_insert_to_mongodb(engagements, 'engagements')

    print("Synthetic data generation complete!")

if __name__ == "__main__":
    main()