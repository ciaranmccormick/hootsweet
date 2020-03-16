import pytest
from hootsweet.locale import ACCEPTED_LANGUAGES, is_valid_language, is_valid_timezone


@pytest.mark.parametrize(
    "test_input,expected", [("Europe/London", True), ("Europa/Mars", False)]
)
def test_is_valid_time_zone(test_input, expected):
    assert expected == is_valid_timezone(test_input)


@pytest.mark.parametrize("test_input", ACCEPTED_LANGUAGES)
def test_is_valid_language_valid(test_input):
    assert is_valid_language(test_input)


@pytest.mark.parametrize("test_input", ["ba", "aa", "rr"])
def test_is_valid_language_not_valid(test_input):
    assert not is_valid_language(test_input)
