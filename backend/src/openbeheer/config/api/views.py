from django.utils.translation import gettext_lazy as _

from drf_spectacular.utils import extend_schema
from mozilla_django_oidc_db.constants import OIDC_ADMIN_CONFIG_IDENTIFIER
from mozilla_django_oidc_db.models import OIDCClient
from msgspec import to_builtins
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView

from openbeheer.types import OIDCInfo


class OIDCInfoView(APIView):
    authentication_classes = ()
    permission_classes = ()

    @extend_schema(
        summary=_("Retrieve OIDC info"),
        description=_("Returns info about OIDC that is needed by the frontend. "),
        tags=["Configuration"],
        responses={
            200: OIDCInfo,
        },
    )
    def get(self, request: Request, *args, **kwargs):
        client = OIDCClient.objects.get(identifier=OIDC_ADMIN_CONFIG_IDENTIFIER)

        oidc_info = OIDCInfo(
            enabled=client.enabled,
            login_url=reverse("oidc_authentication_init", request=request),
        )

        return Response(to_builtins(oidc_info))
