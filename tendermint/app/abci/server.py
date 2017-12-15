import socket
import select
import sys
import logging

from .wire import decode_varint, encode_varint, encode
from .reader import BytesBuffer
from .types_pb2 import Request

# hold the asyncronous state of a connection
# ie. we may not get enough bytes on one read to decode the message

logger = logging.getLogger(__name__)


class Connection:
	def __init__(self, fd: socket, app):
		self.fd: socket = fd
		self.app = app
		self.recBuf = BytesBuffer(bytearray())
		self.resBuf = BytesBuffer(bytearray())
		self.msgLength = 0
		self.inProgress = False  # are we in the middle of a message

	def recv(self):
		# if socket.readable():
		data = self.fd.recv(1024)
		if not data:  # what about len(data) == 0
			raise IOError("dead connection")

		self.recBuf.write(data)


# ABCI server responds to messges by calling methods on the app
class ABCIServer:

	def __init__(self, app, port=5410):
		self.app = app
		# map conn file descriptors to (app, reqBuf, resBuf, msgDecoder)
		self.appMap = {}

		self.port = port
		self.listen_backlog = 10

		self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.listener.setblocking(0)
		self.listener.bind(('', port))

		self.listener.listen(self.listen_backlog)

		self.shutdown = False

		self.read_list = [self.listener]
		self.write_list = []

		self.loopId = 1

	def handle_new_connection(self, r):
		new_fd, new_addr = r.accept()
		new_fd.setblocking(0)  # non-blocking
		self.read_list.append(new_fd)
		self.write_list.append(new_fd)
		print('new connection to', new_addr)

		self.appMap[new_fd] = Connection(new_fd, self.app)

	def handle_conn_closed(self, r):
		self.read_list.remove(r)
		self.write_list.remove(r)
		r.close()
		print("connection closed")

	def handle_recv(self, r: socket):
		#  app, recBuf, resBuf, conn
		conn = self.appMap[r]
		self.loopId += 1
		while True:
			try:
				print("recv loop", self.loopId)
				# check if we need more data first
				if conn.inProgress:
					if conn.msgLength == 0 or conn.recBuf.size() < conn.msgLength:
						conn.recv()
				else:
					if conn.recBuf.size() == 0:
						conn.recv()

				conn.inProgress = True

				# see if we have enough to get the message length
				if conn.msgLength == 0:
					ll = conn.recBuf.peek()
					if conn.recBuf.size() < 1 + ll:
						# we don't have enough bytes to read the length yet
						return
					# print("decoding msg length")
					conn.msgLength = decode_varint(conn.recBuf)

				# see if we have enough to decode the message
				if conn.recBuf.size() < conn.msgLength:
					return

				buf = conn.recBuf.read(conn.msgLength)
				req: Request = Request.FromString(buf)

				conn.msgLength = 0
				conn.inProgress = False

				print(req)
				res = None
				if req.HasField('echo'):
					res = self.app.on_echo(req.echo)
				if req.HasField('flush'):
					res = self.app.on_flush(req.flush)
				if req.HasField('info'):
					res = self.app.on_info(req.info)
				if req.HasField('set_option'):
					res = self.app.on_set_option(req.set_option)
				if req.HasField('deliver_tx'):
					res = self.app.on_deliver_tx(req.deliver_tx)
				if req.HasField('check_tx'):
					res = self.app.on_check_tx(req.check_tx)
				if req.HasField('commit'):
					res = self.app.on_commit(req.commit)
				if req.HasField('query'):
					res = self.app.on_query(req.query)
				if req.HasField('init_chain'):
					res = self.app.on_init_chain(req.init_chain)
				if req.HasField('begin_block'):
					res = self.app.on_begin_block(req.begin_block)
				if req.HasField('end_block'):
					res = self.app.on_end_block(req.end_block)

				if res is not None:
					self.write_response(conn, res)

				if res.HasField('flush'):
					self.flush(conn)
					return

			except IOError as e:
				print("IOError on reading from connection:", e)
				self.handle_conn_closed(r)
				return
			except Exception as e:
				logger.exception("error reading from connection")
				self.handle_conn_closed(r)
				return

	def flush(self, conn):
		conn.fd.send(conn.resBuf.buf)
		conn.resBuf = BytesBuffer(bytearray())

	def write_response(self, conn, res):
		print('Write', res.ByteSize(), encode_varint(res.ByteSize()), res.SerializeToString())
		header = encode_varint(res.ByteSize())
		packet = res.SerializeToString()
		conn.resBuf.write(header)
		conn.resBuf.write(packet)

	def main_loop(self):
		while not self.shutdown:
			r_list, w_list, _ = select.select(
				self.read_list, self.write_list, [], 2.5)

			for r in r_list:
				if (r == self.listener):
					try:
						self.handle_new_connection(r)
					# undo adding to read list ...
					except NameError as e:
						print("Could not connect due to NameError:", e)
					except TypeError as e:
						print("Could not connect due to TypeError:", e)
					except:
						print("Could not connect due to unexpected error:", sys.exc_info()[0])
				else:
					self.handle_recv(r)

	def handle_shutdown(self):
		for r in self.read_list:
			r.close()
		for w in self.write_list:
			try:
				w.close()
			except Exception as e:
				print(e)  # TODO: add logging
		self.shutdown = True
