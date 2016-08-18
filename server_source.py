from socket import socket, SO_REUSEADDR, SOL_SOCKET
from asyncio import Task, coroutine, get_event_loop
from peer import Peer

HOST = 'localhost'
PORT = 9090
ADDR = (HOST, PORT)
ENCODING = 'utf-8'
BUFFER_SIZE = 1024


class EventPeer(Peer):
    def on_received(self, bytes):
        self._server.process(bytes)


class Server(object):
    def __init__(self, loop, port, clients):
        self.loop = loop
        self._serv_sock = socket()
        self._serv_sock.setblocking(0)
        self._serv_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self._serv_sock.bind(('', port))
        self._serv_sock.listen(5)
        self._peers = []
        self._clients = clients
        Task(self._server())

    def remove(self, peer):
        print('EventPeer [{0}] quit.'.format(peer.name))
        self._peers.remove(peer)

    def process(self, message):
        print('%s: %s' % (self.name, bytes.decode(ENCODING)))
        self._clients.process(message)

    def broadcast(self, message):
        for peer in self._peers:
            peer.send(message)

    @coroutine
    def _server(self):
        while True:
            peer_sock, peer_name = yield from self.loop.sock_accept(self._serv_sock)
            peer_sock.setblocking(0)
            peer = EventPeer(self, peer_sock, peer_name)
            self._peers.append(peer)

            message = 'Peer %s connected!\n' % (peer.name,)
            print(message)
            self.broadcast(message)


def run_source_server(loop, clients):
    server = Server(loop, 9090, clients)

    print(server)
    return server
