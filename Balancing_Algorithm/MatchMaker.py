class OrderBook:
    askList = []
    bidList = []

    def addorder(self, order):
        if isinstance(order, Ask):
            print("You've added an Ask order ")
            self.askList.append(order)
        elif isinstance(order, Bid):
            print("You've added an Bid order " )
            self.bidList.append(order)
        elif isinstance(order, list):
            for orders in order[:]:
                print("Oooeh addind a thing from the list")
                self.addorder(self, orders)

    def getbidlist(self):
        return self.askList

    def getaskist(self):
        return self.bidList


class Ask:
    uuid: int
    orderId: int
    volume: int
    price: int

    def __init__(self, uuid, orderid, volume, price):
        self.uuid = uuid
        self.orderId = orderid
        self.volume = volume
        self.price = price

    def __repr__(self):
        return "\nuuid: {}, orderid: {}, volume: {}, price: {}".format(self.uuid, self.orderId, self.volume, self.price)

class Bid:
    uuid: int
    orderId: int
    volume: int
    price: int

    def __init__(self, uuid, orderid, volume, price):
        self.uuid = uuid
        self.orderId = orderid
        self.volume = volume
        self.price = price

    def __repr__(self):
        return "\nuuid: {}, orderid: {}, volume: {}, price: {}".format(self.uuid, self.orderId, self.volume, self.price)