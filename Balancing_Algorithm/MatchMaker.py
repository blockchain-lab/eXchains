class OrderBook:
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


class Ask:
    uuid = 0
    orderId = 0
    volume = 0
    price = 0

    def __init__(self, uuid, orderid, volume, price):
        self.uuid = uuid
        self.orderId = orderid
        self.volume = volume
        self.price = price


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