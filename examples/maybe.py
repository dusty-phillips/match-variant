import random
from functools import partial

from match_variant._maybe import Maybe


def get_a_maybe():
    match random.randint(0, 1):
        case 0:
            return Maybe.nothing()
        case 1:
            return Maybe.just(random.randint(0, 100))


maybe_value = get_a_maybe()

match maybe_value:
    case Maybe.nothing():
        print("I don't feel like guessing")
    case Maybe.just(value):
        print(f"I guess {value}")


try:
    print(maybe_value.unwrap())
except TypeError:
    print("Oops")

print(maybe_value.unwrap(default="BOO!"))

match maybe_value.apply(lambda d: d**2).apply(partial(int.__add__, 2)):
    case Maybe.just(value):
        print(f"Squared plus two: {value}")
    case Maybe.nothing():
        print("got nothing to math on")
