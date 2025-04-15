from msgspec.json import Encoder
from rest_framework.renderers import BaseRenderer
from rest_framework.views import APIView as _APIView

_ENCODER = Encoder()


class MsgspecJSONRenderer(BaseRenderer):
    media_type = "application/json"
    format = "json"
    ensure_ascii = True
    charset = None

    def render(self, data, *_args, **_kwargs):
        if data is None:
            return bytes()

        return _ENCODER.encode(data)


class MsgspecAPIView(_APIView):
    def get_renderers(self) -> list[BaseRenderer]:
        return [MsgspecJSONRenderer()]
