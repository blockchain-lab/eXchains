import sys

from abci.types_pb2 import RequestCheckTx, Response, RequestDeliverTx
from abci.server import ABCIServer
from abci.abci_application import ABCIApplication
from transaction_pb2 import Transaction
import ed25519


class EnergyMarketApplication(ABCIApplication):

	def __init__(self):
		super().__init__()

		self.debug.protocol = False;

		self.state = {
			"contracts": {}
		}
		self.pending_state = {
			"contracts": {}
		}

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
			self.pending_state["contracts"][transaction.usage.contract_uuid]["consumption"] += transaction.usage.consumption
			self.pending_state["contracts"][transaction.usage.contract_uuid]["production"] += transaction.usage.production
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
				"production": 0
			}

		# self.contract[transaction.new_contract.uuid] = transaction.new_contract.public_key
		if transaction.HasField('usage'):
			self.state["contracts"][transaction.usage.contract_uuid]["consumption"] += transaction.usage.consumption
			self.state["contracts"][transaction.usage.contract_uuid]["production"] += transaction.usage.production

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
