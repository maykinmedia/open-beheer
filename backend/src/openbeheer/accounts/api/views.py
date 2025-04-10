from django.utils.translation import gettext_lazy as _

from drf_spectacular.utils import extend_schema
from rest_framework.generics import RetrieveAPIView

from ..models import User
from .serializers import UserSerializer


@extend_schema(
    tags=["Users"],
    summary=_("Who Am I"),
    description=_("Returns the current logged in user."),
    responses={
        200: UserSerializer(),
    },
)
class WhoAmIView(RetrieveAPIView):
    serializer_class = UserSerializer

    def get_object(self) -> User:
        return self.request.user
