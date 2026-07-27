from ape_pie import InvalidURLError
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from msgspec import ValidationError
from msgspec.json import decode
from rest_framework.request import Request
from rest_framework.response import Response

from openbeheer.api.views import MsgspecAPIView
from openbeheer.clients import selectielijst_client
from openbeheer.types import ExternalServiceError, LAXResultaat, ZGWError
from openbeheer.types._zgw import InvalidParam
from openbeheer.utils.decorators import handle_service_errors


@extend_schema_view(
    get=extend_schema(
        operation_id="service_resultaten_retrieve_one",
        tags=["resultaten"],
        summary="Get a Resultaat",
        description="Retrieve a Resultaat from Selectielijst.",
        parameters=[
            OpenApiParameter(name="url", required=True),
        ],
        responses={
            "200": LAXResultaat,
            "400": ZGWError,
            "502": ExternalServiceError,
            "504": ExternalServiceError,
        },
    ),
)
class ResultaatDetailView(MsgspecAPIView):
    """
    Endpoint for Resultaten from the Selectielijst
    """

    @handle_service_errors
    def get(self, request: Request, *args, **kwargs) -> Response:
        with selectielijst_client() as client:
            url = request.GET.get("url", None)
            if url is None:
                return Response(
                    ZGWError(
                        code="Bad request",
                        title="Missing url",
                        detail="",
                        instance="",
                        status=400,
                        invalid_params=[
                            InvalidParam(
                                name="url",
                                code="missing",
                                reason="Query param url should be present.",
                            ),
                        ],
                    ),
                    400,
                )

            try:
                response = client.get(url)
            except InvalidURLError as e:
                return Response(
                    ZGWError(
                        code="Bad request",
                        title="Invalid url",
                        detail=str(e),
                        instance="",
                        status=400,
                        invalid_params=[
                            InvalidParam(
                                name="url",
                                code="invalid",
                                reason="Invalid url provided.",
                            ),
                        ],
                    ),
                    400,
                )

            content: bytes = response.content

            if not response.ok:
                error = decode(content, type=ZGWError)
                Response(error, response.status_code)

            try:
                resultaat = decode(
                    content,
                    type=LAXResultaat,
                    strict=False,
                )
            except ValidationError as e:
                return Response(
                    ZGWError(
                        code="Bad response",
                        title="Server returned out of spec response",
                        detail=str(e),
                        instance="",
                        status=502,
                        invalid_params=[],
                    ),
                    502,
                )

        return Response(resultaat)
