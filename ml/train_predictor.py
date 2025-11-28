#!/usr/bin/env python3
"""
Training script for the course completion time predictor.
This script trains the Linear Regression model on engagement data and saves it to ml/completion_predictor.pkl.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.linear_reg import train_completion_predictor

def main():
    print("Training course completion time predictor...")
    try:
        model, mae = train_completion_predictor()
        print(f"Model trained successfully. MAE: {mae:.2f}")
        print("Model saved to ml/completion_predictor.pkl")
    except Exception as e:
        print(f"Error training model: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()