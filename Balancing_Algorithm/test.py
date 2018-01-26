import MatchMaker
import operator
import blockchain
from random import randint

import CSVparser
import ClientReport
import datetime
import time

def realDataTestMultiLayer():
	# test that read data out of simulatedData file and builds ClientReports

	numClientsPerCluster = 2
	BlockchainGroupSize = 2

	clusters = []

	numBlockchainLayers = 3
	MainCluster = blockchain.blockchain(1*10**numBlockchainLayers, None)

	chain = MainCluster
	for i in range(0, BlockchainGroupSize):
		chain_I = blockchain.blockchain((10**(numBlockchainLayers-1)) + i, chain)
		chain.introduceClient(chain_I)
		for j in range(0, BlockchainGroupSize):
			chain_J = blockchain.blockchain((10 ** (numBlockchainLayers - 2)) + j+BlockchainGroupSize*i, chain_I)
			chain_I.introduceClient(chain_J)
			clusters.append(chain_J)
			for k in range(0, BlockchainGroupSize):
				chain_K = blockchain.blockchain((10 ** (numBlockchainLayers - 3)) + k+BlockchainGroupSize*(j+BlockchainGroupSize*i), chain_J)
				chain_K.introduceClient(None)
				chain_J.introduceClient(chain_K)

	clientOffset = 1440
	dayOffset = 720

	minPerBlock = 5
	secPerBlock = 2
	powSignificance = 1
	powUnit = "Kwh"


	numLayer1Clusters = len(clusters)
	numClients = numClientsPerCluster * numLayer1Clusters
	print("numClients:", numClients, "numLayer1Clusters:", numLayer1Clusters)

	parser = CSVparser.CVSparer('SimulationData.csv', numClients)

	for i in range(0, numClients):
		parser.skipRows(i, dayOffset)
		parser.skipRows(i, i * clientOffset)

	consumptionSum = 0
	productionSum = 0
	prevConsumptionSum = 0
	prevProductionSum = 0

	consPercentageToFlex = 0.2
	prodPercentageToFlex = 0.1

	# while True:
	for clientID in range(0, numClients):
		for min in range(0, minPerBlock):
			row = parser.getNextRow(clientID)
			consumptionSum += int(float(row[3].replace(",", ".")) * powSignificance)
			productionSum += int(float(row[4].replace(",", ".")) * powSignificance)

		uuid = clientID                            # ClientReport ID
		timestamp = str(datetime.datetime.now())   # Time stamp
		defaultConsPrice = 22000                   # Default consumption price /
		defaultProdsPrice = 5000                   # Default production price
		consumption = prevConsumptionSum           # Actual consumption last block
		production = prevProductionSum             # Actual production last block
		predictedCons = {"t+1": int(consumptionSum * (1-consPercentageToFlex))}    # Consumption prediction for coming blocks
		predictedProd = {"t+1": int(productionSum  * (1-prodPercentageToFlex))}    # Production prediction for coming blocks

		consFlex = {randint(150, 220)*100: int(0.2*(consumptionSum*consPercentageToFlex)), # Consumption flexibility options for coming block
					randint(100, 150)*100: int(0.3*(consumptionSum*consPercentageToFlex)),
					randint(50, 100) *100: int(0.5*(consumptionSum*consPercentageToFlex))}

		prodFlex = {randint(150, 220)*100: int(0.5*(consumptionSum*prodPercentageToFlex)), # Production flexibility options for coming block
					randint(100, 150)*100: int(0.3*(consumptionSum*prodPercentageToFlex)),
					randint(50, 100) *100: int(0.2*(consumptionSum*prodPercentageToFlex))}



		report = ClientReport.ClientReport(uuid, timestamp, defaultConsPrice, defaultProdsPrice, consumption,
										   production, predictedCons, predictedProd, consFlex, prodFlex)

		print("Client:", clientID, "reporting to cluster:", clusters[int(clientID / numClientsPerCluster)].uuid)
		clusters[int(clientID / numClientsPerCluster)].addClientreport(report)

		# 0 1 0
		# 2 3 1
		# 4 5 2
		# 6 7 3

		prevConsumptionSum = consumptionSum
		prevProductionSum = productionSum

		consumptionSum = 0
		productionSum = 0

		# print("\n")
		# time.sleep(secPerBlock)

def twoLayerClusterTest():
	# Testing two layer / three cluster model without downward data movement

	numLayerTwoClusters = 10
	layerOneGroupSize = 10
	secPerBlock = 10

	clusters = []

	MainCluster = blockchain.blockchain(100, None)

	start_time = str(datetime.datetime.now())

	for i in range(0, numLayerTwoClusters):
		clusters.append(blockchain.blockchain((i+1)*10, MainCluster))
		for j in range(0, layerOneGroupSize):
			clusters[i].introduceClient(None)
		MainCluster.introduceClient(clusters[i])

	# while True:
	for i in range(0, numLayerTwoClusters):
		cluster = clusters[i]
		for j in range(0, layerOneGroupSize):
			uuid = i*layerOneGroupSize + j  # ClientReport ID
			timestamp = str(datetime.datetime.now())  # Time stamp
			defaultConsPrice = 10  # Default consumption price
			defaultProdsPrice = 1  # Default production price
			consumption = 1000  # Actual consumption last block
			production = 100  # Actual production last block
			if i == 0:
				predictedCons = {"t+1": 200, "t+2": 0}  # Consumption prediction for coming blocks
				predictedProd = {"t+1": 10, "t+2": 0}  # Production prediction for coming blocks
			else:
				predictedCons = {"t+1": 10, "t+2": 0}  # Consumption prediction for coming blocks
				predictedProd = {"t+1": 200, "t+2": 0}  # Production prediction for coming blocks

			consFlex = {}  # Consumption flexibility options for coming block
			prodFlex = {}  # Production flexibility options for coming block

			report = ClientReport.ClientReport(uuid, timestamp, defaultConsPrice, defaultProdsPrice, consumption,
											   production, predictedCons, predictedProd, consFlex, prodFlex)
			cluster.addClientreport(report)

	# time.sleep(secPerBlock)
	print("START:", start_time, "STOP:", str(datetime.datetime.now()))


def oneLayerClusterTest():
	# Testing balancing in multiround single layer/cluster

	numClients = 2
	secPerBlock = 10

	cluster = blockchain.blockchain(0, None)

	while True:
		uuid = 0  # ClientReport ID
		timestamp = str(datetime.datetime.now())  # Time stamp
		defaultConsPrice = 10  # Default consumption price
		defaultProdsPrice = 1  # Default production price
		consumption = 1000  # Actual consumption last block
		production = 100  # Actual production last block
		predictedCons = {"t+1": 200, "t+2": 0}  # Consumption prediction for coming blocks
		predictedProd = {"t+1": 10, "t+2": 0}  # Production prediction for coming blocks
		consFlex = {8: 1000}  # Consumption flexibility options for coming block
		prodFlex = {}  # Production flexibility options for coming block

		report = ClientReport.ClientReport(uuid, timestamp, defaultConsPrice, defaultProdsPrice, consumption,
										   production, predictedCons, predictedProd, consFlex, prodFlex)
		cluster.addClientreport(report)


		uuid = 1  # ClientReport ID
		timestamp = str(datetime.datetime.now())  # Time stamp
		defaultConsPrice = 10  # Default consumption price
		defaultProdsPrice = 1  # Default production price
		consumption = 1000  # Actual consumption last block
		production = 100  # Actual production last block
		predictedCons = {"t+1": 10, "t+2": 0}  # Consumption prediction for coming blocks
		predictedProd = {"t+1": 200, "t+2": 0}  # Production prediction for coming blocks
		consFlex = {}  # Consumption flexibility options for coming block
		prodFlex = {2: 500}  # Production flexibility options for coming block

		report = ClientReport.ClientReport(uuid, timestamp, defaultConsPrice, defaultProdsPrice, consumption,
										   production, predictedCons, predictedProd, consFlex, prodFlex)
		cluster.addClientreport(report)
		time.sleep(secPerBlock)


def clientToOrdersTest():
	# test that rebuilds ClientReports to orderlists

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
	# test that read data out of simulatedData file and builds ClientReports

	numClients = 5
	clientOffset = 1440
	dayOffset = 720

	minPerBlock = 5
	secPerBlock = 2
	powSignificance = 1
	powUnit = "wh"

	parser = CSVparser.CVSparer('SimulationData.csv', numClients)

	for i in range(0, numClients):
		parser.skipRows(i, dayOffset)
		parser.skipRows(i, i * clientOffset)

	consumptionSum = 0
	productionSum = 0
	prevConsumptionSum = 0
	prevProductionSum = 0

	while True:
		for clientID in range(0, numClients):
			for min in range(0, minPerBlock):
				row = parser.getNextRow(clientID)
				consumptionSum += int(float(row[3].replace(",", ".")) * powSignificance)
				productionSum += int(float(row[4].replace(",", ".")) * powSignificance)

			uuid = 0                                   # ClientReport ID
			timestamp = str(datetime.datetime.now())   # Time stamp
			defaultConsPrice = 10                      # Default consumption price
			defaultProdsPrice = 1                      # Default production price
			consumption = prevConsumptionSum           # Actual consumption last block
			production = prevProductionSum             # Actual production last block
			predictedCons = {"t+1": consumptionSum}    # Consumption prediction for coming blocks
			predictedProd = {"t+1": productionSum}     # Production prediction for coming blocks


			consFlex = {randint(6, 9): 100, randint(3, 5): 50, randint(2, 9): -100} # Consumption flexibility options for coming block
			prodFlex = {randint(2, 5): 200, randint(2, 9): -100}                    # Production flexibility options for coming block

			report = ClientReport.ClientReport(uuid, timestamp, defaultConsPrice, defaultProdsPrice, consumption,
											   production, predictedCons, predictedProd, consFlex, prodFlex)

			print(report.reportToAskOrders())
			print(report.reportToBidOrders())

			print(report)
			prevConsumptionSum = consumptionSum
			prevProductionSum = productionSum

			consumptionSum = 0
			productionSum = 0

		print("\n")
		time.sleep(secPerBlock)


def matchMakingTest():
	# simple test that builds an aks and bid list and matches the orders.

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
	print("Remaining Order book:", book.getasklist() + book.getbidlist())
	new_book = engine.merge(book)
	print("Merged Order", new_book.getasklist(), new_book.getbidlist())


# realDataTest()
# twoLayerClusterTest()
realDataTestMultiLayer()