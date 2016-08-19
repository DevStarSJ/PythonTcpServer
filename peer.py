from asyncio import Task, coroutine

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
        return \
            self.loop.sock_sendall(self._sock, data.encode(ENCODING)) \
            if type(data) == str \
            else \
                self.loop.sock_sendall(self._sock, data)

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
            self.on_received(buf)

    def on_received(self, bytes):
        pass
