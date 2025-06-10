import datetime
from typing import Annotated, Mapping

from ape_pie import APIClient
from msgspec import UNSET, Meta, Struct, UnsetType
from rest_framework.request import Request
from msgspec.json import decode
from msgspec import ValidationError, convert
from openbeheer.api.views import ListView
from openbeheer.types._zgw import ZGWResponse
from openbeheer.types.ztc import Status, ValidatieFout, VertrouwelijkheidaanduidingEnum
from openbeheer.types import OBPagedQueryParams, OBField, OBOption
from drf_spectacular.utils import extend_schema, extend_schema_view
from msgspec.inspect import type_info
from openbeheer.api.views import MsgspecAPIView
from openbeheer.clients import pagination_helper, ztc_client
from openbeheer.types.ztc import (
    PaginatedZaakTypeList,
    ZaakType,
)
from rest_framework.response import Response
from furl import furl
from openbeheer.zaaktype.types import (
    OBDetailField,
    ZaaktypeDetailResponse,
    ZaaktypeVersionSummary,
)


class ZaaktypenGetParametersQuery(OBPagedQueryParams, kw_only=True, rename="camel"):
    catalogus: Annotated[
        str | UnsetType, Meta(description="UUID part of the catalogus URL")
    ] = UNSET  # frontend uuid.UUID, backend url
    datum_geldigheid: datetime.date | UnsetType = UNSET
    identificatie: str | UnsetType = UNSET
    page: int = 1
    status: Status = Status.alles  # OZ defaults to definitief
    trefwoorden: Annotated[
        str | UnsetType, Meta(description="Comma separated keywords")
    ] = UNSET


class ZaakTypeSummary(Struct, kw_only=True, rename="camel"):
    # Identificate
    # Omschrijving
    # Actief ja/nee
    # Einddatum
    # Omschrijving
    # Vertrouwelijkheidaanduiding

    identificatie: str
    omschrijving: str
    # Actief ja/nee: calculated
    actief: bool | UnsetType = UNSET
    einde_geldigheid: datetime.date | None = None
    # str, because VertrouwelijkheidaanduidingEnum does not contain "" but OZ does
    # XXX: the "" is actually a fault in the fixtures!
    vertrouwelijkheidaanduiding: str
    versiedatum: datetime.date

    def __post_init__(self):
        self.actief = (
            self.einde_geldigheid is None
            or datetime.date.today() < self.einde_geldigheid
        )


@extend_schema_view(
    get=extend_schema(
        tags=["Zaaktypen"],
        summary="Get zaaktypen",
        parameters=[],
        filters=True,
        description="Retrive zaaktypen from Open Zaak.",
        responses={
            "200": ZGWResponse[ZaakType],
            "400": ValidatieFout,
        },
    )
)
class ZaakTypeListView(ListView[ZaaktypenGetParametersQuery, ZaakType]):
    data_type = ZaakTypeSummary
    query_type = ZaaktypenGetParametersQuery
    endpoint_path = "zaaktypen"

    def parse_ob_fields(
        self,
        params: ZaaktypenGetParametersQuery,
        option_overrides: Mapping[str, list[OBOption]] = {},
    ) -> list[OBField]:
        return super().parse_ob_fields(
            params,
            {
                "vertrouwelijkheidaanduiding": OBOption.from_enum(
                    VertrouwelijkheidaanduidingEnum
                )
            },
        )

    def parse_query_params(self, request: Request, api_client: APIClient):
        params = super().parse_query_params(request, api_client)
        if params.catalogus:
            params.catalogus = f"{api_client.base_url}catalogussen/{params.catalogus}"
        return params

class ZaakTypeDetailView(MsgspecAPIView):
    endpoint_path = "zaaktypen/{uuid}"

    def get_item_data(
        self,
        uuid: str,
    ) -> tuple[
        ZaakType | ValidatieFout,
        int,
    ]:
        with ztc_client() as client:
            response = client.get(
                self.endpoint_path.format(uuid=uuid),
            )

        if not response.ok:
            # error = decode(response.content, type=ValidatieFout) # TODO: the OZ 404 response gives invalid JSON back
            return ValidatieFout(
                code="",
                title="",
                detail="",
                instance="",
                status=response.status_code,
                invalid_params=[],
            ), response.status_code

        content = response.content
        try:
            return decode(
                content,
                type=ZaakType,
                strict=False,
            ), response.status_code
        except ValidationError as e:
            return ValidatieFout(
                code="Bad response",
                title="Server returned out of spec response",
                detail=str(e),
                instance="",
                status=500,
                invalid_params=[],
            ), 500

    def get_item_versions(
        self, identificatie: str
    ) -> tuple[list[ZaakType] | ValidatieFout, int]:
        # TODO: Question: should we keep the versions "paginated"?
        with ztc_client() as client:
            response = client.get(
                "zaaktypen",
                params={"identificatie": identificatie},
            )

        if not response.ok:
            error = decode(response.content, type=ValidatieFout)
            return error, response.status_code

        results: list[ZaakType] = []
        for page_data in pagination_helper(
            client,
            response.json(),
        ):
            decoded_page_data = convert(
                page_data,
                type=PaginatedZaakTypeList,
            )
            results.extend(decoded_page_data.results)

        return results, response.status_code

    def format_zaaktype(self, data: ZaakType) -> Mapping[str, OBDetailField]:
        item_data = {}
        for defined_field in type_info(ZaakType).fields:
            extra_json_schema = getattr(defined_field.type, "extra_json_schema", {})

            item_data[defined_field.name] = OBDetailField(
                label=defined_field.name.replace(
                    "_", " "
                ).capitalize(),  # TODO other way of getting label?
                value=getattr(data, defined_field.name, defined_field.default),
                description=extra_json_schema.get("description", ""),
                required=defined_field.required,
            )

        return item_data

    def format_version(self, data: ZaakType) -> ZaaktypeVersionSummary:
        assert (
            data.url
        )  # The specs say that it is optional, but in practice it's always present
        zaaktype_url = furl(data.url)
        uuid = zaaktype_url.path.segments[-1]

        return ZaaktypeVersionSummary(
            uuid=uuid,
            begin_geldigheid=data.begin_geldigheid,
            einde_geldigheid=data.einde_geldigheid,
            concept=data.concept,
        )

    def get(self, request: Request, uuid: str, *args, **kwargs) -> Response:
        data, status_code = self.get_item_data(uuid)

        if isinstance(data, ValidatieFout):
            return Response(data, status=status_code)

        versions = []
        if data.identificatie:
            versions, status_code = self.get_item_versions(data.identificatie)

            if isinstance(versions, ValidatieFout):
                versions = []

        response_data = ZaaktypeDetailResponse(
            versions=[
                self.format_version(version) for version in versions
            ],  # TODO: do we want the versions in the response or just a summary?
            item_data=self.format_zaaktype(data),
        )

        match data:
            case ValidatieFout():
                return Response(data, status=status_code)
            case _:
                return Response(
                    response_data,
                    status=status_code,
                )
