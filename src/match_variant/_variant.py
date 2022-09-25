import inspect
import types
from contextlib import suppress
from typing import Any, NoReturn, Type


class VariantMeta(type):
    """Placeholder for when we add metaclass features"""

    pass


class Variant(metaclass=VariantMeta):
    def __init_subclass__(cls) -> None:
        """Replace all fields with variants based on the field type annotations"""
        annotations = inspect.get_annotations(cls, eval_str=True)
        for name, annotation in annotations.items():
            nc: Type[cls] = types.new_class(name, bases=(cls,))

            nc.__qualname__ = f"{cls.__qualname__}.{name}"
            nc.__match_args__: tuple[str, ...] = tuple(
                (f"_{index}" for index in range(len(annotation)))
            )
            with suppress(AttributeError):
                nc.__value__ = getattr(cls, name)
            setattr(cls, name, nc)

    def __init__(self, *args: Any) -> None:
        """Construct a Variant, ensuring the correct number of args are supplied"""
        if len(args) != len(self.__match_args__):
            raise TypeError(
                f"{type(self).__qualname__}() takes exactly {len(self.__match_args__)} arguments ({len(args)} given)"
            )

        for index, arg in enumerate(args):
            setattr(self, f"_{index}", arg)

    def __repr__(self):
        """Print a representation of the arguments for the subtype"""
        params = ", ".join(repr(getattr(self, arg)) for arg in self.__match_args__)
        return f"{type(self).__qualname__}({params})"

    def __eq__(self, other):
        """If the instances are the same variant, check they have the same arguments."""

        if type(self) != type(other):
            return NotImplemented

        return all(
            getattr(self, arg) == getattr(other, arg) for arg in self.__match_args__
        )

    def __hash__(self):
        """ADT is expected to be immutable, so it can hash."""

        return hash(tuple(getattr(self, arg) for arg in self.__match_args__))

    @classmethod
    def exhaust(cls, value) -> NoReturn:
        """Instruct type checkers to check variant types exhaustively.

        Note, this relies on Typecheckers special casing Variant as they
        have done with Enum.

        Example:

        match Maybe.just("Value"):
            case Maybe.just(val)
                print(f"Just {val}")
            case Maybe.nothing:
                print("nothing")
            case _ as x:
                exhaust_match(x)
        """
        raise ValueError(f"Unsupported match arm: {value}")
