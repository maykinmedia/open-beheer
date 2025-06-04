from msgspec import Struct


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
    next: str | None  # URL
    previous: str | None  # URL
    results: list[T]
