#!/usr/bin/env python3
from urllib import request
import json
import sys
import ed25519 as ecdsa
import time
import uuid
import transaction_pb2 as tx

class Client:
	def __init__(self, address='localhost', port=46657):
		self.uuid = uuid.uuid4()
		# optional storage of the uuid
		# open('uuid', 'wb').write(self.uuid.bytes)

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
		counter = 1
		try:
			while True:

				msg = {}
				msg['UUID'] = str(self.uuid)
				msg['Timestamp'] = int(time.time())
				msg['Consumption'] = self.data[counter].split(';')[3]
				msg['Production'] = self.data[counter].split(';')[4]

				# kinda ugly way to generate stuff to sign
				payload = bytes(str(msg['UUID']) + str(msg['Timestamp']) + str(msg['Consumption']) + str(msg['Production']), encoding='UTF-8')
				msg['Signature'] = self.priv_key.sign(payload, encoding='base64').decode('ascii')
				#msg_json = json.dumps(msg)
				#msg_json = json.dumps('*'.join((str(self.uuid), str(int(time.time())), self.data[counter].split(';')[3], self.data[counter].split(';')[4])))
				#print(msg_json, json.dumps("chuj"))


				myurl = "http://{}:{}/broadcast_tx_async".format(self.address, self.port)
				req = request.Request(myurl)
				req.add_header('Content-Type', 'application/json; charset=utf-8')
				jsondata = json.dumps(msg)
				jsondataasbytes = jsondata.encode('utf-8')   # needs to be bytes
				req.add_header('Content-Length', len(jsondataasbytes))
				print (jsondataasbytes)

				#with request.urlopen(req, jsondataasbytes) as response:
				#	print(response.read(300))

				# msg = tx.TransactionUsage()
				# msg.contract_uuid = self.uuid.bytes
				# msg.timestamp = int(time.time())
				# msg.consumption = int(float(self.data[counter].split(';')[3].replace(',', '.')) * pow(10, 7)) 
				# msg.production = int(float(self.data[counter].split(';')[4].replace(',', '.')) * pow(10, 7)) 
				# payload = bytes(str(msg.contract_uuid) + str(msg.timestamp) + str(msg.consumption) + str(msg.production), encoding='ascii')
				# msg.signature = self.priv_key.sign(payload, encoding='base64')
				# print(msg)
				# msg_json = msg

				# sending, must be changed
				with request.urlopen('http://{}:{}/broadcast_tx_async?tx={}'.format(self.address, self.port, json.dumps("chuj"))) as response:	        
					print(response.read(300))
				
				# signature verification, should be on server side only
				#try:
				#	self.public_key.verify(msg['Signature'], payload, encoding="base64")
				#except ecdsa.BadSignatureError as e:
				#	print('NOPE')

				input()
				counter += 1
		except KeyboardInterrupt:
			print('\nExiting\n')

if __name__ == '__main__':
	client = Client()
	client.run()
