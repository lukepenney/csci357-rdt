from network import Protocol, StreamSocket

# Reserved protocol number for experiments; see RFC 3692
IPPROTO_RDT = 0xfe


class RDTSocket(StreamSocket):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Other initialization here

    def bind(self, port):
		"""
		TODO: remove comments and see comments in superclass
		Makes sure this port is not in use and attaches it to this socket
		"""
        pass

    def listen(self):
		"""
		Tells this socket that it will be listening for connections
		"""
        pass

    def accept(self):
		"""
		Accepts a connection from some other socket (blocks until other socket tries to connect?)
		"""
        pass

    def connect(self, addr):
		"""
		Initiates connection to some other socket at this address
		"""
        pass

    def send(self, data):
		"""
		Sends data to the socket this one is connected to
		"""
        pass  # probably will call: Protocol.output(seg, host); see also: StreamSocket.recv(self, n=None)


class RDTProtocol(Protocol):
    PROTO_ID = IPPROTO_RDT
    SOCKET_CLS = RDTSocket

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Other initialization here

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
        pass  # probably will call: Protocol.output(self, seg, dst)
