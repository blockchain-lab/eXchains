# Simple read() method around a bytearray


class BytesBuffer:

	def __init__(self, b):
		self.buf = b
		self.readCount = 0

	def count(self):
		return self.readCount

	def reset_count(self):
		self.readCount = 0

	def size(self):
		return len(self.buf)

	def peek(self):
		return self.buf[0]

	def write(self, b):
		# b should be castable to byte array
		self.buf += bytearray(b)

	def read(self, n):
		if len(self.buf) < n:
			print("reader err: buf less than n")
			# TODO: exception
			return
		self.readCount += n
		r = self.buf[:n]
		self.buf = self.buf[n:]
		return r
