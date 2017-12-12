

const protobuf = require('protobufjs'),
	{Connection} = require('./Connection'),
	{Application} = require('./Application'),
	net = require('net'),
	request = require('request');



class TestApplication extends Application {
	constructor(protocol, io) {
		super(protocol);

		this.io = io;
		this.messages = [];
	}

	onDeliverTx(connection, deliver) {
		this.messages.push(deliver.tx.toString('utf8'));
		this.io.emit('message', deliver.tx.toString('utf8'));
		return super.onDeliverTx(connection, deliver);
	}
}

async function start() {
	const protocol = await protobuf.load('types.proto');

	var server = new net.Server(),
		app = require('express')(),
		http = require('http').Server(app),
		io = require('socket.io')(http),
		application = new TestApplication(protocol, io);

	server.on('connection', socket => {
		application.addSocket(socket);
	});
	server.listen(46658);

	app.get('/', function(req, res){
		res.sendFile(__dirname + '/index.html');
	});

	io.on('connection', function(socket){
		console.log('a user connected');
		socket.emit('messages', application.messages);
		socket.on('message', function(msg) {
			request.get(`http://tendermint:46657/broadcast_tx_async?tx=${JSON.stringify(msg)}`, (err, res, body) => {
				console.log('message posted', body);
			});
			console.log('message:', msg);
		});
	});

	http.listen(80, function(){
		console.log('listening on *:80');
	});
};

start();

