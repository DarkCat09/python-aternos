from typing import Final


class AternosError(Exception):

    """Common error class"""


class CloudflareError(AternosError):

    """Raised when the parser is unable
    to bypass Cloudflare protection"""


class CredentialsError(AternosError):

    """Raised when a session cookie is empty
    which means incorrect credentials"""


class TokenError(AternosError):

    """Raised when the parser is unable
    to extract Aternos ajax token"""


class ServerError(AternosError):

    """Common class for server errors

    :param reason: Code which contains error reason
    :type reason: str
    :param message: Error message, defaults to ''
    :type message: str, optional
    """

    def __init__(self, reason: str, message: str = '') -> None:

        self.reason = reason
        super().__init__(message)


class ServerStartError(AternosError):

    """Raised when Aternos can not start Minecraft server

    :param reason: Code which contains error reason
    :type reason: str
    """

    MESSAGE: Final = 'Unable to start server, code: {}'
    reason_msg = {

        'eula':
            'EULA was not accepted. '
            'Use start(accepteula=True)',

        'already': 'Server is already running',
        'wrongversion': 'Incorrect software version installed',

        'file':
            'File server is unavailbale, '
            'view https://status.aternos.gmbh',

        'size': 'Available storage size limit (4 GB) was reached'
    }

    def __init__(self, reason: str) -> None:

        super().__init__(
            reason,
            self.reason_msg.get(
                reason, self.MESSAGE.format(reason)
            )
        )


class FileError(AternosError):

    """Raised when trying to execute a disallowed
    by Aternos file operation"""


class PermissionError(AternosError):

    """Raised when trying to execute a disallowed command,
    usually because of shared access rights"""
