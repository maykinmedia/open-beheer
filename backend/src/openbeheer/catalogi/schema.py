from typing import Any, Literal, _GenericAlias  # TODO Fix undesired import
from drf_spectacular.extensions import OpenApiSerializerExtension
from drf_spectacular.openapi import AutoSchema
from drf_spectacular.utils import Direction
from msgspec import Struct
from msgspec.json import schema_components
from drf_spectacular.plumbing import ResolvedComponent


class MsgSpecExtension(OpenApiSerializerExtension):
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


class MsgSpecStructExtension(MsgSpecExtension):
    target_class = Struct
    match_subclasses = True


class GenericAliasExtension(MsgSpecExtension):
    target_class = _GenericAlias
    match_subclasses = True
