import pytest
from match_variant import Maybe


def test_apply_nothing():
    maybe = Maybe.nothing()

    def no_call_me():
        pytest.fail("I should not be called")

    assert maybe.apply(no_call_me) is maybe


def test_apply_just():
    val = "I am a value"
    maybe = Maybe.just(val)
    assert maybe.apply(str.upper).unwrap() == val.upper()


def test_just_unwrap():
    val = "I am a value"
    j = Maybe.just(val)
    assert j.unwrap() is val


def test_nothing_unwrap_raises():
    with pytest.raises(TypeError) as ex:
        Maybe.nothing().unwrap()

    assert "nothing" in str(ex.value)


def test_nothing_unwrap_default():
    expected = "YAY"
    assert Maybe.nothing().unwrap(default=expected) is expected
