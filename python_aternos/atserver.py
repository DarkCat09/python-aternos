import lxml.html
import aterrors

class AternosServer:

	def __init__(self, servid, atconn):

		self.servid = servid
		self.atconn = atconn

		servreq = self._atserver_request(
			'https://aternos.org/server',
			self.atconn.REQGET
		)
		servtree = lxml.html.fromstring(servreq.content)

		servinfo = servtree.xpath(
			'//div[@class="server-bottom-info server-info"]' + \
			'/div[@class="server-info-container"]' + \
			'/div[@class="server-info-box"]' + \
			'/div[@class="server-info-box-body"]' + \
			'/div[@class="server-info-box-value"]/span'
		)
		self._address = servinfo[0].text
		self._software = servinfo[1].text
		self._version = servinfo[2].text

		self.atconn.get_token(servreq.content)
		self.atconn.generate_sec()

	def start(self, accepteula=True):

		startreq = self._atserver_request(
			'https://aternos.org/panel/ajax/start.php',
			self.atconn.REQGET, sendtoken=True
		)
		startresult = startreq.json()

		if startresult['success']:
			return
		
		error = startresult['error']
		if error == 'eula' and accepteula:
			self.eula()
		elif error == 'eula':
			raise aterrors.AternosServerStartError(
				'EULA was not accepted. Use start(accepteula=True)'
			)
		elif error == 'already':
			raise aterrors.AternosServerStartError(
				'Server is already running'
			)
		else:
			raise aterrors.AternosServerStartError(
				f'Unable to start server. Code: {error}'
			)

	def stop(self):

		self._atserver_request(
			'https://aternos.org/panel/ajax/stop.php',
			self.atconn.REQGET, sendtoken=True
		)

	def cancel(self):

		self._atserver_request(
			'https://aternos.org/panel/ajax/cancel.php',
			self.atconn.REQGET, sendtoken=True
		)

	def restart(self):

		self._atserver_request(
			'https://aternos.org/panel/ajax/restart.php',
			self.atconn.REQGET, sendtoken=True
		)

	def eula(self):

		self._atserver_request(
			'https://aternos.org/panel/ajax/eula.php',
			self.atconn.REQGET, sendtoken=True
		)

	def _atserver_request(
		self, url, method, params=None,
		data=None, headers=None, sendtoken=False):

		return self.atconn.request_cloudflare(
			url=url, method=method,
			params=params, data=data,
			headers=headers,
			reqcookies={
				'ATERNOS_SERVER': self.servid
			},
			sendtoken=sendtoken
		)

	@property
	def address(self):
		return self._address

	@property
	def software(self):
		return self._software
	
	@property
	def version(self):
		return self._version
