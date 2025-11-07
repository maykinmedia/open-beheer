import re
from typing import Annotated, assert_never
from uuid import UUID

from django.utils.translation import gettext as __

from drf_spectacular.utils import extend_schema, extend_schema_view
from msgspec import (
    UNSET,
    Meta,
    Struct,
    ValidationError,
    convert,
    to_builtins,
)
from rest_framework.request import Request
from rest_framework.response import Response

from openbeheer.api.views import (
    DetailView,
    DetailViewWithoutVersions,
    ListView,
    reverse,
)
from openbeheer.types import (
    EigenschapWithUUID,
    ExternalServiceError,
    ZGWError,
)
from openbeheer.types._open_beheer import make_fields_optional
from openbeheer.types._zgw import InvalidParam
from openbeheer.types.ztc import (
    Eigenschap,
    EigenschapRequest,
    EigenschapSpecificatieRequest,
    FormaatEnum,
    PatchedEigenschapRequest,
)
from openbeheer.utils.decorators import handle_service_errors

from ..types import (
    EigenschappenGetParametersQuery,
)


def field_name_of_error(error: ValidationError):
    return match.group(1) if (match := re.search(r"`\$.(.*)`$", str(error))) else ""


class OBEigenschap(Struct):
    "An intermediate Eigenschap used by Open Beheer"

    naam: Annotated[str, Meta(description="De naam van de EIGENSCHAP", max_length=20)]
    definitie: Annotated[
        str,
        Meta(
            description="De beschrijving van de betekenis van deze EIGENSCHAP",
            max_length=255,
        ),
    ]
    formaat: Annotated[
        FormaatEnum,
        Meta(
            description="Het soort tekens waarmee waarden van de EIGENSCHAP kunnen worden vastgelegd.\n\nUitleg bij mogelijke waarden:\n\n* `tekst` - Tekst\n* `getal` - Getal\n* `datum` - Datum\n* `datum_tijd` - Datum/tijd"
        ),
    ]

    def as_spec(self) -> EigenschapSpecificatieRequest:
        match self.formaat:
            case FormaatEnum.tekst:
                lengte = "255"
            case FormaatEnum.getal:
                lengte = "255"  # XXX what??
            case FormaatEnum.datum:
                lengte = "8"  # YYYYMMDD?
            case FormaatEnum.datum_tijd:
                lengte = "14"  # YYYYMMDD HH:mm?
            case _:
                assert_never(self.formaat)

        return EigenschapSpecificatieRequest(
            formaat=self.formaat,
            lengte=lengte,
            kardinaliteit="1",
            groep=UNSET,  # type: ignore
            waardenverzameling=UNSET,  # type: ignore
        )


def fix_input(
    request: Request,
    zaaktype_url: str,
    t: type[EigenschapRequest | PatchedEigenschapRequest] = EigenschapRequest,
) -> Response | None:
    "Update request.data return a Response on error"
    try:
        input = convert(
            dict(request.data.items()),
            OBEigenschap
            if t is not PatchedEigenschapRequest
            else make_fields_optional(OBEigenschap),
        )
    except ValidationError as e:
        return Response(
            data=ZGWError(
                code="invalid",
                status=400,
                title=__("Invalid input."),
                detail="",
                invalid_params=[
                    InvalidParam(
                        field_name_of_error(e),
                        "invalid",
                        reason=str(e).split(" - at ")[0],
                    )
                ],
                instance="",  # TODO: log and add id
            ),
            status=400,
        )

    match input, t:
        case OBEigenschap(), _ if t is EigenschapRequest:
            eigenschap = t(
                naam=input.naam,
                definitie=input.definitie,
                specificatie=input.as_spec(),
                zaaktype=zaaktype_url,
            )
        case _ if t is PatchedEigenschapRequest:
            args = {
                name: value
                for name in dir(input)
                if not name.startswith("_")
                and (value := getattr(input, name, UNSET))
                and value is not UNSET
                and not callable(value)
            }
            eigenschap = t(**args)
        case _:
            assert_never(t)  # pyright: ignore[reportArgumentType]

    request.data.clear()
    data = to_builtins(eigenschap)
    request.data.update(data)


@extend_schema_view(
    get=extend_schema(
        tags=["eigenschappen"],
        summary="Get eigenschappen",
        parameters=[],
        filters=True,
        description="Retrieve eigenschappen from Open Zaak.",
    ),
    post=extend_schema(
        tags=["eigenschappen"],
        summary="Create an eigenschappen",
        description="Create an eigenschappen.",
        request=EigenschapRequest,
        responses={
            "201": Eigenschap,
            "502": ExternalServiceError,
            "504": ExternalServiceError,
        },
    ),
)
class EigenschappenListView(
    ListView[
        EigenschappenGetParametersQuery,
        Eigenschap,
        EigenschapRequest,
    ]
):
    """
    Endpoint for eigenschappen attached to a particular Zaaktype
    """

    data_type = EigenschapRequest
    return_data_type = EigenschapWithUUID
    query_type = EigenschappenGetParametersQuery
    endpoint_path = "eigenschappen"

    @handle_service_errors
    def post(self, request: Request, slug: str = "", **path_params) -> Response:
        # super().post just sends the request.data as-is
        # this patches up some malformed things we receive

        zaaktype_url = reverse(slug)("zaaktype", path_params.get("zaaktype"))
        assert zaaktype_url
        if error := fix_input(request, zaaktype_url, t=EigenschapRequest):
            return error

        return super().post(request, slug, **path_params)


@extend_schema_view(
    get=extend_schema(
        operation_id="service_eigenschappen_retrieve_one",
        tags=["eigenschappen"],
        summary="Get an eigenschappe",
        description="Retrieve an eigenschap from Open Zaak.",
    ),
    patch=extend_schema(
        tags=["eigenschappen"],
        summary="Patch an eigenschappe",
        description="Partially update a eigenschap from Open Zaak.",
        request=PatchedEigenschapRequest,
    ),
    put=extend_schema(
        tags=["eigenschappen"],
        summary="Put an eigenschappe",
        description="Fully update a eigenschap from Open Zaak.",
        request=EigenschapRequest,
    ),
    delete=extend_schema(
        tags=["eigenschappen"],
        summary="Delete an eigenschappe",
        description="Remove permanently a eigenschap from Open Zaak.",
    ),
)
class EigenschappenDetailView(DetailViewWithoutVersions, DetailView[Eigenschap]):
    """
    Endpoint for eigenschappen attached to a particular Zaaktype
    """

    return_data_type = data_type = EigenschapWithUUID
    endpoint_path = "eigenschappen/{uuid}"
    expansions = {}

    def update(
        self, request: Request, slug: str, uuid: UUID, is_partial: bool = True
    ) -> Response:
        t = PatchedEigenschapRequest if is_partial else EigenschapRequest

        zaaktype_url = request.data.get("zaaktype")
        assert zaaktype_url
        if error := fix_input(request, zaaktype_url, t):
            return error

        return super().update(request, slug, uuid, is_partial)
