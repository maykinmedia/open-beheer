from typing import Callable, Protocol

from openbeheer.clients import objecttypen_client, ztc_client


class TestMixinProtocol(Protocol):
    def setUp(self) -> None: ...

    def addCleanup(self, callable: Callable) -> None: ...  # noqa: N802


class ClearCacheMixin:
    def setUp(self: TestMixinProtocol):
        super().setUp()

        objecttypen_client.cache_clear()
        ztc_client.cache_clear()

        self.addCleanup(objecttypen_client.cache_clear)
        self.addCleanup(ztc_client.cache_clear)
