from datetime import date
from enum import Enum
from typing import Annotated
from unittest import TestCase

from hypothesis import assume, given, strategies as st  # noqa: F401
from msgspec import UNSET, Meta, Struct
from msgspec.json import decode, encode

from . import ztc
from ._open_beheer import camelize, ob_fields_of_type, options

ZTC_DATATYPES = [
    struct
    for name in dir(ztc)
    if (struct := getattr(ztc, name))
    and isinstance(struct, type)
    and issubclass(struct, Struct)
]

ZTC_ENUMS = [
    struct
    for name in dir(ztc)
    if (struct := getattr(ztc, name))
    and isinstance(struct, type)
    and issubclass(struct, Enum)
]


@st.composite
def ztc_struct_instances(draw):
    struct_type = draw(st.sampled_from(ZTC_DATATYPES))
    return draw(st.from_type(struct_type))


class OBFieldsTest(TestCase):
    def test_simple_field_type_example(self):
        class MyStruct(Struct):
            boolean: bool
            integer: int
            ieee_754: float
            string: Annotated[str, Meta(max_length=49)]
            text: str
            date: date

        (b, i, f, s, t, d) = ob_fields_of_type(MyStruct)
        assert b.name == "boolean"
        assert b.type == "boolean"
        assert i.name == "integer"
        assert i.type == "number"
        assert f.name == "ieee754"  # camelcased
        assert f.type == "number"
        assert s.name == "string"
        assert s.type == "string"
        assert t.name == "text"
        assert t.type == "text"
        assert d.name == "date"
        assert d.type == "date"

    @given(ztc_struct_instances())
    def test_all_fields_are_present(self, instance: Struct):
        def as_seen_by_frontend(struct) -> dict:
            """Return struct as the dict that is seen by the frontend
            This also asserts that all generated OBFields are serializable
            """
            return decode(encode(struct), type=dict)

        ob_fields = ob_fields_of_type(type(instance))

        ob_fields_as_dict = map(as_seen_by_frontend, ob_fields)
        field_names = {field["name"] for field in ob_fields_as_dict}

        instance_dict = as_seen_by_frontend(instance)
        expected_struct_attributes = set(map(camelize, instance_dict))

        assert field_names == expected_struct_attributes


class OBOptionsTest(TestCase):
    @given(enum=st.sampled_from(ZTC_ENUMS))
    def test_length(self, enum):
        "Every enum member should have an OBOption"
        ob_options = options(enum)
        assert ob_options is not UNSET
        assert len(ob_options) == len(enum)

    @given(enum=st.sampled_from(ZTC_ENUMS))
    def test_values(self, enum: type[Enum]):
        "Every OBOption.value should be a valid Enum value"
        ob_options = options(enum)

        assert ob_options is not UNSET
        for option in ob_options:
            assert option.value in enum

    def test_annotated_enum(self):
        enum_annotation = Annotated[
            ztc.VertrouwelijkheidaanduidingEnum, Meta(description="blabla")
        ]
        ob_options = options(enum_annotation)

        assert ob_options is not UNSET
        assert len(ob_options) == len(ztc.VertrouwelijkheidaanduidingEnum)
