import BalancingAlgorithm as Balancing
import CSVparser
import csv
import time
from array import *


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

        print("Client {}: consumptionSum: {} {}, productionSum: {} {}".format(clientID, consumptionSum, powUnit, productionSum, powUnit))
        consumptionSum = 0
        productionSum = 0
    print("\n")
    time.sleep(secPerBlock)




