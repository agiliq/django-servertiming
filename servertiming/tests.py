from django.test import TestCase

from .middleware import ServerTimingMiddleware


class ServerTimingMiddlewareTest(TestCase):
    def setUp(self):
        self.middleware = ServerTimingMiddleware(get_response=lambda request: {})

    def test_should_add_server_timing_header(self):
        with self.settings(DEBUG=True):
            self.assertTrue(self.middleware.should_add_server_timing_header())

        with self.settings(DEBUG=False):
            self.assertFalse(self.middleware.should_add_server_timing_header())

        with self.settings(DEBUG=True, SERVER_TIMING=False):
            self.assertFalse(self.middleware.should_add_server_timing_header())

        with self.settings(DEBUG=False, SERVER_TIMING=True):
            self.assertTrue(self.middleware.should_add_server_timing_header())

    def test_headers(self):
        with self.settings(SERVER_TIMING=True, DEBUG=True,):
            middleware = ServerTimingMiddleware(get_response=lambda request: {})
            response = middleware({})
            self.assertTrue("Server-Timing" in response)
