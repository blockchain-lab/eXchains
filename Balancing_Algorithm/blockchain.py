import ClientReport
import MatchMaker


class blockchain:
    reportsRecieved = 0
    round = 0
    orderBook = MatchMaker.OrderBook()

    def __init__(self, uuid, clients, parrent):
        self.uuid = uuid
        self.clients = clients
        self.parrent = parrent

    def endOffRound(self):
        matcher = MatchMaker.Matcher(1)

        print("\n#### END OF ROUND {} ####".format(self.round))
        print("Order book:", self.orderBook.getasklist() + self.orderBook.getbidlist())
        print("Trade book:", matcher.match(self.orderBook))
        print("Order book:", self.orderBook.getasklist() + self.orderBook.getbidlist())
        new_book = matcher.merge(self.orderBook)
        print("Merged Order", new_book.getasklist(), new_book.getbidlist())

        self.orderBook = MatchMaker.OrderBook()
        self.reportsRecieved = 0
        self.round += 1

    def addClientreport(self, report):
        self.reportsRecieved += 1
        self.orderBook.add_order(report.reportToAskOrders())
        self.orderBook.add_order(report.reportToBidOrders())

        if self.reportsRecieved == self.clients:
            self.endOffRound()
