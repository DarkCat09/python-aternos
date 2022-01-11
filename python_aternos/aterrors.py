class AternosError(Exception):
	pass

class AternosCredentialsError(AternosError):
	pass

class AternosServerStartError(AternosError):
	pass

class AternosIOError(AternosError):
	pass

class CloudflareError(AternosError):
	pass
