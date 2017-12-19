class ClientReport(object):
    def __init__(self, uuid, timestamp, defaultConsPrice, defaultProdsPrice, consumption, production, predictedCons, predictedProd, consFlex, prodFlex):
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

    def printMessage(self):
        print("Message UUID: {}, timestamp: {}, defaultConsPrice: {}, defaultProdsPrice: {}, consumption: {}, production: {}, predictedCons: {}, predictedProd: {}, consFlex: {}, prodFlex: {}".format(self.uuid, self.timestamp, self.defaultConsPrice, self.defaultProdsPrice, self.consumption, self.production, self.predictedCons, self.predictedProd, self.consFlex, self.prodFlex))
