# The URL for this assignment is:
# https://cs.wheaton.edu/~devinpohly/csci357-s20/project-rdt.pdf
# TODO: having the SYN and ACK information be pseudo-payload is problematic;
#       I should probably just do a flag with S/A or some such

from network import Protocol, StreamSocket
from queue import Queue
from time import sleep


# Reserved protocol number for experiments; see RFC 3692
IPPROTO_RDT = 0xfe


class RDTSocket(StreamSocket):

	def __init__(self, *args, **kwargs):
		"""Initializes a new stream socket"""
		super().__init__(*args, **kwargs)
		# Other initialization here
		
		self.bound_port = -1
		
		self.is_connected = False
		# only used by connected sockets
		self.remote_IP = ''
		self.remote_port = -1

		self.is_listening = False
		self.waiting_connections = Queue()  # only used by listening socket

		self.acked = True  # whether the last sent packet has been acknowledged by the other side

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

		self.proto.listening_sockets[self.bound_port] = self

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
		if self.bound_port == -1:
			raise StreamSocket.NotBound

		if not self.is_listening:
			raise StreamSocket.NotListening

		new_connection = self.waiting_connections.get()  # Note: blocks if empty

		connected_socket = self.proto.socket()
		connected_socket.bound_port = self.bound_port
		connected_socket.is_connected = True
		connected_socket.remote_IP = new_connection[0]
		connected_socket.remote_port = new_connection[1]

		socket_identifier = (connected_socket.bound_port, (connected_socket.remote_IP, connected_socket.remote_port))
		self.proto.connections[socket_identifier] = connected_socket

		return (connected_socket, (connected_socket.remote_IP, connected_socket.remote_port))

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

		socket_identifier = (self.bound_port, (self.remote_IP, self.remote_port))
		self.proto.connections[socket_identifier] = self

		# send initial message to start the connection on the other side
		self.send(b'SYN')

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

		# avoid sending new information until the last information has been acknowledged
		counter = 0
		while not self.acked:
			if counter == 3:
				break  # no response is likely to come; time to give up
			counter += 1
			sleep(0.001)

		local_port_string = RDTSocket.port_string(self.bound_port)
		remote_port_string = RDTSocket.port_string(self.remote_port)

		headers = (local_port_string + remote_port_string).encode('utf-8')
		segment = headers + data

		checksum = RDTSocket.checksum(segment)
		segment = checksum + segment

		self.acked = False
		counter = 0
		while not self.acked:
			if counter == 3:
				return  # no response is likely to come; time to give up
			counter += 1
			super().output(segment, self.remote_IP)
			sleep(0.001)

	@staticmethod
	def port_string(port):
		"""
		Converts an integer port number to a string of length 5
		"""
		port_str = str(port)
		while len(port_str) < 5:
			port_str = "0" + port_str
		return port_str

	@staticmethod
	def checksum(segment):
		return bytes([sum(segment) % 256])

class RDTProtocol(Protocol):
	PROTO_ID = IPPROTO_RDT
	SOCKET_CLS = RDTSocket

	def __init__(self, *args, **kwargs):
		"""Initialize a new instance of the protocol on the given host"""
		super().__init__(*args, **kwargs)
		# Other initialization here
		self.ports_in_use = set()
		self.listening_sockets = dict()  # maps port # to the socket listening on that port
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

		# drop currupt packets
		if not RDTProtocol.valid_checksum(seg):
			return

		remote_port = int(seg[1:6])
		local_port = int(seg[6:11])
		data = seg[11:]

		if not local_port in self.ports_in_use:
			return

		right_socket = self.connections.get((local_port, (rhost, remote_port)))
		#print(self.host.ip + ' received ' + str((local_port, (rhost, remote_port))) + ' containing ' + str(data))

		if right_socket == None:
			right_socket = self.listening_sockets[local_port]
			right_socket.waiting_connections.put((rhost, remote_port))
			if data != b'SYN':
				pass  # TODO: error handling?
		else:
			if data == b'ACK':
				right_socket.acked = True
			elif data == b'SYN':
				pass  # This is *probably* a duplicate packet that's fine to ignore
			else:
				right_socket.deliver(data)
				right_socket.send(b'ACK')

	@staticmethod	
	def valid_checksum(rdt_segment):
		"""
		Checks whether the checksum of this rdt segment is valid
		"""
		return rdt_segment[0:1] == RDTSocket.checksum(rdt_segment[1:])

