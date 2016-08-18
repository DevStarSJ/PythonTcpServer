from peer import Peer
from server import Server


HOST = 'localhost'
PORT = 9090
ADDR = (HOST, PORT)
ENCODING = 'utf-8'
BUFFER_SIZE = 1024


class EventPeer(Peer):
    def on_received(self, bytes):
        self._server.process(self, bytes)


class EventServer(Server):
    def __init__(self, loop, port, clients):
        self._clients = clients
        super().__init__(loop, port)

    def remove(self, peer):
        print('EventPeer [{0}] quit.'.format(peer.name))
        super().remove(peer)

    def process(self, peer, message):
        print('%s: %s' % (peer.name, message.decode(ENCODING)))
        self._clients.process(message)

    def get_peer(self, peer_sock, peer_name):
        return EventPeer(self, peer_sock, peer_name)


def run_source_server(loop, clients):
    server = EventServer(loop, 9090, clients)

    print(server)
    return server
