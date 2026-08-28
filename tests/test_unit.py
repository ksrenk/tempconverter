from converter import celsius_to_fahrenheit


def test_zero_celsius():
    assert celsius_to_fahrenheit(0) == 32


def test_room_temperature():
    assert celsius_to_fahrenheit(25) == 77


def test_boiling_point():
    assert celsius_to_fahrenheit(100) == 212


def test_negative_temperature():
    assert celsius_to_fahrenheit(-40) == -40


def test_decimal_temperature():
    assert celsius_to_fahrenheit(36.6) == 97.88
