import ClientReport
import MatchMaker


class blockchain:

    def __init__(self, uuid, clients, parrent):
        self.uuid = uuid
        self.clients = clients
        self.parrent = parrent
        self.orderBook = MatchMaker.OrderBook()
        self.reportsRecieved = 0
        self.round = 0

    def endOffRound(self):
        matcher = MatchMaker.Matcher(self.uuid)

        print("\n#### END OF ROUND {}  FOR CLUSTER {} ####".format(self.round, self.uuid))
        print("Order book:", self.orderBook.getasklist() + self.orderBook.getbidlist())

        tradeBook = matcher.match(self.orderBook)
        print("Trade book:", tradeBook)


        print("Remaining Order book:", self.orderBook.getasklist() + self.orderBook.getbidlist())
        new_book = matcher.merge(self.orderBook)
        print("Merged Order", new_book.getasklist(), new_book.getbidlist())

        self.orderBook = MatchMaker.OrderBook()
        self.reportsRecieved = 0
        self.round += 1

        return new_book

    # Used for lowest lvl clusters
    def addClientreport(self, report):
        self.reportsRecieved += 1
        self.orderBook.add_order(report.reportToAskOrders())
        self.orderBook.add_order(report.reportToBidOrders())

        # Is done by the test script

        # if self.reportsRecieved == self.clients:
        #     self.endOffRound()

    # Used for mid/ high lvl clusters
    def addOrderBook(self, orderbook):
        self.orderBook.add_order(orderbook.getasklist())
        self.orderBook.add_order(orderbook.getbidlist())

        # Is done by the test script.

        # if self.reportsRecieved == self.clients:
        #     self.endOffRound()
