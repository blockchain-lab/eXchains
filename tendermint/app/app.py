import sys

from abci.wire import hex2bytes, decode_big_endian, encode_big_endian
from abci.server import ABCIServer
from abci.abci_application import ABCIApplication

if __name__ == '__main__':
	l = len(sys.argv)
	if l == 1:
		port = 46658
	elif l == 2:
		port = int(sys.argv[1])
	else:
		print("too many arguments")
		quit()

	app = ABCIApplication()
	server = ABCIServer(app, port)
	server.main_loop()
