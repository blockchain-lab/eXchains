import sys

from abci.types_pb2 import RequestCheckTx, Response, EncodingError, OK, Unauthorized, RequestDeliverTx
from abci.server import ABCIServer
from abci.abci_application import ABCIApplication
from transaction_pb2 import Transaction


class EnergyMarketApplication(ABCIApplication):

	def __init__(self):
		super().__init__()
		self.contracts = {}

	def on_check_tx(self, msg: RequestCheckTx):
		tx = msg.tx
		try:
			transaction = Transaction.FromString(tx)
		except Exception as e:
			print('check_tx decode error:', e)
			res = Response()
			res.check_tx.code = EncodingError
			return res

		print(transaction)

		if transaction.HasField('new_contract'):
			if transaction.new_contract.uuid in self.contracts:
				res = Response()
				res.check_tx.code = Unauthorized
				return res
			# todo: verify signature
			# todo: verify contractor_signature
			# self.contract[transaction.new_contract.uuid] = transaction.new_contract.public_key
		if transaction.HasField('usage'):
			if transaction.usage.contract_uuid not in self.contracts:
				res = Response()
				res.check_tx.code = Unauthorized
				return res
			# todo: verify signature

		res = Response()
		res.check_tx.code = OK
		return res

	# message
	# Transaction
	# {
	# 	oneof
	# value
	# {
	# 	TransactionUsage
	# usage = 1;
	# TransactionNewContract
	# new_contract = 2;
	# TransactionCloseContract
	# close_contract = 3;
	#
	# TransactionStartBalancing
	# balance_start = 4;
	# TransactionBalance
	# balance = 5;
	# TransactionEndBalancing
	# balance_end = 6;
	# }
	# }
	def on_deliver_tx(self, msg: RequestDeliverTx):
		tx = msg.tx
		try:
			transaction = Transaction.FromString(tx)
		except:
			res = Response()
			res.deliver_tx.code = EncodingError
			return res

		print(transaction)

		if transaction.HasField('new_contract'):
			self.contracts[transaction.new_contract.uuid] = {
				"public_key": transaction.new_contract.public_key,
				"consumption": 0,
				"production": 0
			}

		# self.contract[transaction.new_contract.uuid] = transaction.new_contract.public_key
		if transaction.HasField('usage'):
			self.contracts[transaction.usage.contract_uuid]["consumption"] += transaction.usage.consumption
			self.contracts[transaction.usage.contract_uuid]["production"] += transaction.usage.production

		res = Response()
		res.deliver_tx.code = OK
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
