from __future__ import annotations

from collections.abc import MutableMapping, Sequence
from inspect import isclass
from itertools import chain
from typing import (
    TYPE_CHECKING,
    Any,
    Iterator,
    Literal,
    get_args,
)

from drf_spectacular.extensions import (
    OpenApiFilterExtension,
    OpenApiSerializerExtension,
)
from drf_spectacular.plumbing import ResolvedComponent
from msgspec.json import schema_components
from rest_framework.serializers import Field, Serializer
from structlog import get_logger

from openbeheer.types import _open_beheer
from openbeheer.types._drf_spectacular import QueryParamSchema

if TYPE_CHECKING:
    from drf_spectacular.openapi import AutoSchema
    from drf_spectacular.utils import Direction


logger = get_logger(__name__)


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
            if isclass(target) and not isinstance(target, (Serializer, Field)):
                logger.debug("msgspec can't make schema", target=target, exc_info=e)
            return False

    def __init__(self, target):
        super().__init__(target)

        def iter_generics(t):
            yield getattr(t, "__name__", str(t)), t
            for arg in get_args(t):
                yield from iter_generics(arg)

        names, ts = zip(*iter_generics(self.target), strict=True)
        last = len(ts) - 1

        self.__identity_map: dict[str, Any] = {}
        self.__name_map: dict[Any, str] = {}

        for i, t in enumerate(ts):
            name = "_".join(names[i:]) + ("" if i == last else "_")
            # currently mimics the msgspec.schema_components naming scheme
            self.__name_map[t] = name
            # the reverse map so the serializer can map (sub) names back to the type
            self.__identity_map[name] = t

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
                object=getattr(
                    _open_beheer, sub_name, self.__identity_map.get(sub_name, sub_name)
                ),
                schema=sub_schema,
            )
            # we register strings here, but extend_schema registers objects
            # using try because drf throws warnings in the __contains__
            try:
                registry_object = auto_schema.registry[sub_component].object
            except KeyError:
                pass
            else:
                registry_name = (
                    registry_object.__name__
                    if isclass(registry_object)
                    else registry_object
                )
                if registry_name == sub_name:
                    continue

            auto_schema.registry.register_on_missing(sub_component)

        # This is a JSON schema and not an OpenAPI schema. We might need to convert it.
        return component_schema

    def get_name(
        self,
        auto_schema: AutoSchema,
        direction: Literal["request"] | Literal["response"],
    ) -> str | None:
        return self.__name_map.get(self.target)


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
            logger.debug("query_param sub_name", sub_name=sub_name)
            sub_component = ResolvedComponent(
                name=sub_name,
                type=ResolvedComponent.SCHEMA,
                object=sub_name,
                schema=sub_schema,
            )
            auto_schema.registry.register_on_missing(sub_component)

        return results


def _is_type(schema_type: Sequence, expected: str) -> bool:
    """A JSONSchema "type" can be multiple, akin to typing.Union"""
    return (
        schema_type == expected
        if isinstance(schema_type, str)
        else expected in schema_type  # eg "type": ["string", "number"]
    )


def _sub_schemas(schema: MutableMapping) -> Iterator[MutableMapping]:  # noqa: C901
    """
    Walk the schema definitions recursively so that each schema can be processed.
    """
    # adapted from
    # https://github.com/maykinmedia/django-common/blob/800f64d72e2cdd4ad062394e083e62c32ad66575/maykin_common/drf_spectacular/hooks.py

    logger.debug("iterating sub_schemas", schema=schema)
    match schema:
        # array schema type variants
        case {"type": Sequence() as types} if _is_type(types, "array"):
            if item_schema := schema.get("items"):
                logger.debug("yield array item", item_schema=item_schema)
                yield item_schema
                yield from _sub_schemas(item_schema)

            if prefix_items := schema.get("prefixItems"):
                for item_schema in prefix_items:
                    logger.debug("yield array prefixItems", item_schema=item_schema)
                    yield item_schema
                    yield from _sub_schemas(item_schema)
        # object schema type
        case {"properties": props}:
            yield schema
            yield from _sub_schemas(props)
        # any other actual schema that has a 'type' key. At this point, it cannot
        # be a container, as these have been handled before.
        case {"type": Sequence()} | {"$ref": str()}:
            logger.debug("yield schema/ref", schema=schema)
            yield schema
        case {"oneOf": nested} | {"allOf": nested} | {"anyOf": nested}:
            for child in nested:
                yield from _sub_schemas(child)
        case MutableMapping():
            for nested in schema.values():
                if isinstance(nested, MutableMapping):
                    yield from _sub_schemas(nested)
        case _:
            logger.debug("not yielding", schema=schema)


def _inline_ref_with_siblings[Schema: MutableMapping](
    prop_schema: Schema, components
) -> Schema:
    # $refs should not have siblings other than "summary" or "description"
    # https://quobix.com/vacuum/rules/schemas/oas3-no-ref-siblings/
    #
    # inline the ref if it does
    match prop_schema:
        case {"$ref": ref, **siblings} if set(siblings) - {
            "summary",
            "description",
        }:
            ref_name = ref.replace("#/components/schemas/", "")
            del prop_schema["$ref"]
            prop_schema.update(components[ref_name] | siblings)

    return prop_schema


def _cleanup_ref_title[Schema: MutableMapping](
    prop_schema: Schema, components
) -> Schema:
    # cleanup the python import path from schema titles
    match prop_schema:
        case {"title": title} if "openbeheer." in title:
            new = "[".join(t.split(".")[-1] for t in title.split("["))
            prop_schema["title"] = new
    return prop_schema


def post_process_hook(result: MutableMapping, *args, **kwargs):  # noqa: C901
    parameter_objects = (
        param["schema"]
        for path in result["paths"].values()
        for operation in path.values()
        for param in operation.get("parameters", [])
    )

    schema_objects = result.get("components", {}).get("schemas", {})
    if not schema_objects:
        logger.debug("no OAS Schema Objects!")

    for schema in chain(parameter_objects, _sub_schemas(schema_objects)):
        _cleanup_ref_title(schema, schema_objects)
        _inline_ref_with_siblings(schema, schema_objects)

    return result
