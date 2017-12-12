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
			return this.onMessage(connection, req);
		});
		this.connections.push(connection);
	}

	onMessage(connection, message) {
		if (message.echo) {
			return this.createResponse({
				echo: {
					message: message.echo
				}
			});
		}
		if (message.flush) {
			connection.write(this.createResponse({
				flush: {}
			}));
			connection.flush();
			return;
		}
		if (message.info) {
			return this.onInfo(connection, message.info);
		}
		if (message.setOption) {
			return this.onSetOption(connection, message.setOption);
		}
		if (message.deliverTx) {
			return this.onDeliverTx(connection, message.deliverTx);
		}
		if (message.checkTx) {
			return this.onCheckTx(connection, message.checkTx);
		}
		if (message.commit) {
			return this.onCommit(connection, message.commit);
		}
		if (message.initChain) {
			return this.onInitChain(connection, message.initChain);
		}
		if (message.beginBlock) {
			return this.onBeginBlock(connection, message.beginBlock);
		}
		if (message.endBlock) {
			return this.onEndBlock(connection, message.endBlock);
		}
	}

	createResponse(obj) {
		var message = this.proto.Response.create(obj);
		console.log(message);
		return this.proto.Response.encode(message).finish();
	}

	/**
	 * @param  {Connection}
	 * @param  {info}
	 * {
	 * 	version: string
	 * }
	 * @return {Buffer?}
	 */
	onInfo(connection, info) {
		return this.createResponse({
			info: {
				data: 'test application',
				version: '1.0.0'
			}
		});
	}

	/**
	 * @param  {Connection}
	 * @param  {option}
	 * {
	 *  key: string,
	 *  value: string
	 * }
	 * @return {Buffer?}
	 */
	onSetOption(connection, option) {
		return this.createResponse({
			setOption: {
				log: 'Nothing done'
			}
		});
	}

	/**
	 * @param  {Connection}
	 * @param  {deliver}
	 * {
	 * 	tx: bytes
	 * }
	 * @return {Buffer?}
	 */
	onDeliverTx(connection, deliver) {
		return this.createResponse({
			deliverTx: {
				code: this.proto.CodeType.OK,
				bytes: deliver.tx
			}
		});
	}

	/**
	 * @param  {Connection}
	 * @param  {check}
	 * {
	 * 	tx: bytes
	 * }
	 * @return {Buffer?}
	 */
	onCheckTx(connection, check) {
		return this.createResponse({
			checkTx: {
				code: this.proto.CodeType.OK,
				bytes: check.tx
			}
		});
	}

	/**
	 * @param  {Connection}
	 * @param  {}
	 * @return {Buffer?}
	 */
	onCommit(connection, empty) {
		return this.createResponse({
			commit: {
				code: this.proto.CodeType.OK,
				// bytes: [],
				log: 'Nothing done'
			}
		});
	}

	/**
	 * @param  {Connection}
	 * @param  {init}
	 * {
	 * 	validators: [{
	 * 		pubKey: bytes
	 * 		power: Long
	 * 	}]
	 * }
	 * @return {Buffer?}
	 */
	onInitChain(connection, init) {
		this.validators = init.validators;
		return this.createResponse({
			initChain: {}
		});
	}

	/**
	 * @param  {Connection}
	 * @param  {begin}
	 * {
	 * 	hash: bytes
	 * 	header: {
	 * 		chainId: string
	 * 		height: Long
	 * 		time: Long
	 * 		numTxs: Long
	 * 		lastBlockId: {
	 * 			hash: bytes
	 * 			parts: {
	 * 				total: Long
	 * 				hash: bytes
	 * 			}
	 * 		}
	 * 	}
	 * }
	 * @return {Buffer?}
	 */
	onBeginBlock(connection, begin) {
		return this.createResponse({
			beginBlock: {}
		});
	}

	/**
	 * @param  {Con}
	 * @param  {end}
	 * {
	 * 	height: Long
	 * }
	 * @return {Buffer?}
	 */
	onEndBlock(connection, end) {
		return this.createResponse({
			endBlock: {
				// Changed validators
				diffs: []
			}
		});
	}
};