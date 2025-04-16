from furl import furl
import datetime

from django.utils.translation import gettext_lazy as _

from drf_spectacular.utils import extend_schema
from msgspec.structs import asdict
from msgspec import Struct, convert
from msgspec.json import decode
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from openbeheer.api.views import MsgspecAPIView
from openbeheer.clients import ztc_client
from openbeheer.types import (
    URL,
    Catalogus,
    OBField,
    OBFieldType,
    OBList,
    OBPagination,
    ZGWError,
    ZGWResponse,
    as_ob_option,
)


@extend_schema(
    summary=_("Catalogussen"),
)
class CatalogussenView(MsgspecAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request: Request):
        """Paginated list of Catalogussen.

        Available API filters *=exposed:
            domein str (exact)
            * domein__in str,str,... (comma sep exact)
            rsin (exact)
            * rsin__in str,str,... (comma sep exact)
        """
        page_size = 100  # TODO: magic number
        client = ztc_client()

        class Exposed(Struct):
            domein__in: str = ""
            rsin__in: str = ""
            page: int = 1

        params = convert(request.query_params, Exposed, strict=False)
        base_params = {"pageSize": page_size}

        with client:
            response = client.get(
                "catalogussen",
                params=base_params | asdict(params),
            )

        if not response.ok:
            error = decode(response.content, type=ZGWError)
            return Response(error, status=response.status_code)

        data = decode(response.content, type=ZGWResponse[Catalogus])

        self_url = furl(request.build_absolute_uri())
        next_url = self_url.copy()
        next_url.args.set("page", params.page + 1)
        prev_url = self_url.copy()
        prev_url.args.set("page", params.page - 1)

        resp = OBList(
            fields=[
                OBField[str](
                    name="domein",
                    type=OBFieldType.string,
                    filter_lookup="domein__in",
                    value=params.domein__in,
                ),
                OBField[str](
                    name="rsin",
                    type=OBFieldType.string,
                    filter_lookup="rsin__in",
                    value=params.rsin__in,
                ),
                OBField[str](
                    name="contactpersoon_beheer_naam",
                    type=OBFieldType.string,
                ),
                OBField[URL](name="url", type=OBFieldType.string),
                OBField[str](
                    name="contactpersoon_beheer_telefoonnummer", type=OBFieldType.string
                ),
                OBField[str](
                    name="contactpersoon_beheer_emailadres", type=OBFieldType.string
                ),
                # XXX: Erhmmm. What's a Field, really?
                # OBField[list[URL]](name="zaaktypen", type=OBFieldType.string?),
                # OBField[list[URL]](name="besluittypen", type=OBFieldType.string?),
                # OBField[list[URL]](name="informatieobjecttypen", type=OBFieldType.string?),
                OBField[str](name="naam", type=OBFieldType.string),
                OBField[str](name="versie", type=OBFieldType.string),
                OBField[datetime.date](name="begindatum_versie", type=OBFieldType.date),
            ],
            pagination=OBPagination(
                count=data.count,
                page=params.page,
                next=data.next and URL(str(next_url)),
                previous=data.previous and URL(str(prev_url)),
                page_size=page_size,
            ),
            results=data.results,
        )

        return Response(resp, status=response.status_code)
