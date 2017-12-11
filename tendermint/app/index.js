

const protobuf = require('protobufjs'),
	{Connection} = require('./Connection'),
	{Application} = require('./Application'),
	net = require('net');


/*
Type {
  constructor: 
   { [Function: Type]
     className: 'Type',
     generateConstructor: [Function: generateConstructor],
     fromJSON: [Function: fromJSON],
     d: [Function: decorateType] },
  toJSON: [Function: toJSON],
  resolveAll: [Function: resolveAll],
  get: [Function: get],
  add: [Function: add],
  remove: [Function: remove],
  isReservedId: [Function: isReservedId],
  isReservedName: [Function: isReservedName],
  create: [Function: create],
  setup: [Function: setup],
  encode: [Function: encode_setup],
  encodeDelimited: [Function: encodeDelimited],
  decode: [Function: decode_setup],
  decodeDelimited: [Function: decodeDelimited],
  verify: [Function: verify_setup],
  fromObject: [Function: fromObject],
  toObject: [Function: toObject] 
}
*/
async function start() {
	const protocol = await protobuf.load('types.proto'),
		Request = protocol.lookupType('Request'),
		Response = protocol.lookupType('Response'),
		ResponseFlush = protocol.lookupType('ResponseFlush');

	var server = new net.Server(),
		openConnections = [],
		application = new Application(protocol);

	server.on('connection', socket => {
		application.addSocket(socket);
	});
	server.listen(46658);
	console.log(require('util').inspect(protocol.lookup('types').Response, {colors: true, depth: 1}));


};

start();

