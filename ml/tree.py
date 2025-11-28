# app/ml/tree.py
import joblib
from sklearn.ensemble import RandomForestClassifier
def train_tree(X, y):
    clf = RandomForestClassifier(random_state=42)
    clf.fit(X, y)
    joblib.dump(clf, 'models/perf_forest.joblib')
    return clf

# y could be labels: 'low','medium','high' mapped to ints
