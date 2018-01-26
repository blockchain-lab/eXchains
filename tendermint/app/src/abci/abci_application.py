from .types_pb2 import Response, RequestEcho, RequestFlush, RequestInfo, RequestSetOption, RequestDeliverTx, \
	RequestCheckTx, RequestCommit, RequestQuery, RequestInitChain, RequestBeginBlock, RequestEndBlock

from google.protobuf import json_format
import json
import base64
import binascii

class ABCIApplication:

	def __init__(self):
		self.last_block_app_hash = b''
		self.last_block_height = 0

		self.validators = []

		with open("/tendermint/priv_validator.json", "r") as f:
			dict = json.load(f)
			self.public_key = binascii.unhexlify(dict["pub_key"]["data"])
			print(self.public_key, len(self.public_key))

		self.debug = {
			"protocol": True,
			"connection": True,
			"messages": True
		}

	def on_echo(self, msg: RequestEcho):
		if self.debug['messages']:
			print('onEcho(message=' + msg.message + ')')
		res = Response()
		res.echo.message = msg.message
		return res

	def on_flush(self, msg: RequestFlush):
		if self.debug['protocol']:
			print('onFlush()')
		res = Response()
		res.flush.SetInParent()
		return res

	def on_info(self, msg: RequestInfo):
		if self.debug['messages']:
			print('onInfo(version=' + msg.version + ')')
		res = Response()
		res.info.data = ""
		res.info.version = "1.0.0"
		res.info.last_block_height = self.last_block_height
		res.info.last_block_app_hash = self.last_block_app_hash
		return res

	def on_set_option(self, msg: RequestSetOption):
		if self.debug['messages']:
			print('onSetOption(key=' + msg.key + ',value=' + msg.value + ')')
		res = Response()
		res.set_option.log = ''
		return res

	def on_deliver_tx(self, msg: RequestDeliverTx):
		if self.debug['messages']:
			print('onDeliverTx(tx=', msg.tx, ')')
		res = Response()
		res.deliver_tx.code = 0
		# res.deliver_tx.SetInParent()
		return res

	def on_check_tx(self, msg: RequestCheckTx):
		if self.debug['messages']:
			print('onCheckTx(tx=', msg.tx, ')')
		res = Response()
		res.check_tx.code = 0
		# res.check_tx.SetInParent()
		return res

	def on_commit(self, msg: RequestCommit):
		if self.debug['messages']:
			print('onCommit()')
		res = Response()
		res.commit.code = 0
		return res

	# message RequestQuery{
	#   bytes data = 1;
	#   string path = 2;
	#   int64 height = 3;
	#   bool prove = 4;
	# }
	def on_query(self, msg: RequestQuery):
		if self.debug['messages']:
			print('onQuery(path=' + msg.path + ', data=' + str(msg.data) + ')')
		res = Response()
		res.query.code = 0
		return res

	def on_init_chain(self, msg: RequestInitChain):
		if self.debug['messages']:
			print('onInitChain(...)')

		msgdict = json_format.MessageToDict(msg, False, True)
		# print(msgdict)
		self.validators = []
		for validator in msgdict["validators"]:
			key = base64.b64decode(validator["pub_key"])[1:]
			self.validators.append(key)
			print(key, len(key))

		res = Response()
		res.init_chain.SetInParent()
		return res

	def on_begin_block(self, msg: RequestBeginBlock):
		if self.debug['messages']:
			print('onBeginBlock(...)')
		res = Response()
		res.begin_block.SetInParent()
		# make sure we don't want to define something else here ;)
		self.last_block_app_hash = msg.hash

		return res

	def on_end_block(self, msg: RequestEndBlock):
		if self.debug['messages']:
			print('onEndBlock(height=' + str(msg.height) + ')')
		res = Response()
		res.end_block.SetInParent()

		self.last_block_height = msg.height
		return res
