class AternosError(Exception):
	pass

class CloudflareError(AternosError):
	pass

class CredentialsError(AternosError):
	pass

class ServerError(AternosError):
	pass

class FileError(AternosError):
	pass
