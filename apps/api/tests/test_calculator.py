from app.agents.tools.calculator import calculate


def test_addition_and_multiplication():
    assert calculate("25 * 4 + 10") == 110.0


def test_parentheses():
    assert calculate("(10 + 5) * 2") == 30.0


def test_power():
    assert calculate("2 ** 8") == 256.0