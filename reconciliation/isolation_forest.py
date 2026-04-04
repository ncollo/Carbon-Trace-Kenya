from sklearn.ensemble import IsolationForest
import numpy as np


def train_isolation_forest(X):
    model = IsolationForest(random_state=42)
    model.fit(X)
    return model


def score_records(model, X):
    scores = model.decision_function(X)
    return scores
