from socket import socket, SO_REUSEADDR, SOL_SOCKET
from asyncio import Task, coroutine, get_event_loop


HOST = 'localhost'
PORT = 9090
ADDR = (HOST, PORT)
ENCODING = 'utf-8'
BUFFER_SIZE = 1024


class Peer(object):
    def __init__(self, server, sock, name):
        self.loop = server.loop
        self.name = name
        self._sock = sock
        self._server = server
        Task(self._peer_handler())

    def send(self, data):
        return self.loop.sock_sendall(self._sock, data.encode(ENCODING))

    @coroutine
    def _peer_handler(self):
        try:
            yield from self._peer_loop()
        except IOError:
            pass
        finally:
            self._server.remove(self)

    @coroutine
    def _peer_loop(self):
        while True:
            buf = yield from self.loop.sock_recv(self._sock, BUFFER_SIZE)
            if buf == b'':
                break

            message = '%s: %s' % (self.name, buf.decode(ENCODING))

            print(message)
            print('in source to forward')
            self._server._clients.forward(buf)


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
        self._peers.remove(peer)
        self.broadcast('Peer %s quit!\n' % (peer.name))

    def broadcast(self, message):
        for peer in self._peers:
            peer.send(message)

    @coroutine
    def _server(self):
        while True:
            peer_sock, peer_name = yield from self.loop.sock_accept(self._serv_sock)
            peer_sock.setblocking(0)
            peer = Peer(self, peer_sock, peer_name)
            self._peers.append(peer)

            message = 'Peer %s connected!\n' % (peer.name,)
            print(message)
            self.broadcast(message)


def run_source_server(loop, clients):
    server = Server(loop, 9090, clients)

    print(server)
    return server
