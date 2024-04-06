# type: ignore
from __future__ import annotations

from typing import Callable, Generic, TypeVar, final

from ._variant import Variant

T = TypeVar("T")
U = TypeVar("U")
_RAISE = object()


@final
class Maybe(Generic[T], Variant):
    """Represent an optional value.

    This is a Variant type that can be either `just(something)` or `nothing`.

    When used with a typechecker, can eliminate bugs caused by missed `is None`
    checks.
    """

    just: (T,)
    nothing: ()

    def apply(self, func: Callable[[T], U]) -> Maybe[U]:
        """Apply a function to the contained value.

        If this is a `Maybe.just` variant, return a `Maybe.just` with the given function
        applied to the value inside the `Maybe.just`. Otherwise, return `Maybe.nothing`
        unchanged.

        Example:

        >>> from basicenum.maybe import Maybe
        >>> Maybe.just("hello").apply(str.upper)
        <Maybe.just: 'HELLO'>
        >>>
        >>> Maybe.nothing().apply(str.upper)
        <Maybe.nothing>
        >>>
        """
        match self:
            case Maybe.just(val):
                return Maybe.just(func(val))
            case Maybe.nothing():
                return self

    def filter(self, func: Callable[[T], bool]) -> Maybe[T]:
        """Filter the contained value.

        If this is a `Maybe.just` variant and the given function returns `True`, return a `Maybe.just` with the unmodified value.
        Otherwise, return `Maybe.nothing`.

        Example:

        >>> from basicenum.maybe import Maybe
        >>> Maybe.just("hello").filter(lambda x: len(x) > 3)
        <Maybe.just: 'hello'>
        >>>
        >>> Maybe.just("abc").filter(lambda x: len(x) > 3)
        <Maybe.nothing>
        >>>
        >>> Maybe.nothing().filter(lambda x: len(x) > 3)
        <Maybe.nothing>
        """
        match self:
            case Maybe.just(val):
                if func(val):
                    return self
                return Maybe.nothing()
            case Maybe.nothing():
                return self

    def unwrap(self, *, default: T = _RAISE) -> T:
        """
        Access the value inside the Maybe.just.

        If this is a Maybe.just value, return the contents of the unwrapped object

        If it is Maybe.nothing and `default` is not provided, this will raise a `TypeError`.
        If it is Maybe.nothing and `default` is provided, it will return the provided default value

        Example:

        >>> from basicenum.maybe import Maybe
        >>> Maybe.just("hello").unwrap()
        'hello'
        >>> Maybe.nothing().unwrap(default="default")
        'default'
        >>> Maybe.nothing().unwrap()
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
          File "/Users/dustyphillips/Desktop/Code/basicenum/src/basicenum/maybe.py", line 62, in unwrap
            raise TypeError(
        TypeError: Attempted to unwrap Maybe.nothing(); can only unwrap Maybe.just(val)
        >>>
        """
        match self:
            case Maybe.just(val):
                return val
            case Maybe.nothing():
                if default is _RAISE:
                    raise TypeError(
                        "Attempted to unwrap Maybe.nothing(); can only unwrap Maybe.just(val)"
                    )
                return default

    def __iter__(self) -> None:
        """Iterate over the Maybe.

        If this is a Maybe.just value, yield the value

        If it is Maybe.nothing, do nothing.

        Example:

        >>> from basicenum.maybe import Maybe
        >>> for val in Maybe.just("hello"): print(val)
        hello
        >>> for val in Maybe.nothing(): print(val)
        >>>
        """
        match self:
            case Maybe.just(val):
                yield val
            case Maybe.nothing():
                pass

