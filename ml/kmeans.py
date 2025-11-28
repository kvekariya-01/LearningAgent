# app/ml/kmeans.py
import os
import json
import joblib
import numpy as np
from sklearn.mixture import GaussianMixture

def aggregate_engagement_data(engagements_file='data/engagements.json', learners_file='data/learners.json'):
    with open(engagements_file) as f:
        engagements = json.load(f)
    with open(learners_file) as f:
        learners = json.load(f)
    
    learner_data = {l['id']: {'total_time': 0, 'scores': [], 'style': l['learning_style']} for l in learners}
    
    for e in engagements:
        lid = e['learner_id']
        if lid in learner_data:
            learner_data[lid]['total_time'] += e.get('duration', 0) or 0
            if e.get('score') is not None:
                learner_data[lid]['scores'].append(e['score'])
    
    features = []
    styles = []
    for lid, data in learner_data.items():
        avg_score = np.mean(data['scores']) if data['scores'] else 0
        features.append([data['total_time'], avg_score])
        styles.append(data['style'])
    
    return np.array(features), styles

def train_kmeans_with_styles(engagements_file='data/engagements.json', learners_file='data/learners.json', n_clusters=3):
    X, styles = aggregate_engagement_data(engagements_file, learners_file)
    gm = GaussianMixture(n_components=n_clusters, random_state=42)
    gm.fit(X)

    # Derive learning_style per cluster (most common style in cluster)
    cluster_styles = {}
    for i in range(n_clusters):
        cluster_indices = np.where(gm.predict(X) == i)[0]
        cluster_s = [styles[j] for j in cluster_indices]
        if cluster_s:
            most_common = max(set(cluster_s), key=cluster_s.count)
            cluster_styles[i] = most_common
        else:
            cluster_styles[i] = 'unknown'

    # Save model and mapping
    os.makedirs('ml', exist_ok=True)
    joblib.dump({'model': gm, 'cluster_styles': cluster_styles}, 'ml/kmeans.pkl')
    return gm, cluster_styles

def predict_kmeans(X_new):
    if not os.path.exists('ml/kmeans.pkl'):
        raise FileNotFoundError("Model file 'ml/kmeans.pkl' not found. Please train the model first.")
    data = joblib.load('ml/kmeans.pkl')
    gm = data['model']
    cluster_styles = data['cluster_styles']
    clusters = gm.predict(X_new)
    styles = [cluster_styles[c] for c in clusters]
    return styles

# Legacy functions for compatibility
def train_kmeans(X, n_clusters=3):
    gm = GaussianMixture(n_components=n_clusters, random_state=42)
    gm.fit(X)
    os.makedirs('ml', exist_ok=True)
    joblib.dump(gm, 'ml/kmeans.pkl')
    return gm

# usage:
# X = df[['avg_time_per_session','video_completion_rate','quiz_accuracy']]
# train_kmeans(X, n_clusters=4)