import MatchMaker


class ClientReport:
    def __init__(self, uuid, timestamp, defaultConsPrice, defaultProdsPrice, consumption, production, predictedCons,
                 predictedProd, consFlex, prodFlex):
        self.uuid = uuid
        self.timestamp = timestamp
        self.defaultConsPrice = defaultConsPrice
        self.defaultProdsPrice = defaultProdsPrice
        self.consumption = consumption
        self.production = production
        self.predictedCons = predictedCons
        self.predictedProd = predictedProd
        self.consFlex = consFlex
        self.prodFlex = prodFlex

    def __repr__(self):
        return "\nMessage UUID: {}, timestamp: {}, defaultConsPrice: {}, defaultProdsPrice: {}, consumption: {}, " \
               "production: {}, predictedCons: {}, predictedProd: {}, consFlex: {}, prodFlex: {}" \
               .format(self.uuid, self.timestamp, self.defaultConsPrice, self.defaultProdsPrice, self.consumption,
                       self.production, self.predictedCons, self.predictedProd, self.consFlex, self.prodFlex)

    def reportToAskOrders(self):
        askOrders = []
        orderID = 0

        askOrders.append(MatchMaker.Ask(self.uuid, orderID, self.predictedCons["t+1"], self.defaultConsPrice, self.timestamp))
        orderID += 1

        maxFlex = self.predictedCons["t+1"];

        for price, volume in self.consFlex.items():
            if volume > 0:
                askOrders.append(MatchMaker.Ask(self.uuid, orderID, volume, price, self.timestamp))
                orderID += 1

        for price, volume in self.prodFlex.items():
            if volume < 0:
                maxFlex += volume
                if maxFlex < 0:
                    break
                askOrders.append(MatchMaker.Ask(self.uuid, orderID, volume, price, self.timestamp))
                orderID += 1

        return askOrders

    def reportToBidOrders(self):
        bidOrders = []
        orderID = 0

        bidOrders.append(MatchMaker.Bid(self.uuid, orderID, self.predictedProd["t+1"], self.defaultProdsPrice, self.timestamp))
        orderID += 1

        maxFlex = self.predictedProd["t+1"];

        for price, volume in self.prodFlex.items():
            if volume > 0:
                bidOrders.append(MatchMaker.Bid(self.uuid, orderID, volume, price, self.timestamp))
                orderID += 1

        for price, volume in self.consFlex.items():
            if volume < 0:
                maxFlex += volume
                if maxFlex < 0:
                    break
                bidOrders.append(MatchMaker.Bid(self.uuid, orderID, volume, price, self.timestamp))
                orderID += 1

        return bidOrders
