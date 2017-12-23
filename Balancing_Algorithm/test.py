import MatchMaker
import operator

import CSVparser
import ClientReport
import datetime
import time

def clientToOrdersTest():


    uuid = 0                                    # ClientReport ID
    timestamp = str(datetime.datetime.now())    # Time stamp
    defaultConsPrice = 10                       # Default consumption price
    defaultProdsPrice = 1                       # Default production price
    consumption = 1000                          # Actual consumption last block
    production = 100                            # Actual production last block
    predictedCons = {"t+1": 1000, "t+2": 1000}  # Consumption prediction for coming blocks
    predictedProd = {"t+1": 100, "t+2": 1000}   # Production prediction for coming blocks
    consFlex = {5: 100, 3: 50, 4: -100}         # Consumption flexibility options for coming block
    prodFlex = {6: 200, 7: -100}                # Production flexibility options for coming block

    report = ClientReport.ClientReport(uuid, timestamp, defaultConsPrice, defaultProdsPrice, consumption, production, predictedCons, predictedProd, consFlex, prodFlex)
    askOrders = report.reportToAskOrders()
    bidOrders = report.reportToBidOrders()
    print(report)
    print(askOrders)
    print(bidOrders)


def realDataTest():
    numClients = 5
    clientOffset = 1440
    dayOffset = 720

    minPerBlock = 5
    secPerBlock = 2
    powSignificance = 1000
    powUnit = "Kwh"

    parser = CSVparser.CVSparer('SimulationData.csv', numClients)

    for i in range(0, numClients):
        parser.skipRows(i, dayOffset)
        parser.skipRows(i, i * clientOffset)

    consumptionSum = 0
    productionSum = 0

    while True:
        for clientID in range(0, numClients):
            for min in range(0, minPerBlock):
                row = parser.getNextRow(clientID)
                consumptionSum += int(float(row[3].replace(",", ".")) * powSignificance)
                productionSum += int(float(row[4].replace(",", ".")) * powSignificance)

            report = ClientReport.ClientReport(0, str(datetime.datetime.now()), 5, 5, consumptionSum, productionSum,
                                               {"t+1": 1, "t+2": 2}, {"t+1": 1, "t+2": 2}, {"12.00": 300},
                                               {"11.00": 100})

            print(report.reportToAskOrders())
            print(report.reportToBidOrders())

            report.printMessage()
            consumptionSum = 0
            productionSum = 0

        print("\n")
        time.sleep(secPerBlock)


def matchMakingTest():
    book = MatchMaker.OrderBook()

    koop = MatchMaker.Ask(1, 0, 61, 70, 1)

    koop1 = MatchMaker.Ask(2, 0, 50, 50, 1)
    koop2 = MatchMaker.Ask(3, 0, 40, 35, 1)
    koop3 = MatchMaker.Ask(4, 0, 45, 35, 1)

    verkoop = MatchMaker.Bid(0, 1, 20, 29, 1)
    verkoop1 = MatchMaker.Bid(0, 2, 47, 31, 1)

    verkoop2 = MatchMaker.Bid(0, 3, 43, 32, 1)
    verkoop3 = MatchMaker.Bid(0, 4, 33, 31, 1)

    kooplijst = [koop, koop1, koop2, koop3, verkoop, verkoop1, verkoop2, verkoop3]
    # kooplijst = [koop, verkoop, verkoop1]

    book.add_order(kooplijst)

    engine = MatchMaker.Matcher(123)

    print("Order book:", book.getasklist() + book.getbidlist())
    print("Trade book:", engine.match(book))
    print("Order book:", book.getasklist() + book.getbidlist())
    new_book = engine.merge(book)
    print("Merged Order", new_book.getasklist(), new_book.getbidlist())


clientToOrdersTest()