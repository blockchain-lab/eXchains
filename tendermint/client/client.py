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


class Client(Process):
	def __init__(self, address='localhost', port=46657, data_file='data.csv', time_interval=900):
		'''Initialize client with provided parameters, generate keys'''
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
			"method": 'broadcast_tx_commit',
			"params": [base64.b64encode(binarystring).decode('ascii')],
			"jsonrpc": "2.0",
			"id": "not_important"
		}).encode())

		result = urlopen(request).read().decode()
		print(result)

	def run(self):
		'''Main loop of the client, sends data retrieved from the file to the ABCI server'''
		self.register_to_abci()

		minPerBlock = 5
		clientOffset = 1440 # minutes in one day
		dayOffset = 720

		powSignificance = pow(10, 7)
		powUnit = "wh"

		consumptionSum = 0
		productionSum = 0
		prevConsumptionSum = 0
		prevProductionSum = 0

		# make each client start on different day
		for i in range(0, randint(0, 25)):
			for j in range(0, clientOffset):
				self.data_file.readline()

		# make clients start with noon data
		for i in range(0, dayOffset):
			self.data_file.readline()

		counter = 1
		try:
			while True:
				msg = tx.Transaction()
				msg.usage.contract_uuid = self.uuid.bytes
				msg.usage.timestamp = int(time.time())
				
				

				# need to sum, as data is only per minute
				for minute in range(0, minPerBlock):
					row = self.data_file.readline()
					#int(float(self.data[counter].split(';')[3].replace(',', '.')) * pow(10, 7))
					consumptionSum += int(float(row.split(';')[3].replace(",", ".")) * powSignificance)
					productionSum += int(float(row.split(';')[4].replace(",", ".")) * powSignificance)
				msg.usage.consumption = prevConsumptionSum
				msg.usage.production = prevProductionSum

				msg.usage.prediction_consumption['t+1'] = consumptionSum
				msg.usage.prediction_production['t+1'] = productionSum

				# TODO not indexed talk about what todo
				# consFlex = {randint(6, 9): 100, randint(3, 5): 50, randint(2, 9): -100} # Consumption flexibility options for coming block
				# prodFlex = {randint(2, 5): 200, randint(2, 9): -100}
				msg.usage.consumption_flexibility[0] = 0
				msg.usage.production_flexibility[2] = 500

				msg.usage.default_consumption_price = 10
				msg.usage.default_production_price = 1

				payload = self.uuid.bytes + \
						  msg.usage.timestamp.to_bytes(8, byteorder='big') + \
						  msg.usage.consumption.to_bytes(8, byteorder='big') + \
						  msg.usage.production.to_bytes(8, byteorder='big')
				msg.usage.signature = self.priv_key.sign(payload)
				print(msg)
				data = msg.SerializeToString()
				self.send_request(data)

				prevConsumptionSum = consumptionSum
				prevProductionSum = productionSum

				consumptionSum = 0
				productionSum = 0

				if self.time_interval == 0:
					input()
				else:
					time.sleep(self.time_interval)

				counter += 1
		except KeyboardInterrupt:
			print('\nExiting\n')


if __name__ == '__main__':
	n = 1 
	if len(sys.argv) == 2:
		n = int(sys.argv[1])

	for x in range(n):
		c = Client(time_interval=6)
		if c.time_interval == 0:
			c.run()
		else:
			c.start()
