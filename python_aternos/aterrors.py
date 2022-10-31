"""Exception classes"""

from typing import Final


class AternosError(Exception):

    """Common error class"""


class CloudflareError(AternosError):

    """Raised when the parser is unable
    to bypass Cloudflare protection"""


class CredentialsError(AternosError):

    """Raised when a session cookie is empty
    which means incorrect credentials"""


class TwoFactorAuthError(CredentialsError):

    """Raised if 2FA is enabled,
    but code was not passed to a login function"""


class TokenError(AternosError):

    """Raised when the parser is unable
    to extract Aternos ajax token"""


class ServerError(AternosError):

    """Common class for server errors"""

    def __init__(self, reason: str, message: str = '') -> None:
        """Common class for server errors

        Args:
            reason (str): Code which contains error reason
            message (str, optional): Error message
        """

        self.reason = reason
        super().__init__(message)


class ServerStartError(AternosError):

    """Raised when Aternos can not start Minecraft server"""

    MESSAGE: Final = 'Unable to start server, code: {}'
    reason_msg = {

        'eula':
            'EULA was not accepted. '
            'Use start(accepteula=True)',

        'already': 'Server has already started',
        'wrongversion': 'Incorrect software version installed',

        'file':
            'File server is unavailbale, '
            'view https://status.aternos.gmbh',

        'size': 'Available storage size limit (4 GB) has been reached'
    }

    def __init__(self, reason: str) -> None:
        """Raised when Aternos
        can not start Minecraft server

        Args:
            reason (str):
                Code which contains error reason
        """

        super().__init__(
            reason,
            self.reason_msg.get(
                reason,
                self.MESSAGE.format(reason)
            )
        )


class FileError(AternosError):

    """Raised when trying to execute a disallowed
    by Aternos file operation"""


# PermissionError is a built-in,
# so this exception called AternosPermissionError
class AternosPermissionError(AternosError):

    """Raised when trying to execute a disallowed command,
    usually because of shared access rights"""
