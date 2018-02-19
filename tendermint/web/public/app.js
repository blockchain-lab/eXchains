var Transaction, // Protobuf Transaction
	// Current application state
	applicationState = {
		balance: {
			round: 0,
			mode: 0
		},
		contracts: {}
	},
	currentTransactions = [],
	channel = new CommunicationChannel("ws://localhost:46657/websocket");

// var appDebugState = new Vue({
// 	el: "#app-debug-state",
// 	data: {
// 		state: applicationState
// 	}
// });
// var appDebugTransactions = new Vue({
// 	el: "#app-debug-transactions",
// 	data: {
// 		transactions: currentTransactions
// 	}
// });
var appRoundState = new Vue({
	el: "#app-round-state",
	data: {
		state: _.cloneDeep(applicationState),
		lastTrade: null,
		unbalanceBefore: null,
		unbalanceAfter: null
	}
});
var appRoundTransactions = new Vue({
	el: "#app-round-transactions",
	data: {
		state: currentTransactions,
		info: "bla"
	}
});

function createTransaction(data) {
	var t = Transaction.encode(data).finish();
	return bufferToBase64(t);
}

function onTransaction(transaction) {
	console.log(transaction);
	if (transaction.newContract) {
		applicationState.contracts[
			bufferToUUID(base64ToBuffer(transaction.newContract.uuid))
		] = {
			public_key: base64ToBuffer(transaction.newContract.publicKey),
			consumption: 0,
			production: 0,
			prediction_consumption: {},
			prediction_production: {},
			consumption_flexibility: {},
			production_flexibility: {},
			default_production_price: 0,
			default_consumption_price: 0
		};
	}
	if (transaction.usage) {
		var contract =
			applicationState.contracts[
				bufferToUUID(base64ToBuffer(transaction.usage.contractUuid))
			];
		contract.consumption = transaction.usage.consumption;
		contract.production = transaction.usage.production;
		contract.prediction_consumption =
			transaction.usage.predictionConsumption;
		contract.prediction_production = transaction.usage.predictionProduction;
		contract.consumption_flexibility =
			transaction.usage.consumptionFlexibility;
		contract.production_flexibility =
			transaction.usage.productionFlexibility;
		contract.default_consumption_price =
			transaction.usage.defaultConsumptionPrice;
		contract.default_production_price =
			transaction.usage.defaultProductionPrice;
	}
	if (transaction.balanceStart) {
		applicationState.balance.mode = 1;
	}
	if (transaction.balance) {
		appRoundState.lastTrade = _.cloneDeep(transaction.balance);

		let staticProduction = 0,
			staticConsumption = 0,
			flexibleProduction = 0,
			flexibleConsumption = 0;

		let prebalanceUnbalance = 0,
			prebalanceProductionPrice = 0,
			prebalanceConsumptionPrice = 0,
			defaultProductionPrice = 500,
			defaultConsumptionPrice = 22000;

		_.each(applicationState.contracts, contract => {
			staticProduction += sumMapValues(contract.prediction_production);
			staticConsumption += sumMapValues(contract.prediction_consumption);
			flexibleConsumption += sumMapValues(
				contract.consumption_flexibility
			);
			flexibleProduction += sumMapValues(contract.production_flexibility);

			var difference =
				sumMapValues(contract.prediction_production) -
				sumMapValues(contract.predictionConsumption);
			// var difference =
			// 	sumMapValues(contract.prediction_production) +
			// 	sumMapValues(contract.production_flexibility) -
			// 	sumMapValues(contract.prediction_consumption) -
			// 	sumMapValues(contract.consumption_flexibility);
			prebalanceUnbalance += difference;

			var productionPrice =
				(sumMapValues(contract.prediction_production) +
					sumMapValues(contract.production_flexibility)) *
				contract.default_production_price;
			prebalanceProductionPrice += productionPrice;

			var consumptionPrice =
				(sumMapValues(contract.prediction_consumption) +
					sumMapValues(contract.consumption_flexibility)) *
				contract.default_consumption_price;
			prebalanceConsumptionPrice += consumptionPrice;
		});

		let postbalanceVolume = 0,
			postbalanceProductionPrice = 0,
			postbalanceConsumptionPrice = 0;
		/*
			class OrderType(Enum):
			ASK = 1
			BID = 2
		 */
		_.each(transaction.balance.trades, trade => {
			let volume = parseInt(trade.volume, 10);
			let price = parseInt(trade.price, 10);
			// if (!trade.volume || !trade.price) {
			// 	return;
			// }
			if (isNaN(volume)) {
				volume = 0;
			}
			if (isNaN(price)) {
				price = 0;
			}
			if (parseInt(trade.orderType, 10) == 1) {
				postbalanceVolume += volume;
				postbalanceConsumptionPrice += volume * price;
			}
			if (parseInt(trade.orderType, 10) == 2) {
				postbalanceProductionPrice += volume * price;
			}
		});

		// postbalanceProductionPrice +=
		// 	staticProduction * defaultProductionPrice +
		// 	Math.max(flexibleProduction - postbalanceVolume, 0) *
		// 		defaultProductionPrice;

		// postbalanceConsumptionPrice +=
		// 	staticConsumption * defaultConsumptionPrice +
		// 	Math.max(flexibleConsumption - postbalanceVolume, 0) *
		// 		defaultConsumptionPrice;

		// console.log(prebalanceUnbalance, postbalanceVolume);
		// console.log(
		// 	staticProduction,
		// 	flexibleProduction,
		// 	staticConsumption,
		// 	flexibleConsumption
		// );
		appRoundState.unbalanceBefore = `${Math.abs(
			prebalanceUnbalance
		)} P:€${defaultProductionPrice} C:€${defaultConsumptionPrice}`;
		appRoundState.unbalanceAfter = `${Math.abs(
			postbalanceVolume - staticProduction - flexibleProduction
		)} P:€${roundBy(
			postbalanceProductionPrice / postbalanceVolume,
			2
		)} C:€${roundBy(postbalanceConsumptionPrice / postbalanceVolume, 2)}`;
		chartConfig.data.labels.push(transaction.balance.timestamp);
		chartConfig.data.datasets[0].data.push(Math.abs(prebalanceUnbalance));
		chartConfig.data.datasets[1].data.push(
			Math.abs(postbalanceVolume - staticProduction - flexibleProduction)
		);
		theChart.update();
	}
	if (transaction.balanceEnd) {
		applicationState.balance.round = transaction.balanceEnd.roundNumber;
		applicationState.balance.mode = 0;
	}
	appRoundState.state = _.cloneDeep(applicationState);
}
// <- -> ^ ˅
protobuf.load("transaction.proto", function(err, root) {
	Transaction = root.lookupType("Transaction");
	channel.request(
		{
			method: "subscribe",
			params: {
				query: "tm.event='Tx'"
			}
		},
		function(data) {},
		function(event) {
			var rawTx = event.data.data.tx;
			var transaction = Transaction.decode(
				base64ToBuffer(rawTx)
			).toJSON();
			transaction.type = Object.keys(transaction)[0];

			currentTransactions.unshift(_.cloneDeep(transaction));
			onTransaction(transaction);
		}
	);
	channel.request(
		{
			method: "abci_query",
			params: {
				path: "state"
			}
		},
		function(result) {
			console.log(hexToString(result.response.key));
			_.merge(
				applicationState,
				JSON.parse(hexToString(result.response.value))
			);
		}
	);
});
window.chartColors = {
	red: "rgb(255, 99, 132)",
	orange: "rgb(255, 159, 64)",
	yellow: "rgb(255, 205, 86)",
	green: "rgb(75, 192, 192)",
	blue: "rgb(54, 162, 235)",
	purple: "rgb(153, 102, 255)",
	grey: "rgb(201, 203, 207)"
};
var chartConfig = {
	type: "line",
	data: {
		labels: [],
		datasets: [
			{
				label: "Prebalance",
				backgroundColor: window.chartColors.red,
				borderColor: window.chartColors.red,
				data: [],
				fill: false
			},
			{
				label: "Postbalance",
				fill: false,
				backgroundColor: window.chartColors.blue,
				borderColor: window.chartColors.blue,
				data: []
			}
		]
	},
	options: {
		responsive: true,
		title: {
			display: false,
			text: ""
		},
		tooltips: {
			mode: "index",
			intersect: false
		},
		hover: {
			mode: "nearest",
			intersect: true
		},
		scales: {
			xAxes: [
				{
					display: true,
					scaleLabel: {
						display: false,
						labelString: "Time"
					}
				}
			],
			yAxes: [
				{
					display: true,
					scaleLabel: {
						display: true,
						labelString: "Volume"
					}
				}
			]
		}
	}
};

window.onload = function() {
	var ctx = document.getElementById("chart").getContext("2d");
	window.theChart = new Chart(ctx, chartConfig);
};
