from typing import Any, Literal, get_args, get_origin
from drf_spectacular.extensions import OpenApiSerializerExtension
from drf_spectacular.openapi import AutoSchema
from drf_spectacular.utils import Direction
from msgspec import Struct
from msgspec.json import schema_components
from drf_spectacular.plumbing import ResolvedComponent, get_class
from drf_spectacular.extensions import OpenApiFilterExtension
import enum

from openbeheer.types._drf_spectacular import QueryParamSchema


SUPPORTED_MSG_CLASSES = (Struct, enum.StrEnum)


class MsgSpecExtension(OpenApiSerializerExtension):
    """Generate API Schema from MsgSpec types."""

    @classmethod
    def _matches(cls, target: Any) -> bool:
        # For generic types
        if get_origin(target):
            if issubclass(get_origin(target), SUPPORTED_MSG_CLASSES):
                return True

            # Example: list[OBOption] origin is list, and not in SUPPORTED_MSG_CLASSES,
            # but the argument OBOption is a Struct, so it needs to use this extension.
            return any(cls._matches(arg) for arg in get_args(target))

        return issubclass(get_class(target), SUPPORTED_MSG_CLASSES)

    def map_serializer(
        self, auto_schema: AutoSchema, direction: Direction
    ) -> dict[str, Any]:
        (out,), components = schema_components(
            (self.target,), ref_template="#/components/schemas/{name}"
        )
        # This is the schema of the current component. However, its schema may reference other components that
        # also need to be registered in the schema.
        component_schema = out
        if "$ref" in out:
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
        """Get a name for a component

        Msgspec builds the names for the classes, we can extract it from the schema. The name
        is used by other components with internal references, so it is important that it is predictable.

        However, if we are building the name for a type like ``list[SomeStruct]``, ``out`` will not have a ``$ref``
        key, but it will be in the shape ``{"type": "array", "items": {"$ref": "ref/to/SomeStruct"}}``.
        So in this case we need to create the name ourselves.
        """

        (out,), components = schema_components((self.target,), ref_template="{name}")
        if out.get("type") == "array" and "$ref" in out.get("items", {}):
            return f"list_{out['items']['$ref']}"

        return out["$ref"]


class MsgSpecFilterBackend:
    pass


class MsgSpecQueryParamsExtension(OpenApiFilterExtension):
    target_class = MsgSpecFilterBackend
    match_subclasses = True

    def get_schema_operation_parameters(
        self, auto_schema: "AutoSchema", *args, **kwargs
    ) -> list[dict[str, Any]]:
        filters = getattr(auto_schema.view, "query_type", None)

        (out,), components = schema_components(
            (filters,), ref_template="#/components/schemas/{name}"
        )

        # Extract the component which contains the schema of the "query_type" object
        component_name = out["$ref"].replace("#/components/schemas/", "")
        component_schema = components.pop(component_name)

        # Manually construct the schema for the query params
        results = [
            QueryParamSchema.from_json_schema(query_name, query_schema)
            for query_name, query_schema in component_schema["properties"].items()
        ]

        # Register any additional component needed for the schema of the query parameters
        for sub_name, sub_schema in components.items():
            sub_component = ResolvedComponent(
                name=sub_name,
                type=ResolvedComponent.SCHEMA,
                object=sub_name,
                schema=sub_schema,
            )
            auto_schema.registry.register_on_missing(sub_component)

        return results
