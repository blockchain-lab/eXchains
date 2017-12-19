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
                self.addorder(orders)

    def getbidlist(self):
        return self.askList

    def getaskist(self):
        return self.bidList


class Ask:
    uuid: int
    orderId: int
    volume: int
    price: int
    Asks = []
    Bids = []


class Bid:
    uuid = 0
    orderId = 0
    volume = 0
    price = 0

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

class Trades:
    transactions = []

    def addtransaction(self, transaction):
        self.transactions.append(transaction)

    def printtrades(self):
        for transaction in self.transactions:
            print("ID: {}, Type: {}, Energy: {}, Price: {}".format(transaction.ID, transaction.type, transaction.energy, transaction.price))


class Transaction:

    def __init__(self, clientID, type, energy, price):
        self.ID = clientID
        self.type = type
        self.energy = energy
        self.price = price