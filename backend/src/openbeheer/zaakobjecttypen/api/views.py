from datetime import date, timedelta
from typing import Iterable

from django.utils.translation import gettext_lazy as __

import structlog
from ape_pie import APIClient
from drf_spectacular.utils import extend_schema, extend_schema_view
from furl import furl
from msgspec import ValidationError

from openbeheer.api.views import (
    DetailView,
    DetailViewWithoutVersions,
    ListView,
    fetch_one,
)
from openbeheer.clients import objecttypen_client
from openbeheer.helpers import retrieve_objecttypen
from openbeheer.types import (
    ExpandableZaakObjectTypeWithUUID,
    ExternalServiceError,
    ZGWError,
)
from openbeheer.types._open_beheer import (
    ZaakObjectTypeWithUUID,
)
from openbeheer.types.objecttypen import ObjectType
from openbeheer.types.ztc import (
    PatchedZaakObjectTypeRequest,
    ZaakObjectType,
    ZaakObjectTypeRequest,
)

from ..types import (
    ZaakobjecttypenGetParametersQuery,
)

logger = structlog.get_logger(__name__)


@extend_schema_view(
    get=extend_schema(
        tags=["zaakobjecttypen"],
        summary="Get zaakobjecttypen",
        parameters=[],
        filters=True,
        description="Retrive zaakobjecttypen from Open Zaak.",
    ),
    post=extend_schema(
        tags=["zaakobjecttypen"],
        summary="Create an zaakobjecttypen",
        description="Create an zaakobjecttypen.",
        request=ZaakObjectTypeRequest,
        responses={
            "201": ZaakObjectType,
            "502": ExternalServiceError,
            "504": ExternalServiceError,
        },
    ),
)
class ZaakObjectTypeListView(
    ListView[
        ZaakobjecttypenGetParametersQuery,
        ZaakObjectType,
        ZaakObjectType,
    ]
):
    """
    Endpoint for zaakobjecttypen attached to a particular Zaaktype
    """

    data_type = ZaakObjectType
    return_data_type = ZaakObjectTypeWithUUID
    query_type = ZaakobjecttypenGetParametersQuery
    endpoint_path = "zaakobjecttypen"

    def get_post_defaults(self) -> dict:
        """Return dynamic default values for creating a ZaakObjectType"""
        objecttypen = retrieve_objecttypen()

        if len(objecttypen.keys()) == 0:
            raise ValidationError(__("No objecttypes present in the Objects API."))

        defaults = {
            "objecttype": list(objecttypen.keys())[0],
            "beginGeldigheid": date.today().isoformat(),
            "eindeGeldigheid": (
                date.today() + timedelta(days=365)
            ).isoformat(),  # Some time in the future...
            "relatieOmschrijving": "Relation with Objecttype",
            "anderObjecttype": False,
        }

        return defaults


def expand_zaakobjecttype(
    client: APIClient, zaakobjecttypen: Iterable[ZaakObjectType]
) -> Iterable[ObjectType | None]:
    # We are in the detail endpoint, so there is only one ZaakObjectType
    zaakobjecttype = list(zaakobjecttypen)[0]
    objecttype_uuid = furl(zaakobjecttype.objecttype).path.segments[-1]

    try:
        with objecttypen_client() as ot_client:
            objecttype = fetch_one(
                ot_client, f"objecttypes/{objecttype_uuid}", ObjectType
            )
    except ValidationError:
        logger.warning(
            "Open Zaak and Objecttypes API out of sync.",
            zaakobjecttype=zaakobjecttype.url,
        )
        return [None]

    return [objecttype]


@extend_schema_view(
    get=extend_schema(
        operation_id="service_zaakobjecttypen_retrieve_one",
        tags=["zaakobjecttypen"],
        summary="Get an zaakobjecttype",
        description="Retrieve an zaakobjecttype from Open Zaak.",
        responses={
            "200": ZaakObjectType,
            "400": ZGWError,
        },
    ),
    patch=extend_schema(
        tags=["zaakobjecttypen"],
        summary="Patch an zaakobjecttype",
        description="Partially update a zaakobjecttype from Open Zaak.",
        request=PatchedZaakObjectTypeRequest,
        responses={
            "200": ZaakObjectType,
            "400": ZGWError,
        },
    ),
    put=extend_schema(
        tags=["zaakobjecttypen"],
        summary="Put an zaakobjecttype",
        description="Fully update a zaakobjecttype from Open Zaak.",
        request=ZaakObjectTypeRequest,
        responses={
            "200": ZaakObjectType,
            "400": ZGWError,
        },
    ),
    delete=extend_schema(
        tags=["zaakobjecttypen"],
        summary="Delete an zaakobjecttype",
        description="Remove permanently a zaakobjecttype from Open Zaak.",
        responses={
            "204": None,
            "400": ZGWError,
        },
    ),
)
class ZaakObjectTypeDetailView(DetailViewWithoutVersions, DetailView[ZaakObjectType]):
    """
    Endpoint for zaakobjecttypen attached to a particular Zaaktype
    """

    return_data_type = data_type = ExpandableZaakObjectTypeWithUUID
    endpoint_path = "zaakobjecttypen/{uuid}"
    expansions = {"objecttype": expand_zaakobjecttype}
