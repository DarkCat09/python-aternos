class AternosError(Exception):

	"""Common error class"""	

class CloudflareError(AternosError):
	
	"""Raises when the parser is unable to bypass Cloudflare protection"""	

class CredentialsError(AternosError):
	
	"""Raises when a session cookie is empty which means incorrect credentials"""

class TokenError(AternosError):
	
	"""Raises when the parser is unable to extract Aternos ajax token"""

class ServerError(AternosError):
	
	"""Common class for server errors"""

class ServerEulaError(ServerError):

	"""Raises when trying to start without confirming Mojang EULA"""

class ServerRunningError(ServerError):

	"""Raises when trying to start already running server"""

class ServerSoftwareError(ServerError):

	"""Raises when Aternos notifies about incorrect software version"""

class ServerStorageError(ServerError):

	"""Raises when Aternos notifies about violation of storage limits (4 GB for now)"""

class FileError(AternosError):
	pass
