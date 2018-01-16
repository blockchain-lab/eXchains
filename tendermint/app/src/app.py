import sys

from abci.types_pb2 import RequestCheckTx, Response, RequestDeliverTx, RequestQuery
from abci.server import ABCIServer
from abci.abci_application import ABCIApplication
from transaction_pb2 import Transaction
import ed25519
from MatchMaker import Matcher, OrderBook
from ClientReport import ClientReport
import uuid
import time
import json
import base64
from multiprocessing import Process
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from google.protobuf import json_format

signed_types = ['new_contract', 'usage']

class EnergyMarketApplication(ABCIApplication):

	def __init__(self, address='tendermint', port=46657):
		super().__init__()
		self.address = address
		self.port = port
		# in seconds
		self.balancing_interval = 20

		self.debug.update({
			"protocol": False,
			"signing": False,
			"check_tx": False,
			"deliver_tx": False,
			"messages": False
		})

		self.state = {
			"contracts": {}
		}
		self.pending_state = {
			"contracts": {}
		}

		self.orderBook = MatchMaker.OrderBook()
		self.tradeBook = []

		self.balancer = Process(target=self.balancing_timer)
		self.balancer.start()

	def balancing_timer(self):
		while True:
			time.sleep(self.balancing_interval)

			url = 'http://{}:{}/'.format(self.address, self.port)  # Set destination URL here
			message = Transaction()
			message.balance.timestamp = int(time.time())
			binarystring = message.SerializeToString()

			request = Request(url, json.dumps({
				"method": 'broadcast_tx_sync',
				"params": [base64.b64encode(binarystring).decode('ascii')],
				"jsonrpc": "2.0",
				"id": "not_important"
			}).encode())

			result = urlopen(request).read().decode()

	def check_signature(self, transaction_type, transaction):
		payload = None
		# if !transaction.HasField('signature'):
		# 	return False

		signature = transaction.signature
		public_key = None
		if transaction_type == 'new_contract':
			public_key = transaction.public_key
			payload = transaction.uuid + int(transaction.timestamp).to_bytes(8, 'big') + transaction.public_key

		if transaction_type == 'usage':
			public_key = bytes.fromhex(self.pending_state["contracts"][self.bytes_to_string_uuid(transaction.contract_uuid)]["public_key"])
			payload = transaction.contract_uuid + \
				int(transaction.timestamp).to_bytes(8, 'big') + \
				int(transaction.consumption).to_bytes(8, 'big') + \
				int(transaction.production).to_bytes(8, 'big')

		if self.debug['signing']:
			print(transaction_type, public_key, payload, transaction)

		if payload is None:
			return False

		try:
			verify = ed25519.VerifyingKey(public_key)
			verify.verify(signature, payload)
		except AssertionError:
			return False
		return True

	# 00000000-0000-0000-0000-000000000000
	def bytes_to_string_uuid(self, uuid_in_bytes):
		uuid_str = uuid_in_bytes.hex()
		uuid_str = uuid_str[0:8] + '-' + uuid_str[8:12] + '-' + uuid_str[12:16] + '-' + uuid_str[16:20] + '-' + uuid_str[20:]
		return uuid_str

	def on_check_tx(self, msg: RequestCheckTx):
		tx = msg.tx
		try:
			transaction = Transaction.FromString(tx)
		except Exception as e:
			print('check_tx decode error:', e)
			res = Response()
			res.check_tx.code = 400
			return res
		if self.debug['check_tx']:
			print(transaction)

		descriptor, value = transaction.ListFields()[0]
		transaction_type = descriptor.name
		if signed_types.count(transaction_type) > 0:
			if not self.check_signature(transaction_type, value):
				res = Response()
				res.check_tx.code = 401
				return res

		if transaction_type == 'new_contract':
			if self.bytes_to_string_uuid(transaction.new_contract.uuid) in self.pending_state["contracts"]:
				res = Response()
				res.check_tx.code = 401
				return res

			self.pending_state["contracts"][self.bytes_to_string_uuid(value.uuid)] = {
				"public_key": value.public_key.hex(),
				"consumption": 0,
				"production": 0
			}

		# todo: verify contractor_signature
		elif transaction.HasField('usage'):
			if self.bytes_to_string_uuid(transaction.usage.contract_uuid) not in self.pending_state["contracts"]:
				res = Response()
				res.check_tx.code = 401
				return res

			self.pending_state["contracts"][self.bytes_to_string_uuid(transaction.usage.contract_uuid)]["consumption"] = transaction.usage.consumption
			self.pending_state["contracts"][self.bytes_to_string_uuid(transaction.usage.contract_uuid)]["production"] = transaction.usage.production

		elif transaction.HasField('balance_start'):
			pass
		elif transaction.HasField('balance'):
			pass
		elif transaction.HasField('balance_end'):
			pass

		else:
			res = Response()
			res.check_tx.code = 400
			return res

		res = Response()
		res.check_tx.code = 0
		return res

	def on_deliver_tx(self, msg: RequestDeliverTx):
		tx = msg.tx
		try:
			transaction = Transaction.FromString(tx)
		except:
			res = Response()
			res.deliver_tx.code = 400
			return res

		if self.debug['deliver_tx']:
			print(transaction)

		descriptor, value = transaction.ListFields()[0]
		transaction_type = descriptor.name

		if transaction.HasField('new_contract'):
			self.state["contracts"][self.bytes_to_string_uuid(transaction.new_contract.uuid)] = {
				"public_key": transaction.new_contract.public_key.hex(),
				"consumption": 0,
				"production": 0,
				"prediction_consumption": {},
				"prediction_production": {},
				"consumption_flexibility": {},
				"production_flexibility": {}
			}

		# self.contract[transaction.new_contract.uuid] = transaction.new_contract.public_key
		if transaction.HasField('usage'):
			contract_uuid = self.bytes_to_string_uuid(transaction.usage.contract_uuid)
			# We need to have the maps in dictionary format.
			usage = json_format.MessageToDict(transaction.usage, False, True)
			self.state["contracts"][contract_uuid]["consumption"] = transaction.usage.consumption
			self.state["contracts"][contract_uuid]["production"] = transaction.usage.production

			self.state["contracts"][contract_uuid]["prediction_consumption"] = usage["prediction_consumption"]
			self.state["contracts"][contract_uuid]["prediction_production"] = usage["prediction_production"]

			self.state["contracts"][contract_uuid]["consumption_flexibility"] = usage["consumption_flexibility"]
			self.state["contracts"][contract_uuid]["production_flexibility"] = usage["production_flexibility"]

		if transaction.HasField('balance_start'):
			# start balancing in different process
			self.balancer = Process(target=self.balance)
			self.balancer.start()

		if transaction.HasField('balance'):
			pass

		if transaction.HasField('balance_end'):
			pass

		res = Response()
		res.deliver_tx.code = 0

		type_tag = res.deliver_tx.tags.add()
		type_tag.key = 'type'
		type_tag.value_string = transaction_type

		return res

	def balance(self):

		self.orderBook = OrderBook()

		for client_uuid in self.state['contracts']:
			client_report = ClientReport(client_uuid, int(time.time()),
										self.state['contracts'][client_uuid]['default_consumption_price'], # not implemented?
										self.state['contracts'][client_uuid]['default_production_price'], # not implemented?
										self.state['contracts'][client_uuid]['consumption'],
										self.state['contracts'][client_uuid]['production'],
										self.state['contracts'][client_uuid]['prediction_consumption'],
										self.state['contracts'][client_uuid]['prediction_production'],
										self.state['contracts'][client_uuid]['consumption_flexibility'],
										self.state['contracts'][client_uuid]['production_flexibility'])
			# print(client_report)
			orders.add_order(client_report.reportToAskOrders())
			orders.add_order(client_report.reportToBidOrders())

		print("Order book:", self.orderBook.getasklist() + self.orderBook.getbidlist())

		matcher = Matcher(uuid.uuid4())
		self.tradeBook.clear()
		self.tradeBook = matcher.match(orders)

		print("Trade book:", self.tradeBook)
		print("Remaining Order book:", self.orderBook.getasklist() + self.orderBook.getbidlist())

		new_book = self.matcher.merge(self.orderBook)
		print("Merged Order", new_book.getasklist(), new_book.getbidlist())



		# store result
		# if chosen one propose block


	def on_end_block(self, msg):
		self.pending_state = self.state.copy()
		return super().on_end_block(msg)

	def on_query(self, msg: RequestQuery):
		if self.debug['messages']:
			print('onQuery(path=' + msg.path + ', data=' + str(msg.data) + ')')
		res = Response()

		if msg.path == 'state':
			res.query.key = bytes('state', 'utf8')
			res.query.value = bytes(json.dumps(self.state), 'utf8')

		res.query.code = 0
		return res


if __name__ == '__main__':
	l = len(sys.argv)
	if l == 1:
		port = 46658
	elif l == 2:
		port = int(sys.argv[1])
	else:
		print("too many arguments")
		quit()

	app = EnergyMarketApplication()
	server = ABCIServer(app, port)
	server.main_loop()
