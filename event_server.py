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
    def __init__(self, loop, port, client_server, logger):
        self._client_server = client_server
        self._logger = logger
        super().__init__(loop, port)

    def remove(self, peer):
        self._logger.quit_log(peer)
        super().remove(peer)

    def process(self, peer, message):
        self._logger.event_message_log(peer, message)
        self._client_server.process(message)

    def get_peer(self, peer_sock, peer_name):
        return EventPeer(self, peer_sock, peer_name)

    def on_connected(self, peer):
        self._logger.connect_log(peer)


def run_event_server(loop, client_server, logger):
    server = EventServer(loop, PORT, client_server, logger)
    print(server)
    return server
