"""JSON values as they are read from settings and written to standard output."""

import json
from typing import cast

type Json = None | bool | int | float | str | list[Json] | dict[str, Json]
type Object = dict[str, Json]


def loads(text: str) -> Json:
    def refuse(value: str) -> None:
        raise ValueError("Nonfinite JSON number")

    return cast(Json, json.loads(text, parse_constant=refuse))


def dumps(value: Json) -> str:
    return json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(",", ":"))
