import pytest

from match_variant import Result, Trapped, trap


def test_apply_error():
    result = Result.error(ValueError("nope"))

    def no_call_me():
        pytest.fail("I should not be called")

    assert result.apply(no_call_me) is result


def test_apply_ok():
    val = "I am a value"
    result = Result.ok(val)
    assert result.apply(str.upper).unwrap() == val.upper()


def test_unwrap_ok():
    val = "I am a value"
    result = Result.ok(val)
    assert result.unwrap() is val


def test_unwrap_error_raises():
    my_exception = ValueError("Oops")
    with pytest.raises(ValueError) as ex:
        Result.error(my_exception).unwrap()
    assert ex.value is my_exception


def test_trapped_ok():
    val = "some value"
    t = Trapped()
    t.ok(val)
    assert t.result == Result.ok(val)
    assert t.result.unwrap() is val


def test_trapped_error():
    val = ValueError("some value")
    t = Trapped()
    t.error(val)
    assert t.result == Result.error(val)
    with pytest.raises(ValueError) as ex:
        t.result.unwrap()
    assert ex.value is val


def test_trap_ok():
    value = "Hello"
    with trap(ValueError) as result:
        result.ok(value)

    assert result.result == Result.ok(value)
    assert result.result.unwrap() is value


def test_trap_exception():
    value = ValueError("Nope")
    with trap(ValueError) as result:
        raise value

    assert result.result == Result.error(value)


def test_trap_exception_multiple():
    value = ValueError("Nope")
    with trap(ValueError, KeyError) as result:
        raise value

    assert result.result == Result.error(value)


def test_trap_no_ok_call():
    with trap(ValueError) as result:
        pass

    with pytest.raises(TypeError) as ex:
        result.result.unwrap()

    assert "never" in str(ex.value)
