from .types_pb2 import ResponseInfo, RequestInfo, Response, RequestFlush


class ABCIApplication:

    def __init__(self):
        self.blockHash = b''
        self.blockHeight = 0

    def info(self, msg: RequestInfo):
        print('onInfo(version=' + msg.version + ')')
        res = Response()
        res.info.data = ""
        res.info.version = "1.0.0"
        return res

    def flush(self, msg: RequestFlush):
        print('onFlush()')
