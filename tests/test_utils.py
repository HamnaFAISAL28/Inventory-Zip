import pytest

from inventory import utils


def test_format_currency():
    assert utils.format_currency(1234.5) == "$1,234.50"
    assert utils.format_currency(2, symbol="Rs ") == "Rs 2.00"


def test_slugify():
    assert utils.slugify("  Hello, World! ") == "hello-world"


def test_chunk():
    assert list(utils.chunk([1, 2, 3, 4, 5], 2)) == [[1, 2], [3, 4], [5]]
    with pytest.raises(ValueError):
        list(utils.chunk([1], 0))


def test_clamp():
    assert utils.clamp(5, 0, 3) == 3
    assert utils.clamp(-1, 0, 3) == 0
    assert utils.clamp(2, 0, 3) == 2
    with pytest.raises(ValueError):
        utils.clamp(1, 5, 1)


@pytest.mark.parametrize("raw,expected", [("yes", True), ("0", False), (" ON ", True), ("no", False)])
def test_parse_bool(raw, expected):
    assert utils.parse_bool(raw) is expected


def test_parse_bool_invalid():
    with pytest.raises(ValueError):
        utils.parse_bool("maybe")


def test_truncate():
    assert utils.truncate("short", 10) == "short"
    assert utils.truncate("a very long sentence", 10) == "a very ..."
