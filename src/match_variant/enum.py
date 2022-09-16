import inspect
from typing import Any
from functools import lru_cache

from .variant import Variant
from .maybe import Maybe


class Enum(Variant):
    """Variants can model simple enums.

    The Variant class stores any default value assigned to a
    field in the special __value__ field. This class has an
    lru_cached `from_value` class function to look up the field
    given a value.

    Example:

    class HttpStatus(Enum):
        ok: () = 200
        not_found: () = 404

    match HttpStatus.from_value(200):
        case HttpStatus.ok():
            print("got a success response")
        case HttpStatus.not_found():
            print("it's not anywhere")
        case _:
            print("Unexpected status")
    """

    @classmethod
    @lru_cache
    def from_value(cls, value: Any) -> Maybe:
        """
        Given a value, return the variant associated with
        that field.

        Returns a Maybe that is set to Maybe.nothing if the
        field is not set.
        """
        last_class = None
        for parent_class in cls.__mro__:
            if parent_class == Enum:
                break
            last_class = parent_class

        for field_name in inspect.get_annotations(last_class):
            field = getattr(last_class, field_name)
            if hasattr(field, "__value__") and field.__value__ == value:
                return Maybe.just(field())

        return Maybe.nothing()
