from typing import Annotated
from msgspec import Meta, Struct


class InvalidParam(Struct):
    name: Annotated[str, Meta(description="Naam van het veld met ongeldige gegevens")]
    code: Annotated[str, Meta(description="Systeemcode die het type fout aangeeft")]
    reason: Annotated[
        str, Meta(description="Uitleg wat er precies fout is met de gegevens")
    ]


class ZGWError(Struct, rename="camel"):
    code: Annotated[str, Meta(description="Systeemcode die het type fout aangeeft")]
    title: Annotated[str, Meta(description="Generieke titel voor het type fout")]
    status: Annotated[int, Meta(description="De HTTP status code")]
    detail: Annotated[
        str, Meta(description="Extra informatie bij de fout, indien beschikbaar")
    ]
    instance: Annotated[
        str,
        Meta(
            description="URI met referentie naar dit specifiek voorkomen van de fout. Deze kan gebruikt worden in combinatie met server logs, bijvoorbeeld."
        ),
    ]
    invalid_params: list[InvalidParam]
    type: (
        Annotated[
            str,
            Meta(
                description="URI referentie naar het type fout, bedoeld voor developers"
            ),
        ]
        | None
    ) = None


class ZGWResponse[T](Struct):
    count: int
    next: str | None  # URL
    previous: str | None  # URL
    results: list[T]
