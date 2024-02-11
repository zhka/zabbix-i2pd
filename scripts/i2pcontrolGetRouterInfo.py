#!/usr/bin/env python3
###############################################################
#                                                             #
#  Script for get i2p stats via i2pcontrol protocol           #
#  Konstantin A Zhuravlev aka ZhuKoV <zhukov@zhukov.int.ru>   #
#                                                             #
###############################################################

# I2pcontrol address and port (default: 127.0.0.1:7650)
address = '127.0.0.1'
port = 7650
# Authentication password (default: itoopie)
password = 'itoopie'
# TLS
tls = True
insecure = True # If i2pcontrol use self-signed certificate

###############################################################
import sys
import json
import http.client
import ssl

DEBUG = False

class i2pconnect:
	def __init__(self, i2pcontrol_host, i2pcontrol_port, tls=True, insecure=True):
		if tls:
			if insecure:
				self.connection = http.client.HTTPSConnection(i2pcontrol_host, i2pcontrol_port, context = ssl._create_unverified_context())
			else:
				http.client.HTTPSConnection(i2pcontrol_host, i2pcontrol_port)
		else:
			self.connection = http.client.HTTPConnection(i2pcontrol_host, i2pcontrol_port)
		self.connection.connect()
		if DEBUG:
			self.connection.debuglevel = 1

	def login(self, password):
		self.connection.request('POST', '/',
		"{\"id\":1,\"method\":\"Authenticate\",\"params\":{\"API\":1,\"Password\":\"%s\"},\"jsonrpc\":\"2.0\"}" % (password),
		{'Content-Type': 'application/json' })
		response = self.connection.getresponse()
		result = json.loads(response.read())
		if DEBUG:
			print(json.dumps(result, indent=4, sort_keys=True))
		if result['result']['API'] != 1:
			raise APIError('Mismatched i2pcontrol version')
		token = result['result']['Token']
		self.auth_token = token

	def _request(self, method, params):
		if self.auth_token == '':
			raise APIError('No authenticate')
		data = {'id':1, 'jsonrpc': '2.0'}
		data['method'] = method
		data['params'] = params
		data['params']['Token'] = self.auth_token
		self.connection.request('POST', '/', json.dumps(data),
				{'Content-Type': 'application/json' })
		response = self.connection.getresponse()
		result = json.loads(response.read())
		if DEBUG:
			print(json.dumps(result, indent=4, sort_keys=True))
		return result

	def echo(self, echostr=''):
		return self._request('Echo', {'Echo': echostr})

	def getRouterInfo(self):
		return self._request('RouterInfo', 
			{
			'i2p.router.status':'',
			'i2p.router.uptime':'',
			'i2p.router.version':'',
			'i2p.router.net.bw.inbound.15s':'',
			'i2p.router.net.bw.outbound.15s':'',
			'i2p.router.net.total.received.bytes':'',
			'i2p.router.net.total.sent.bytes':'',
			'i2p.router.net.status':'',
			'i2p.router.net.tunnels.participating':'',
			'i2p.router.net.tunnels.successrate':'',
			'i2p.router.netdb.activepeers':'',
			'i2p.router.netdb.knownpeers':''
			})


####################################################################

i2p = i2pconnect(address, port, tls, insecure)
i2p.login(password)
routerInfo = i2p.getRouterInfo()
print(json.dumps(routerInfo['result'], indent=4, sort_keys=True))
