const {Connection} = require('./Connection'),
	EMPTY_BUFFER = Buffer.alloc(0);


module.exports.Application = class Application {
	constructor(protocol) {
		this.connections = [];
		this.protocol = protocol;

		this.proto = protocol.lookup('types');
	}

	addSocket(socket) {
		console.log('new connection');
		var connection = new Connection(socket, (packet) => {
			var req = this.proto.Request.decode(packet);
			console.log(require('util').inspect(req, {colors: true, depth: 3}));
			if (req.flush) {
				connection.write(this.createResponse({
					flush: {}
				}));
				connection.flush();
				return;
			} 
			return this.onMessage(connection, req);
		});
		this.connections.push(connection);
	}

	onMessage(connection, message) {
		if (message.info) {
			return this.onInfo(connection, message.info);
		}
		if (message.initChain) {
			return this.onInitChain(connection, message.initChain)
		}
	}

	onInfo(connection, info) {
		return this.createResponse({
			info: {
				data: 'test application',
				version: '1.0.0'
			}
		});
	}

	onInitChain(connection, init) {
		this.validators = init.validators;
		return this.createResponse({
			initChain: {}
		});
	}

	createResponse(obj) {
		var message = this.proto.Response.create(obj);
		return this.proto.Response.encode(message).finish();
	}

};