from openbeheer.types import ZGWError


def format_related_resource_error(
    field_name: str, error: ZGWError, index: int
) -> ZGWError:
    if not hasattr(error, "invalid_params") or not isinstance(
        error.invalid_params, list
    ):
        return error

    for invalid_param in error.invalid_params:
        invalid_param.name = ".".join([field_name, str(index), invalid_param.name])

    return error
