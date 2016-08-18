from socket import socket, SO_REUSEADDR, SOL_SOCKET
from asyncio import Task, coroutine
from peer import Peer

class Server(object):
    def __init__(self, loop, port):
        self.loop = loop
        self._serv_sock = socket()
        self._serv_sock.setblocking(0)
        self._serv_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self._serv_sock.bind(('', port))
        self._peers = []

    def listen(self, num_listen):
        self._serv_sock.listen(num_listen)
        Task(self._server())

    def remove(self, peer):
        self._peers.remove(peer)

    def process(self, message):
        pass

    def broadcast(self, message):
        for peer in self._peers:
            peer.send(message)

    @coroutine
    def _server(self):
        while True:
            peer_sock, peer_name = yield from self.loop.sock_accept(self._serv_sock)
            peer_sock.setblocking(0)

            peer = self.get_peer(peer_sock, peer_name)
            self.on_connected(peer)

    def on_connected(self, peer):
        self._peers.append(peer)

        message = 'Peer %s connected!\n' % (peer.name,)
        print(message)
        self.broadcast(message)

    def get_peer(self, peer_sock, peer_name):
        return Peer(self, peer_sock, peer_name)