from typing import Any
from drf_spectacular.extensions import OpenApiSerializerExtension
from drf_spectacular.plumbing import ResolvedComponent
from drf_spectacular.openapi import AutoSchema
from drf_spectacular.utils import Direction

from rest_framework.views import APIView
from msgspec import Struct
from msgspec.json import schema



class MsgSpecExtension(OpenApiSerializerExtension):
    target_class = Struct
    match_subclasses = True

    def map_serializer(self, auto_schema: AutoSchema, direction: Direction) -> dict[str, Any]:
        msgspec_schema = schema(self.target)
        # TODO make schema compatible

        return msgspec_schema


