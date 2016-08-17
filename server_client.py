from socket import socket, SO_REUSEADDR, SOL_SOCKET
from asyncio import Task, coroutine, get_event_loop


HOST = 'localhost'
PORT = 9099
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
        return self.loop.sock_sendall(self._sock, data)

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
            id = int(buf.decode(ENCODING))
            print('id',id)
            self._server._clients[self] = id
            print(self._server._clients)


class Server(object):
    def __init__(self, loop, port):
        self.loop = loop
        self._serv_sock = socket()
        self._serv_sock.setblocking(0)
        self._serv_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self._serv_sock.bind(('', port))
        self._serv_sock.listen(5)
        self._peers = []
        self._clients = {}
        self._followers = {}
        Task(self._server())

    def remove(self, peer):
        self._peers.remove(peer)
        if peer in self._clients:
            id = self._clients[peer]

            if id in self._followers:
                del self._followers[id]

            del self._clients[peer]

        print('Peer %s quit!\n' % (peer.name))

    def forward(self, message):
        print('in clients before forward : ', message)
        tokens = message.decode(ENCODING).split('|')

        if len(tokens) < 2:
            return
        
        sequence_number = int(tokens[0])
        event_type = tokens[1]

        if event_type == 'B':
            self.broadcast(sequence_number)
            return

        if len(tokens) < 3:
            return

        from_user_id = int(tokens[2])

        if event_type == 'S':
            pass # 아직 구현전
        
        if len(tokens) < 4:
            return

        to_user_id = int(tokens[3])

        if event_type == 'P':
            self.private_message(to_user_id, sequence_number)
            return
        elif event_type == 'F':
            self.follow(from_user_id, to_user_id, sequence_number)
            return
        
    def private_message(self, id, sequence_number):
        print('print message [%s] : %s' % (str(id), str(sequence_number)))
        message = '[%s] : private message from source.' % (str(sequence_number))
        self.send_message(id, message)

    def broadcast(self, sequence_number):
        message = '[%s] : This is broadcast message' % (str(sequence_number))

        for peer in self._peers:
            peer.send(bytearray(message, ENCODING))

    def follow(self, from_id, to_id, sequence_number):
        if not self.find_id(to_id):
            print('[%s] : Follow failed. [%s] is not connected.' % (str(sequence_number), str(to_id)))
            return

        if from_id in self._followers.keys():
            if not to_id in self._followers[from_id]:
                self._followers[from_id].append(to_id)
        else:
            self._followers[from_id] = [ to_id ]

        message = '[%s] : [%s] follows you.' % (str(sequence_number), str(to_id))
        print(message)
        self.send_message(to_id, message)
        
    def send_message(self, id, message):
        peers = [ p for p, i in self._clients.items() if i == id ]
        if len(peers) > 0:
            peers[0].send(bytearray(message, ENCODING))

    def find_id(self, id):
        peers = [ p for p, i in self._clients.items() if i == id ]
        return len(peers) > 0

    @coroutine
    def _server(self):
        while True:
            peer_sock, peer_name = yield from self.loop.sock_accept(self._serv_sock)
            peer_sock.setblocking(0)
            peer = Peer(self, peer_sock, peer_name)
            self._peers.append(peer)
            print('client peer : ', self._peers)

            message = 'Peer %s connected!\n' % (peer.name,)
            print(message)
            self.broadcast(message)


def run_client_server(loop):
    server = Server(loop, PORT)

    print(server)
    return server

if __name__ == '__main__':
    run_server(PORT)
