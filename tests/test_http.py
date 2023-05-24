#!/usr/bin/env python3

import unittest

from python_aternos import Client
from tests import mock


class TestHttp(unittest.TestCase):

    def test_basic(self) -> None:
        with mock.mock:
            Client().login('test', '')
            # no exception = ok

    def test_servers(self) -> None:
        with mock.mock:
            at = Client()
            at.login('test', '')
            srvs = at.account.list_servers(cache=False)
            self.assertTrue(srvs)

    def test_status(self) -> None:
        with mock.mock:
            at = Client()
            at.login('test', '')
            srv = at.account.list_servers(cache=False)[0]
            self.assertEqual(
                srv.subdomain,
                'world35v',
            )
            self.assertEqual(
                srv.is_java,
                True,
            )


if __name__ == '__main__':
    unittest.main()
