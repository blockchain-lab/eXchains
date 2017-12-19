from enum import Enum
import operator

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
                print("Oooeh adding a thing from the list")
                self.addorder(orders)

    def getbidlist(self):
        return self.bidList

    def getasklist(self):
        return self.askList

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

    def __repr__(self):
        return "uuid: {}, orderid: {}, volume: {}, price: {}".format(self.uuid, self.orderId, self.volume, self.price)


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
        return "uuid: {}, orderid: {}, volume: {}, price: {}".format(self.uuid, self.orderId, self.volume, self.price)


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
        return "uuid: {}, orderid: {}, volume: {}, price: {}".format(self.uuid, self.orderId, self.volume, self.price)


class Trades:
    transactions = []

    def addtransaction(self, transaction):
        self.transactions.append(transaction)

    def printtrades(self):
        for transaction in self.transactions:
            print("ID: {}, Type: {}, Energy: {}, Price: {}".format(transaction.ID, transaction.type, transaction.energy, transaction.price))


class OrderType(Enum):
    ASK = 1
    BID = 2


class Transaction:
    def __init__(self, uuid, orderid, ordertype: OrderType, volume, price):
        self.ID = uuid
        self.orderId = orderid
        self.orderType = ordertype
        self.volume = volume
        self.price = price

    def __repr__(self):
        return "ID: {}, Type: {}, Energy: {}, Price: {}".format(self.ID, self.orderId,self.orderType, self.volume,self.price)

class Matcher:
    def match(self,orderbook: OrderBook):
        askList = sorted(orderbook.getasklist(), key=operator.attrgetter('price', 'volume'), reverse=True)
        bidList = sorted(orderbook.getbidlist(), key=operator.attrgetter('price', 'volume'), reverse=False)



        previousprice = 0;
        while len(askList) != 0 and len(bidList) != 0 and askList[0].price > bidList[0].price:
            # The top orders orders for a certain price point will always be full filled
            # This is to encourage offering at prices that are good for the market
            if (previousprice!=askList[0].price and previousprice != bidList[0].price):
                volume = min(askList[0].volume, bidList[0].volume)
                print("New matching round, price will be: {}".format((askList[0].price+bidList[0].price)/2))
                print(bidList[0])
                print(askList[0])
                if askList[0].volume == volume:
                    askList.pop(0)
                else:
                    askList[0].volume -= volume
                    print(askList[0])

                if bidList[0].volume == volume:
                    askList.pop(0)
                else:
                    bidList[0].volume -= volume
                    print(bidList[0])


        print("No matches can be made anymore")