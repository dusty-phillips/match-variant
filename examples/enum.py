from match_variant import Enum, Maybe


class HttpStatus(Enum):
    ok: () = 200
    not_found: () = 404


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
