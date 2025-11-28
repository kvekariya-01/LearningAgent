#!/usr/bin/env python3
"""
Training script for the learner profiling classifier.
This script trains the K-Means model on engagement data and saves it to ml/kmeans.pkl.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.kmeans import train_kmeans_with_styles

def main():
    print("Training learner profiling classifier...")
    try:
        km, cluster_styles = train_kmeans_with_styles()
        print(f"Model trained successfully with {len(cluster_styles)} clusters.")
        print("Cluster styles:", cluster_styles)
        print("Model saved to ml/kmeans.pkl")
    except Exception as e:
        print(f"Error training model: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()