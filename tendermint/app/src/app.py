import sys

from abci.types_pb2 import RequestCheckTx, Response, RequestDeliverTx
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


class EnergyMarketApplication(ABCIApplication):

	def __init__(self, address='tendermint', port=46657):
		super().__init__()
		self.address = address
		self.port = port
		# in seconds
		self.balancing_interval = 20
		self.debug.protocol = False;

		self.state = {
			"contracts": {}
		}
		self.pending_state = {
			"contracts": {}
		}

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

	def check_signature(self, public_key, transaction_type, transaction):
		payload = None
		# if !transaction.HasField('signature'):
		# 	return False

		signature = transaction.signature
		if transaction_type == 'new_contract':
			payload = transaction.uuid + int(transaction.timestamp).to_bytes(8, 'big') + transaction.public_key

		if transaction_type == 'usage':
			payload = transaction.contract_uuid + \
				int(transaction.timestamp).to_bytes(8, 'big') + \
				int(transaction.consumption).to_bytes(8, 'big') + \
				int(transaction.production).to_bytes(8, 'big')

		print(payload, transaction)
		if payload is None:
			return False
		
		try:
			verify = ed25519.VerifyingKey(public_key)
			verify.verify(signature, payload)
		except AssertionError:
			return False
		return True

	def on_check_tx(self, msg: RequestCheckTx):
		tx = msg.tx
		try:
			transaction = Transaction.FromString(tx)
		except Exception as e:
			print('check_tx decode error:', e)
			res = Response()
			res.check_tx.code = 400
			return res

		print(transaction)

		if transaction.HasField('new_contract'):
			if transaction.new_contract.uuid in self.pending_state["contracts"]:
				res = Response()
				res.check_tx.code = 401
				return res

			if not self.check_signature(transaction.new_contract.public_key, 'new_contract', transaction.new_contract):
				res = Response()
				res.check_tx.code = 401
				return res

			self.pending_state["contracts"][transaction.new_contract.uuid] = {
				"public_key": transaction.new_contract.public_key,
				"consumption": 0,
				"production": 0
			}

		# todo: verify contractor_signature
		elif transaction.HasField('usage'):
			if transaction.usage.contract_uuid not in self.pending_state["contracts"]:
				res = Response()
				res.check_tx.code = 401
				return res

			if not self.check_signature(self.pending_state["contracts"][transaction.usage.contract_uuid]["public_key"], 'usage', transaction.usage):
				res = Response()
				res.check_tx.code = 401
				return res
			self.pending_state["contracts"][transaction.usage.contract_uuid]["consumption"] = transaction.usage.consumption
			self.pending_state["contracts"][transaction.usage.contract_uuid]["production"] = transaction.usage.production

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

		print(transaction)

		if transaction.HasField('new_contract'):
			self.state["contracts"][transaction.new_contract.uuid] = {
				"public_key": transaction.new_contract.public_key,
				"consumption": 0,
				"production": 0,
				"prediction_consumption": {},
				"prediction_production": {},
				"consumption_flexibility": {},
				"production_flexibility": {}
			}

		# self.contract[transaction.new_contract.uuid] = transaction.new_contract.public_key
		if transaction.HasField('usage'):
			self.state["contracts"][transaction.usage.contract_uuid]["consumption"] = transaction.usage.consumption
			self.state["contracts"][transaction.usage.contract_uuid]["production"] = transaction.usage.production

			self.state["contracts"][transaction.usage.contract_uuid]["prediction_consumption"] = transaction.usage.prediction_consumption
			self.state["contracts"][transaction.usage.contract_uuid]["prediction_production"] = transaction.usage.prediction_production

			self.state["contracts"][transaction.usage.contract_uuid]["consumption_flexibility"] = transaction.usage.consumption_flexibility
			self.state["contracts"][transaction.usage.contract_uuid]["production_flexibility"] = transaction.usage.production_flexibility

		if transaction.HasField('balance_start'):
			pass

		if transaction.HasField('balance'):
			orders = OrderBook()
			print(self.state['contracts'])
			for client_uuid in self.state['contracts']:
				client_report = ClientReport(client_uuid, \
											 int(time.time()), \
											 0, \
											 0, \
											 self.state['contracts'][client_uuid]['consumption'], \
											 self.state['contracts'][client_uuid]['production'], \
											 self.state['contracts'][client_uuid]['prediction_consumption'], \
											 self.state['contracts'][client_uuid]['prediction_production'], \
											 self.state['contracts'][client_uuid]['consumption_flexibility'], \
											 self.state['contracts'][client_uuid]['production_flexibility'])
				print(client_report)
				orders.add_order(client_report.reportToAskOrders())
				orders.add_order(client_report.reportToBidOrders())
			matcher = Matcher(uuid.uuid4())
			# TODO: make some nicer prints or remove them at all
			print(orders.getbidlist(), orders.getasklist())
			matcher.match(orders)
			print(orders.getbidlist(), orders.getasklist())

		if transaction.HasField('balance_end'):
			pass

		res = Response()
		res.deliver_tx.code = 0
		return res

	def on_end_block(self, msg):
		self.pending_state = self.state.copy()
		return super().on_end_block(msg)


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
