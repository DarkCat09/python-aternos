import unittest
from typing import Optional

from python_aternos import Client

AUTH_USER = 'world35g'
AUTH_PSWD = 'world35g'
AUTH_MD5 = '0efdb2cd6b36d5e54d0e3c161e567a4e'


class TestLogin(unittest.TestCase):

    def setUp(self) -> None:

        self.at: Optional[Client] = None

    def test_md5(self) -> None:

        self.assertEqual(
            Client.md5encode(AUTH_PSWD),
            AUTH_MD5
        )

    def test_auth(self) -> None:

        self.at = Client.from_hashed(AUTH_USER, AUTH_MD5)
        self.assertIsNotNone(self.at)

    def test_servers(self) -> None:

        if self.at is None:
            self.at = Client.from_hashed(
                AUTH_USER, AUTH_MD5
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
                AUTH_USER, AUTH_MD5
            )

        self.at.logout()


if __name__ == '__main__':
    unittest.main()
