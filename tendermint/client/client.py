#!/usr/bin/env python3
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import ed25519 as ecdsa
import time
import uuid
import transaction_pb2 as tx
import base64
import json

class Client:
	def __init__(self, address='localhost', port=46657, data_file='data.csv', time_interval=900):
		'''Initialize client with provided parameters, generate keys'''
		self.uuid = uuid.uuid4()
		# optional storage of the uuid
		# open('uuid', 'wb').write(self.uuid.bytes)

		self.address = address
		self.port = port
		self.data_file = data_file
		self.time_interval = time_interval
		
		self.priv_key, self.public_key = ecdsa.create_keypair()
		# optional storage of keys
		#open("private_key","wb").write(self.priv_key.to_bytes())

		with open(self.data_file, 'r') as data:
			self.data = data.readlines()

	def register_to_abci(self):
		msg = tx.Transaction()
		msg.new_contract.uuid = self.uuid.bytes
		msg.new_contract.timestamp = int(time.time())
		msg.new_contract.public_key = self.public_key.to_bytes()
		payload = self.uuid.bytes + \
				  msg.new_contract.timestamp.to_bytes(8, byteorder='big') + \
				  self.public_key.to_bytes()
		msg.new_contract.signature = self.priv_key.sign(payload)
		data = msg.SerializeToString()

		self.send_request(data)

	def send_request(self, binarystring):
		url = 'http://{}:{}/'.format(self.address, self.port)  # Set destination URL here
		
		request = Request(url, json.dumps({
			"method": 'broadcast_tx_sync',
			"params": [base64.b64encode(binarystring).decode('ascii')],
			"jsonrpc": "2.0",
			"id": "not_important"
		}).encode())
		
		result = urlopen(request).read().decode()
		print(result)

	def run(self):
		'''Main loop of the client, sends data retrieved from the file to the ABCI server'''
		self.register_to_abci()
		counter = 1
		try:
			while True:
				msg = tx.Transaction()
				msg.usage.contract_uuid = self.uuid.bytes
				msg.usage.timestamp = int(time.time())
				msg.usage.consumption = int(float(self.data[counter].split(';')[3].replace(',', '.')) * pow(10, 7))
				msg.usage.production = int(float(self.data[counter].split(';')[4].replace(',', '.')) * pow(10, 7))
		

				msg.usage.prediction_consumption['t+1'] = 10
				msg.usage.prediction_consumption['t+2'] = 20
				msg.usage.prediction_production['t+1'] = 3
				msg.usage.consumption_flexibility[0] = 0
				msg.usage.production_flexibility[2] = 500

				payload = self.uuid.bytes + \
						  msg.usage.timestamp.to_bytes(8, byteorder='big') + \
						  msg.usage.consumption.to_bytes(8, byteorder='big') + \
						  msg.usage.production.to_bytes(8, byteorder='big')
				msg.usage.signature = self.priv_key.sign(payload)
				data = msg.SerializeToString()
				self.send_request(data)
				
				if self.time_interval == 0:
					input()
				else:
					time.sleep(self.time_interval)

				counter += 1
		except KeyboardInterrupt:
			print('\nExiting\n')

if __name__ == '__main__':
	client = Client(time_interval=0)
	client.run()
