from .types_pb2 import Response, RequestEcho, RequestFlush, RequestInfo, RequestSetOption, RequestDeliverTx, \
	RequestCheckTx, RequestCommit, RequestQuery, RequestInitChain, RequestBeginBlock, RequestEndBlock, OK


class ABCIApplication:

	def __init__(self):
		self.blockHash = b''
		self.blockHeight = 0

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
		return res

	def on_set_option(self, msg: RequestSetOption):
		print('onSetOption(key=' + msg.key + ',value=' + msg.value + ')')
		res = Response()
		res.set_option.log = ''
		return res

	def on_deliver_tx(self, msg: RequestDeliverTx):
		print('onDeliverTx(tx=', msg.tx, ')')
		res = Response()
		res.deliver_tx.code = OK
		# res.deliver_tx.SetInParent()
		return res

	def on_check_tx(self, msg: RequestCheckTx):
		print('onCheckTx(tx=', msg.tx, ')')
		res = Response()
		res.check_tx.code = OK
		# res.check_tx.SetInParent()
		return res

	def on_commit(self, msg: RequestCommit):
		print('onCommit()')
		res = Response()
		res.commit.code = OK
		return res

	def on_query(self, msg: RequestQuery):
		print('onQuery(...)')
		res = Response()
		res.query.code = OK
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
		return res

	def on_end_block(self, msg: RequestEndBlock):
		print('onEndBlock(...)')
		res = Response()
		res.end_block.SetInParent()
		return res
