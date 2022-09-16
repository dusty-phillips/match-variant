from __future__ import annotations
from contextlib import contextmanager
from typing import Generic, TypeVar, Union, final

from .variant import Variant
from .maybe import Maybe


T = TypeVar("T")
E = TypeVar("E", bound=BaseException)
U = TypeVar("U")


@final
class Result(Generic[T, E], Variant):
    """Model a potential Result.

    Provides an alternative to exception-based python. Used with
    the trap context manager, converts exceptions to Result objects
    that can be captured and evaluated using match.
    """

    ok: (T,)
    error: (E,)

    def apply(self, func: Callable[[T], U]) -> Result[U, E]:
        """Apply a function to the contained value.

        If this is a `Result.ok` variant, return a `Result.ok` with the given function
        applied to the value inside the `Result.ok`. Otherwise, return `Result.error`
        unchanged.

        Example:

        >>> from basicenum.result import Result
        >>> Result.ok("hello").apply(str.upper)
        <Result.ok: 'HELLO'>
        >>>
        >>> Result.error(ValueError("oops")).apply(str.upper)
        <Result.error: ValueError('oops')>
        >>>
        """
        match self:
            case Result.ok(val):
                return Result.ok(func(val))
            case Result.error(_):
                return self

    def unwrap(self) -> T:
        """
        Access the value inside the Result.ok.just.

        If this is a Result.ok value, return the contents of the unwrapped object

        If it is Result.error, raise the error.

        Example:

        >>> from basicenum.result import Result
        >>> Result.ok("hello").unwrap()
        'hello'
        >>> Result.error(ValueError("oops")).unwrap()
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
          File "__main__", line 71, in unwrap
            raise ex
        ValueError: oops
        """
        match self:
            case Result.ok(val):
                return val
            case Result.error(ex):
                raise ex

    def to_maybe(self) -> Maybe[T]:
        """Convert the result to an option, discarding the error if any"""
        match self:
            case Result.ok(value):
                return Maybe.just(value)
            case Result.error(_):
                return Maybe.nothing()


class Trapped(Generic[T, E]):
    """Capture a trapped exception or value result.

    See `trap`.
    """

    value: Union[Result[T, E], None] = None

    def ok(self, value: T):
        """Set the trapped result to an ok value."""
        self.value = Result.ok(value)

    def error(self, value: E):
        """Set the trapped result to an error value.

        Typically called automaticaly by the `trap` contextmanager.
        """
        self.value = Result.error(value)

    @property
    def result(self) -> Result[T, E]:
        """Return the result that was set inside the with statement.

        If an exception was trapped, the Result will be an error.

        If no ok was set inside the with statement, raises TypeError.
        """
        if self.value is None:
            return Result.error(TypeError("Trapped.ok was never called"))

        return self.value


@contextmanager
def trap(*exceptions):
    """
    Run a section of code and convert it to a Result type.

    Yields a Trapped object. Typical usage as follows:

    d = {"key": "value"}
    with trap(KeyError) as trapped:
        trapped.ok(d["key"])

    match trapped.result:
        case Result.ok(val):
            print(f"Got a value: {val}")
        case Result.error(val):
            print(f"Got an error: {val}")
        case _ as x:
            Result.exhaust(x)
    """
    if not (exceptions):
        exceptions = (Exception,)

    trapped = Trapped()
    try:
        yield trapped
    except exceptions as ex:
        trapped.error(ex)
