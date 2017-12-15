#!/usr/bin/env python3
from urllib import request
import json
import sys
import ed25519 as ecdsa
import time
import uuid

class Client:
	def __init__(self, address='localhost', port=46657):
		self.uuid = uuid.uuid4()
		open('uuid', 'wb').write(self.uuid.bytes)

		self.address = address
		self.port = port
		self.priv_key, self.public_key = ecdsa.create_keypair()

		# optional storage of keys
		#open("private_key","wb").write(self.priv_key.to_bytes())

		with open(sys.argv[1], 'r') as data:
			self.data = data.readlines()

	def register_to_abci(self):
		#send public key and UUID
		pass

	def run(self):
		counter = 0
		try:
			while True:
				msg = {}
				msg['UUID'] = self.uuid
				msg['Timestamp'] = int(time.time())
				msg['Consumption'] = self.data[counter][3]
				msg['Production'] = self.data[counter][4]

				# kinda ugly way to generate stuff to sign
				payload = bytes(str(msg['UUID']) + str(msg['Timestamp']) + str(msg['Consumption']) + str(msg['Production']), encoding='UTF-8')
				msg['Signature'] = self.priv_key.sign(payload, encoding='base64')
				
				# sending, must be changed
				# with request.urlopen('http://{}:{}/broadcast_tx_async?tx={}'.format(self.address, self.port, json.dumps(msg))) as response:	        
				# 	print(response.read(300))
				
				# signature verification, should be on server side only
				try:
					self.public_key.verify(msg['Signature'], payload, encoding="base64")
					print('Signature ok')
				except ecdsa.BadSignatureError as e:
					print('NOPE')
				

				input()
				counter += 1
		except KeyboardInterrupt:
			print('\nExiting\n')

if __name__ == '__main__':
	client = Client()
	client.run()
