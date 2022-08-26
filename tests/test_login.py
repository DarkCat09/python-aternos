import unittest

from python_aternos import Client

AUTH_USER = 'world35g'
AUTH_PSWD = 'world35g'
AUTH_MD5 = '0efdb2cd6b36d5e54d0e3c161e567a4e'


class TestLogin(unittest.TestCase):

    def test_md5(self) -> None:

        self.assertEqual(
            Client.md5encode(AUTH_PSWD),
            AUTH_MD5
        )

    def test_auth(self) -> None:

        at = Client.from_hashed(AUTH_USER, AUTH_MD5)
        self.assertIsNotNone(at)

    def test_servers(self) -> None:

        at = Client.from_hashed(
            AUTH_USER, AUTH_MD5
        )

        srvs = len(
            at.list_servers(
                cache=False
            )
        )
        self.assertTrue(srvs > 0)


if __name__ == '__main__':
    unittest.main()
