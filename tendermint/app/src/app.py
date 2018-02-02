import sys
from abci.types_pb2 import RequestCheckTx, Response, RequestDeliverTx, RequestQuery
from abci.server import ABCIServer
from abci.abci_application import ABCIApplication
from transaction_pb2 import Transaction
import ed25519
from MatchMaker import Matcher, OrderBook
from MatchMaker import Transaction as Trade
from ClientReport import ClientReport
import uuid
import time
import json
from google.protobuf import json_format
import operator
import random
import os
from hashlib import sha256
import balance

from multiprocessing import Manager

signed_types = ['new_contract', 'usage', 'close_contract']
COLLECTING_MODE = 0
BALANCING_MODE = 1


class EnergyMarketApplication(ABCIApplication):

	def __init__(self, address=os.environ.get("TENDERMINT_HOST", "tendermint"), port=46657):
		super().__init__()
		self.address = address
		self.port = port
		# in seconds
		self.balancing_interval = 30
		self.last_balance_timestamp = int(time.time())

		self.debug.update({
			"protocol": False,
			"signing": False,
			"check_tx": False,
			"deliver_tx": False,
			"messages": False
		})

		self.current_node_id = None

		self.state = {
			"contracts": {},
			"balance": {
				"round": 0,
				"mode": COLLECTING_MODE
			}
		}
		self.pending_state = {
			"contracts": {},
			"balance": {
				"round": 0,
				"mode": COLLECTING_MODE
			}
		}

		self.checked_txs_hashes = []

		self.last_trade_list = []

		# messages pending from current onDeliverTx
		self.pending_changes = []

		self.multiprocessing_manager = Manager()
		self.multiprocessing_que = self.multiprocessing_manager.Queue()
		self.balancer = balance.Balancer(self.address, self.port, self.multiprocessing_que)
		self.balancer.start()

	def check_signature(self, transaction_type, transaction):
		payload = None

		signature = transaction.signature
		public_key = None
		if transaction_type == 'new_contract':
			public_key = transaction.public_key
			payload = transaction.uuid + int(transaction.timestamp).to_bytes(8, 'big') + transaction.public_key

		if transaction_type == 'usage':
			public_key = bytes.fromhex(self.pending_state["contracts"][self.bytes_to_string_uuid(transaction.contract_uuid)]["public_key"])
			transaction.signature = bytes(0)
			payload = transaction.SerializeToString()

		if transaction_type == 'close_contract':
			public_key = bytes.fromhex(self.state["contracts"][self.bytes_to_string_uuid(transaction.uuid)]["public_key"])
			transaction.signature = bytes(0)
			payload = transaction.SerializeToString() 

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
			if self.bytes_to_string_uuid(transaction.usage.contract_uuid) not in self.pending_state["contracts"] or self.state["balance"]["mode"] != COLLECTING_MODE:
				res = Response()
				res.check_tx.code = 401
				return res

			self.pending_state["contracts"][self.bytes_to_string_uuid(transaction.usage.contract_uuid)]["consumption"] = transaction.usage.consumption
			self.pending_state["contracts"][self.bytes_to_string_uuid(transaction.usage.contract_uuid)]["production"] = transaction.usage.production

		elif transaction.HasField('close_contract'):
			if self.bytes_to_string_uuid(transaction.close_contract.uuid) not in self.state['contracts']:
				res = Response()
				res.check_tx.code = 401
				return res

		elif transaction.HasField('balance_start'):
			if self.state["balance"]["mode"] != COLLECTING_MODE or transaction.balance_start.round_number != self.state["balance"]["round"]:
				self.log("onCheckBalanceStart: Reject invalid mode")
				res = Response()
				res.check_tx.code = 401
				return res
			if self.debug['check_tx']:
				self.log("onCheckBalanceStart: Accept")
			self.checked_txs_hashes.append(sha256(msg.tx).hexdigest())

		elif transaction.HasField('balance'):
			if self.state["balance"]["mode"] != BALANCING_MODE or transaction.balance.round_number != self.state["balance"]["round"]:
				self.log("onCheckBalance: Reject invalid mode")
				res = Response()
				res.check_tx.code = 401
				return res
			else:
				for (received_trade, trade) in zip(transaction.balance.trades, self.last_trade_list):
					attributes = operator.attrgetter('uuid', 'order_id', 'order_type', 'volume', 'price')
					new_trade = Trade(*attributes(received_trade))
					if new_trade != trade:
						self.log("onCheckBalance: Reject invalid trade")
						res = Response()
						res.check_tx.code = 401
						return res
			if self.debug['check_tx']:
				self.log("onCheckBalance: Accept")
			self.checked_txs_hashes.append(sha256(msg.tx).hexdigest())

		elif transaction.HasField('balance_end'):
			if self.state["balance"]["mode"] != BALANCING_MODE or transaction.balance_end.round_number != self.state["balance"]["round"]:
				self.log("onCheckBalanceEnd: Reject invalid mode")
				res = Response()
				res.check_tx.code = 401
				return res
			if self.debug['check_tx']:
				self.log("onCheckBalanceEnd: Accept")
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

		if transaction_type == 'balance_start' or transaction_type == 'balance':
			h = sha256(msg.tx).hexdigest()
			if h not in self.checked_txs_hashes:
				print(transaction_type, 'ignored', h)
				res = Response()
				res.deliver_tx.code = 0
				return res
			else:
				self.checked_txs_hashes.remove(h)

		if transaction.HasField('new_contract'):
			self.state["contracts"][self.bytes_to_string_uuid(transaction.new_contract.uuid)] = {
				"public_key": transaction.new_contract.public_key.hex(),
				"consumption": 0,
				"production": 0,
				"prediction_consumption": {},
				"prediction_production": {},
				"consumption_flexibility": {},
				"production_flexibility": {},
				"default_consumption_price": 0,
				"default_production_price": 0,
				"is_used": False
			}

		# self.contract[transaction.new_contract.uuid] = transaction.new_contract.public_key
		elif transaction.HasField('usage'):
			contract_uuid = self.bytes_to_string_uuid(transaction.usage.contract_uuid)
			# We need to have the maps in dictionary format.
			usage = json_format.MessageToDict(transaction.usage, False, True)

			self.state["contracts"][contract_uuid]["consumption"] = int(transaction.usage.consumption)
			self.state["contracts"][contract_uuid]["production"] = int(transaction.usage.production)

			self.state["contracts"][contract_uuid]["prediction_consumption"] = dict([time, int(value)] for time, value in usage["prediction_consumption"].items())
			self.state["contracts"][contract_uuid]["prediction_production"] = dict([time, int(value)] for time, value in usage["prediction_production"].items())

			self.state["contracts"][contract_uuid]["consumption_flexibility"] = dict([int(price), int(amount)] for price, amount in usage["consumption_flexibility"].items())
			self.state["contracts"][contract_uuid]["production_flexibility"] = dict([int(price), int(amount)] for price, amount in usage["production_flexibility"].items())

			self.state["contracts"][contract_uuid]["default_consumption_price"] = int(usage["default_consumption_price"])
			self.state["contracts"][contract_uuid]["default_production_price"] = int(usage["default_production_price"])

			self.state['contracts'][contract_uuid]['is_used'] = True

		elif transaction.HasField('close_contract'):
			uuid = self.bytes_to_string_uuid(transaction.close_contract.uuid)
			del(self.state['contracts'][uuid])

		elif transaction.HasField('balance_start'):
			if self.state["balance"]["mode"] == COLLECTING_MODE:
				if self.debug['deliver_tx']:
					self.log("onBalanceStart")
				self.select_node()
				self.state["balance"]["mode"] = BALANCING_MODE
				self.run_balance()
				self.multiprocessing_que.put(["balance_start", self.last_trade_list])
				if self.public_key == self.current_node_id:
					self.pending_changes.append("balance")

		elif transaction.HasField('balance'):
			if self.debug['deliver_tx']:
				self.log("onBalance")
			if self.public_key == self.current_node_id:
				self.pending_changes.append("balance_end")

		elif transaction.HasField('balance_end'):
			if self.debug['deliver_tx']:
				self.log("onBalanceEnd")

			self.state["balance"]["round"] += 1

			self.multiprocessing_que.put(["balance_end", self.state["balance"]["round"]])

			self.state["balance"]["mode"] = COLLECTING_MODE
			self.last_balance_timestamp = int(time.time())
		
		else:
			res = Response()
			res.deliver_tx.code = 400
			return res

		res = Response()
		res.deliver_tx.code = 0

		type_tag = res.deliver_tx.tags.add()
		type_tag.key = 'type'
		type_tag.value_string = transaction_type

		return res

	def on_end_block(self, msg):
		self.pending_state = self.state.copy()
		return super().on_end_block(msg)

	def on_commit(self, msg):
		for msg in self.pending_changes:
			self.multiprocessing_que.put(['message', msg])
		self.pending_changes = []

		return super().on_commit(msg)

	def select_node(self):
		random.seed(self.last_block_app_hash)
		self.current_node_id = random.choice(self.validators)
		if self.public_key == self.current_node_id:
			print("Node {} is responsible for balancing".format(self.name))

	def run_balance(self):
		orders = OrderBook()
		for client_uuid in self.state['contracts']:
			if self.state['contracts'][client_uuid]['is_used']:
				client_report = ClientReport(client_uuid, \
											int(time.time()), \
											self.state['contracts'][client_uuid]['default_consumption_price'], \
											self.state['contracts'][client_uuid]['default_production_price'], \
											self.state['contracts'][client_uuid]['consumption'], \
											self.state['contracts'][client_uuid]['production'], \
											self.state['contracts'][client_uuid]['prediction_consumption'], \
											self.state['contracts'][client_uuid]['prediction_production'], \
											self.state['contracts'][client_uuid]['consumption_flexibility'], \
											self.state['contracts'][client_uuid]['production_flexibility'])
				orders.add_order(client_report.reportToAskOrders())
				orders.add_order(client_report.reportToBidOrders())
		
		matcher = Matcher(uuid.uuid4())
		self.last_trade_list = matcher.match(orders)
		# print(self.last_trade_list)

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
