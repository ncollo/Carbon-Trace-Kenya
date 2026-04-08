from federated.fl_aggregator import federated_average


def test_federated_average_empty():
    assert federated_average([]) == {}


def test_federated_average_single_model():
    assert federated_average([{"w": 2.5}]) == {"w": 2.5}


def test_federated_average_two_models():
    assert federated_average([{"w": 1.0}, {"w": 3.0}]) == {"w": 2.0}


def test_federated_average_multiple_keys():
    result = federated_average([{"w": 1.0, "b": 2.0}, {"w": 3.0, "b": 4.0}])

    assert result == {"w": 2.0, "b": 3.0}


def test_federated_average_missing_key():
    result = federated_average([{"w": 1.0}, {"b": 3.0}])

    assert result == {"w": 0.5, "b": 1.5}
