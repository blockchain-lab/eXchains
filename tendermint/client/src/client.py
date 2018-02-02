#!/usr/bin/env python3
from urllib.request import Request, urlopen
import ed25519 as ecdsa
import time
import uuid
import transaction_pb2 as tx
import base64
import json
from random import randint
from multiprocessing import Process
import sys
import os
from google.protobuf import json_format

class Client(Process):
	def __init__(self, address=os.environ.get("TENDERMINT_HOST", "tendermint"), port=46657, data_file='data.csv', time_interval=900):
		'''Client simulates behavior of a smart meter. It registers to the ABCI and then keep posting all necessary data in the transactions.'''
		super().__init__()
		self.uuid = uuid.uuid4()
		# optional storage of the uuid
		# open('uuid', 'wb').write(self.uuid.bytes)

		self.address = address
		self.port = port
		self.time_interval = time_interval

		self.priv_key, self.public_key = ecdsa.create_keypair()
		# optional storage of keys
		# open("private_key","wb").write(self.priv_key.to_bytes())

		self.data_file = open(data_file, "r")
		# skipping header
		self.data_file.readline()

	def register_to_abci(self):
		'''Method used when the client makes the first connection to the ABCI'''
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
		'''Method responsible for sending any transactions to the ABCI'''
		url = 'http://{}:{}/'.format(self.address, self.port)  # Set destination URL here

		request = Request(url, json.dumps({
			"method": 'broadcast_tx_commit',
			"params": [base64.b64encode(binarystring).decode('ascii')],
			"jsonrpc": "2.0",
			"id": "not_important"
		}).encode())

		result = urlopen(request).read()
		print(result)

	def run(self):

		time.sleep(int(os.environ.get("STARTUP_DELAY", 5)))

		'''Main loop of the client, sends data retrieved from the file to the ABCI server'''
		self.register_to_abci()

		# Variables needed for simulating the smart meter signals
		min_per_block = 5
		client_offset = 1440 # minutes in one day
		day_offset = 720
		pow_significance = pow(10, 1)

		consumption_sum = 0
		production_sum = 0
		prev_consumption_sum = 0
		prev_production_sum = 0
		consumption_percentage_to_flexibility = 0.2
		production_percentage_to_flexibility = 0.1

		# make each client start on different day
		for i in range(0, randint(0, 25)):
			for j in range(0, client_offset):
				self.data_file.readline()

		# make clients start with noon data
		for i in range(0, day_offset):
			self.data_file.readline()

		counter = 1
		try:
			while True:
				msg = tx.Transaction()
				msg.usage.contract_uuid = self.uuid.bytes
				msg.usage.timestamp = int(time.time())
				
				# need to sum, as data is only per minute
				for minute in range(0, min_per_block):
					row = self.data_file.readline()
					consumption_sum += int(float(row.split(';')[3].replace(",", ".")) * pow_significance)
					production_sum += int(float(row.split(';')[4].replace(",", ".")) * pow_significance)

				msg.usage.consumption = prev_consumption_sum
				msg.usage.production = prev_production_sum

				# Consumption prediction for coming blocks
				msg.usage.prediction_consumption['t+1'] = int(consumption_sum * (1 - consumption_percentage_to_flexibility))
				# Production prediction for coming blocks
				msg.usage.prediction_production['t+1']  = int(production_sum  * (1 - production_percentage_to_flexibility))

				# Consumption flexibility options for coming block
				msg.usage.consumption_flexibility[randint(150, 220) * 100] = int(0.2 * (consumption_sum * consumption_percentage_to_flexibility))
				msg.usage.consumption_flexibility[randint(100, 150) * 100] = int(0.3 * (consumption_sum * consumption_percentage_to_flexibility))
				msg.usage.consumption_flexibility[randint(50, 100)  * 100] = int(0.5 * (consumption_sum * consumption_percentage_to_flexibility))

				# Production flexibility options for coming block
				msg.usage.production_flexibility[randint(150, 220) * 100] = int(0.5 * (consumption_sum * production_percentage_to_flexibility))	
				msg.usage.production_flexibility[randint(100, 150) * 100] = int(0.3 * (consumption_sum * production_percentage_to_flexibility))
				msg.usage.production_flexibility[randint(50, 100)  * 100] = int(0.2 * (consumption_sum * production_percentage_to_flexibility))

				msg.usage.default_consumption_price = 22000
				msg.usage.default_production_price = 500
				msg.usage.signature = self.priv_key.sign(msg.usage.SerializeToString())

				# print("Sending message: {}".format(msg))
				data = msg.SerializeToString()
				self.send_request(data)

				prev_consumption_sum = consumption_sum
				prev_production_sum = production_sum

				consumption_sum = 0
				production_sum = 0

				# In case of no time interval, new transactions are sent by the user manually
				if self.time_interval == 0:
					input()
				else:
					time.sleep(self.time_interval)

				counter += 1

		except (KeyboardInterrupt, EOFError):
			msg = tx.Transaction()
			msg.close_contract.uuid = self.uuid.bytes
			msg.close_contract.timestamp = int(time.time())
			msg.close_contract.signature = self.priv_key.sign(msg.close_contract.SerializeToString())
			data = msg.SerializeToString()
			self.send_request(data)

			print('\nExiting\n')


if __name__ == '__main__':
	'''Execution of file creates number of clients specified as the first parameter, time interval as second'''
	n = 1
	t = 0
	if len(sys.argv) > 1:
		try:
			n = int(sys.argv[1])
			t = int(sys.argv[2])
		except ValueError:
			print('Provide correct number of clients and/or time interval')
			quit()

	for x in range(n):
		# Don't use multiple clients with manual transactions
		c = Client(time_interval=t)

		if c.time_interval == 0:
			c.run()
		else:
			c.start()
		time.sleep(1)