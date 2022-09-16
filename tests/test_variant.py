import pytest

from match_variant import Variant


class TestVariant(Variant):
    option0: ()
    option1: (str,)
    option2: (str, int)
    option_list: (list[str],)


def test_too_many_args():
    with pytest.raises(TypeError) as ex:
        b = TestVariant.option1("Too", "many", "args")

    ex_str = str(ex.value)
    assert "1" in ex_str
    assert "3" in ex_str


def test_adt():
    assert TestVariant.option1.__qualname__ == "TestVariant.option1"


def test_match_args():
    assert TestVariant.option0().__match_args__ == ()
    assert TestVariant.option1("one").__match_args__ == ("_0",)
    assert TestVariant.option2("one", 2).__match_args__ == ("_0", "_1")


def test_match_no_args():
    match TestVariant.option0():
        case TestVariant.option0():
            pass
        case _:
            pytest.fail("Should be option0")


def test_match_one_arg():
    match TestVariant.option1("boo"):
        case TestVariant.option1(val):
            assert val == "boo"
        case _:
            pytest.fail("Should be option1")


def test_match_two_args():
    match TestVariant.option2("boo", 2):
        case TestVariant.option2(val, val2):
            assert val == "boo"
            assert val2 == 2
        case _:
            pytest.fail("Should be option2")


def test_repr():
    o = TestVariant.option0()
    assert repr(o) == "TestVariant.option0()"
    o = TestVariant.option1("one")
    assert repr(o) == "TestVariant.option1('one')"
    o = TestVariant.option2("one", 2)
    assert repr(o) == "TestVariant.option2('one', 2)"


@pytest.mark.parametrize(
    ["self", "other", "expected"],
    [
        pytest.param(
            TestVariant.option_list([]),
            TestVariant.option_list([]),
            True,
            id="equal options",
        ),
        pytest.param(
            TestVariant.option0(), TestVariant.option0(), True, id="equal option0"
        ),
        pytest.param(
            TestVariant.option_list([]),
            TestVariant.option_list(["something"]),
            False,
            id="equal variant, unequal value",
        ),
        pytest.param(
            TestVariant.option_list([]),
            TestVariant.option0(),
            False,
            id="left option_list right option0",
        ),
        pytest.param(
            TestVariant.option0(),
            TestVariant.option_list([]),
            False,
            id="right option_list left option0",
        ),
        pytest.param(
            TestVariant.option_list([]), "a string", False, id="different type"
        ),
    ],
)
def test_is_eq(self, other, expected):
    assert (self == other) is expected


def test_hash_identical_val_hashable():
    val = "something"
    assert hash(TestVariant.option1(val)) == hash(TestVariant.option1(val))


def test_hash_different_equal_object_values():
    assert hash(TestVariant.option1(("one",))) == hash(TestVariant.option1(("one",)))


def test_hashed_same_variant_different_value():
    assert hash(TestVariant.option1("one")) != hash(TestVariant.option1("two"))


def test_hash_no_args_is_hashable():
    assert hash(TestVariant.option0()) == hash(TestVariant.option0())


def test_hash_multi_args_is_hashable():
    assert hash(TestVariant.option2("one", 2)) == hash(TestVariant.option2("one", 2))


def test_hash_unhashable_value_fails():
    with pytest.raises(TypeError) as ex:
        hash(TestVariant.option1([]))

    assert "unhashable" in str(ex.value)


def test_can_add_hashable_to_set():
    assert {TestVariant.option1("one"), TestVariant.option1("one")} == {
        TestVariant.option1("one")
    }
    assert {TestVariant.option0(), TestVariant.option0()} == {TestVariant.option0()}


@pytest.mark.parametrize(
    ["self", "cls", "expected"],
    [
        pytest.param(
            TestVariant.option0(), TestVariant.option0, True, id="noargs is class"
        ),
        pytest.param(
            TestVariant.option1("blah"),
            TestVariant.option1,
            True,
            id="withargs is class",
        ),
        pytest.param(
            TestVariant.option0(),
            TestVariant.option1,
            False,
            id="noargs is not with args",
        ),
        pytest.param(TestVariant.option0(), TestVariant, True, id="noargs is class"),
    ],
)
def test_instance_check(self, cls, expected):
    assert isinstance(self, cls) == expected


def test_exhaust():
    with pytest.raises(ValueError) as ex:
        match TestVariant.option1("Value"):
            case TestVariant.option0:
                pytest.fail("Should not match nothing on a value")
            case _ as x:
                TestVariant.exhaust(x)

    ex_str = str(ex.value)
    assert "TestVariant.option1" in ex_str
    assert "Value" in ex_str
