import CSVparser
import ClientReport
import datetime
import time


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
    parser.skipRows(i, i*clientOffset)

consumptionSum = 0
productionSum = 0

while True:
    for clientID in range(0, numClients):
        for min in range(0, minPerBlock):
            row = parser.getNextRow(clientID)
            consumptionSum += int(float(row[3].replace(",", "."))*powSignificance)
            productionSum += int(float(row[4].replace(",", "."))*powSignificance)

        report = ClientReport.ClientReport(0, str(datetime.datetime.now()), 5, 5, consumptionSum, productionSum, {"t+1": 1, "t+2": 2},  {"t+1": 1, "t+2": 2}, {"12.00": 300}, {"11.00": 100})

        print(report.reportToAskOrders())
        print(report.reportToBidOrders())

        report.printMessage()
        consumptionSum = 0
        productionSum = 0

    print("\n")
    time.sleep(secPerBlock)




