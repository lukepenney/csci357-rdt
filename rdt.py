# The URL for this assignment is:
# https://cs.wheaton.edu/~devinpohly/csci357-s20/project-rdt.pdf

from network import Protocol, StreamSocket

# Reserved protocol number for experiments; see RFC 3692
IPPROTO_RDT = 0xfe


class RDTSocket(StreamSocket):

	def __init__(self, *args, **kwargs):
		"""Initializes a new stream socket"""
		super().__init__(*args, **kwargs)
		# Other initialization here
		self.bound_port = -1
		self.is_listening = False
		self.is_connected = False
		self.remote_IP = ''
		self.remote_port = -1

	def bind(self, port):
		"""
		Binds the socket to a local port

		If the port is already in use by another socket on this host, then the
		method should raise Socket.AddressInUse.  If the socket is already
		connected, it should raise StreamSocket.AlreadyConnected.
		"""
		if self.bound_port != -1:
			raise super().AlreadyConnected

		if port in self.proto.ports_in_use:
			raise super().AddressInUse

		self.bound_port = port
		self.proto.ports_in_use.add(port)

	def listen(self):
		"""
		Identifies the stream socket as a listening (server) socket and begins
		to listen for and queue incoming connections

		If the socket has not been bound to a local address on which to listen,
		this method should raise StreamSocket.NotBound.  If the socket is
		already connected, it should raise StreamSocket.AlreadyConnected.
		"""
		if self.bound_port == -1:
			raise super().NotBound

		if self.is_connected:
			raise super().AlreadyConnected

		self.is_listening = True

		# TODO: later: anything else to do for this?

	def accept(self):
		"""
		Accepts a single incoming connection, waiting for one if there are none
		pending.

		Returns a pair (socket, (addr, port)) giving a socket that may be used
		to communicate with the connecting client, and the remote socket
		address.

		If this is called on a socket which is not listening, the method should
		raise StreamSocket.NotListening.
		"""
		if not self.is_listening:
			raise StreamSocket.NotListening

		# TODO:
		# check connection queue
		# if no connections waiting, block
		# if connection, remove from queue and attach to new socket; return
		#  that socket with (remote_addr, remote_port)
		# (note: this socket keeps listening afterwards)
		return (None, ('', -1))

	def connect(self, addr):
		"""
		Connects the socket to a remote socket address

		If the socket is not yet bound to a local port, the implementation
		should choose an unused port for this socket's local address.

		If the socket is already connected, this method should raise
		StreamSocket.AlreadyConnected.  If the socket is listening, it should
		raise StreamSocket.AlreadyListening.
		"""
		if self.is_connected:
			raise super().AlreadyConnected

		if self.is_listening:
			raise super().AlreadyListening

		if self.bound_port == -1:
			port = 1
			while port in self.proto.ports_in_use: # find unused port
				port += 1
				# No error check for running out of port numbers, but if every
				# single possible port is in use, we probably have big problems
				# on our hands anyway
			self.bind(port)

		self.is_connected = True

		self.remote_IP = addr[0]
		self.remote_port = addr[1]

		# TODO: later: anything else to make the connection?

	def send(self, data):
		"""
		Sends the provided message data to the remote host

		This method is called by the application to send message data (bytes)
		over a connected socket.  It should handle any socket-level sending
		behavior, such as setting ARQ timers.

		If the socket is not connected, this should raise
		StreamSocket.NotConnected.
		"""
		if self.bound_port == -1:
			raise super().NotBound

		if not self.is_connected:
			raise super().NotConnected

		# TODO: later: will also need to set timers, etc

		headers = b'' # TODO: later: What should headers be?
		segment = headers + data

		super().output(segment, (self.remote_IP, self.remote_port))


class RDTProtocol(Protocol):
	PROTO_ID = IPPROTO_RDT
	SOCKET_CLS = RDTSocket

	def __init__(self, *args, **kwargs):
		"""Initialize a new instance of the protocol on the given host"""
		super().__init__(*args, **kwargs)
		# Other initialization here
		self.ports_in_use = set()
		# self.connections maps (local_port, (remote_IP, remote_port)) to socket
		self.connections = dict()

	def input(self, seg, rhost):
		"""
		Handles an incoming segment

		This method is called by the network-layer thread when a segment is
		received for this protocol, providing the segment data (bytes) and
		network-layer address of the source host.

		It should handle any protocol-level receive behavior such as
		demultiplexing and error detection, then pass the segment and source
		address to the correct socket for handling.
		"""

		# TODO: later: may be useful:
		# https://en.wikipedia.org/wiki/User_Datagram_Protocol#UDP_datagram_structure
		# https://en.wikipedia.org/wiki/Transmission_Control_Protocol#TCP_segment_structure

		# TODO:
		# get headers and data from seg; use headers to identify local and remote port #'s
		# use port #'s and rhost - which is remote_IP - to identify the right socket
		# deliver data, using right_socket.deliver(data)
		# - if the socket is listening, will need to queue the connection instead
		# - probably will need to collaborat with send() to do things like timers and resending, etc
		pass
