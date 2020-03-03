# https://cs.wheaton.edu/~devinpohly/csci357-s20/project-rdt.pdf
from network import Protocol, StreamSocket

# Reserved protocol number for experiments; see RFC 3692
IPPROTO_RDT = 0xfe


class RDTSocket(StreamSocket):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		# Other initialization here
		self.bound_port = -1
		self.is_listening = False
		self.is_connected = False

	def bind(self, port):
		if self.bound_port != -1:
			raise super().AlreadyConnected

		if port in self.proto.ports_in_use:
			raise super().AddressInUse

		self.bound_port = port
		self.proto.ports_in_use.add(port)

	def listen(self):
		if self.bound_port == -1:
			raise super().NotBound

		if self.is_connected:
			raise super().AlreadyConnected

		self.is_listening = True

		# TODO: "begins to listen for and queue incoming connections"

	def accept(self):
		if not self.is_listening:
			raise StreamSocket.NotListening

		pass

	def connect(self, addr):
		if self.bound_port == -1:
			raise super().NotBound

		pass

	def send(self, data):
		if self.bound_port == -1:
			raise super().NotBound

		pass  # probably will call: Protocol.output(seg, host); see also: StreamSocket.recv(self, n=None)


class RDTProtocol(Protocol):
	PROTO_ID = IPPROTO_RDT
	SOCKET_CLS = RDTSocket

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		# Other initialization here
		self.ports_in_use = set()

	def input(self, seg, rhost):
	   pass  # probably will call: Protocol.output(self, seg, dst)
