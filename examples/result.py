import math
import random

from match_variant import Result, trap

with trap(ZeroDivisionError) as trapped:
    i = random.randint(0, 4)
    trapped.ok(1 / i)

print(trapped.result)

result = trapped.result

match result:
    case Result.ok(value):
        print(f"got {value}")
    case Result.error(_):
        print("Something went wrong")


print(result.to_maybe())

print(result.apply(math.sqrt).unwrap())
