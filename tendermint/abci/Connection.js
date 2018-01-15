const maxWriteBufferLength = 4096,
	EMPTY_BUFFER = Buffer.alloc(0); // Any more and flush

module.exports.Connection = class Connection extends require('events') {
	constructor(socket, messageHandler) {
		super();
		this.socket = socket;
		this.receiveBuffer = EMPTY_BUFFER;
		this.transmitBuffer = EMPTY_BUFFER;
		this.waitingResult = false;
		this.messageHandler = messageHandler;

		// Handle ABCI requests.
		socket.on('data', (data) => {
			this.appendData(data);
		});
		socket.on('end', () => {
			this.emit('end');
		});
	}

	appendData(buf) {
		if (buf.length > 0) {
			this.receiveBuffer = Buffer.concat([this.receiveBuffer, buf]);
		}
		// console.log(this.receiveBuffer);
		
		if (this.waitingResult) {
			return;
		}

		if (!this.hasEnoughData()) {
			return;
		}

		var headerLength = this.receiveBuffer[0] + 1;
		var packetLength = this.decodeLength(this.receiveBuffer);
		var header = this.receiveBuffer.slice(0, headerLength);
		var packet = this.receiveBuffer.slice(headerLength, packetLength + headerLength);
		this.receiveBuffer = this.receiveBuffer.slice(packetLength + headerLength);
		
		this.socket.pause();
		this.waitingResult = true;

		// console.log(header, packet);
		var response = this.messageHandler(packet);
		if (response instanceof Promise) {
			response.then(result => {
				if (result) {
					this.write(result);
				}
				this.waitingResult = false;
				this.appendData(EMPTY_BUFFER); // Make sure there are no other pending messages
				this.socket.resume();
			});
		} else {
			if (response) {
				this.write(response);
			}
			this.waitingResult = false;
			this.appendData(EMPTY_BUFFER); // Make sure there are no other pending messages
			this.socket.resume();
		}
	}

	write(packet) {
		if (packet.length == 0) {
			return;
		}
		let header = this.encodeLength(packet.length);
		// console.log(packet.length, header, packet);
		this.transmitBuffer = Buffer.concat([this.transmitBuffer, header, packet]);
		if (this.transmitBuffer.length >= maxWriteBufferLength) {
			this.flush();
		}
	}

	flush() {
		this.socket.write(this.transmitBuffer);
		this.transmitBuffer = EMPTY_BUFFER;
	}

	encodeLength(length) {
		var parts = [];
		while(length > 0) {
			parts.unshift(length & 0xFF);
			length = length >> 8;
		}
		parts.unshift(parts.length);
		return Buffer.from(parts);
	}

	decodeLength(buf) {
		// The person who made this protocol should perish.
		var lengthLength = buf[0];
		var length = 0;
		for (let i = 0; i < lengthLength; i += 1) {
			length += buf[i + 1] << (8 * (lengthLength - i - 1));
		}
		return length;
	}

	hasEnoughData() {
		if (this.receiveBuffer.length == 0) {
			return false;
		}
		// The person who made this protocol should perish.
		var lengthLength = this.receiveBuffer[0];
		// Not all length bytes are here yet.
		if (this.receiveBuffer.length < (lengthLength + 1)) {
			return false;
		}
		var length = this.decodeLength(this.receiveBuffer);
		if (this.receiveBuffer.length < (length + 1 + lengthLength)) {
			return false;
		}
		return true;
	}

	close() {
		this.socket.destroy();
	}
}