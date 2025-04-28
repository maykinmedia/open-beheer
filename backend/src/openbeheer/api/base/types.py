from typing import TypedDict, Optional


class FieldOption(TypedDict):
    """
    Close to @maykin-ui/admin-ui Option for use in datagrid.
    """

    label: str
    value: str

class Paginator(TypedDict):
    """
    Close to @maykin-ui/admin-ui PaginatorProps for use in datagrid.
    """
    count: int
    page: int
    page_size: int

class TypedField(TypedDict):
    """
    Close to @maykin-ui/admin-ui TypedField for use in datagrid.
    """

    options: Optional[list[FieldOption]]
    filterable: bool
    name: str
    type: str
    filter_value: Optional[str]