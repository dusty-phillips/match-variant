from match_variant import Enum, Maybe


class MyEnum(Enum):
    a: () = 1  # type: ignore
    b: () = 2  # type: ignore
    c: (int,)  # type: ignore


def test_from_value_exists():
    assert MyEnum.from_value(1).unwrap() == MyEnum.a()


def test_from_value_no_exist():
    assert isinstance(MyEnum.from_value(99), Maybe.nothing)
