import uuid

from django.utils.translation import gettext_lazy as _

from drf_spectacular.utils import extend_schema
from msgspec.json import decode
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from openbeheer.api.views import MsgspecAPIView
from openbeheer.clients import zrc_client
from openbeheer.types import (
    OBField,
    OBFieldType,
    OBList,
    OBPagination,
    OBSelection,
    Zaak,
    ZGWError,
    ZGWResponse,
    as_ob_option,
)


@extend_schema(
    summary=_("Zaken"),
)
class ZakenView(MsgspecAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        page = int(request.GET.get("page", 1))
        page_size = 100  # TODO: magic number
        client = zrc_client()
        with client:
            response = client.get(
                "zaken",
                params={
                    "expand": ["status", "status.statustype"],
                    "pageSize": page_size,
                },
            )

        if not response.ok:
            error = decode(response.content, type=ZGWError)
            return Response(error, status=response.status_code)

        data = decode(response.content, type=ZGWResponse[Zaak])

        # XXX: Not filterable on API, should we even return OBOption to frontend?
        statustypes = sorted(
            {
                as_ob_option(st)
                for z in data.results
                if (s := z._expand.status) and (st := s._expand.statustype)
            },
            key=lambda o: o.label,
        )

        resp = OBList(
            fields=[
                OBField(
                    name="status",
                    type=OBFieldType.string,  # actually url
                    # filter_lookup="",
                    # value=None,
                    options=statustypes,
                ),
                OBField(name="identificatie", type=OBFieldType.string),
                OBField(name="uuid", type=OBFieldType.string),
                OBField(name="toelichting", type=OBFieldType.string),
                OBField(name="omschrijving", type=OBFieldType.string),
                OBField(name="registratiedatum", type=OBFieldType.date),
                OBField(name="startdatum", type=OBFieldType.date),
                OBField(name="einddatum", type=OBFieldType.date),
            ],
            pagination=OBPagination(
                count=data.count,
                page=page,
                next=data.next,
                previous=data.previous,
                page_size=page_size,
            ),
            results=data.results,
            selection=OBSelection[uuid.UUID](
                key="uuid",
                selection={},
            ),
        )

        return Response(resp, status=response.status_code)
