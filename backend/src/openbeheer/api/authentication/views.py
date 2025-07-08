from django.contrib.auth import login, logout
from django.utils.translation import gettext_lazy as _

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .authentication import AnonCSRFSessionAuthentication
from .serializers import AuthSerializer


@extend_schema(
    summary=_("Login"),
    responses={
        204: None,
    },
)
class LoginView(APIView):
    authentication_classes = (AnonCSRFSessionAuthentication,)
    permission_classes = ()
    serializer_class = AuthSerializer

    def post(self, request: Request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        login(request, serializer.validated_data["user"])
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(
    summary=_("Logout"),
    responses={
        204: None,
    },
)
class LogoutView(APIView):
    serializer_class = None

    def post(self, request: Request, *args, **kwargs):
        logout(request)

        return Response(status=status.HTTP_204_NO_CONTENT)
