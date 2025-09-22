from string import ascii_lowercase

from django.test import SimpleTestCase

import msgspec
from hypothesis import given, strategies as st

from .. import camelize


def field_names():
    "Snake case field names"
    return st.lists(
        st.text(alphabet=ascii_lowercase, min_size=1, max_size=60),
        min_size=1,
    ).map("_".join)


def expanded():
    "_expand. ... field names"
    return st.lists(field_names(), min_size=1).map(
        lambda parts: "_expand." + ".".join(parts)
    )


class CamelizeTests(SimpleTestCase):
    @given(field_names() | expanded())
    def test_it_retains_its_length_modulo_underscore(self, field_name: str):
        camel = camelize(field_name)
        # first char can be an underscore
        org_length = sum((s != "_" for s in field_name[1:]), start=1)
        assert len(camel) == org_length

    @given(field_names())
    def test_it_does_the_same_as_msgspec_camel_renaming(self, field_name: str):
        # use it as an int field
        MyStruct = msgspec.defstruct("MyStruct", [(field_name, int)], rename="camel")  # noqa: N806

        # round trip through msgspec
        my_struct: dict = msgspec.json.decode(msgspec.json.encode(MyStruct(123)))

        camel = camelize(field_name)

        assert my_struct[camel] == 123

    @given(expanded())
    def test_expanded_fields_startwith__expand(self, expand: str):
        camel = camelize(expand)
        assert camel.startswith("_expand.")

    @given(st.lists(field_names(), min_size=1))
    def test_camelizing_a_expanded_fieldname_is_the_same_as_concatation_of_camelized_parts(
        self, parts: str
    ):
        assert camelize("_expand." + ".".join(parts)) == "_expand." + ".".join(
            map(camelize, parts)
        )
