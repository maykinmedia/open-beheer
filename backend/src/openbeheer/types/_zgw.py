from msgspec import Struct

from . import URL


class InvalidParam(Struct):
    name: str
    code: str
    reason: str


class ZGWError(Struct, rename="camel"):
    type: str
    code: str
    title: str
    status: int
    detail: str
    instance: str
    invalid_params: None | list[InvalidParam]


class ZGWResponse[T](Struct):
    count: int
    next: URL | None
    previous: URL | None
    results: list[T]
