import numpy as np

from reconciliation.isolation_forest import score_records, train_isolation_forest


def test_train_and_score_clean_data():
    rng = np.random.default_rng(42)
    X = rng.normal(0, 0.1, size=(50, 2))

    model = train_isolation_forest(X)
    scores = score_records(model, X)

    assert len(scores) == 50
    assert (scores > -0.5).all()


def test_train_and_score_with_outlier():
    rng = np.random.default_rng(123)
    normal = rng.normal(0, 0.1, size=(50, 2))
    X = np.vstack([normal, [[10, 10]]])

    model = train_isolation_forest(X)
    scores = score_records(model, X)

    assert scores[-1] < scores[:-1].mean()


def test_score_shape():
    rng = np.random.default_rng(7)
    X = rng.normal(0, 0.2, size=(12, 3))

    model = train_isolation_forest(X)
    scores = score_records(model, X)

    assert scores.shape == (12,)
