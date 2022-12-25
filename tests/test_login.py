#!/usr/bin/env python3

import unittest
from typing import Optional

from python_aternos import Client
from tests import files


class TestLogin(unittest.TestCase):

    def setUp(self) -> None:

        credentials = files.read_sample('login_pswd.txt')

        if len(credentials) < 2:
            self.skipTest(
                'File "login_pswd.txt" '
                'has incorrect format!'
            )

        self.user = credentials[0]
        self.pswd = credentials[1]

        self.at: Optional[Client] = None

    def test_auth(self) -> None:

        self.at = Client.from_hashed(self.user, self.pswd)
        self.assertIsNotNone(self.at)

    def test_servers(self) -> None:

        if self.at is None:
            self.at = Client.from_hashed(
                self.user, self.pswd
            )

        srvs = len(
            self.at.list_servers(
                cache=False
            )
        )
        self.assertTrue(srvs > 0)

    def test_logout(self) -> None:

        if self.at is None:
            self.at = Client.from_hashed(
                self.user, self.pswd
            )

        self.at.logout()


if __name__ == '__main__':
    unittest.main()
