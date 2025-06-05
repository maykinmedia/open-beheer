from typing import Any, Literal, get_origin  # TODO Fix undesired import
from drf_spectacular.extensions import OpenApiSerializerExtension
from drf_spectacular.openapi import AutoSchema
from drf_spectacular.utils import Direction
from msgspec import Struct
from msgspec.json import schema_components
from drf_spectacular.plumbing import ResolvedComponent, get_class
import enum

SUPPORTED_MSG_CLASSES = (
    Struct, enum.StrEnum
)

class MsgSpecExtension(OpenApiSerializerExtension):
    @classmethod
    def _matches(cls, target: Any) -> bool:
        # For generic types
        if get_origin(target):
            return issubclass(get_origin(target), SUPPORTED_MSG_CLASSES)
        return issubclass(get_class(target), SUPPORTED_MSG_CLASSES)

    def map_serializer(
        self, auto_schema: AutoSchema, direction: Direction
    ) -> dict[str, Any]:
        (out,), components = schema_components(
            (self.target,), ref_template="#/components/schemas/{name}"
        )
        # This is the schema of the current component. However, its schema may reference other components that
        # also need to be registered in the schema.
        component_name = out["$ref"].replace("#/components/schemas/", "")
        component_schema = components.pop(component_name)

        # Extracting and registering sub components
        for sub_name, sub_schema in components.items():
            sub_component = ResolvedComponent(
                name=sub_name,
                type=ResolvedComponent.SCHEMA,
                object=sub_name,
                schema=sub_schema,
            )
            auto_schema.registry.register_on_missing(sub_component)

        # This is a JSON schema and not an OpenAPI schema. We might need to convert it.
        return component_schema

    def get_name(
        self,
        auto_schema: AutoSchema,
        direction: Literal["request"] | Literal["response"],
    ) -> str | None:
        # msgspec builds the names for the classes, we can extract it from the schema
        # This needs to remain in sync with the name that we
        (out,), components = schema_components((self.target,), ref_template="{name}")
        return out["$ref"]
