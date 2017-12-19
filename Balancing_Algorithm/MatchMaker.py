class OrderBook():
    Asks = []
    Bids = []

    


class Bid:
    uuid = 0
    orderId = 0
    volume =0
    price = 0

    def __init__(self, uuid, orderid, volume, price):
        self.uuid = uuid
        self.orderId = orderid
        self.volume = volume
        self.price = price


class Ask:
    uuid = 0
    orderId = 0
    volume =0
    price = 0

    def __init__(self, uuid, orderid, volume, price):
        self.uuid = uuid
        self.orderId = orderid
        self.volume = volume
        self.price = price
