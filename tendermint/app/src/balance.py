
from app import BALANCING_MODE, COLLECTING_MODE
import time
import os
from multiprocessing import Process
from transaction_pb2 import Transaction
import base64
import json
from urllib.request import Request, urlopen


class Balancer(Process):
	def __init__(self, address=os.environ.get("TENDERMINT_HOST", "tendermint"), port=46657, que=None):
		super().__init__()
		self.address = address
		self.port = port

		self.mode = COLLECTING_MODE
		self.round = 0

		self.balancing_interval = 30
		self.last_balance_timestamp = int(time.time())

		self.que = que

		self.pending_messages = []

		self.last_trade_list = []

	def run(self):
		while True:
			while self.que.qsize() > 0:
				entry = self.que.get()
				if entry[0] == 'balance_end':
					self.mode = COLLECTING_MODE
					self.round = entry[1]
					self.last_balance_timestamp = int(time.time())
				elif entry[0] == 'balance_start':
					self.mode = BALANCING_MODE
					self.last_trade_list = entry[1]

				elif entry[0] == 'message':
					self.pending_messages.append(entry[1])

			for msg in self.pending_messages:
				self.send_message(msg)
			self.pending_messages = []

			if self.mode == COLLECTING_MODE and (int(time.time()) - self.balancing_interval) > self.last_balance_timestamp:
				self.pending_messages.append("balance_start")

			time.sleep(1)

	def send_message(self, message_type):
		url = 'http://{}:{}/'.format(self.address, self.port)  # Set destination URL here
		message = Transaction()
		method = ''

		if message_type == 'balance_start':
			method = 'broadcast_tx_sync'
			message.balance_start.timestamp = int(time.time())
			message.balance_start.round_number = self.round

		elif message_type == 'balance':
			method = 'broadcast_tx_sync'
			message.balance.timestamp = int(time.time())
			message.balance.round_number = self.round
			for trade in self.last_trade_list:
				new_trade = message.balance.trades.add()
				new_trade.uuid = trade.uuid
				new_trade.order_id = trade.order_id
				new_trade.order_type = trade.order_type
				new_trade.volume = trade.volume
				new_trade.price = trade.price

		elif message_type == 'balance_end':
			method = 'broadcast_tx_sync'
			message.balance_end.timestamp = int(time.time())
			message.balance_end.round_number = self.round

		print("Sending message: {}".format(message))
		binarystring = message.SerializeToString()
		request = Request(url, json.dumps({
			"method": method,
			"params": [base64.b64encode(binarystring).decode('ascii')],
			"jsonrpc": "2.0",
			"id": "not_important"
		}).encode())
		result = urlopen(request, None, 10)
		print(result.read().decode())

