from marshmallow import Schema, fields, validate, ValidationError, post_load
from datetime import datetime

# Learner Schemas
class ActivitySchema(Schema):
    timestamp = fields.Str(required=True)
    activity_type = fields.Str(required=True, validate=validate.OneOf([
        'started', 'viewed', 'completed', 'module_completed', 'quiz_attempted', 'reviewed', 'abandoned'
    ]))
    duration = fields.Float(required=True, validate=validate.Range(min=0))
    score = fields.Float(validate=validate.Range(min=0, max=100), allow_none=True)

class LearnerProfileSchema(Schema):
    learning_style_confidence = fields.Float(validate=validate.Range(min=0, max=1))
    primary_interest_areas = fields.List(fields.Str())
    skill_levels = fields.Dict(values=fields.Str())
    accessibility_needs = fields.List(fields.Str())
    study_schedule = fields.Dict()
    motivation_factors = fields.List(fields.Str())
    learning_pace_preference = fields.Str(validate=validate.OneOf(['slow', 'normal', 'fast', 'mixed']))
    engagement_history = fields.Dict()

class LearningMetricsSchema(Schema):
    total_study_time = fields.Float(validate=validate.Range(min=0))
    average_session_length = fields.Float(validate=validate.Range(min=0))
    completion_rate = fields.Float(validate=validate.Range(min=0, max=1))
    knowledge_retention_score = fields.Float(validate=validate.Range(min=0, max=1))
    skill_progression = fields.List(fields.Dict())
    learning_velocity_trend = fields.Str(validate=validate.OneOf(['accelerating', 'stable', 'decelerating']))
    preferred_study_times = fields.List(fields.Str())
    difficulty_adjustment_count = fields.Int(validate=validate.Range(min=0))

class LearnerCreateSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    age = fields.Int(required=True, validate=validate.Range(min=1, max=120))
    gender = fields.Str(required=True, validate=validate.OneOf(['male', 'female', 'other']))
    learning_style = fields.Str(required=True, validate=validate.OneOf(['visual', 'auditory', 'kinesthetic', 'reading']))
    preferences = fields.List(fields.Str(), required=True, validate=validate.Length(min=1))
    profile = fields.Nested(LearnerProfileSchema, allow_none=True)
    learning_metrics = fields.Nested(LearningMetricsSchema, allow_none=True)
    
    @post_load
    def ensure_profile_defaults(self, data, **kwargs):
        # Ensure profile and learning_metrics have defaults if not provided
        if 'profile' not in data or data['profile'] is None:
            data['profile'] = {}
        if 'learning_metrics' not in data or data['learning_metrics'] is None:
            data['learning_metrics'] = {}
        return data

class LearnerUpdateSchema(Schema):
    name = fields.Str(validate=validate.Length(min=1, max=100))
    age = fields.Int(validate=validate.Range(min=1, max=120))
    gender = fields.Str(validate=validate.OneOf(['male', 'female', 'other']))
    learning_style = fields.Str(validate=validate.OneOf(['visual', 'auditory', 'kinesthetic', 'reading']))
    preferences = fields.List(fields.Str(), validate=validate.Length(min=1))

class ActivityLogSchema(Schema):
    activity_type = fields.Str(required=True, validate=validate.OneOf([
        'started',           # Content access initiated
        'viewed',            # Content viewed (partial)
        'completed',         # Full content completion
        'module_completed',  # Module/section completion
        'quiz_attempted',    # Quiz or assessment taken
        'reviewed',          # Content revisited
        'abandoned'          # Content started but not finished
    ]))
    duration = fields.Float(required=True, validate=validate.Range(min=0))
    score = fields.Float(validate=validate.Range(min=0, max=100))

class ProgressLogSchema(Schema):
    milestone = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    engagement_score = fields.Float(validate=validate.Range(min=0, max=100))
    learning_velocity = fields.Float(validate=validate.Range(min=0))

class CompletionPredictionSchema(Schema):
    avg_score = fields.Float(required=True, validate=validate.Range(min=0, max=100))
    time_spent = fields.Float(required=True, validate=validate.Range(min=0))
    difficulty = fields.Int(required=True, validate=validate.Range(min=1, max=5))

class DifficultyAdjustmentSchema(Schema):
    recent_score = fields.Float(required=True, validate=validate.Range(min=0, max=100))

# Content Schemas
class ContentMetadataSchema(Schema):
    topics = fields.List(fields.Str())
    prerequisites = fields.List(fields.Str())
    learning_objectives = fields.List(fields.Str())
    estimated_completion_time = fields.Int(validate=validate.Range(min=0), allow_none=True)
    difficulty_score = fields.Int(validate=validate.Range(min=1, max=10))
    skill_requirements = fields.Dict(values=fields.Str())
    content_sources = fields.List(fields.Str())
    accessibility_features = fields.List(fields.Str())
    assessment_criteria = fields.List(fields.Str())
    related_content = fields.List(fields.Str())

class ContentCreateSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    description = fields.Str(required=True, validate=validate.Length(min=1, max=1000))
    content_type = fields.Str(required=True, validate=validate.OneOf(['video', 'quiz', 'article', 'project', 'assignment', 'interactive']))
    course_id = fields.Str(required=True)
    module_id = fields.Str(allow_none=True)
    difficulty_level = fields.Str(required=True, validate=validate.OneOf(['beginner', 'intermediate', 'advanced']))
    tags = fields.List(fields.Str())
    metadata = fields.Nested(ContentMetadataSchema, allow_none=True)
    
    @post_load
    def ensure_metadata_defaults(self, data, **kwargs):
        if 'metadata' not in data or data['metadata'] is None:
            data['metadata'] = {}
        return data

class ContentUpdateSchema(Schema):
    title = fields.Str(validate=validate.Length(min=1, max=200))
    description = fields.Str(validate=validate.Length(min=1, max=1000))
    content_type = fields.Str(validate=validate.OneOf(['video', 'quiz', 'article', 'project', 'assignment', 'interactive']))
    course_id = fields.Str()
    module_id = fields.Str(allow_none=True)
    difficulty_level = fields.Str(validate=validate.OneOf(['beginner', 'intermediate', 'advanced']))
    tags = fields.List(fields.Str())
    metadata = fields.Nested(ContentMetadataSchema, allow_none=True)

# Engagement Schemas
class InteractionMetricsSchema(Schema):
    click_count = fields.Int(validate=validate.Range(min=0))
    scroll_depth = fields.Float(validate=validate.Range(min=0, max=1))
    pause_count = fields.Int(validate=validate.Range(min=0))
    replay_count = fields.Int(validate=validate.Range(min=0))
    completion_percentage = fields.Float(validate=validate.Range(min=0, max=1))
    attention_span = fields.Float(validate=validate.Range(min=0))
    interaction_frequency = fields.Float(validate=validate.Range(min=0))
    device_type = fields.Str()
    browser_type = fields.Str()

class EngagementPatternSchema(Schema):
    learning_session_id = fields.Str(allow_none=True)
    previous_engagement_time = fields.DateTime(allow_none=True)
    engagement_frequency_score = fields.Float(validate=validate.Range(min=0, max=1))
    consistency_score = fields.Float(validate=validate.Range(min=0, max=1))
    engagement_streak = fields.Int(validate=validate.Range(min=0))
    preferred_engagement_times = fields.List(fields.Str())
    engagement_method = fields.Str(validate=validate.OneOf(['standard', 'guided', 'self_paced']))

class EngagementCreateSchema(Schema):
    learner_id = fields.Str(required=True)
    content_id = fields.Str(required=True)
    course_id = fields.Str(required=True)
    engagement_type = fields.Str(required=True, validate=validate.OneOf(['view', 'complete', 'quiz_attempt', 'feedback', 'pause', 'resume']))
    duration = fields.Float(allow_none=True, validate=validate.Range(min=0))
    score = fields.Float(allow_none=True, validate=validate.Range(min=0, max=100))
    feedback = fields.Str(allow_none=True)
    interaction_metrics = fields.Nested(InteractionMetricsSchema, allow_none=True)
    engagement_pattern = fields.Nested(EngagementPatternSchema, allow_none=True)
    
    @post_load
    def ensure_engagement_defaults(self, data, **kwargs):
        if 'interaction_metrics' not in data or data['interaction_metrics'] is None:
            data['interaction_metrics'] = {}
        if 'engagement_pattern' not in data or data['engagement_pattern'] is None:
            data['engagement_pattern'] = {}
        return data

class EngagementUpdateSchema(Schema):
    engagement_type = fields.Str(validate=validate.OneOf(['view', 'complete', 'quiz_attempt', 'feedback', 'pause', 'resume']))
    duration = fields.Float(allow_none=True, validate=validate.Range(min=0))
    score = fields.Float(allow_none=True, validate=validate.Range(min=0, max=100))
    feedback = fields.Str(allow_none=True)
    interaction_metrics = fields.Nested(InteractionMetricsSchema, allow_none=True)
    engagement_pattern = fields.Nested(EngagementPatternSchema, allow_none=True)

# Learning History Schemas
class LearningHistorySchema(Schema):
    total_modules_completed = fields.Int(validate=validate.Range(min=0))
    total_time_spent = fields.Float(validate=validate.Range(min=0))
    average_score = fields.Float(validate=validate.Range(min=0, max=100))
    best_score = fields.Float(validate=validate.Range(min=0, max=100))
    improvement_rate = fields.Float(validate=validate.Range(min=0))
    skill_breakdown = fields.Dict(values=fields.Dict(values=fields.Float()))
    module_completion_sequence = fields.List(fields.Str())
    learning_gaps_identified = fields.List(fields.Str())
    mastery_levels = fields.Dict(values=fields.Str())

class LearningVelocitySchema(Schema):
    current_velocity = fields.Float(validate=validate.Range(min=0))
    velocity_trend = fields.Str(validate=validate.OneOf(['accelerating', 'stable', 'decelerating']))
    peak_velocity = fields.Float(validate=validate.Range(min=0))
    average_session_length = fields.Float(validate=validate.Range(min=0))
    study_frequency = fields.Float(validate=validate.Range(min=0))
    optimal_pace_indicator = fields.Float(validate=validate.Range(min=0, max=1))

class ProgressLogCreateSchema(Schema):
    learner_id = fields.Str(required=True)
    milestone = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    engagement_score = fields.Float(validate=validate.Range(min=0, max=100))
    learning_velocity = fields.Nested(LearningVelocitySchema, allow_none=True)
    learning_history = fields.Nested(LearningHistorySchema, allow_none=True)

class AnalyticsQuerySchema(Schema):
    group_by = fields.Str(validate=validate.OneOf(['learning_style', 'gender', 'age']))
    learner_id = fields.Str()

# Validation functions
def validate_learner_data(data):
    schema = LearnerCreateSchema()
    errors = schema.validate(data)
    if errors:
        raise ValidationError(errors)
    return data

def validate_learner_update_data(data):
    schema = LearnerUpdateSchema()
    errors = schema.validate(data)
    if errors:
        raise ValidationError(errors)
    return data

def validate_activity_data(data):
    schema = ActivityLogSchema()
    errors = schema.validate(data)
    if errors:
        raise ValidationError(errors)
    return data

def validate_content_data(data):
    schema = ContentCreateSchema()
    errors = schema.validate(data)
    if errors:
        raise ValidationError(errors)
    return data

def validate_content_update_data(data):
    schema = ContentUpdateSchema()
    errors = schema.validate(data)
    if errors:
        raise ValidationError(errors)
    return data

def validate_engagement_data(data):
    schema = EngagementCreateSchema()
    errors = schema.validate(data)
    if errors:
        raise ValidationError(errors)
    return data

def validate_engagement_update_data(data):
    schema = EngagementUpdateSchema()
    errors = schema.validate(data)
    if errors:
        raise ValidationError(errors)
    return data

def validate_progress_data(data):
    schema = ProgressLogSchema()
    errors = schema.validate(data)
    if errors:
        raise ValidationError(errors)
    return data

def validate_progress_log_data(data):
    schema = ProgressLogCreateSchema()
    errors = schema.validate(data)
    if errors:
        raise ValidationError(errors)
    return data

def validate_prediction_data(data):
    schema = CompletionPredictionSchema()
    errors = schema.validate(data)
    if errors:
        raise ValidationError(errors)
    return data

def validate_difficulty_adjustment_data(data):
    schema = DifficultyAdjustmentSchema()
    errors = schema.validate(data)
    if errors:
        raise ValidationError(errors)
    return data

def validate_analytics_query_data(data):
    schema = AnalyticsQuerySchema()
    errors = schema.validate(data)
    if errors:
        raise ValidationError(errors)
    return data