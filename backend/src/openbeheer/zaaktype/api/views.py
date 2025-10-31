from __future__ import annotations

import datetime  # noqa: TC003
from functools import partial
from typing import (
    TYPE_CHECKING,
    Annotated,
    Callable,
    Iterable,
    Mapping,
    override,
)

from django.utils.translation import gettext as _

import structlog
from ape_pie import APIClient
from drf_spectacular.utils import extend_schema, extend_schema_view
from furl import furl
from msgspec import UNSET, Meta, UnsetType
from msgspec.json import decode
from msgspec.structs import asdict, replace
from rest_framework import status
from rest_framework.response import Response

from openbeheer.api.views import (
    DetailView,
    DetailWithVersions,
    ListView,
    MsgspecAPIView,
    create_many,
    fetch_all,
    fetch_one,
    make_expansion,
)
from openbeheer.clients import (
    iter_pages,
    selectielijst_client,
    ztc_client,
)
from openbeheer.helpers import retrieve_objecttypen
from openbeheer.types import (
    BesluitTypeWithUUID,
    DetailResponse,
    EigenschapWithUUID,
    FrontendFieldsets,
    InformatieObjectTypeWithUUID,
    OBField,
    OBOption,
    OBPagedQueryParams,
    ResultaatTypeWithUUID,
    RolTypeWithUUID,
    StatusTypeWithUUID,
    VersionSummary,
    ZGWError,
    ZGWResponse,
)
from openbeheer.types._open_beheer import (
    CamelCaseFieldName,
    ExpandableZaakObjectTypeWithUUID,
    ExpandableZaakType,
    ExpandableZaakTypeRequest,
    LAXProcesType,
    VersionedResourceSummary,
    ZaakObjectTypeExtension,
    ZaakObjectTypeWithUUID,
    ZaakTypeInformatieObjectTypeWithUUID,
    ZaakTypeWithUUID,
    fetch_selectielijst_resultaat_options,
    ob_fields_of_type,
)
from openbeheer.types.ztc import (
    BrondatumArchiefprocedure,
    EigenschapSpecificatie,
    InformatieObjectType,
    PaginatedZaakTypeList,
    PatchedZaakTypeRequest,
    Status,
    StatusType,
    VertrouwelijkheidaanduidingEnum,
    ZaakType,
    ZaakTypeRequest,
)
from openbeheer.utils import camelize
from openbeheer.zaaktype.constants import (
    TEMPLATE_MAPPING,
    ZAAKTYPE_FIELDSETS,
    OptionalZaakType,
    Sjabloon,
)
from openbeheer.zaaktype.utils import format_related_resource_error

if TYPE_CHECKING:
    from uuid import UUID

    from ape_pie import APIClient
    from rest_framework.request import Request

logger = structlog.get_logger(__name__)


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


class ZaakTypeSummary(VersionedResourceSummary, kw_only=True, rename="camel"):
    url: str
    identificatie: str
    omschrijving: str
    # str, because VertrouwelijkheidaanduidingEnum does not contain "" but OZ does
    vertrouwelijkheidaanduiding: str
    versiedatum: datetime.date
    # Actief true/false: calculated for ja/nee in the frontend
    actief: bool | UnsetType = UNSET
    einde_geldigheid: datetime.date | None = None
    concept: bool | UnsetType = UNSET


@extend_schema_view(
    get=extend_schema(
        tags=["Zaaktypen"],
        summary="Get zaaktypen",
        parameters=[],
        filters=True,
        description="Retrieve zaaktypen from Open Zaak.",
    ),
    post=extend_schema(
        tags=["Zaaktypen"],
        summary="Create a zaaktype",
        description="Create a zaaktype.",
        request=ExpandableZaakTypeRequest,
        responses={
            "201": ExpandableZaakType,
            "400": list[ZGWError],
            "500": list[ZGWError],
        },
    ),
)
class ZaakTypeListView(
    ListView[ZaaktypenGetParametersQuery, ZaakTypeSummary, ZaakType]
):
    return_data_type = ZaakTypeSummary
    data_type = ZaakType
    query_type = ZaaktypenGetParametersQuery
    endpoint_path = "zaaktypen"

    @override
    def parse_ob_fields(
        self,
        params: ZaaktypenGetParametersQuery,
        option_overrides: Mapping[str, list[OBOption]] = {},
        **_,
    ) -> list[OBField]:
        order = [
            "url",
            "identificatie",
            "omschrijving",
            "vertrouwelijkheidaanduiding",
            "versiedatum",
            "actief",
            "eindeGeldigheid",
            "concept",
        ]
        return super().parse_ob_fields(
            params,
            dict(option_overrides)
            | {
                "vertrouwelijkheidaanduiding": OBOption.from_enum(
                    VertrouwelijkheidaanduidingEnum
                )
            },
            sort_key=lambda f: order.index(f.name),
            base_editable=lambda _: False,  # no editable fields
        )

    @override
    def create_related(self, api_client, obj, request_data):
        zaaktype = ExpandableZaakType(**asdict(obj))

        posted_expansions = request_data.get("_expand", {})

        all_errors = []

        def inject_foreignkeys(key) -> Iterable[Mapping]:
            # add missing foreign keys
            # defaults | posted | overrides
            return (
                {"catalogus": obj.catalogus} | data | {"zaaktype": obj.url}
                for data in posted_expansions.get(key, [])
            )

        besluittypen, errors = create_many(
            api_client,
            "besluittypen",
            BesluitTypeWithUUID,
            inject_foreignkeys("besluittypen"),
            partial(format_related_resource_error, "besluittypen"),
        )
        all_errors.extend(errors)
        statustypen, errors = create_many(
            api_client,
            "statustypen",
            StatusType,
            inject_foreignkeys("statustypen"),
            partial(format_related_resource_error, "statustypen"),
        )
        all_errors.extend(errors)
        resultaattypen, errors = create_many(
            api_client,
            "resultaattypen",
            ResultaatTypeWithUUID,
            inject_foreignkeys("resultaattypen"),
            partial(format_related_resource_error, "resultaattypen"),
        )
        all_errors.extend(errors)
        eigenschappen, errors = create_many(
            api_client,
            "eigenschappen",
            EigenschapWithUUID,
            inject_foreignkeys("eigenschappen"),
            partial(format_related_resource_error, "eigenschappen"),
        )
        all_errors.extend(errors)
        informatieobjecttypen, errors = create_many(
            api_client,
            "informatieobjecttypen",
            InformatieObjectTypeWithUUID,
            inject_foreignkeys("informatieobjecttypen"),
            partial(format_related_resource_error, "informatieobjecttypen"),
        )
        all_errors.extend(errors)
        roltypen, errors = create_many(
            api_client,
            "roltypen",
            RolTypeWithUUID,
            inject_foreignkeys("roltypen"),
            partial(format_related_resource_error, "roltypen"),
        )
        all_errors.extend(errors)
        deelzaaktypen, errors = create_many(
            api_client,
            "zaaktypen",
            ZaakTypeWithUUID,
            posted_expansions.get("deelzaaktypen", []),
            partial(format_related_resource_error, "deelzaaktypen"),
        )
        all_errors.extend(errors)
        zaakobjecttypen, errors = create_many(
            api_client,
            "zaakobjecttypen",
            ZaakObjectTypeWithUUID,
            inject_foreignkeys("zaakobjecttypen"),
            partial(format_related_resource_error, "zaakobjecttypen"),
        )
        all_errors.extend(errors)

        # M2M
        zaaktype.besluittypen = [t.url for t in besluittypen if t.url] + (
            zaaktype.besluittypen or []
        )
        zaaktype.statustypen = [t.url for t in statustypen if t.url]
        zaaktype.resultaattypen = [t.url for t in resultaattypen if t.url]
        zaaktype.eigenschappen = [t.url for t in eigenschappen if t.url]
        zaaktype.informatieobjecttypen = [t.url for t in informatieobjecttypen if t.url]
        zaaktype.roltypen = [t.url for t in roltypen if t.url]
        # accepts existing
        zaaktype.deelzaaktypen = [t.url for t in deelzaaktypen if t.url] + (
            zaaktype.deelzaaktypen or []
        )
        zaaktype.zaakobjecttypen = [t.url for t in zaakobjecttypen if t.url]

        # existing besluittypen and deelzaaktypen are not expanded (yet?)
        zaaktype._expand = replace(
            zaaktype._expand,
            besluittypen=besluittypen,
            statustypen=statustypen,
            resultaattypen=resultaattypen,
            eigenschappen=eigenschappen,
            informatieobjecttypen=informatieobjecttypen,
            roltypen=roltypen,
            deelzaaktypen=deelzaaktypen,
            zaakobjecttypen=zaakobjecttypen,
        )

        return zaaktype, all_errors

    def parse_query_params(self, request: Request, api_client: APIClient):
        params = super().parse_query_params(request, api_client)
        if params.catalogus:
            params.catalogus = f"{api_client.base_url}catalogussen/{params.catalogus}"
        return params


def expand_deelzaaktype(
    client: APIClient, zaaktypen: Iterable[ZaakType]
) -> list[list[ZaakType | None]]:
    return [
        [
            fetch_one(client, dz_url, ZaakType) if dz_url else None
            for dz_url in (zt.deelzaaktypen or [])
        ]
        for zt in zaaktypen
    ]


def expand_selectielijstprocestype(
    client: APIClient, zaaktypen: Iterable[ZaakType]
) -> Iterable[LAXProcesType | None]:
    # There is only one zaaktype, since we are expanding
    # the retrieve endpoint.
    zaaktype = list(zaaktypen)[0]
    if not zaaktype.selectielijst_procestype:
        return [None]

    with selectielijst_client() as client:
        return [
            fetch_one(client, zaaktype.selectielijst_procestype, LAXProcesType)
            if zaaktype.selectielijst_procestype
            else None
            for zaaktype in zaaktypen
        ]


def expand_zaakobjecttypen(
    client: APIClient, zaaktypen: Iterable[ZaakType]
) -> Iterable[Iterable[ExpandableZaakObjectTypeWithUUID | None]]:
    def expand_zaakobjecttypen(
        zaaktype: ZaakType,
    ) -> Iterable[ExpandableZaakObjectTypeWithUUID | None]:
        if not zaaktype.zaakobjecttypen:
            return []

        dict_objecttypen = retrieve_objecttypen()

        zaakobjecttypen = fetch_all(
            client,
            "zaakobjecttypen",
            {"zaaktype": zaaktype.url},
            ExpandableZaakObjectTypeWithUUID,
        )
        for zaakobjecttype in zaakobjecttypen:
            try:
                zaakobjecttype._expand = ZaakObjectTypeExtension(
                    objecttype=dict_objecttypen[zaakobjecttype.objecttype]
                )
            except KeyError:
                logger.warning(
                    "Open Zaak and Objecttypes API out of sync.",
                    zaakobjecttype=zaakobjecttype.url,
                    zaaktype=zaaktype.url,
                )
        return zaakobjecttypen

    return [expand_zaakobjecttypen(zaaktype) for zaaktype in zaaktypen]


def expand_zaaktype_informatieobjecttype(
    client: APIClient, zaaktypen: Iterable[ZaakType]
) -> Iterable[Iterable[ZaakTypeInformatieObjectTypeWithUUID | None]]:
    # There is only one zaaktype, since we are expanding
    # the retrieve endpoint.
    zaaktypen = list(zaaktypen)
    assert len(zaaktypen) == 1
    zaaktype = zaaktypen[0]

    return [
        fetch_all(
            client,
            "zaaktype-informatieobjecttypen",
            {"zaaktype": zaaktype.url, "status": "alles"},
            ZaakTypeInformatieObjectTypeWithUUID,
        )
    ]


@extend_schema_view(
    get=extend_schema(
        operation_id="service_zaaktype_retrieve_one",
        tags=["Zaaktypen"],
        summary="Get a zaaktype",
        description="Retrive a zaaktype from Open Zaak.",
        request=None,
        responses={
            "200": DetailResponse[ExpandableZaakType],
            "400": ZGWError,
        },
    ),
    patch=extend_schema(
        tags=["Zaaktypen"],
        summary="Patch a zaaktype",
        description=(
            "Partially update a zaaktype from Open Zaak. According to OZ specs, this should only work with"
            " draft zaaktypen. In practice, it modifies also the non-draft zaaktypen."
        ),
        request=PatchedZaakTypeRequest,
        responses={
            "200": DetailResponse[ExpandableZaakType],
            "400": ZGWError,
        },
    ),
    put=extend_schema(
        tags=["Zaaktypen"],
        summary="Put a zaaktype",
        description=(
            "Fully update a zaaktype from Open Zaak. According to OZ specs, this should only work with"
            " draft zaaktypen. In practice, it modifies also the non-draft zaaktypen."
        ),
        request=ZaakTypeRequest,
        responses={
            "200": DetailResponse[ExpandableZaakType],
            "400": ZGWError,
        },
    ),
    delete=extend_schema(
        tags=["Zaaktypen"],
        summary="Delete a zaaktype",
        description=(
            "Delete a zaaktype from Open Zaak. According to OZ specs, this should only work with"
            " draft zaaktypen. In practice, it deletes also the published zaaktypen."
        ),
        request=None,
        responses={
            "204": None,
            "400": ZGWError,
        },
    ),
)
class ZaakTypeDetailView(DetailWithVersions, DetailView[ExpandableZaakType]):
    data_type = ExpandableZaakType
    return_data_type = DetailResponse[ExpandableZaakType]
    endpoint_path = "zaaktypen/{uuid}"
    serializer_class = None

    @staticmethod
    def _get_params_with_status(zaaktype: ZaakType):
        return {"zaaktype": zaaktype.url, "status": "alles"}

    @staticmethod
    def _key(zaaktype: ZaakType):
        return {"zaaktype": zaaktype.url}

    expansions = {
        "besluittypen": make_expansion(
            "besluittypen",
            # "zaaktypen" is probably a typo in the VNG spec, it doesn't look like
            # it actually accepts multiple so we can't use a __in
            lambda zt: {"zaaktypen": zt.url, "status": "alles"},  # pyright: ignore[reportAttributeAccessIssue]
            BesluitTypeWithUUID,
        ),
        "statustypen": make_expansion(
            "statustypen", _get_params_with_status, StatusTypeWithUUID
        ),
        "resultaattypen": make_expansion(
            "resultaattypen", _get_params_with_status, ResultaatTypeWithUUID
        ),
        "eigenschappen": make_expansion(
            "eigenschappen", _get_params_with_status, EigenschapWithUUID
        ),
        "informatieobjecttypen": make_expansion(
            "informatieobjecttypen",
            _get_params_with_status,
            InformatieObjectTypeWithUUID,
        ),
        "roltypen": make_expansion(
            "roltypen", _get_params_with_status, RolTypeWithUUID
        ),
        "deelzaaktypen": expand_deelzaaktype,
        "zaakobjecttypen": expand_zaakobjecttypen,
        "selectielijst_procestype": expand_selectielijstprocestype,
        "zaaktypeinformatieobjecttypen": expand_zaaktype_informatieobjecttype,
    }

    read_only_expansions: set[CamelCaseFieldName] = {
        camelize(f)
        for f in expansions
        if f not in PatchedZaakTypeRequest.__struct_fields__
    }

    def get_item_versions(
        self, slug: str, data: ZaakType
    ) -> tuple[list[ZaakType] | ZGWError, int]:
        with ztc_client() as client:
            response = client.get(
                "zaaktypen",
                params={"identificatie": data.identificatie, "status": "alles"},
            )

        if not response.ok:
            error = decode(response.content, type=ZGWError)
            return error, response.status_code

        zaaktypen = decode(response.content, type=PaginatedZaakTypeList)

        results = list(iter_pages(client, zaaktypen))

        return results, response.status_code

    def format_version(self, data: ZaakType) -> VersionSummary:
        assert (
            data.url
        )  # The specs say that it is optional, but in practice it's always present
        zaaktype_url = furl(data.url)
        uuid = zaaktype_url.path.segments[-1]

        return VersionSummary(
            uuid=uuid,
            begin_geldigheid=data.begin_geldigheid,
            einde_geldigheid=data.einde_geldigheid,
            concept=data.concept,
        )

    def get_fields(
        self,
        data: ExpandableZaakType,
        option_overrides: Mapping[CamelCaseFieldName, list[OBOption]] = {},
        *,
        base_editable: Callable[[CamelCaseFieldName], bool] = bool,
    ) -> Iterable[OBField]:
        selectielijst_options = (
            fetch_selectielijst_resultaat_options(
                procestype_url=data.selectielijst_procestype
            )
            if data.selectielijst_procestype
            else []
        )

        yield from super().get_fields(
            data,
            option_overrides={
                "_expand.zaaktypeinformatieobjecttypen.informatieobjecttype": self.get_informatieobjecttype_options(
                    data
                ),
                "_expand.resultaattypen.selectielijstklasse": selectielijst_options,
                "_expand.eigenschappen.statustype": [
                    OBOption(label=statustype.omschrijving, value=statustype.url)
                    for statustype in (
                        data._expand.statustypen
                        if data._expand.statustypen is not UNSET
                        else []
                    )
                ],
            },
            base_editable=lambda name: name not in self.read_only_expansions,
        )
        yield from ob_fields_of_type(
            EigenschapSpecificatie, prefix="_expand.eigenschappen.specificatie."
        )
        yield from ob_fields_of_type(
            BrondatumArchiefprocedure,
            prefix="_expand.resultaattypen.brondatumArchiefprocedure.",
            base_editable=lambda _: False,  # read-only
        )

    def get_fieldsets(self) -> FrontendFieldsets:
        return ZAAKTYPE_FIELDSETS

    def get_informatieobjecttype_options(self, zaaktype: ZaakType) -> list[OBOption]:
        today = datetime.date.today().isoformat()
        with ztc_client() as client:
            informatieobjecttypen = fetch_all(
                client,
                "informatieobjecttypen",
                # You can only relate a Zaaktype and an Informatieobjecttype if they belong to the same catalogus.
                params={
                    "catalogus": zaaktype.catalogus,
                    "status": "definitief",
                    "datumGeldigheid": today,
                },
                result_type=InformatieObjectType,
            )

        return [
            OBOption(
                label=informatieobjecttype.omschrijving, value=informatieobjecttype.url
            )
            for informatieobjecttype in informatieobjecttypen
        ]


class ZaakTypePublishView(MsgspecAPIView):
    endpoint_path = "zaaktypen/{uuid}/publish"

    @extend_schema(
        operation_id="service_zaaktypen_publish",
        summary="Publish a zaaktype",
        tags=["Zaaktypen"],
        responses={
            204: None,
            400: ZGWError,
        },
    )
    def post(self, request: Request, slug: str, uuid: UUID) -> Response:
        "Publish a zaaktype"
        with ztc_client(slug) as client:
            response = client.post(
                self.endpoint_path.format(uuid=uuid),
            )

            if not response.ok:
                error = decode(response.content)
                return Response(
                    error,
                    status=response.status_code,
                )

        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema_view(
    get=extend_schema(
        operation_id="template_zaaktype_list",
        tags=["Sjablonen"],
        summary="Get ZaakTypeSjablonen",
        responses={200: ZGWResponse[Sjabloon[OptionalZaakType]]},
    )
)
class ZaakTypeTemplateListView(MsgspecAPIView):
    def get(self, request: Request) -> Response:
        results = list(TEMPLATE_MAPPING.values())
        return Response(
            data=ZGWResponse(
                count=len(results),
                next=None,
                previous=None,
                results=results,
            )
        )


@extend_schema_view(
    get=extend_schema(
        tags=["Sjablonen"],
        summary="Get ZaakTypeSjabloon",
        responses={200: Sjabloon[OptionalZaakType]},
    )
)
class ZaakTypeTemplateView(MsgspecAPIView):
    def get(self, request: Request, uuid: UUID) -> Response:
        try:
            return Response(data=TEMPLATE_MAPPING[uuid])
        except KeyError:
            return Response(
                data=ZGWError(
                    title=_("Not Found"),
                    detail=_("Unknown ZaakTypeTemplate {uuid}").format(uuid=str(uuid)),
                    code="not_found",
                    instance="",
                    status=404,
                )
            )
