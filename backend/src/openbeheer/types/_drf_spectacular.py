from msgspec import field, Struct, to_builtins
from drf_spectacular.extensions import _SchemaType

class QueryParamSchema(Struct):
    in_: str = field(name="in")
    name: str
    schema: _SchemaType

    @classmethod
    def from_json_schema(cls, name: str, schema: _SchemaType) -> _SchemaType:
        query_param_schema = cls(in_="query", name=name, schema=schema)
        return to_builtins(query_param_schema)

