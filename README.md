# match-variant

Variant algebraic datatypes that work with the Python 3.10 match statement.

Python's match statement for pattern matching is a delightful innovation,
but it doesn't have the power of similar statements in functional progamming
languages due to Python's lack of a Variant datatype. This package brings
Variant types to the Python language.

If you are unfamiliar variant types, they are all about representing "this or that"
structures that can be statically analyzed. Common examples include optional
types ("just a value or no value"), result types ("successful value or error
value"), or authentication roles ("anonymous user or normal user or superuser").

It may be helpful to think of variants as an Enum where each value can hold
structured data and each type can have a different structure. 

## Quick example

Consider a simplification of the `Maybe` type that ships with this package:

```python
@final
class Maybe(Generic[T], Variant):
    just: (T,)
    nothing: ()
```

We'll talk more about the specifics of `Maybe` later; for now know that this
class represents an optional value that can be fully typechecked (once
typecheckers catch up). Any one instance of this either has a value, identified
by `just` or no value identified by `maybe` and can be easily tested with the
`match` statement:

```python
match get_a_maybe_from_somewhere():
    case Maybe.just(value):
        print(f"I got a legitimate {value}")
    case Maybe.nothing():
        print("Sorry, I didn't get anything")
```

## Variant

The meat of this package is the `Variant` class. Subclass it to create your own
custom variants. Each field on the class must have a type annotation that is a tuple
of the types that variant expects:

```python
from match_variant import Variant

class Role(Variant):
    anonymous: ()
    unauthenticated: (str, str)
    normal: (str,)
    admin: (str, dict[str, bool],)
```

Any one user can be in exactly one of these four roles. With Python's robust
structured pattern matching, your code can match on it to determine which
role is currently in use, capturing or guarding patterns to adjust the behaviour:

```python
class Role(Variant):
    anonymous: ()
    unauthenticated: (str, str)
    normal: (str,)
    admin: (str, dict[str, bool],)
```

### Case exhaustion

Type checkers do not know about this code yet, but we are assuming
they will special case `Variant`s the same way they do with `enum`
in the standard library. Once this is implemented, you will be able to get typechecker errors when you miss a match arm using the `exhaust` method supplied with all `Variant`s:


```python
# This "should" fail type checking because not all roles were tested
match user:
    case Role.anonymous():
        print("we only handled anonymous")
    case _:
        Role.exhaust(user)
```
As well as failing static analysis, the `exhaust` method will
throw an exception at runtime if it is hit.

## `Variant` instances we ship

We ship a few common variant classes partially as a demo of this
functionality and partially as a convenience for very common
cases.

### The `Maybe` Type

Null, or None in Python has been described as the billion dollar
mistake and current sentiment seems to be that it should be
avoided in favour of optional types. Well, here's your optional
type!

The maybe class has two variants: `just` and `nothing`, which
represent either a generic value or no value. It also contains a
couple helper functions (we are open to adding others; submit a PR
or issue) to transform or extract the value.

#### Constructing `Maybe`

Just use one of the two class constructors defined as fields
on the `Maybe` class:

```python
import random
from match_variant.maybe import Maybe

def get_a_maybe():
    match random.randint(0, 1):
        case 0:
            return Maybe.nothing()
        case 1:
            return Maybe.just("some value")
```

#### Matching on `Maybe`

Works as expected:

```python
match get_a_maybe():
    case Maybe.nothing():
        print("I don't feel like guessing")
    case Maybe.just(value):
        print(f"I guess {value}")
```

**Gotcha alert:** You need to supply empty parens when
instantiating or matching a Variant that has no value.

#### Unwrapping a `Maybe`

For convenience, you can extract the value inside a `Maybe.just`
without a `match` statement. A `TypeError` will be raised if it
receives a `Maybe.nothing` instance:

```python
>>> get_a_maybe().unwrap()
2
>>> get_a_maybe().unwrap()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "maybe.py", line 77, in unwrap
    raise TypeError(
TypeError: Attempted to unwrap Maybe.nothing(); can only unwrap Maybe.just(val)
```

If you don't want an exception, you can supply a default value as a *keyword* argument:

```python
get_a_maybe().unwrap(default="BOO!")
```

#### Applying a function to a Maybe

The `Maybe.apply` function can be used to perform an operation on
the value inside a `Maybe` *if the value is a `Maybe.just`*. If
the value is nothing, then no work is performed. This can lead to
some interesting function chaining applications.

`Maybe.apply` accepts a single argument: a function or callable. The callable accepts the argument inside the `Maybe.just` and is only called if the `Maybe` is an instance of the `Maybe.just` variant:

```python
match maybe_value \
        .apply(lambda d: d ** 2) \
        .apply(partial(int.__add__, 2)):
    case Maybe.just(value):
        print(f"Squared plus two: {value}")
    case Maybe.nothing():
        print("got nothing to math on")
```

### The `Result` Type

The `Result` type is similar to option, but allows an exception to
be attached to the error type. A context manager is supplied to
automatically convert exceptions to results.

The benefit (and drawback) of `Result` is that it forces calling
code to either handle or return the `Result`, whereas there is no
type-safe way to specify that a function will or will not throw
a specific exception.

Typical usage is with the `trap` context manager:

```python
import random
from match_variant import trap, Result


with trap(ZeroDivisionError) as trapped:
    i = random.randint(0, 4)
    trapped.ok(1 / i)

print(trapped.result)
```

`Result`s can be matched on:

```python
match result:
    case Result.ok(value):
        print(f"got {value}")
    case Result.error(_):
        print("Something went wrong")
```

`Result` has `apply` and `unwrap` methods similar to `Maybe`:


```python
print(result.apply(math.sqrt).unwrap())
```

Unlike `Maybe`, `Result.unwrap` does not accept a default argument. If you try
to unwrap a `Result.error`, the original exception is raised.

Convert a `Result` to a `Maybe` using `Result.to_maybe`:

```python
print(result.to_maybe())
```

### The `Enum` Type

You can supply variant fields with a default value, which will be
made available on the `__value__` field for the variant to use ase
you like. One option is to use it as a better-performing
replacement for the `enum` module. As a convenience, we supply the
`Enum` class to work more easily with these types.

Consider an example `HttpStatus` class:

```python
class HttpStatus(Enum):
    ok: () = 200
    not_found: () = 404
```

Enum provides a `from_value` class method to convert values to
instances. Because not all possible values can return an instance,
this function returns a `Maybe`. This works beautifully with the `match` statement's structured typing:

```python
for value in (200, 404, 600):
    match HttpStatus.from_value(value):
        case Maybe.just(HttpStatus.ok()):
            print(f"Request was successful")
        case Maybe.just(HttpStatus.not_found()):
            print("Request was not found")
        case Maybe.just(_):
            print(f"Unexpected status code: {value}")
        case Maybe.nothing():
            print(f"No idea what we got here")
```

# Contributing

PRs are more than welcome.
