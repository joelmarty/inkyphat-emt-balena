import os

from unittest import TestCase, skipIf
from emt import api
from dotenv import load_dotenv, find_dotenv
import logging
import http.client

logging.basicConfig(level=logging.DEBUG)
httpclient_logger = logging.getLogger("http.client")


def httpclient_logging_patch(level=logging.DEBUG):
    """Enable HTTPConnection debug logging to the logging framework"""

    def httpclient_log(*args):
        httpclient_logger.log(level, " ".join(args))

    # mask the print() built-in in the http.client module to use
    # logging instead
    http.client.print = httpclient_log
    # enable debugging
    http.client.HTTPConnection.debuglevel = 1


@skipIf(find_dotenv('local.env') == '', reason='api credentials not found')
class TestEMTClient(TestCase):

    @classmethod
    def setUpClass(cls):
        load_dotenv(find_dotenv('local.env'))
        cls.client_id = os.getenv('EMT_CLIENT_ID')
        cls.pass_key = os.getenv('EMT_PASS_KEY')
        httpclient_logging_patch()

    def test_login(self):
        emt_client = api.EMTClient(self.client_id, self.pass_key)
        emt_client.login()
        logged_in = emt_client.is_logged_in()
        self.assertTrue(logged_in)

    def test_get_arrival_times(self):
        emt_client = api.EMTClient(self.client_id, self.pass_key)
        emt_client.login()
        arrival_times = emt_client.get_arrival_times('394', '120')
        print(arrival_times)
        self.assertEqual(arrival_times.stop_name, 'Silvano-Esperanza')
        self.assertIsNotNone(arrival_times.arrivals)
        self.assertIsNotNone(arrival_times.incident)
