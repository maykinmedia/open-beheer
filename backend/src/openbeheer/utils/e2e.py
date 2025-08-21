import re
from contextlib import asynccontextmanager

from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core.cache import cache
from django.core.servers.basehttp import ThreadedWSGIServer
from django.db import connection
from django.test.testcases import LiveServerThread, QuietWSGIRequestHandler

from playwright.async_api import async_playwright


@asynccontextmanager
async def browser_page(log_levels: list["str"] | None = None):
    if log_levels is None:
        log_levels = ["debug"]

    async with async_playwright() as p:
        launch_kwargs = {
            "headless": settings.PLAYWRIGHT_HEADLESS,
        }

        browser = await getattr(p, settings.PLAYWRIGHT_BROWSER).launch(**launch_kwargs)
        context = await browser.new_context()
        await context.tracing.start(screenshots=True, snapshots=True, sources=True)

        page = await context.new_page()
        page.on(
            "console",
            lambda message: message.type in log_levels
            and print(message.type.upper(), message),
        )

        save_trace = settings.PLAYWRIGHT_SAVE_TRACE
        try:
            yield page
            save_trace = False
        finally:
            if save_trace:
                await context.tracing.stop(path=settings.PLAYWRIGHT_TRACE_PATH)
            await browser.close()


class LiveServerThreadWithReuse(LiveServerThread):
    """Live server thread with reuse of local addresses

    Prevents "socket.error: [Errno 48] Address already in use" by reusing the address.
    """

    server_class: type[ThreadedWSGIServer]

    def _create_server(self, connections_override=None):
        return self.server_class(
            (self.host, self.port),
            QuietWSGIRequestHandler,
            allow_reuse_address=True,
            connections_override=connections_override,
        )


class PlaywrightTestCase(StaticLiveServerTestCase):
    fixtures = []
    server_thread_class = LiveServerThreadWithReuse

    @classmethod
    def get_unique_port(cls):
        """
        If the tests are run in parallel (--parallel 4), each process needs a unique port.
        The port is determined based on the database name and port setting (E2E_PORT).

        - Look at a possible number of the test database, default to 0 if none was matched.
        - Sum it with the default port and compute the unique port.
        - Returnn the unique port.
        """
        base_port = 8000

        # TODO: Find more elegand way of doing this
        db_name = connection.settings_dict["NAME"]
        match = re.search(r"\d+", db_name)
        if not match:
            return base_port

        index = int(match[0])
        return base_port + index

    @classmethod
    def setUpClass(cls):
        """
        If the tests are run in parallel (--parallel 4), each process needs a unique port.
        The port (defaults to settings.E2E_PORT) is set on the class and used when starting the test server.
        See `get_unique_port` for more information.
        """
        cls.port = cls.get_unique_port()
        super().setUpClass()

    def setUp(self):
        super().setUp()
        self.addCleanup(cache.clear)
