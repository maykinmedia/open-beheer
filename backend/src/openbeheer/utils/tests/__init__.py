from django.test import TestCase as _TestCase, tag

from maykin_common.vcr import VCRMixin as _VCRMixin
from rest_framework.test import APITestCase as _APITestCase
from vcr.cassette import Cassette


@tag("vcr")
class VCRMixin(_VCRMixin):
    def _get_vcr_kwargs(self, **kwargs):
        """In order to keep diffs small and easily scanable, this filters some headers
        that aren't particularly interesting for our behaviours.

        Applied before the maykin_common once and whatever kwargs you pass in.
        """

        def delete_response_headers(response):
            for header in [
                "Content-Security-Policy",  # we're not a browser
                "Date",  # use git log if you need this
                "Server",  # don't care about server, just what's served
            ]:
                response["headers"].pop(header, None)
            return response

        return {
            "filter_headers": [
                "Authorization",  # don't store tokens
                "User-Agent",  # Don't store requests version
            ],
            "before_record_response": delete_response_headers,
        } | super()._get_vcr_kwargs(**kwargs)


class VCRAPITestCase(VCRMixin, _APITestCase):
    """A DRF ``APITestCase`` with the ``VCRMixin`` and a ``vcr`` tag.

    Use this for testing DRF views that talk to the HTTP backends.
    """

    cassette: Cassette | None = None


class VCRTestCase(VCRMixin, _TestCase):
    """A DRF ``APITestCase`` with the ``VCRMixin`` and a ``vcr`` tag.

    Use this for testing DRF views that talk to the HTTP backends.
    """

    cassette: Cassette | None = None
