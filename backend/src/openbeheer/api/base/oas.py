from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from openapi_parser import parse
from openapi_parser.specification import Operation, Property, Content, Parameter
from rest_framework.request import Request
from rest_framework.response import Response
from zgw_consumers.models import Service

from .types import TypedField

CACHE_TIMEOUT = 86400  # 24 hours


class OASOperationNotFound(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


def get_fields_from_oas(
        request: Request, service: Service, method: str, path: str
) -> list[TypedField]:
    """
    Retrieves all fields from the properties defined in the OAS result schema
    for a specific endpoint. Caching is used to improve performance.

    Args:
        request: The HTTP request object.
        service: The service for which the OpenAPI spec is being fetched.
        method: The HTTP method (e.g., 'GET', 'POST').
        path: The path of the API endpoint.

    Returns:
        A list of TypedField objects corresponding to the OAS properties.
    """

    return [
        convert_oas_property_to_field(p, request, service, method, path)
        for p in get_oas_result_properties(service, method, path)
    ]


def convert_oas_property_to_field(
        prop: Property, request: Request, service: Service, method: str, path: str
) -> TypedField:
    """
    Converts a single OAS property to a TypedField definition.

    Args:
        prop: The OAS property to convert.
        request: The HTTP request object.
        service: The service associated with the OpenAPI spec.
        method: The HTTP method (e.g., 'GET', 'POST').
        path: The path of the API endpoint.

    Returns:
        A TypedField object corresponding to the OAS property.
    """
    name = prop.name
    schema = prop.schema
    supported_params = get_oas_parameter_names(service, method, path)

    return {
        "options": [
            {
                "label": o.replace("_", " ").replace("-", " "),
                "value": o
            }
            for o in schema.enum
        ] if schema.enum else None,
        "filterable": name in supported_params,
        "name": name,
        "type": schema.type.name.lower(),
        "filter_value": request.query_params.get(
            name) if name in supported_params else None,
    }


# Schema resolving


def get_oas_result_properties(
        service: Service, method: str, path: str
) -> list[Property]:
    """
    Retrieve the list of properties from the returned object(s)s in the OAS response
    schema.

    Args:
        service: The service for which the OpenAPI spec is being fetched.
        method: The HTTP method (e.g., 'GET', 'POST').
        path: The path of the API endpoint.

    Returns:
        A list of Property objects defined in the OAS 'results' object.
    """
    is_detail = "{" in path  # If a placeholder is used, we assume it's the uuid.
    properties = get_oas_properties(service, method, path)

    if is_detail:
        return properties
    return next(
        p.schema.items.properties for p in properties if p.name == "results"
    )


def get_oas_properties(service: Service, method: str, path: str) -> list[Property]:
    """
    Retrieve the list of top-level properties from the OAS response schema.

    Args:
        service: The service for which the OpenAPI spec is being fetched.
        method: The HTTP method (e.g., 'GET', 'POST').
        path: The path of the API endpoint.

    Returns:
        A list of top-level Property objects from the OAS response schema.
    """
    return get_oas_content(service, method, path).schema.properties


def get_oas_content(service: Service, method: str, path: str) -> Content:
    """
    Retrieve the first content block from the OAS 200 response.

    Args:
        service: The service for which the OpenAPI spec is being fetched.
        method: The HTTP method (e.g., 'GET', 'POST').
        path: The path of the API endpoint.

    Returns:
        The Content object corresponding to the 200 response of the OAS operation.
    """
    return next(r for r in get_oas_response(service, method, path).content)


def get_oas_parameter_names(service: Service, method: str, path: str) -> list[str]:
    """
    Return the names of all parameters defined for the given operation in the OAS.

    Args:
        service: The service for which the OpenAPI spec is being fetched.
        method: The HTTP method (e.g., 'GET', 'POST').
        path: The path of the API endpoint.

    Returns:
        A list of parameter names defined in the OAS operation.
    """
    return [p.name for p in get_oas_parameters(service, method, path)]


def get_oas_parameters(service: Service, method: str, path: str) -> list[Parameter]:
    """
    Retrieve the list of parameters for the given operation from the OAS.

    Args:
        service: The service for which the OpenAPI spec is being fetched.
        method: The HTTP method (e.g., 'GET', 'POST').
        path: The path of the API endpoint.

    Returns:
        A list of Parameter objects defined in the OAS operation.
    """
    return get_oas_operation(service, method, path).parameters


def get_oas_response(service: Service, method: str, path: str) -> Response:
    """
    Retrieve the 200 OK response object for the specified operation.

    Args:
        service: The service for which the OpenAPI spec is being fetched.
        method: The HTTP method (e.g., 'GET', 'POST').
        path: The path of the API endpoint.

    Returns:
        The Response object corresponding to the 200 OK response in the OAS operation.
    """
    return next(
        r for r in get_oas_operation(service, method, path).responses if r.code == 200
    )


def get_oas_operation(service: Service, method: str, path: str) -> Operation:
    """
    Return the operation object from the OpenAPI specification that matches
    the given method and path.

    Args:
        service: The service for which the OpenAPI spec is being fetched.
        method: The HTTP method (e.g., 'GET', 'POST').
        path: The path of the API endpoint.

    Raises:
        OASOperationNotFound: If the operation is not found in the OAS for the given method and path.

    Returns:
        The Operation object corresponding to the specified method and path in the OAS.
    """
    spec = get_spec(service)
    paths = spec.paths

    try:
        path_match = next(
            p for p in paths if p.url == path or p.url == f"/{path.strip('/')}"
        )
        operation_match = next(
            o for o in path_match.operations if o.method.name.lower() == method.lower()
        )

        return operation_match
    except StopIteration:
        raise OASOperationNotFound(
            f"OAS does not specify the current action for {method} {path}.")


def get_spec(service: Service):
    """
    Fetches and parses the OpenAPI specification (OAS) for the given service.

    Args:
        service: The service for which the OpenAPI spec is being fetched.

    Returns:
        The parsed OpenAPI specification.

    Raises:
        ImproperlyConfigured: If no OAS URL is provided for the service.
    """
    cache_key = f"{__name__}.get_spec#{service.pk}"
    cache_value = cache.get(cache_key)

    if cache_value:
        return cache_value
    oas_url = service.oas  # POSSIBLE TODO: oas_file not supported

    if not oas_url:
        raise ImproperlyConfigured(
            f"Please specify a OAS URL for {service.label} Service.")

    spec = parse(oas_url)

    cache.set(cache_key, spec, timeout=CACHE_TIMEOUT)
    return spec
