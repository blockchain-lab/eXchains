

class CommunicationChannel {
	constructor(url) {
		this.socket = new WebSocket(url);

		this.pending = {};
		this.listeners = {};
		this.subscriptions = [];
		this.nextId = 1;

		this.socket.addEventListener('message', (event) => {
			this.onMessage(event);
		});
	}

	onMessage(event) {
		var data = JSON.parse(event.data);
		console.log(JSON.stringify(data));
		if (Boolean(this.pending[data.id])) {
			this.pending[data.id](data.result);
			delete this.pending[data.id];
		}
		if (Boolean(this.listeners[data.id])) {
			this.listeners[data.id](data.result);
		}
	}

	request(req, callback, event_listener) {
		if (this.socket.readyState == 0) {
			this.socket.addEventListener('open', () => {
				this.request(req, callback, event_listener);
			});
		} else {
			let id = "request_" + String(this.nextId++);
			this.pending[id] = callback;
			req = {
				method: req.method,
				params: req.params,
				jsonrpc: "2.0",
				id: id
			};
			if (event_listener && req.method === 'subscribe') {
				this.listeners[id + "#event"] = event_listener;
				this.subscriptions.push(req);
			}
			console.log(JSON.stringify(req));
			this.socket.send(JSON.stringify(req));
		}
	}
}


function stringToHex(s) {
	// utf8 to latin1
	var s = unescape(encodeURIComponent(s))
	var h = ''
	for (var i = 0; i < s.length; i++) {
		h += s.charCodeAt(i).toString(16)
	}
	return h
}

function hexToString(h) {
	var s = ''
	for (var i = 0; i < h.length; i += 2) {
		s += String.fromCharCode(parseInt(h.substr(i, 2), 16))
	}
	return decodeURIComponent(escape(s))
}

function bufferToHex(buf) {
	var str = '';
	for (var i = 0; i < 16; i += 1) {
		str += buf[i].toString(16);
	}
	return str;
}

function bufferToBase64(buf) {
	return btoa(String.fromCharCode.apply(null, buf))
}

function base64ToBuffer(base64str) {
	var rawStr = atob(base64str),
		buff = new Uint8Array(rawStr.length);
	for (var i = 0; i < rawStr.length; i += 1) {
		buff[i] = rawStr.charCodeAt(i);
	}
	return buff;
}

function bufferToUUID(buf) {
	var str = bufferToHex(buf);
	str = str.substr(0, 8) + '-' + str.substr(8, 12) + '-' + str.substr(12, 16) + '-' + str.substr(16, 20) + '-' + str.substr(20);
	return str;
}

function genUUIDBuffer() {
	// xx xx xx xx - xx xx - 4x xx - yx xx-xxxxxxxxxxxx
	var buf = new Uint8Array(16);
	for (var i = 0; i < 16; i++) {
		buf[i] = (Math.random() * 256) | 0;
	}
	buf[6] = buf[6] & 0x0F | 0x40; // 0b0100xxxx
	buf[8] = buf[8] & 0x3F | 0x80; // 0b10xxxxxx
	return buf;
}