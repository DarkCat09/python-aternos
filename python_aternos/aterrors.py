class AternosError(Exception):

	"""Common error class"""	

class CloudflareError(AternosError):
	
	"""Raised when the parser is unable to bypass Cloudflare protection"""	

class CredentialsError(AternosError):
	
	"""Raised when a session cookie is empty which means incorrect credentials"""

class TokenError(AternosError):
	
	"""Raised when the parser is unable to extract Aternos ajax token"""

class ServerError(AternosError):
	
	"""Common class for server errors"""

class ServerEulaError(ServerError):

	"""Raised when trying to start without confirming Mojang EULA"""

class ServerRunningError(ServerError):

	"""Raised when trying to start already running server"""

class ServerSoftwareError(ServerError):

	"""Raised when Aternos notifies about incorrect software version"""

class ServerStorageError(ServerError):

	"""Raised when Aternos notifies about violation of storage limits (4 GB for now)"""

class FileError(AternosError):
	
	"""Raised when trying to execute a disallowed by Aternos file operation"""
