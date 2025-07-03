from typing import Any, Literal

import structlog
from drf_spectacular.extensions import (
    OpenApiFilterExtension,
    OpenApiSerializerExtension,
)
from drf_spectacular.openapi import AutoSchema
from drf_spectacular.plumbing import ResolvedComponent
from drf_spectacular.utils import Direction
from msgspec.json import schema_components
from rest_framework.serializers import Serializer

from openbeheer.types._drf_spectacular import QueryParamSchema

logger = structlog.get_logger(__name__)


def camelize_serializer_fields(result, generator, request, public):
    """Simplified version of the bugged
    drf_spectacular.contrib.djangorestframework_camel_case.camelize_serializer_fields

    The original can't handle the "items" of an array be False
    {'type': 'array', 'minItems': 2, 'maxItems': 2, 'prefixItems': [{'type': 'string'}, {'$ref': '#/components/schemas/FrontendFieldSet'}], 'items': False}

    It is within spec. It says "prefixItems" is complete, and no more items are valid:
    https://json-schema.org/understanding-json-schema/reference/array

    TODO: use upstream when fixed https://github.com/tfranzel/drf-spectacular/pull/1432
    """

    def camelize_str(key: str) -> str:
        if "_" not in key or key == "_expand":
            return key
        return "".join(s.title() if n else s for n, s in enumerate(key.split("_")))

    def camelize_component(schema: dict, name: str | None = None) -> dict:
        if schema.get("type") == "object":
            if "properties" in schema:
                schema["properties"] = {
                    camelize_str(field_name): camelize_component(
                        field_schema, field_name
                    )
                    for field_name, field_schema in schema["properties"].items()
                }
            if "required" in schema:
                schema["required"] = [
                    camelize_str(field) for field in schema["required"]
                ]
        elif schema.get("type") == "array" and isinstance(schema["items"], dict):
            camelize_component(schema["items"])
        return schema

    for (_, component_type), component in generator.registry._components.items():
        if component_type == "schemas":
            camelize_component(component.schema)

    # inplace modification of components also affect result dict, so regeneration is not necessary
    return result


class MsgSpecExtension(OpenApiSerializerExtension):
    """Generate API Schema from MsgSpec types."""

    @classmethod
    def _matches(cls, target: Any) -> bool:
        """Match based on whether Msgspec can generate a schema"""
        try:
            return bool(schema_components((target,)))
        except Exception as e:
            if not isinstance(target, Serializer):
                logger.debug("msgspec can't make schema", target=target, exc_info=e)
            return False

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

        return out.get("$ref")


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
