import ClientReport
import MatchMaker


class blockchain:

    def __init__(self, uuid, parrent):
        self.uuid = uuid
        self.clients = {}
        self.parrent = parrent
        self.orderBook = MatchMaker.OrderBook()
        self.reportsRecieved = 0
        self.round = 0
        self.clientCount = 0

    def feedback(self, orderbook):
        print("Cluster {} got back this list {}".format(self.uuid , orderbook))
        #TODO verdeel terug gekomen oders over clients

    def endOffRound(self):
        matcher = MatchMaker.Matcher(self.uuid)

        print("\n#### END OF ROUND {}  FOR CLUSTER {} ####".format(self.round, self.uuid))
        print("Order book:", self.orderBook.getasklist() + self.orderBook.getbidlist())

        tradeBook = matcher.match(self.orderBook)
        print("Trade book:", tradeBook)

        print("Remaining Order book:", self.orderBook.getasklist() + self.orderBook.getbidlist())
        new_book = matcher.merge(self.orderBook)
        print("Merged Order", new_book.getasklist(), new_book.getbidlist())

        # if top cluster start sending
        if self.parrent is None:
            for uuid, client in self.clients.items():
                transactions = []
                for trade in tradeBook:
                    if trade.uuid == uuid:
                        transactions.append(trade)
                client.feedback(transactions)

        # if not top cluster send new book up
        else:
            self.parrent.addOrderBook(new_book)

        self.orderBook = MatchMaker.OrderBook()
        self.reportsRecieved = 0
        self.round += 1

        return new_book

    # Used for lowest lvl clusters
    def addClientreport(self, report):
        self.reportsRecieved += 1
        self.orderBook.add_order(report.reportToAskOrders())
        self.orderBook.add_order(report.reportToBidOrders())

        if self.reportsRecieved == len(self.clients):
            self.endOffRound()

    # Used for mid/ high lvl clusters
    def addOrderBook(self, orderbook):
        self.reportsRecieved += 1
        self.orderBook.add_order(orderbook.getasklist())
        self.orderBook.add_order(orderbook.getbidlist())

        if self.reportsRecieved == len(self.clients):
            self.endOffRound()

    def introduceClient(self, client):
        self.clientCount = self.clientCount + 1
        if client is None:
            self.clients[self.clientCount] = blockchain(self.clientCount, None)
        else:
            self.clients[client.uuid] = client

