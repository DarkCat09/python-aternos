"""Contains a function for hashing"""

import hashlib


def md5encode(passwd: str) -> str:
    """Encodes the given string with MD5

    Args:
        passwd (str): String to encode

    Returns:
        Hexdigest hash of the string in lowercase
    """

    encoded = hashlib.md5(passwd.encode('utf-8'))
    return encoded.hexdigest().lower()
