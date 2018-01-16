import ClientReport
import MatchMaker


class blockchain:

    def __init__(self, uuid, parent):
        self.uuid = uuid
        self.clients = {}
        self.parrent = parent
        self.orderBook = MatchMaker.OrderBook()
        self.reportsRecieved = 0
        self.round = 0
        self.clientCount = 0
        self.tradeBook = []

        self.matcher = MatchMaker.Matcher(self.uuid)

    def feedback(self, transactions):
        trade_list = self.matcher.unmerge(self.orderBook, transactions)
        print("\nCluster {} got back from above unmerged: {}".format(self.uuid, trade_list))
        print("and internal trade list", self.tradeBook)

        for uuid, client in self.clients.items():
            transactions = []
            for trade in trade_list:
                if trade.uuid == uuid:
                    transactions.append(trade)
            for trade in self.tradeBook:
                if trade.uuid == uuid:
                    transactions.append(trade)
            client.feedback(transactions)

        self.orderBook = MatchMaker.OrderBook()
        self.reportsRecieved = 0
        self.round += 1


    def endOffRound(self):


        print("\n#### END OF ROUND {}  FOR CLUSTER {} ####".format(self.round, self.uuid))
        print("Order book:", self.orderBook.getasklist() + self.orderBook.getbidlist())
        self.tradeBook.clear()
        self.tradeBook = self.matcher.match(self.orderBook)
        print("Trade book:", self.tradeBook)

        print("Remaining Order book:", self.orderBook.getasklist() + self.orderBook.getbidlist())
        new_book = self.matcher.merge(self.orderBook)
        print("Merged Order", new_book.getasklist(), new_book.getbidlist())

        # if top cluster start sending data down
        if self.parrent is None:
            for uuid, client in self.clients.items():
                transactions = []
                for trade in self.tradeBook:
                    print("Client UUID:", uuid, "trade.uuid:", trade.uuid)
                    if trade.uuid == uuid:
                        transactions.append(trade)
                client.feedback(transactions)

        # if not top cluster send new book up
        else:
            self.parrent.addOrderBook(new_book)

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
            pass
            self.clients[self.clientCount] = blockchain(self.clientCount, None)
        else:
            self.clients[client.uuid] = client

