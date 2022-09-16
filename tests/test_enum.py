from match_variant.enum import Enum
from match_variant.maybe import Maybe


class MyEnum(Enum):
    a: () = 1
    b: () = 2
    c: (int,)


def test_from_value_exists():
    assert MyEnum.from_value(1).unwrap() == MyEnum.a()


def test_from_value_no_exist():
    assert isinstance(MyEnum.from_value(99), Maybe.nothing)
