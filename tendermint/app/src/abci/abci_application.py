from .types_pb2 import Response, RequestEcho, RequestFlush, RequestInfo, RequestSetOption, RequestDeliverTx, \
	RequestCheckTx, RequestCommit, RequestQuery, RequestInitChain, RequestBeginBlock, RequestEndBlock


class ABCIApplication:

	def __init__(self):
		self.last_block_app_hash = b''
		self.last_block_height = 0

	def on_echo(self, msg: RequestEcho):
		print('onEcho(message=' + msg.message + ')')
		res = Response()
		res.echo.message = msg.message
		return res

	def on_flush(self, msg: RequestFlush):
		print('onFlush()')
		res = Response()
		res.flush.SetInParent()
		return res

	def on_info(self, msg: RequestInfo):
		print('onInfo(version=' + msg.version + ')')
		res = Response()
		res.info.data = ""
		res.info.version = "1.0.0"
		res.info.last_block_height = self.last_block_height
		res.info.last_block_app_hash = self.last_block_app_hash
		return res

	def on_set_option(self, msg: RequestSetOption):
		print('onSetOption(key=' + msg.key + ',value=' + msg.value + ')')
		res = Response()
		res.set_option.log = ''
		return res

	def on_deliver_tx(self, msg: RequestDeliverTx):
		print('onDeliverTx(tx=', msg.tx, ')')
		res = Response()
		res.deliver_tx.code = 0
		# res.deliver_tx.SetInParent()
		return res

	def on_check_tx(self, msg: RequestCheckTx):
		print('onCheckTx(tx=', msg.tx, ')')
		res = Response()
		res.check_tx.code = 0
		# res.check_tx.SetInParent()
		return res

	def on_commit(self, msg: RequestCommit):
		print('onCommit()')
		res = Response()
		res.commit.code = 0
		return res

	def on_query(self, msg: RequestQuery):
		print('onQuery(...)')
		res = Response()
		res.query.code = 0
		return res

	def on_init_chain(self, msg: RequestInitChain):
		print('onInitChain(...)')
		res = Response()
		res.init_chain.SetInParent()
		return res

	def on_begin_block(self, msg: RequestBeginBlock):
		print('onBeginBlock(...)')
		res = Response()
		res.begin_block.SetInParent()
		# make sure we don't want to define something else here ;)
		self.last_block_app_hash = msg.hash

		return res

	def on_end_block(self, msg: RequestEndBlock):
		print('onEndBlock(height=' + str(msg.height) + ')')
		res = Response()
		res.end_block.SetInParent()

		self.last_block_height = msg.height
		return res
