var Transaction, // Protobuf Transaction
	// Current application state
	applicationState = {
		balance: {
			round: 0,
			state: 'COLLECTING'
		},
		contracts: {}
	}, 
	currentTransactions = [],
	channel = new CommunicationChannel("ws://localhost:46657/websocket");



var appDebugState = new Vue({
	el: '#app-debug-state',
	data: {
		state: applicationState
	}
});
var appDebugTransactions = new Vue({
	el: '#app-debug-transactions',
	data: {
		transactions: currentTransactions
	}
});
var appRoundState = new Vue({
	el: '#app-round-state',
	data: {
		state: applicationState
	}
});
var appRoundState = new Vue({
	el: '#app-round-transactions',
	data: {
		transactions: currentTransactions,
		info: 'bla' 
	}
})

function createTransaction(data) {
	var t = Transaction.encode(data).finish();
	return bufferToBase64(t);
}

function onTransaction(transaction) {
	if (transaction.newContract) {
		applicationState.constracts[bufferToUUID(base64ToBuffer(transaction.newContract.uuid))] = {
			public_key: base64ToBuffer(transaction.new_contract.public_key),
			consumption: 0,
			production: 0,
			prediction_consumption: {},
			prediction_production: {},
			consumption_flexibility: {},
			production_flexibility: {}
		}
	}
	if (transaction.usage) {
		var contract = applicationState.constracts[bufferToUUID(base64ToBuffer(transaction.usage.contractUuid))];
		contract.consumption = transaction.usage.consumption;
		contract.production = transaction.usage.production;
		contract.prediction_consumption = transaction.usage.prediction_consumption;
		contract.prediction_production = transaction.usage.prediction_production;
		contract.consumption_flexibility = transaction.usage.consumption_flexibility;
		contract.production_flexibility = transaction.usage.production_flexibility;
	}
	if (transaction.beginBalance) { 
		applicationState.balance.state = 'BALANCING';
	}
	if (transaction.endBalance) {
		applicationState.balance.round = transaction.endBalance.round;
		applicationState.balance.state = 'COLLECTING';
	}
}
protobuf.load("transaction.proto", function(err, root) {
	Transaction = root.lookupType('Transaction');
	channel.request({
		method: 'subscribe',
		params: {
			query: "tm.event='Tx'"
		}
	}, function(data) {}, function(event) {
		var rawTx = event.data.data.tx;
		var transaction = Transaction.decode(base64ToBuffer(rawTx)).toJSON();
		currentTransactions.unshift(transaction);
		onTransaction(transaction);
	});
	channel.request({
		method: 'abci_query',
		params: {
			path: 'state'
		}
	}, function(result) {
		console.log(hexToString(result.response.key));
		_.merge(applicationState, JSON.parse(hexToString(result.response.value)))
		// applicationState = ;
	});
});